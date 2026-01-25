import os
import json
import requests
from typing import Optional, Dict, Any

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
        try:
            with open(audio_path, 'rb') as audio_file:
                response = requests.post(
                    url,
                    files={'file': audio_file},
                    data={'model': 'whisper-1'} # Default model expected by some local servers
                )
                response.raise_for_status()
                return response.json().get('text', None)
        except requests.RequestException as e:
            print(f"Local Whisper transcription error: {e}")
            return None

    def _transcribe_groq(self, audio_path: str) -> Optional[str]:
        """
        Transcribe audio using Groq Whisper API.

        :param audio_path: Path to the audio file
        :return: Transcribed text or None
        """
        if not self.api_keys['groq']:
            raise ValueError("Groq API key not configured")

        try:
            with open(audio_path, 'rb') as audio_file:
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
                        'model': self.config.get('groq_stt_model', 'whisper-large-v3')
                    }
                )
                response.raise_for_status()
                return response.json().get('text', None)
        except requests.RequestException as e:
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
        else:
            raise ValueError(f"Unsupported LLM provider: {self.llm_provider}")

    def _process_ollama(self, text: str, context: Optional[str] = None) -> str:
        """
        Process text using local Ollama instance.

        :param text: User input/instruction
        :param context: Optional previous conversation context
        :return: LLM processed output
        """
        url = self.config.get('ollama_url', 'http://localhost:11434/api/generate')
        model = self.config.get('ollama_model', 'llama3')
        
        prompt = text
        if context:
            prompt = f"Previous Context:\n{context}\n\nInstruction:\n{text}"

        try:
            response = requests.post(
                url,
                json={
                    'model': model,
                    'prompt': prompt,
                    'stream': False
                }
            )
            response.raise_for_status()
            return response.json().get('response', '')
        except requests.RequestException as e:
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

            response = requests.post(
                'https://openrouter.ai/api/v1/chat/completions',
                headers={
                    'Authorization': f'Bearer {self.api_keys["openrouter"]}',
                    'Content-Type': 'application/json'
                },
                json={
                    'model': self.config.get('openrouter_llm_model', self.config.get('llm_model', 'openai/gpt-oss-120b:free')),
                    'messages': messages
                }
            )
            response.raise_for_status()
            result = response.json()
            return result['choices'][0]['message']['content']
        except requests.RequestException as e:
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
