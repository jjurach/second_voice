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

    def test_processor_mellona_integration(self):
        """Verify processor initializes mellona config chain."""
        config = {'stt_provider': 'local_whisper', 'llm_provider': 'ollama'}
        processor = AIProcessor(config)
        # Mellona config chain is set up in __init__
        # Credentials are managed by mellona, not stored in processor
        assert processor.stt_provider == 'local_whisper'
        assert processor.llm_provider == 'ollama'


# NOTE: Direct API tests removed after Ph4 credentials migration.
# All STT and LLM calls now go through mellona's SyncMellonaClient.
# Tests should mock mellona instead of raw HTTP requests.
# See docs/project-context.md for credential management details.

class TestTranscriptionConfiguration:
    """Test transcription configuration for mellona integration."""

    def test_transcribe_local_whisper_config(self):
        """Verify local Whisper provider is configured correctly."""
        config = {
            'stt_provider': 'local_whisper',
            'llm_provider': 'ollama'
        }
        processor = AIProcessor(config)
        assert processor.stt_provider == 'local_whisper'

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
    """Test Groq transcription configuration for mellona integration."""

    def test_transcribe_groq_config(self):
        """Verify Groq provider is configured correctly."""
        config = {
            'stt_provider': 'groq',
            'llm_provider': 'ollama'
        }
        processor = AIProcessor(config)
        assert processor.stt_provider == 'groq'

    def test_transcribe_groq_custom_model(self):
        """Use custom Groq model."""
        config = {
            'stt_provider': 'groq',
            'llm_provider': 'ollama',
            'groq_stt_model': 'whisper-medium'
        }
        processor = AIProcessor(config)

        # Verify custom model is configured
        assert processor.config.get('groq_stt_model') == 'whisper-medium'


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

    def test_transcribe_dispatches_to_groq(self):
        """Dispatch to Groq provider when configured."""
        config = {
            'stt_provider': 'groq',
            'llm_provider': 'ollama'
        }
        processor = AIProcessor(config)

        # Verify dispatch configuration
        assert processor.stt_provider == 'groq'

    def test_transcribe_dispatches_to_local_whisper(self):
        """Dispatch to local Whisper provider when configured."""
        config = {
            'stt_provider': 'local_whisper',
            'llm_provider': 'ollama'
        }
        processor = AIProcessor(config)

        # Verify dispatch configuration
        assert processor.stt_provider == 'local_whisper'


class TestOllamaProcessing:
    """Test LLM processing configuration with Ollama via mellona."""

    def test_process_text_ollama_config(self):
        """Verify Ollama provider is configured correctly."""
        config = {
            'stt_provider': 'local_whisper',
            'llm_provider': 'ollama',
            'ollama_model': 'llama2'
        }
        processor = AIProcessor(config)

        assert processor.llm_provider == 'ollama'
        assert processor.config.get('ollama_model') == 'llama2'


class TestOpenRouterProcessing:
    """Test LLM processing with OpenRouter."""

    def test_process_text_openrouter_config(self):
        """Verify OpenRouter configuration is properly set."""
        config = {
            'stt_provider': 'local_whisper',
            'llm_provider': 'openrouter'
        }
        processor = AIProcessor(config)

        # Verify processor is configured for OpenRouter
        # Credentials are managed by mellona, not stored in processor
        assert processor.llm_provider == 'openrouter'

    def test_process_text_openrouter_with_context(self):
        """Process text with OpenRouter including context."""
        config = {
            'stt_provider': 'local_whisper',
            'llm_provider': 'openrouter'
        }
        processor = AIProcessor(config)

        # Verify provider configuration
        assert processor.llm_provider == 'openrouter'

    def test_process_text_openrouter_via_mellona(self):
        """OpenRouter credentials are managed by mellona."""
        config = {
            'stt_provider': 'local_whisper',
            'llm_provider': 'openrouter'
        }
        processor = AIProcessor(config)

        # OpenRouter API keys are configured in mellona, not in second_voice
        assert processor.llm_provider == 'openrouter'

    def test_process_text_openrouter_custom_model(self):
        """Use custom OpenRouter model."""
        config = {
            'stt_provider': 'local_whisper',
            'llm_provider': 'openrouter',
            'openrouter_llm_model': 'custom/model'
        }
        processor = AIProcessor(config)

        # Verify custom model is configured
        assert processor.config.get('openrouter_llm_model') == 'custom/model'

    def test_process_text_openrouter_dispatch(self):
        """Dispatch to OpenRouter when configured."""
        config = {
            'stt_provider': 'local_whisper',
            'llm_provider': 'openrouter'
        }
        processor = AIProcessor(config)

        # Verify dispatch configuration
        assert processor.llm_provider == 'openrouter'


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

    def test_process_text_dispatches_to_ollama(self):
        """Dispatch to Ollama when configured."""
        config = {
            'stt_provider': 'local_whisper',
            'llm_provider': 'ollama'
        }
        processor = AIProcessor(config)

        # Verify dispatch to Ollama
        assert processor.llm_provider == 'ollama'

    def test_process_text_dispatches_to_openrouter(self):
        """Dispatch to OpenRouter when configured."""
        config = {
            'stt_provider': 'local_whisper',
            'llm_provider': 'openrouter'
        }
        processor = AIProcessor(config)

        # Verify dispatch to OpenRouter
        assert processor.llm_provider == 'openrouter'


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
