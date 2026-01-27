"""
Unit tests for AIProcessor.
Tests transcription, LLM processing, and context management with mocked APIs.
"""
import os
import pytest
from unittest import mock
from pathlib import Path

from second_voice.core.processor import AIProcessor


class TestProcessorInitialization:
    """Test AIProcessor initialization."""

    def test_processor_init_default_providers(self):
        """Initialize processor with default providers."""
        config = {
            'stt_provider': 'local_whisper',
            'llm_provider': 'ollama'
        }

        processor = AIProcessor(config)

        assert processor.stt_provider == 'local_whisper'
        assert processor.llm_provider == 'ollama'

    def test_processor_init_custom_providers(self):
        """Initialize processor with custom providers."""
        config = {
            'stt_provider': 'groq',
            'llm_provider': 'openrouter'
        }

        processor = AIProcessor(config)

        assert processor.stt_provider == 'groq'
        assert processor.llm_provider == 'openrouter'

    def test_processor_loads_groq_api_key_from_env(self):
        """Load Groq API key from environment variable."""
        with mock.patch.dict(os.environ, {'GROQ_API_KEY': 'test-groq-key'}):
            config = {'stt_provider': 'local_whisper', 'llm_provider': 'ollama'}
            processor = AIProcessor(config)

        assert processor.api_keys['groq'] == 'test-groq-key'

    def test_processor_loads_groq_api_key_from_config(self):
        """Load Groq API key from config if not in environment."""
        with mock.patch.dict(os.environ, {}, clear=True):
            config = {
                'stt_provider': 'local_whisper',
                'llm_provider': 'ollama',
                'groq_api_key': 'config-groq-key'
            }
            processor = AIProcessor(config)

        assert processor.api_keys['groq'] == 'config-groq-key'

    def test_processor_env_overrides_config_groq_key(self):
        """Environment variable takes precedence over config for Groq key."""
        with mock.patch.dict(os.environ, {'GROQ_API_KEY': 'env-key'}):
            config = {
                'stt_provider': 'local_whisper',
                'llm_provider': 'ollama',
                'groq_api_key': 'config-key'
            }
            processor = AIProcessor(config)

        assert processor.api_keys['groq'] == 'env-key'

    def test_processor_loads_openrouter_api_key_from_env(self):
        """Load OpenRouter API key from environment variable."""
        with mock.patch.dict(os.environ, {'OPENROUTER_API_KEY': 'test-openrouter-key'}):
            config = {'stt_provider': 'local_whisper', 'llm_provider': 'ollama'}
            processor = AIProcessor(config)

        assert processor.api_keys['openrouter'] == 'test-openrouter-key'


class TestLocalWhisperTranscription:
    """Test transcription with local Whisper service."""

    def test_transcribe_local_whisper_success(self, mock_audio_file, requests_mock):
        """Successfully transcribe audio with local Whisper."""
        # Mock health check endpoint
        requests_mock.get(
            'http://localhost:9090/health',
            json={'status': 'ok'}
        )
        # Mock transcription endpoint
        requests_mock.post(
            'http://localhost:9090/v1/audio/transcriptions',
            json={'text': 'Hello, this is a test'}
        )

        config = {
            'stt_provider': 'local_whisper',
            'llm_provider': 'ollama',
            'local_whisper_url': 'http://localhost:9090/v1/audio/transcriptions'
        }
        processor = AIProcessor(config)

        result = processor.transcribe(str(mock_audio_file))

        assert result == 'Hello, this is a test'

    def test_transcribe_local_whisper_custom_url(self, mock_audio_file, requests_mock):
        """Use custom Whisper service URL."""
        # Mock health check endpoint (GET to same URL since replace won't match)
        requests_mock.get(
            'http://custom:8000/transcribe',
            json={'status': 'ok'}
        )
        # Mock transcription endpoint
        requests_mock.post(
            'http://custom:8000/transcribe',
            json={'text': 'Custom service'}
        )

        config = {
            'stt_provider': 'local_whisper',
            'llm_provider': 'ollama',
            'local_whisper_url': 'http://custom:8000/transcribe'
        }
        processor = AIProcessor(config)

        result = processor.transcribe(str(mock_audio_file))

        assert result == 'Custom service'

    def test_transcribe_local_whisper_network_error(self, mock_audio_file):
        """Handle network error gracefully."""
        import requests as req_module
        config = {
            'stt_provider': 'local_whisper',
            'llm_provider': 'ollama'
        }
        processor = AIProcessor(config)

        with mock.patch("second_voice.core.processor.requests.post",
                       side_effect=req_module.RequestException("Connection refused")):
            result = processor.transcribe(str(mock_audio_file))

        assert result is None

    def test_transcribe_local_whisper_http_error(self, mock_audio_file, requests_mock):
        """Handle HTTP error gracefully."""
        # Mock health check endpoint
        requests_mock.get(
            'http://localhost:9090/health',
            json={'status': 'ok'}
        )
        # Mock transcription endpoint with error
        requests_mock.post(
            'http://localhost:9090/v1/audio/transcriptions',
            status_code=500,
            json={'error': 'Server error'}
        )

        config = {
            'stt_provider': 'local_whisper',
            'llm_provider': 'ollama'
        }
        processor = AIProcessor(config)

        result = processor.transcribe(str(mock_audio_file))

        assert result is None

    def test_transcribe_file_not_found(self):
        """Raise error when audio file doesn't exist."""
        config = {
            'stt_provider': 'local_whisper',
            'llm_provider': 'ollama'
        }
        processor = AIProcessor(config)

        with pytest.raises(FileNotFoundError):
            processor.transcribe('/nonexistent/audio.wav')


