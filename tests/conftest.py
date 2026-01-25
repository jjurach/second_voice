"""
Shared test fixtures and configuration.
Provides mocks for external API services and test utilities.
"""
import os
import json
import tempfile
from pathlib import Path
from unittest import mock
import pytest


@pytest.fixture
def temp_dir():
    """Temporary directory for test files."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def use_live_api():
    """Check if live API testing is enabled via environment variable."""
    return os.getenv("ENABLE_LIVE_API", "0") == "1"


@pytest.fixture
def use_live_groq():
    """Check if live Groq API testing is enabled."""
    return os.getenv("ENABLE_LIVE_GROQ", "0") == "1" or os.getenv("ENABLE_LIVE_API", "0") == "1"


@pytest.fixture
def use_live_whisper():
    """Check if live Whisper service testing is enabled."""
    return os.getenv("ENABLE_LIVE_WHISPER", "0") == "1" or os.getenv("ENABLE_LIVE_API", "0") == "1"


@pytest.fixture
def use_live_ollama():
    """Check if live Ollama service testing is enabled."""
    return os.getenv("ENABLE_LIVE_OLLAMA", "0") == "1" or os.getenv("ENABLE_LIVE_API", "0") == "1"


@pytest.fixture
def use_live_openrouter():
    """Check if live OpenRouter API testing is enabled."""
    return os.getenv("ENABLE_LIVE_OPENROUTER", "0") == "1" or os.getenv("ENABLE_LIVE_API", "0") == "1"


# ============================================================================
# Mock Config Fixtures
# ============================================================================

@pytest.fixture
def mock_config_dict():
    """Default mock configuration dictionary."""
    return {
        "provider": "groq",
        "groq": {
            "api_key": "test-groq-key-12345",
            "model": "whisper-large-v3",
        },
        "whisper": {
            "base_url": "http://localhost:9090",
            "model": "base",
        },
        "ollama": {
            "base_url": "http://localhost:11434",
            "model": "mistral",
        },
        "openrouter": {
            "api_key": "test-openrouter-key",
            "model": "mistralai/mistral-7b-instruct",
        },
        "mode": "menu",
        "editor": "nano",
    }


@pytest.fixture
def mock_config_file(temp_dir, mock_config_dict):
    """Create a temporary config file and return its path."""
    config_path = temp_dir / "config.json"
    with open(config_path, "w") as f:
        json.dump(mock_config_dict, f)
    return config_path


# ============================================================================
# Mock API Fixtures
# ============================================================================

@pytest.fixture
def mock_groq_client():
    """Mock Groq API client."""
    with mock.patch("groq.Groq") as mock_client:
        instance = mock.MagicMock()
        mock_client.return_value = instance

        # Mock transcription response
        instance.audio.transcriptions.create.return_value = mock.MagicMock(
            text="This is a transcribed text from audio."
        )

        # Mock chat completion response
        instance.chat.completions.create.return_value = mock.MagicMock(
            choices=[mock.MagicMock(message=mock.MagicMock(content="Mock LLM response"))]
        )

        yield instance


@pytest.fixture
def mock_whisper_service(requests_mock):
    """Mock local Whisper service HTTP endpoint."""
    base_url = "http://localhost:9090"

    # Mock transcription endpoint
    requests_mock.post(
        f"{base_url}/asr",
        json={"result": {"transcription": "This is a Whisper transcription."}}
    )

    return base_url


@pytest.fixture
def mock_ollama_service(requests_mock):
    """Mock local Ollama service HTTP endpoint."""
    base_url = "http://localhost:11434"

    # Mock chat completion endpoint
    requests_mock.post(
        f"{base_url}/api/chat",
        json={"message": {"content": "Mock Ollama response"}}
    )

    return base_url


@pytest.fixture
def mock_openrouter_client():
    """Mock OpenRouter API client."""
    with mock.patch("requests.post") as mock_post:
        mock_response = mock.MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "choices": [{"message": {"content": "Mock OpenRouter response"}}]
        }
        mock_post.return_value = mock_response
        yield mock_post


# ============================================================================
# Utility Fixtures
# ============================================================================

@pytest.fixture
def mock_audio_file(temp_dir):
    """Create a mock audio file for testing."""
    audio_file = temp_dir / "test_audio.wav"
    # Write minimal WAV header (RIFF format)
    wav_data = (
        b'RIFF'
        b'\x24\x00\x00\x00'  # File size
        b'WAVE'
        b'fmt '
        b'\x10\x00\x00\x00'  # Subchunk1Size
        b'\x01\x00'          # AudioFormat (1 = PCM)
        b'\x01\x00'          # NumChannels (1 = mono)
        b'\x44\xac\x00\x00'  # SampleRate (44100 Hz)
        b'\x88\x58\x01\x00'  # ByteRate
        b'\x02\x00'          # BlockAlign
        b'\x10\x00'          # BitsPerSample
        b'data'
        b'\x00\x00\x00\x00'  # Subchunk2Size (0 bytes of audio data)
    )
    with open(audio_file, "wb") as f:
        f.write(wav_data)
    return audio_file


@pytest.fixture
def mock_device_list():
    """Mock list of audio input devices."""
    return [
        {"index": 0, "name": "Default Device", "max_input_channels": 2},
        {"index": 1, "name": "Microphone", "max_input_channels": 1},
        {"index": 2, "name": "Line In", "max_input_channels": 2},
    ]


@pytest.fixture(autouse=True)
def cleanup_audio_resources():
    """Clean up audio resources before each test to prevent warnings during teardown."""
    yield
    # Clean up any remaining audio streams or resources
    try:
        import sounddevice as sd
        # Close any remaining streams
        if hasattr(sd, 'default_speaker') and sd.default_speaker is not None:
            try:
                sd.default_speaker.close()
            except:
                pass
        if hasattr(sd, 'default_microphone') and sd.default_microphone is not None:
            try:
                sd.default_microphone.close()
            except:
                pass
    except:
        pass

    # Force garbage collection to clean up __del__ methods
    import gc
    gc.collect()
