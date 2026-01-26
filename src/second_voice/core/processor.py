import os
import json
import requests
import logging
from typing import Optional, Dict, Any
from urllib.parse import urljoin

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

        :param config: Configuration dictionary containing provider settings
        """
        self.config = config
        self.stt_provider = config.get('stt_provider', 'local_whisper')
        self.llm_provider = config.get('llm_provider', 'ollama')
        
        # API configurations
        self.api_keys = {
            'groq': os.environ.get('GROQ_API_KEY', config.get('groq_api_key', '')),
            'openrouter': os.environ.get('OPENROUTER_API_KEY', config.get('openrouter_api_key', ''))
        }

    def transcribe(self, audio_path: str) -> Optional[str]:
        """
        Transcribe audio using configured STT provider.

        :param audio_path: Path to the audio file
        :return: Transcribed text or None if transcription fails
        """
        if not os.path.exists(audio_path):
            raise FileNotFoundError(f"Audio file not found: {audio_path}")

        if self.stt_provider == 'groq':
            return self._transcribe_groq(audio_path)
        elif self.stt_provider == 'local_whisper':
            return self._transcribe_local_whisper(audio_path)
        else:
            raise ValueError(f"Unsupported STT provider: {self.stt_provider}")

    def _transcribe_local_whisper(self, audio_path: str) -> Optional[str]:
        """
        Transcribe audio using Local Whisper service.

        :param audio_path: Path to the audio file
        :return: Transcribed text or None
        """
        url = self.config.get('local_whisper_url', 'http://localhost:9090/v1/audio/transcriptions')
        timeout = self.config.get('local_whisper_timeout', 60)

        logger.debug(f"Whisper config - URL: {url}, timeout: {timeout}s")

        # First, check if the service is reachable
        health_url = url.replace('/v1/audio/transcriptions', '/health')
        logger.debug(f"Checking Whisper service health at {health_url}...")
        try:
            health_response = requests.get(health_url, timeout=5)
            logger.debug(f"Whisper health check: {health_response.status_code}")
        except requests.RequestException as health_error:
            logger.warning(f"Whisper service health check failed: {type(health_error).__name__}: {health_error}")
            print(f"Local Whisper transcription error: Service unavailable ({type(health_error).__name__})")
            return None

        try:
            logger.debug(f"Opening audio file: {audio_path}")
            file_size = os.path.getsize(audio_path)
            logger.debug(f"Audio file size: {file_size} bytes")

            with open(audio_path, 'rb') as audio_file:
                logger.debug(f"Sending transcription request to {url}")
                response = requests.post(
                    url,
                    files={'file': audio_file},
                    data={'model': 'whisper-1'},
                    timeout=timeout
                )
                logger.debug(f"Received response: status={response.status_code}")
                response.raise_for_status()
                result = response.json().get('text', None)
                logger.debug(f"Transcription successful, text length: {len(result) if result else 0}")
                return result
        except requests.Timeout as e:
            logger.error(f"Whisper request timeout after {timeout}s: {e}")
            print(f"Local Whisper transcription error: Request timeout (exceeded {timeout}s)")
            return None
        except requests.ConnectionError as e:
            logger.error(f"Whisper connection error: {type(e).__name__}: {e}")
            print(f"Local Whisper transcription error: Connection failed ({type(e).__name__})")
            return None
        except requests.RequestException as e:
            logger.error(f"Whisper request error: {type(e).__name__}: {e}")
            print(f"Local Whisper transcription error: {type(e).__name__}: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error during transcription: {type(e).__name__}: {e}")
            print(f"Local Whisper transcription error: Unexpected error: {type(e).__name__}: {e}")
            return None

    def _transcribe_groq(self, audio_path: str) -> Optional[str]:
        """
        Transcribe audio using Groq Whisper API.

        :param audio_path: Path to the audio file
        :return: Transcribed text or None
        """
        if not self.api_keys['groq']:
            raise ValueError("Groq API key not configured")

        timeout = self.config.get('groq_timeout', 60)
        model = self.config.get('groq_stt_model', 'whisper-large-v3')
        logger.debug(f"Groq transcription - model: {model}, timeout: {timeout}s")

        try:
            file_size = os.path.getsize(audio_path)
            logger.debug(f"Opening audio file: {audio_path} ({file_size} bytes)")

            with open(audio_path, 'rb') as audio_file:
                logger.debug(f"Sending transcription request to Groq API")
                # Use OpenAI-compatible endpoint
                response = requests.post(
                    'https://api.groq.com/openai/v1/audio/transcriptions',
                    headers={
                        'Authorization': f'Bearer {self.api_keys["groq"]}'
                    },
                    files={
                        'file': (os.path.basename(audio_path), audio_file, 'audio/wav')
                    },
                    data={
                        'model': model
                    },
                    timeout=timeout
                )
                logger.debug(f"Groq response: status={response.status_code}")
                response.raise_for_status()
                result = response.json().get('text', None)
                logger.debug(f"Groq transcription successful, text length: {len(result) if result else 0}")
                return result
        except requests.Timeout as e:
            logger.error(f"Groq request timeout after {timeout}s: {e}")
            print(f"Transcription error: Request timeout (exceeded {timeout}s)")
            return None
        except requests.RequestException as e:
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

        # Prepare the full CLI command
        cmd_parts = [
            'cline', 'generate',
            '--model', model
        ]

        # Add API key if available
        if api_key:
            cmd_parts.extend(['--api-key', api_key])

        # Add context if available
        if context:
            cmd_parts.extend(['--context', context])

        # Add the input text
        cmd_parts.extend(['--input', text])

        try:
            logger.debug(f"Running Cline CLI command: {' '.join(shlex.quote(part) for part in cmd_parts)}")
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

        prompt = text
        if context:
            prompt = f"Previous Context:\n{context}\n\nInstruction:\n{text}"

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
        Process text using OpenRouter LLM.

        :param text: User input/instruction
        :param context: Optional previous conversation context
        :return: LLM processed output
        """
        if not self.api_keys['openrouter']:
            raise ValueError("OpenRouter API key not configured")

        timeout = self.config.get('openrouter_timeout', 60)
        model = self.config.get('openrouter_llm_model', self.config.get('llm_model', 'openai/gpt-oss-120b:free'))
        logger.debug(f"OpenRouter LLM config - model: {model}, timeout: {timeout}s")

        try:
            # Prepare messages with optional context
            messages = []
            if context:
                messages.append({
                    "role": "system",
                    "content": f"Previous conversation context: {context}"
                })

            messages.append({
                "role": "user",
                "content": text
            })

            logger.debug(f"Sending request to OpenRouter API with model: {model}")
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
            response.raise_for_status()
            result = response.json()
            content = result['choices'][0]['message']['content']
            logger.debug(f"OpenRouter processing successful, response length: {len(content)}")
            return content
        except requests.Timeout as e:
            error_msg = f"OpenRouter request timeout after {timeout}s"
            logger.error(f"{error_msg}: {e}")
            print(f"LLM processing error: {error_msg}")
            return f"Error: {error_msg}"
        except requests.RequestException as e:
            logger.error(f"OpenRouter request error: {type(e).__name__}: {e}")
            print(f"LLM processing error: {e}")
            return f"Error processing request: {e}"

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