class TestGroqTranscription:
    """Test transcription with Groq API."""

    def test_transcribe_groq_success(self, mock_audio_file, requests_mock):
        """Successfully transcribe audio with Groq API."""
        requests_mock.post(
            'https://api.groq.com/openai/v1/audio/transcriptions',
            json={'text': 'Groq transcription result'}
        )

        config = {
            'stt_provider': 'groq',
            'llm_provider': 'ollama',
            'groq_api_key': 'test-key',
            'groq_stt_model': 'whisper-large-v3'
        }
        processor = AIProcessor(config)

        result = processor.transcribe(str(mock_audio_file))

        assert result == 'Groq transcription result'

    def test_transcribe_groq_missing_api_key(self, mock_audio_file):
        """Raise error when Groq API key is missing."""
        config = {
            'stt_provider': 'groq',
            'llm_provider': 'ollama'
            # No API key provided
        }
        processor = AIProcessor(config)

        with pytest.raises(ValueError, match="Groq API key not configured"):
            processor.transcribe(str(mock_audio_file))

    def test_transcribe_groq_custom_model(self, mock_audio_file, requests_mock):
        """Use custom Groq model."""
        requests_mock.post(
            'https://api.groq.com/openai/v1/audio/transcriptions',
            json={'text': 'Result'}
        )

        config = {
            'stt_provider': 'groq',
            'llm_provider': 'ollama',
            'groq_api_key': 'test-key',
            'groq_stt_model': 'whisper-medium'
        }
        processor = AIProcessor(config)

        result = processor.transcribe(str(mock_audio_file))

        # Check that request was made with custom model
        assert len(requests_mock.request_history) > 0

    def test_transcribe_groq_api_error(self, mock_audio_file, requests_mock):
        """Handle Groq API error gracefully."""
        requests_mock.post(
            'https://api.groq.com/openai/v1/audio/transcriptions',
            status_code=401,
            json={'error': 'Unauthorized'}
        )

        config = {
            'stt_provider': 'groq',
            'llm_provider': 'ollama',
            'groq_api_key': 'invalid-key'
        }
        processor = AIProcessor(config)

        result = processor.transcribe(str(mock_audio_file))

        assert result is None


class TestTranscriptionDispatch:
    """Test transcription provider selection."""

    def test_transcribe_invalid_provider(self, mock_audio_file):
        """Raise error for unsupported STT provider."""
        config = {
            'stt_provider': 'unknown_provider',
            'llm_provider': 'ollama'
        }
        processor = AIProcessor(config)

        with pytest.raises(ValueError, match="Unsupported STT provider"):
            processor.transcribe(str(mock_audio_file))

    def test_transcribe_dispatches_to_groq(self, mock_audio_file, requests_mock):
        """Dispatch to Groq provider when configured."""
        requests_mock.post(
            'https://api.groq.com/openai/v1/audio/transcriptions',
            json={'text': 'Groq result'}
        )

        config = {
            'stt_provider': 'groq',
            'llm_provider': 'ollama',
            'groq_api_key': 'test'
        }
        processor = AIProcessor(config)

        result = processor.transcribe(str(mock_audio_file))

        assert result == 'Groq result'

    def test_transcribe_dispatches_to_local_whisper(self, mock_audio_file, requests_mock):
        """Dispatch to local Whisper provider when configured."""
        # Mock health check endpoint
        requests_mock.get(
            'http://localhost:9090/health',
            json={'status': 'ok'}
        )
        # Mock transcription endpoint
        requests_mock.post(
            'http://localhost:9090/v1/audio/transcriptions',
            json={'text': 'Whisper result'}
        )

        config = {
            'stt_provider': 'local_whisper',
            'llm_provider': 'ollama'
        }
        processor = AIProcessor(config)

        result = processor.transcribe(str(mock_audio_file))

        assert result == 'Whisper result'


