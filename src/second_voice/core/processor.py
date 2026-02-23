import os
import json
import requests
import logging
from typing import Optional, Dict, Any
from urllib.parse import urljoin
from pathlib import Path

from mellona import SyncMellonaClient, get_config

from ..utils.headers import Header, generate_title, infer_project_name
from ..utils.timestamp import create_whisper_filename

# Set up logging
logger = logging.getLogger(__name__)

class AIProcessor:
    """
    Process audio transcription and language model inference.

    Supports multiple Speech-to-Text and Language Model providers.
    """

    def __init__(self, config):
        """
        Initialize processor with configuration.

        :param config: ConfigurationManager instance containing provider settings
        """
        self.config = config
        self.stt_provider = config.get('stt_provider', 'local_whisper')
        self.llm_provider = config.get('llm_provider', 'ollama')

        # Set up mellona config chain
        # Includes second_voice settings and mellona config
        second_voice_config_path = config.config_path if hasattr(config, 'config_path') else os.path.expanduser('~/.config/second_voice/settings.json')
        mellona_config_path = os.path.expanduser('~/.config/mellona/config.yaml')
        get_config(config_chain=[
            second_voice_config_path,
            mellona_config_path,
        ])

        # API configurations
        self.api_keys = {
            'groq': os.environ.get('GROQ_API_KEY', config.get('groq_api_key', '')),
            'openrouter': os.environ.get('OPENROUTER_API_KEY', config.get('openrouter_api_key', ''))
        }

    def _detect_meta_operation(self, text: str) -> bool:
        """
        Detect if user is asking for a transformation of their own text.

        Returns True if keywords indicating meta-operations are detected:
        outline, summarize, reorder, rearrange, list, bullets, organize

        :param text: User input text
        :return: True if meta-operation keywords detected
        """
        keywords = {'outline', 'summarize', 'reorder', 'rearrange', 'list', 'bullets', 'organize'}
        text_lower = text.lower()
        return any(keyword in text_lower for keyword in keywords)

    def transcribe(self, audio_path: str, recording_timestamp: Optional[str] = None) -> Optional[str]:
        """
        Transcribe audio using configured STT provider.

        :param audio_path: Path to the audio file
        :param recording_timestamp: Optional timestamp from recording for matching whisper file
        :return: Transcribed text or None if transcription fails
        """
        if not os.path.exists(audio_path):
            raise FileNotFoundError(f"Audio file not found: {audio_path}")

        if self.stt_provider == 'groq':
            transcript = self._transcribe_groq(audio_path)
        elif self.stt_provider == 'local_whisper':
            transcript = self._transcribe_local_whisper(audio_path)
        else:
            raise ValueError(f"Unsupported STT provider: {self.stt_provider}")

        # Save whisper output for recovery
        if transcript and recording_timestamp:
            self._save_whisper_output(transcript, recording_timestamp)

        return transcript

    def _save_whisper_output(self, transcript: str, recording_timestamp: str):
        """Save whisper output to file for recovery.

        :param transcript: Transcribed text
        :param recording_timestamp: Timestamp from recording for matching
        """
        temp_dir = self.config.get('temp_dir', './tmp')
        os.makedirs(temp_dir, exist_ok=True)
        whisper_path = create_whisper_filename(temp_dir, recording_timestamp)
        try:
            with open(whisper_path, 'w', encoding='utf-8') as f:
                f.write(transcript)
            logger.info(f"Whisper output saved: {whisper_path}")
            if self.config.get('debug'):
                print(f"Debug: Saved whisper transcript to {whisper_path}")
        except Exception as e:
            logger.warning(f"Could not save whisper output: {e}")
            if self.config.get('debug'):
                print(f"Debug: Failed to save whisper output: {e}")

    def process_with_headers_and_fallback(self, transcript: str, recording_path: Optional[str] = None,
                                          context: Optional[str] = None) -> str:
        """Process transcript with header injection and fallback on LLM failure.

        :param transcript: Raw whisper output
        :param recording_path: Path to recording (for source header)
        :param context: Session context
        :return: LLM output with headers or fallback transcript
        """
        # Parse existing headers if present
        existing_header = Header.from_string(transcript)

        if not existing_header:
            # Build new header
            source = Path(recording_path).name if recording_path else "unknown"
            title = generate_title(transcript)
            project = infer_project_name(transcript)

            header = Header(
                source=source,
                status="Awaiting transformation",
                title=title,
                project=project
            )
        else:
            header = existing_header

        # Prepend header to input
        header_text = header.to_string(include_title=False, include_project=False)
        augmented_transcript = f"{header_text}\n\n{transcript}"

        try:
            # Process with LLM
            result = self.process_text(augmented_transcript, context)

            # Ensure output has headers
            output_header = Header.from_string(result)
            if not output_header:
                # Inject headers into output
                result_header = Header(
                    source=f"second-voice from {header.source}",
                    status="Awaiting ingest",
                    title=generate_title(result),
                    project=infer_project_name(result)
                )
                result = f"{result_header.to_string(True, True)}\n\n{result}"

            return result
        except Exception as e:
            logger.error(f"LLM processing failed: {e}")
            logger.info("Falling back to raw whisper output")

            # Return raw transcript as fallback
            fallback_msg = (
                "⚠️ **Warning**: LLM processing failed, returning raw transcript.\n\n"
                f"Error: {str(e)}\n\n"
                f"---\n\n"
                f"{transcript}"
            )
            return fallback_msg

    def _transcribe_local_whisper(self, audio_path: str) -> Optional[str]:
        """
        Transcribe audio using Local Whisper service via mellona.

        :param audio_path: Path to the audio file
        :return: Transcribed text or None
        """
        try:
            logger.debug(f"Opening audio file: {audio_path}")
            file_size = os.path.getsize(audio_path)
            logger.debug(f"Audio file size: {file_size} bytes")

            with SyncMellonaClient() as client:
                logger.debug(f"Sending transcription request to local_whisper provider via mellona")
                response = client.transcribe(audio_path, provider="local_whisper")
                logger.debug(f"Transcription successful, text length: {len(response.text) if response.text else 0}")
                return response.text
        except Exception as e:
            logger.error(f"Local Whisper transcription error: {type(e).__name__}: {e}")
            print(f"Local Whisper transcription error: {type(e).__name__}: {e}")
            return None

    def _transcribe_groq(self, audio_path: str) -> Optional[str]:
        """
        Transcribe audio using Groq Whisper API via mellona.

        :param audio_path: Path to the audio file
        :return: Transcribed text or None
        """
        model = self.config.get('groq_stt_model', 'whisper-large-v3')
        logger.debug(f"Groq transcription - model: {model}")

        try:
            file_size = os.path.getsize(audio_path)
            logger.debug(f"Opening audio file: {audio_path} ({file_size} bytes)")

            with SyncMellonaClient() as client:
                logger.debug(f"Sending transcription request to Groq provider via mellona")
                response = client.transcribe(audio_path, provider="groq", model=model)
                logger.debug(f"Groq transcription successful, text length: {len(response.text) if response.text else 0}")
                return response.text
        except Exception as e:
            logger.error(f"Groq transcription error: {type(e).__name__}: {e}")
            print(f"Transcription error: {e}")
            return None

    def process_text(self, text: str, context: Optional[str] = None) -> str:
        """
        Process text through LLM with optional context.

        :param text: User input/instruction
        :param context: Optional previous conversation context
        :return: LLM processed output
        """
        if self.llm_provider == 'openrouter':
            return self._process_openrouter(text, context)
        elif self.llm_provider == 'ollama':
            return self._process_ollama(text, context)
        elif self.llm_provider == 'cline':
            return self._process_cline(text, context)
        else:
            raise ValueError(f"Unsupported LLM provider: {self.llm_provider}")

    def _process_cline(self, text: str, context: Optional[str] = None) -> str:
        """
        Process text using Cline CLI provider.

        :param text: User input/instruction
        :param context: Optional previous conversation context
        :return: LLM processed output
        """
        import subprocess
        import shlex

        model = self.config.get('cline_llm_model', 'default-model')
        timeout = self.config.get('cline_timeout', 120)
        api_key = os.environ.get('CLINE_API_KEY', self.config.get('cline_api_key', ''))

        logger.debug(f"Cline CLI config - model: {model}, timeout: {timeout}s")

        # Build system prompt for cleanup operations
        system_prompt = (
            "You are a speech cleanup assistant. Your job is to clean up transcribed speech by:\n"
            "1. Removing stutters and repeated phrases\n"
            "2. Consolidating similar ideas into coherent statements\n"
            "3. Fixing grammar and improving sentence structure\n"
            "4. Maintaining the original meaning and intent\n\n"
            "IMPORTANT: Do NOT answer questions or provide new information. Only clean up the language.\n\n"
            "OUTPUT FORMAT: Output ONLY the cleaned text. No preamble, no introduction, no quotation marks. "
            "Just the cleaned speech itself."
        )

        # Check for meta-operations (outline, summarize, etc.)
        if self._detect_meta_operation(text):
            system_prompt += (
                "\n\nEXCEPTION: If the user's text contains a request to transform their own words "
                "(keywords: outline, summarize, reorder, rearrange, list, bullets, organize), "
                "perform that transformation instead. Still output only the result, no preamble."
            )

        # Build the input with system prompt prepended
        full_input = f"{system_prompt}\n\nUser's transcribed speech:\n{text}"
        if context:
            full_input = f"{system_prompt}\n\nPrevious Context:\n{context}\n\nUser's transcribed speech:\n{text}"

        # Prepare the full CLI command
        cmd_parts = [
            'cline', 'generate',
            '--model', model
        ]

        # Add API key if available
        if api_key:
            cmd_parts.extend(['--api-key', api_key])

        # Add the input text with system prompt
        cmd_parts.extend(['--input', full_input])

        try:
            logger.debug(f"Running Cline CLI command with system prompt")
            result = subprocess.run(
                cmd_parts,
                capture_output=True,
                text=True,
                timeout=timeout
            )

            if result.returncode != 0:
                error_msg = f"Cline CLI error: {result.stderr.strip()}"
                logger.error(error_msg)
                return f"Error: {error_msg}"

            processed_text = result.stdout.strip()
            logger.debug(f"Cline CLI processing successful, response length: {len(processed_text)}")
            return processed_text

        except subprocess.TimeoutExpired:
            error_msg = f"Cline CLI request timeout after {timeout}s"
            logger.error(error_msg)
            print(f"Cline CLI processing error: {error_msg}")
            return f"Error: {error_msg}"
        except Exception as e:
            error_msg = f"Cline CLI processing error: {type(e).__name__}: {e}"
            logger.error(error_msg)
            print(f"Cline CLI processing error: {e}")
            return f"Error processing request: {e}"

    def _process_ollama(self, text: str, context: Optional[str] = None) -> str:
        """
        Process text using local Ollama instance.

        :param text: User input/instruction
        :param context: Optional previous conversation context
        :return: LLM processed output
        """
        url = self.config.get('ollama_url', 'http://localhost:11434/api/generate')
        model = self.config.get('ollama_model', 'llama3')
        timeout = self.config.get('ollama_timeout', 300)

        logger.debug(f"Ollama config - URL: {url}, model: {model}, timeout: {timeout}s")

        # Build system prompt for cleanup operations
        system_prompt = (
            "You are a speech cleanup assistant. Your job is to clean up transcribed speech by:\n"
            "1. Removing stutters and repeated phrases\n"
            "2. Consolidating similar ideas into coherent statements\n"
            "3. Fixing grammar and improving sentence structure\n"
            "4. Maintaining the original meaning and intent\n\n"
            "IMPORTANT: Do NOT answer questions or provide new information. Only clean up the language.\n\n"
            "OUTPUT FORMAT: Output ONLY the cleaned text. No preamble, no introduction, no quotation marks. "
            "Just the cleaned speech itself."
        )

        # Check for meta-operations (outline, summarize, etc.)
        if self._detect_meta_operation(text):
            system_prompt += (
                "\nEXCEPTION: If the user's text contains a request to transform their own words "
                "(keywords: outline, summarize, reorder, rearrange, list, bullets, organize), "
                "perform that transformation instead. Still output only the result, no preamble.\n"
            )

        # Build the full prompt
        if context:
            prompt = f"{system_prompt}\nPrevious Context:\n{context}\n\nUser's transcribed speech:\n{text}"
        else:
            prompt = f"{system_prompt}\nUser's transcribed speech:\n{text}"

        try:
            logger.debug(f"Sending request to Ollama at {url}")
            response = requests.post(
                url,
                json={
                    'model': model,
                    'prompt': prompt,
                    'stream': False
                },
                timeout=timeout
            )
            logger.debug(f"Ollama response: status={response.status_code}")
            response.raise_for_status()
            result = response.json().get('response', '')
            logger.debug(f"Ollama processing successful, response length: {len(result)}")
            return result
        except requests.Timeout as e:
            error_msg = f"Ollama request timeout after {timeout}s"
            logger.error(f"{error_msg}: {e}")
            print(f"Ollama processing error: {error_msg}")
            return f"Error: {error_msg}"
        except requests.ConnectionError as e:
            error_msg = f"Ollama connection failed ({type(e).__name__})"
            logger.error(f"{error_msg}: {e}")
            print(f"Ollama processing error: {error_msg}")
            return f"Error: {error_msg}"
        except requests.RequestException as e:
            logger.error(f"Ollama request error: {type(e).__name__}: {e}")
            print(f"Ollama processing error: {e}")
            return f"Error processing request: {e}"

    def _process_openrouter(self, text: str, context: Optional[str] = None) -> str:
        """
        Process text using OpenRouter LLM with automatic model fallback.

        :param text: User input/instruction
        :param context: Optional previous conversation context
        :return: LLM processed output
        """
        if not self.api_keys['openrouter']:
            raise ValueError("OpenRouter API key not configured")

        timeout = self.config.get('openrouter_timeout', 60)

        # Define fallback model chain - diverse set of FREE models
        # Extracted from OpenRouter's current available free models (29 total)
        # Prioritized by size/quality for text cleanup tasks
        fallback_models = [
            # Tier 1: Large, high-quality models
            'meta-llama/llama-3.3-70b-instruct',        # 70B, excellent quality
            'nousresearch/hermes-3-llama-3.1-405b',     # 405B, state-of-art
            'google/gemma-3-27b-it',                    # 27B, good quality
            'qwen/qwen3-next-80b-a3b-instruct',         # 80B, powerful
            'openai/gpt-oss-120b',                      # 120B, good general purpose

            # Tier 2: Medium-sized reliable models
            'google/gemma-3-12b-it',                    # 12B, good balance
            'mistralai/mistral-small-3.1-24b-instruct', # 24B, fast
            'meta-llama/llama-3.2-3b-instruct',         # 3B, lightweight
            'arcee-ai/trinity-large-preview',           # Large, preview
            'upstage/solar-pro-3',                      # Optimized for text

            # Tier 3: Alternative providers
            'google/gemma-3-4b-it',                     # 4B, very fast
            'openai/gpt-oss-20b',                       # 20B, alternative
            'qwen/qwen3-coder',                         # 480B, coder-optimized
            'z-ai/glm-4.5-air',                         # GLM model, multilingual
            'deepseek/deepseek-r1-0528',                # DeepSeek reasoning

            # Tier 4: Other free options
            'nvidia/nemotron-3-nano-30b-a3b',           # NVIDIA model
            'arcee-ai/trinity-mini',                    # Smaller trinity
            'qwen/qwen3-4b',                            # Qwen small
            'liquid/lfm-2.5-1.2b-instruct',             # LiquidAI small
        ]

        # Get user-configured model and add to front if specified
        user_model = self.config.get('openrouter_llm_model', self.config.get('llm_model'))
        if user_model and user_model not in fallback_models:
            fallback_models.insert(0, user_model)

        model = fallback_models[0]
        logger.debug(f"OpenRouter LLM config - primary model: {model}, timeout: {timeout}s, fallback chain: {len(fallback_models)} models")

        # Build system prompt for cleanup operations
        system_prompt = (
            "You are a speech cleanup assistant. Your job is to clean up transcribed speech by:\n"
            "1. Removing stutters and repeated phrases\n"
            "2. Consolidating similar ideas into coherent statements\n"
            "3. Fixing grammar and improving sentence structure\n"
            "4. Maintaining the original meaning and intent\n\n"
            "IMPORTANT: Do NOT answer questions or provide new information. Only clean up the language.\n\n"
            "OUTPUT FORMAT: Output ONLY the cleaned text. No preamble, no introduction, no quotation marks. "
            "Just the cleaned speech itself."
        )

        # Check for meta-operations (outline, summarize, etc.)
        if self._detect_meta_operation(text):
            system_prompt += (
                "\n\nEXCEPTION: If the user's text contains a request to transform their own words "
                "(keywords: outline, summarize, reorder, rearrange, list, bullets, organize), "
                "perform that transformation instead. Still output only the result, no preamble."
            )

        # Prepare messages with cleanup system prompt and optional context
        messages = [
            {
                "role": "system",
                "content": system_prompt
            }
        ]

        if context:
            messages.append({
                "role": "system",
                "content": f"Previous conversation context: {context}"
            })

        messages.append({
            "role": "user",
            "content": text
        })

        # Try each model in the fallback chain
        last_error = None
        for model_index, model in enumerate(fallback_models):
            try:
                logger.debug(f"Attempting OpenRouter request with model {model_index + 1}/{len(fallback_models)}: {model}")
                response = requests.post(
                    'https://openrouter.ai/api/v1/chat/completions',
                    headers={
                        'Authorization': f'Bearer {self.api_keys["openrouter"]}',
                        'Content-Type': 'application/json'
                    },
                    json={
                        'model': model,
                        'messages': messages
                    },
                    timeout=timeout
                )
                logger.debug(f"OpenRouter response: status={response.status_code}")

                # Log response body for non-200 status codes before raising
                if response.status_code != 200:
                    try:
                        error_body = response.text
                        logger.error(f"OpenRouter API error {response.status_code} with model {model}: {error_body}")
                    except Exception:
                        pass

                response.raise_for_status()
                result = response.json()
                content = result['choices'][0]['message']['content']
                logger.info(f"OpenRouter processing successful with model: {model} (attempt {model_index + 1}/{len(fallback_models)})")
                logger.debug(f"Response length: {len(content)}")

                # Success - print fallback notice if we didn't use the first model
                if model_index > 0:
                    print(f"Note: Used fallback model {model} after {model_index} failure(s)")

                return content

            except requests.HTTPError as e:
                status_code = e.response.status_code if e.response else "unknown"
                error_body = e.response.text if e.response else ""

                # Parse error details for better logging
                if status_code == 401:
                    error_msg = "Invalid or missing OpenRouter API key"
                elif status_code == 404:
                    error_msg = f"Model not found: {model}"
                elif status_code == 429:
                    error_msg = f"Rate limit exceeded for model: {model}"
                else:
                    error_msg = f"API error {status_code} for model {model}"

                logger.warning(f"{error_msg}. Error body: {error_body}")
                last_error = error_msg

                # If this is the last model, don't try more
                if model_index >= len(fallback_models) - 1:
                    break

                # Try next model
                logger.info(f"Trying next fallback model...")
                continue

            except requests.Timeout as e:
                error_msg = f"Request timeout after {timeout}s with model {model}"
                logger.warning(f"{error_msg}: {e}")
                last_error = error_msg

                if model_index >= len(fallback_models) - 1:
                    break
                continue

            except requests.RequestException as e:
                error_msg = f"Request error with model {model}: {type(e).__name__}"
                logger.warning(f"{error_msg}: {e}")
                last_error = error_msg

                if model_index >= len(fallback_models) - 1:
                    break
                continue

        # All models failed - report the error
        error_summary = f"All {len(fallback_models)} OpenRouter models failed. Last error: {last_error}"
        logger.error(error_summary)
        print(f"LLM processing error: {error_summary}")
        return f"Error: {error_summary}"

    def process_document_creation(self, transcript: str, recording_path: Optional[str] = None,
                                  project: Optional[str] = None) -> str:
        """
        Process transcript into a structured markdown document.

        Uses a specialized system prompt focused on document organization rather than cleanup.

        :param transcript: Raw transcribed text
        :param recording_path: Path to the recording (for metadata)
        :param project: Optional project name for metadata
        :return: Structured markdown document with headers and formatting
        """
        # Build document system prompt
        system_prompt = """You are a document structuring assistant.
The user has spoken freely about a topic or ideas.

Your job is to:
1. Extract the main topic (becomes document title)
2. Identify 3-5 key sections or themes
3. List specific points under each section as bullet points
4. Organize logically (chronologically, by importance, or by theme)
5. Clean up grammar and remove speech artifacts (ums, ahs, stutters)
6. Keep the user's original meaning and intent intact

OUTPUT FORMAT:
- Use markdown formatting
- Start with # Title (one H1)
- Use ## Section Headers for each topic (H2)
- Use - bullet points for details
- Use paragraphs when topic needs explanation
- No metadata, no preamble, just the document

IMPORTANT: Output ONLY the markdown document.
Do not include explanations or instructions.
The document should be ready to save immediately."""

        # Prepare augmented input with system prompt
        full_input = f"{system_prompt}\n\nSpoken content to structure:\n{transcript}"

        try:
            # Process with LLM using document prompt (not cleanup prompt)
            result = self._process_with_document_prompt(full_input)

            if not result:
                logger.error("Document processing returned empty result")
                return None

            # Inject metadata headers
            source = Path(recording_path).name if recording_path else "voice-input"
            title = generate_title(result)
            inferred_project = project or infer_project_name(result)

            header = Header(
                source=source,
                status="Structured from voice",
                title=title,
                project=inferred_project
            )

            # Prepend header to structured document
            header_text = header.to_string(include_title=True, include_project=True)
            final_doc = f"{header_text}\n\n{result}"

            return final_doc

        except Exception as e:
            logger.error(f"Document creation failed: {e}")
            # Fallback: return raw transcript with error header
            fallback_msg = (
                f"⚠️ **Warning**: Document structuring failed, returning raw transcript.\n\n"
                f"Error: {str(e)}\n\n"
                f"---\n\n"
                f"{transcript}"
            )
            return fallback_msg

    def _process_with_document_prompt(self, text: str) -> str:
        """
        Process text through LLM with document structuring prompt.

        Routes to appropriate LLM provider configured in self.llm_provider.

        :param text: Full input including system prompt and content
        :return: Structured document output
        """
        if self.llm_provider == 'openrouter':
            return self._process_openrouter_document(text)
        elif self.llm_provider == 'ollama':
            return self._process_ollama_document(text)
        elif self.llm_provider == 'cline':
            return self._process_cline_document(text)
        else:
            raise ValueError(f"Unsupported LLM provider: {self.llm_provider}")

    def _process_ollama_document(self, text: str) -> str:
        """Process document using local Ollama instance."""
        url = self.config.get('ollama_url', 'http://localhost:11434/api/generate')
        model = self.config.get('ollama_model', 'llama3')
        timeout = self.config.get('ollama_timeout', 300)

        logger.debug(f"Ollama document processing - URL: {url}, model: {model}, timeout: {timeout}s")

        try:
            logger.debug(f"Sending document request to Ollama at {url}")
            response = requests.post(
                url,
                json={
                    'model': model,
                    'prompt': text,
                    'stream': False
                },
                timeout=timeout
            )
            logger.debug(f"Ollama response: status={response.status_code}")
            response.raise_for_status()
            result = response.json().get('response', '')
            logger.debug(f"Ollama document processing successful, response length: {len(result)}")
            return result
        except requests.Timeout as e:
            error_msg = f"Ollama request timeout after {timeout}s"
            logger.error(f"{error_msg}: {e}")
            raise
        except Exception as e:
            logger.error(f"Ollama document processing error: {type(e).__name__}: {e}")
            raise

    def _process_cline_document(self, text: str) -> str:
        """Process document using Cline CLI provider."""
        import subprocess
        import shlex

        model = self.config.get('cline_llm_model', 'default-model')
        timeout = self.config.get('cline_timeout', 120)
        api_key = os.environ.get('CLINE_API_KEY', self.config.get('cline_api_key', ''))

        logger.debug(f"Cline CLI document processing - model: {model}, timeout: {timeout}s")

        cmd_parts = [
            'cline', 'generate',
            '--model', model
        ]

        if api_key:
            cmd_parts.extend(['--api-key', api_key])

        cmd_parts.extend(['--input', text])

        try:
            logger.debug(f"Running Cline CLI command for document processing")
            result = subprocess.run(
                cmd_parts,
                capture_output=True,
                text=True,
                timeout=timeout
            )

            if result.returncode != 0:
                error_msg = f"Cline CLI error: {result.stderr.strip()}"
                logger.error(error_msg)
                raise RuntimeError(error_msg)

            processed_text = result.stdout.strip()
            logger.debug(f"Cline document processing successful, response length: {len(processed_text)}")
            return processed_text

        except subprocess.TimeoutExpired:
            error_msg = f"Cline CLI request timeout after {timeout}s"
            logger.error(error_msg)
            raise
        except Exception as e:
            logger.error(f"Cline document processing error: {type(e).__name__}: {e}")
            raise

    def _process_openrouter_document(self, text: str) -> str:
        """Process document using OpenRouter with fallback models."""
        if not self.api_keys['openrouter']:
            raise ValueError("OpenRouter API key not configured")

        timeout = self.config.get('openrouter_timeout', 60)

        # Same fallback models as regular processing
        fallback_models = [
            'meta-llama/llama-3.3-70b-instruct',
            'nousresearch/hermes-3-llama-3.1-405b',
            'google/gemma-3-27b-it',
            'qwen/qwen3-next-80b-a3b-instruct',
            'openai/gpt-oss-120b',
            'google/gemma-3-12b-it',
            'mistralai/mistral-small-3.1-24b-instruct',
            'meta-llama/llama-3.2-3b-instruct',
            'arcee-ai/trinity-large-preview',
            'upstage/solar-pro-3',
        ]

        user_model = self.config.get('openrouter_llm_model', self.config.get('llm_model'))
        if user_model and user_model not in fallback_models:
            fallback_models.insert(0, user_model)

        logger.debug(f"OpenRouter document processing - primary model: {fallback_models[0]}, fallback chain: {len(fallback_models)} models")

        last_error = None
        for model_index, model in enumerate(fallback_models):
            try:
                logger.debug(f"Attempting OpenRouter document request with model {model_index + 1}/{len(fallback_models)}: {model}")
                response = requests.post(
                    'https://openrouter.ai/api/v1/chat/completions',
                    headers={
                        'Authorization': f'Bearer {self.api_keys["openrouter"]}',
                        'Content-Type': 'application/json'
                    },
                    json={
                        'model': model,
                        'messages': [{'role': 'user', 'content': text}]
                    },
                    timeout=timeout
                )
                logger.debug(f"OpenRouter response: status={response.status_code}")
                response.raise_for_status()
                result = response.json()
                content = result['choices'][0]['message']['content']
                logger.info(f"OpenRouter document processing successful with model: {model} (attempt {model_index + 1}/{len(fallback_models)})")
                return content

            except requests.HTTPError as e:
                status_code = e.response.status_code if e.response else "unknown"
                logger.warning(f"OpenRouter API error {status_code} with model {model}")
                last_error = f"API error {status_code}"

                if model_index >= len(fallback_models) - 1:
                    break
                continue

            except requests.Timeout:
                error_msg = f"Request timeout after {timeout}s with model {model}"
                logger.warning(error_msg)
                last_error = error_msg

                if model_index >= len(fallback_models) - 1:
                    break
                continue

            except requests.RequestException as e:
                error_msg = f"Request error with model {model}: {type(e).__name__}"
                logger.warning(error_msg)
                last_error = error_msg

                if model_index >= len(fallback_models) - 1:
                    break
                continue

        error_summary = f"All {len(fallback_models)} OpenRouter models failed. Last error: {last_error}"
        logger.error(error_summary)
        raise RuntimeError(error_summary)

    def save_context(self, context: str, max_context_length: int = 1000):
        """
        Save context to a temporary file in the configured temp directory.

        :param context: Context text to save
        :param max_context_length: Maximum length of context to retain
        """
        temp_dir = self.config.get('temp_dir', './tmp')
        context_path = os.path.join(temp_dir, 'tmp-context.txt')
        
        # Truncate context if needed
        truncated_context = context[-max_context_length:]
        
        with open(context_path, 'w') as f:
            f.write(truncated_context)

    def load_context(self) -> Optional[str]:
        """
        Load the most recent context from temporary files.

        :return: Loaded context or None
        """
        temp_dir = self.config.get('temp_dir', './tmp')
        context_path = os.path.join(temp_dir, 'tmp-context.txt')
        
        try:
            with open(context_path, 'r') as f:
                return f.read()
        except FileNotFoundError:
            return None

    def clear_context(self):
        """
        Clear the saved context.
        """
        self.save_context('')
