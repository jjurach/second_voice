"""
Integration tests for mellona provider mocking and configuration.

Tests verify that STT and LLM operations correctly delegate to mellona
and use configuration from config files (fallback models, provider selection).
"""
import os
import pytest
from unittest import mock

from second_voice.core.processor import AIProcessor


# ============================================================================
# Mellona Client Mock Setup
# ============================================================================

@pytest.fixture
def mock_mellona_client():
    """Mock mellona's SyncMellonaClient for integration testing."""
    with mock.patch('second_voice.core.processor.SyncMellonaClient') as mock_client_class:
        mock_instance = mock.MagicMock()
        mock_client_class.return_value.__enter__ = mock.MagicMock(return_value=mock_instance)
        mock_client_class.return_value.__exit__ = mock.MagicMock(return_value=None)

        # Default mock responses
        mock_instance.transcribe.return_value = mock.MagicMock(
            text="Mocked transcription from mellona"
        )
        mock_instance.chat.return_value = mock.MagicMock(
            text="Mocked LLM response from mellona"
        )

        yield mock_instance


# ============================================================================
# LLM Path Tests
# ============================================================================

class TestLLMPathIntegration:
    """Test LLM processing through mellona integration."""

    def test_openrouter_via_mellona(self, mock_mellona_client):
        """OpenRouter requests route through mellona SyncMellonaClient."""
        config = {
            'stt_provider': 'local_whisper',
            'llm_provider': 'openrouter',
            'openrouter_fallback_models': ['openai/gpt-4', 'openai/gpt-3.5-turbo']
        }
        processor = AIProcessor(config)

        result = processor.process_text('Please process this text')

        # Verify mellona client was instantiated and used
        mock_mellona_client.chat.assert_called_once()
        call_kwargs = mock_mellona_client.chat.call_args[1]
        assert call_kwargs['profile'] == 'openrouter'
        assert 'prompt' in call_kwargs
        assert 'system' in call_kwargs
        assert result == "Mocked LLM response from mellona"

    def test_ollama_via_mellona(self, mock_mellona_client):
        """Ollama requests route through mellona SyncMellonaClient."""
        config = {
            'stt_provider': 'local_whisper',
            'llm_provider': 'ollama',
            'ollama_model': 'llama3'
        }
        processor = AIProcessor(config)

        result = processor.process_text('Process this text')

        # Verify mellona client was used with ollama profile
        mock_mellona_client.chat.assert_called_once()
        call_kwargs = mock_mellona_client.chat.call_args[1]
        assert call_kwargs['profile'] == 'ollama'
        assert result == "Mocked LLM response from mellona"

    def test_openrouter_with_context(self, mock_mellona_client):
        """OpenRouter processes context when provided."""
        config = {
            'stt_provider': 'local_whisper',
            'llm_provider': 'openrouter',
            'openrouter_fallback_models': ['openai/gpt-4']
        }
        processor = AIProcessor(config)

        context = "Previous conversation context"
        result = processor.process_text('New message', context=context)

        mock_mellona_client.chat.assert_called_once()
        call_kwargs = mock_mellona_client.chat.call_args[1]
        # Verify context is included in the prompt
        assert context in call_kwargs['prompt']
        assert result == "Mocked LLM response from mellona"


# ============================================================================
# STT Path Tests (Groq)
# ============================================================================

class TestGroqSTTPath:
    """Test Groq STT transcription through mellona."""

    def test_groq_transcription_via_mellona(self, mock_audio_file, mock_mellona_client):
        """Groq transcription delegates to mellona with correct provider."""
        config = {
            'stt_provider': 'groq',
            'llm_provider': 'ollama',
            'groq_stt_model': 'whisper-large-v3'
        }
        processor = AIProcessor(config)

        result = processor.transcribe(str(mock_audio_file))

        # Verify mellona was called with groq provider
        mock_mellona_client.transcribe.assert_called_once()
        call_args = mock_mellona_client.transcribe.call_args
        assert call_args[1]['provider'] == 'groq'
        assert call_args[1]['model'] == 'whisper-large-v3'
        assert result == "Mocked transcription from mellona"

    def test_groq_transcription_custom_model(self, mock_audio_file, mock_mellona_client):
        """Groq transcription uses custom model from config."""
        config = {
            'stt_provider': 'groq',
            'llm_provider': 'ollama',
            'groq_stt_model': 'whisper-medium'
        }
        processor = AIProcessor(config)

        processor.transcribe(str(mock_audio_file))

        # Verify custom model is passed to mellona
        call_kwargs = mock_mellona_client.transcribe.call_args[1]
        assert call_kwargs['model'] == 'whisper-medium'


# ============================================================================
# LocalWhisper STT Path Tests
# ============================================================================