class TestOllamaProcessing:
    """Test LLM processing with Ollama."""

    def test_process_text_ollama_success(self, requests_mock):
        """Successfully process text with Ollama."""
        requests_mock.post(
            'http://localhost:11434/api/generate',
            json={'response': 'Ollama response'}
        )

        config = {
            'stt_provider': 'local_whisper',
            'llm_provider': 'ollama',
            'ollama_url': 'http://localhost:11434/api/generate',
            'ollama_model': 'llama2'
        }
        processor = AIProcessor(config)

        result = processor.process_text('Hello, how are you?')

        assert result == 'Ollama response'

    def test_process_text_ollama_with_context(self, requests_mock):
        """Process text with Ollama including context."""
        requests_mock.post(
            'http://localhost:11434/api/generate',
            json={'response': 'Response with context'}
        )

        config = {
            'stt_provider': 'local_whisper',
            'llm_provider': 'ollama'
        }
        processor = AIProcessor(config)

        result = processor.process_text('Question', context='Previous answer')

        # Check that request was made
        assert len(requests_mock.request_history) > 0

    def test_process_text_ollama_custom_url(self, requests_mock):
        """Use custom Ollama service URL."""
        requests_mock.post(
            'http://custom-ollama:11434/generate',
            json={'response': 'Custom response'}
        )

        config = {
            'stt_provider': 'local_whisper',
            'llm_provider': 'ollama',
            'ollama_url': 'http://custom-ollama:11434/generate'
        }
        processor = AIProcessor(config)

        result = processor.process_text('Test')

        assert result == 'Custom response'

    def test_process_text_ollama_network_error(self):
        """Handle Ollama network error gracefully."""
        import requests as req_module
        config = {
            'stt_provider': 'local_whisper',
            'llm_provider': 'ollama',
            'ollama_url': 'http://unreachable:11434/api/generate'
        }
        processor = AIProcessor(config)

        with mock.patch("second_voice.core.processor.requests.post",
                       side_effect=req_module.RequestException("Connection refused")):
            result = processor.process_text('Test')

        assert "Error" in result

    def test_process_text_ollama_http_error(self, requests_mock):
        """Handle Ollama HTTP error gracefully."""
        requests_mock.post(
            'http://localhost:11434/api/generate',
            status_code=500,
            json={'error': 'Server error'}
        )

        config = {
            'stt_provider': 'local_whisper',
            'llm_provider': 'ollama'
        }
        processor = AIProcessor(config)

        result = processor.process_text('Test')

        assert "Error" in result


class TestOpenRouterProcessing:
    """Test LLM processing with OpenRouter."""

    def test_process_text_openrouter_success(self, requests_mock):
        """Successfully process text with OpenRouter."""
        requests_mock.post(
            'https://openrouter.ai/api/v1/chat/completions',
            json={
                'choices': [{'message': {'content': 'OpenRouter response'}}]
            }
        )

        config = {
            'stt_provider': 'local_whisper',
            'llm_provider': 'openrouter',
            'openrouter_api_key': 'test-key'
        }
        processor = AIProcessor(config)

        result = processor.process_text('Hello')

        assert result == 'OpenRouter response'

    def test_process_text_openrouter_with_context(self, requests_mock):
        """Process text with OpenRouter including context."""
        requests_mock.post(
            'https://openrouter.ai/api/v1/chat/completions',
            json={
                'choices': [{'message': {'content': 'Response with context'}}]
            }
        )

        config = {
            'stt_provider': 'local_whisper',
            'llm_provider': 'openrouter',
            'openrouter_api_key': 'test-key'
        }
        processor = AIProcessor(config)

        result = processor.process_text('Question', context='Previous context')

        assert result == 'Response with context'

    def test_process_text_openrouter_missing_api_key(self):
        """Raise error when OpenRouter API key is missing."""
        config = {
            'stt_provider': 'local_whisper',
            'llm_provider': 'openrouter'
            # No API key provided
        }
        processor = AIProcessor(config)

        with pytest.raises(ValueError, match="OpenRouter API key not configured"):
            processor.process_text('Test')

    def test_process_text_openrouter_custom_model(self, requests_mock):
        """Use custom OpenRouter model."""
        requests_mock.post(
            'https://openrouter.ai/api/v1/chat/completions',
            json={
                'choices': [{'message': {'content': 'Response'}}]
            }
        )

        config = {
            'stt_provider': 'local_whisper',
            'llm_provider': 'openrouter',
            'openrouter_api_key': 'test-key',
            'openrouter_llm_model': 'custom/model'
        }
        processor = AIProcessor(config)

        result = processor.process_text('Test')

        # Check that request was made
        assert len(requests_mock.request_history) > 0

    def test_process_text_openrouter_api_error(self, requests_mock):
        """Handle OpenRouter API error gracefully."""
        requests_mock.post(
            'https://openrouter.ai/api/v1/chat/completions',
            status_code=401,
            json={'error': 'Unauthorized'}
        )

        config = {
            'stt_provider': 'local_whisper',
            'llm_provider': 'openrouter',
            'openrouter_api_key': 'invalid-key'
        }
        processor = AIProcessor(config)

        result = processor.process_text('Test')

        assert "Error" in result


class TestLLMProcessingDispatch:
    """Test LLM processing provider selection."""

    def test_process_text_invalid_provider(self):
        """Raise error for unsupported LLM provider."""
        config = {
            'stt_provider': 'local_whisper',
            'llm_provider': 'unknown_provider'
        }
        processor = AIProcessor(config)

        with pytest.raises(ValueError, match="Unsupported LLM provider"):
            processor.process_text('Test')

    def test_process_text_dispatches_to_ollama(self, requests_mock):
        """Dispatch to Ollama when configured."""
        requests_mock.post(
            'http://localhost:11434/api/generate',
            json={'response': 'Ollama'}
        )

        config = {
            'stt_provider': 'local_whisper',
            'llm_provider': 'ollama'
        }
        processor = AIProcessor(config)

        result = processor.process_text('Test')

        assert result == 'Ollama'

    def test_process_text_dispatches_to_openrouter(self, requests_mock):
        """Dispatch to OpenRouter when configured."""
        requests_mock.post(
            'https://openrouter.ai/api/v1/chat/completions',
            json={'choices': [{'message': {'content': 'OpenRouter'}}]}
        )

        config = {
            'stt_provider': 'local_whisper',
            'llm_provider': 'openrouter',
            'openrouter_api_key': 'test'
        }
        processor = AIProcessor(config)

        result = processor.process_text('Test')

        assert result == 'OpenRouter'


class TestContextManagement:
    """Test context saving and loading."""

    def test_save_context(self, temp_dir):
        """Save context to file."""
        config = {
            'stt_provider': 'local_whisper',
            'llm_provider': 'ollama',
            'temp_dir': str(temp_dir)
        }
        processor = AIProcessor(config)

        processor.save_context('This is my context')

        context_file = temp_dir / 'tmp-context.txt'
        assert context_file.exists()
        assert context_file.read_text() == 'This is my context'

    def test_load_context(self, temp_dir):
        """Load context from file."""
        config = {
            'stt_provider': 'local_whisper',
            'llm_provider': 'ollama',
            'temp_dir': str(temp_dir)
        }
        processor = AIProcessor(config)

        processor.save_context('Saved context')
        loaded = processor.load_context()

        assert loaded == 'Saved context'

    def test_load_context_not_found(self, temp_dir):
        """Load context returns None when file doesn't exist."""
        config = {
            'stt_provider': 'local_whisper',
            'llm_provider': 'ollama',
            'temp_dir': str(temp_dir)
        }
        processor = AIProcessor(config)

        result = processor.load_context()

        assert result is None

    def test_save_context_truncates_long_context(self, temp_dir):
        """Truncate context to maximum length."""
        config = {
            'stt_provider': 'local_whisper',
            'llm_provider': 'ollama',
            'temp_dir': str(temp_dir)
        }
        processor = AIProcessor(config)

        long_context = 'A' * 2000
        processor.save_context(long_context, max_context_length=100)

        loaded = processor.load_context()

        assert len(loaded) == 100
        assert loaded == 'A' * 100

    def test_clear_context(self, temp_dir):
        """Clear saved context."""
        config = {
            'stt_provider': 'local_whisper',
            'llm_provider': 'ollama',
            'temp_dir': str(temp_dir)
        }
        processor = AIProcessor(config)

        processor.save_context('Context to clear')
        processor.clear_context()

        loaded = processor.load_context()

        assert loaded == ''

    def test_save_context_creates_temp_dir(self, temp_dir):
        """save_context uses configured temp directory."""
        subdir = temp_dir / "processor_tmp"
        subdir.mkdir(exist_ok=True)

        config = {
            'stt_provider': 'local_whisper',
            'llm_provider': 'ollama',
            'temp_dir': str(subdir)
        }
        processor = AIProcessor(config)

        processor.save_context('Context in custom temp dir')

        context_file = subdir / 'tmp-context.txt'
        assert context_file.exists()