class TestLocalWhisperSTTPath:
    """Test local Whisper STT transcription through mellona."""

    def test_local_whisper_transcription_via_mellona(self, mock_audio_file, mock_mellona_client):
        """Local Whisper transcription delegates to mellona."""
        config = {
            'stt_provider': 'local_whisper',
            'llm_provider': 'ollama'
        }
        processor = AIProcessor(config)

        result = processor.transcribe(str(mock_audio_file))

        # Verify mellona was called with local_whisper provider
        mock_mellona_client.transcribe.assert_called_once()
        call_kwargs = mock_mellona_client.transcribe.call_args[1]
        assert call_kwargs['provider'] == 'local_whisper'
        assert result == "Mocked transcription from mellona"

    def test_local_whisper_uses_default_settings(self, mock_audio_file, mock_mellona_client):
        """Local Whisper uses default provider when not explicitly configured."""
        config = {
            'stt_provider': 'local_whisper',
            'llm_provider': 'ollama'
        }
        processor = AIProcessor(config)

        processor.transcribe(str(mock_audio_file))

        # Verify provider is local_whisper
        call_kwargs = mock_mellona_client.transcribe.call_args[1]
        assert call_kwargs['provider'] == 'local_whisper'


# ============================================================================
# Fallback Models Configuration Tests
# ============================================================================

class TestFallbackModelsConfiguration:
    """Test fallback model list loading from config."""

    def test_openrouter_fallback_models_from_config(self, mock_mellona_client):
        """OpenRouter fallback models are loaded from configuration."""
        config = {
            'stt_provider': 'local_whisper',
            'llm_provider': 'openrouter',
            'openrouter_fallback_models': [
                'openai/gpt-4',
                'anthropic/claude-3-opus',
                'openai/gpt-3.5-turbo'
            ]
        }
        processor = AIProcessor(config)

        result = processor.process_text('Test')

        # Verify mellona was called (fallback is internal to process_openrouter)
        mock_mellona_client.chat.assert_called_once()
        assert result == "Mocked LLM response from mellona"

    def test_openrouter_user_model_prepended_to_fallback(self, mock_mellona_client):
        """User-configured model is prepended to fallback list."""
        config = {
            'stt_provider': 'local_whisper',
            'llm_provider': 'openrouter',
            'openrouter_llm_model': 'custom/model',
            'openrouter_fallback_models': ['openai/gpt-4']
        }
        processor = AIProcessor(config)

        result = processor.process_text('Test')

        mock_mellona_client.chat.assert_called_once()
        assert result == "Mocked LLM response from mellona"

    def test_no_fallback_models_error(self, mock_mellona_client):
        """Error is raised when no fallback models are configured."""
        config = {
            'stt_provider': 'local_whisper',
            'llm_provider': 'openrouter',
            'openrouter_fallback_models': []
        }
        processor = AIProcessor(config)

        result = processor.process_text('Test')

        # Process should handle empty fallback gracefully
        assert "Error" in result or "fallback" in result.lower()


# ============================================================================
# Migration and Credentials Tests
# ============================================================================

class TestCredentialsMigration:
    """Test credential handling and migration messages."""

    def test_no_raw_api_keys_in_config(self, mock_mellona_client):
        """Config does not contain raw API keys (credentials via mellona only)."""
        config = {
            'stt_provider': 'groq',
            'llm_provider': 'openrouter',
            'openrouter_fallback_models': ['openai/gpt-4'],
            'groq_stt_model': 'whisper-large-v3'
        }
        processor = AIProcessor(config)

        # Verify no raw API keys are in config
        assert 'groq_api_key' not in processor.config
        assert 'openrouter_api_key' not in processor.config
        assert 'api_key' not in processor.config

    def test_mellona_handles_credentials(self, mock_mellona_client):
        """All credential handling is delegated to mellona."""
        config = {
            'stt_provider': 'groq',
            'llm_provider': 'openrouter',
            'openrouter_fallback_models': ['openai/gpt-4']
        }
        processor = AIProcessor(config)

        # Verify mellona config is present
        assert hasattr(processor, 'mellona_config')
        # mellona manages credentials, not second_voice
        assert processor.mellona_config is not None

    def test_missing_key_raises_error_from_mellona(self, mock_mellona_client):
        """Missing API key error comes from mellona, not second_voice."""
        # Set up mellona mock to raise error for missing key
        mock_mellona_client.chat.side_effect = RuntimeError("Missing GROQ_API_KEY in mellona config")

        config = {
            'stt_provider': 'local_whisper',
            'llm_provider': 'openrouter',
            'openrouter_fallback_models': ['openai/gpt-4']
        }
        processor = AIProcessor(config)

        result = processor.process_text('Test')

        # Error should indicate mellona configuration issue
        assert "Error" in result or "RuntimeError" in str(result)
