# Testing Guide

This guide covers both Python unit tests for the core application and integration testing for the Whisper server.

---

## 1. Python Unit Tests (Pytest)

### Quick Start

Run all tests with:
```bash
pytest
```

Run with verbose output:
```bash
pytest -v
```

### Test Coverage

Current coverage: **49%** overall, with critical modules at 100%:
- `config.py`: 100% (33/33 statements)
- `processor.py`: 100% (89/89 statements)
- `recorder.py`: 86% (68/79 statements)

Run tests with coverage report:
```bash
pytest --cov=src/second_voice --cov-report=term-missing
```

Generate HTML coverage report:
```bash
pytest --cov=src/second_voice --cov-report=html
```

### Test Organization

#### Config Module Tests (`tests/test_config.py`)
25 tests covering:
- Default configuration values
- File loading and merging
- Environment variable overrides (with proper precedence)
- Configuration access methods (`.get()`, `[]`, `.set()`)
- Configuration persistence (save/load)
- Temporary directory creation

Run with:
```bash
pytest tests/test_config.py -v
```

#### Processor Module Tests (`tests/test_processor.py`)
37 tests covering:
- Groq API transcription (mocked)
- Local Whisper service transcription (mocked)
- Ollama LLM processing (mocked)
- OpenRouter LLM processing (mocked)
- Context saving/loading/clearing
- API key handling (env var and config)
- Error handling for missing keys and network errors

Run with:
```bash
pytest tests/test_processor.py -v
```

#### Recorder Module Tests (`tests/test_recorder.py`)
24 tests covering:
- Audio recording initialization
- RMS amplitude calculation
- Recording start/stop operations
- Temporary file creation and cleanup
- Audio device enumeration
- Resource cleanup

Run with:
```bash
pytest tests/test_recorder.py -v
```

#### Mode Tests (`tests/test_modes.py`)
8 existing tests (unchanged):
- GUI mode detection
- TUI mode detection
- Menu mode detection
- Mode instantiation

### Mocking Strategy

All external services are mocked by default for fast, offline testing:

#### Services Mocked
- **Groq API** - Speech-to-text transcription
- **Local Whisper** - HTTP service for transcription
- **Ollama** - Local LLM inference
- **OpenRouter** - Cloud LLM API
- **Audio devices** - Device enumeration and recording

#### Enabling Live API Testing

To test against real services (requires valid API keys and running services):

```bash
# All services
ENABLE_LIVE_API=1 pytest

# Specific services
ENABLE_LIVE_GROQ=1 pytest
ENABLE_LIVE_WHISPER=1 pytest
ENABLE_LIVE_OLLAMA=1 pytest
ENABLE_LIVE_OPENROUTER=1 pytest
```

### Common Test Commands

#### Run specific test file
```bash
pytest tests/test_config.py
```

#### Run specific test class
```bash
pytest tests/test_config.py::TestConfigurationDefaults
```

#### Run specific test
```bash
pytest tests/test_config.py::TestConfigurationDefaults::test_default_config_contains_required_keys
```

#### Run tests matching a pattern
```bash
pytest -k "config"
pytest -k "groq"
pytest -k "whisper"
```

#### Show test collection without running
```bash
pytest --collect-only
pytest -q --collect-only
```

#### Run with short traceback format
```bash
pytest --tb=short
```

#### Run with detailed output
```bash
pytest -vv
```

#### Run in parallel (install pytest-xdist)
```bash
pip install pytest-xdist
pytest -n auto
```

### Test Infrastructure

#### pytest.ini
Located in project root, configures:
- Test discovery in `tests/` directory
- Python module naming conventions
- Markers for test classification
- Output formatting

#### conftest.py
Located in `tests/` directory, provides:
- Mock fixtures for API clients (Groq, OpenRouter)
- HTTP service mocks (Whisper, Ollama)
- Temporary directory fixtures
- Mock audio file fixtures
- Environment variable control fixtures

#### Fixtures Available

##### Temporary Directories
```python
def test_something(temp_dir):
    # temp_dir is a Path object pointing to a temporary directory
    config_file = temp_dir / "config.json"
```

##### Mock Audio Files
```python
def test_recording(mock_audio_file):
    # mock_audio_file is a valid WAV file path
    result = processor.transcribe(str(mock_audio_file))
```

##### API Control Flags
```python
def test_groq(use_live_groq):
    # use_live_groq is True if ENABLE_LIVE_GROQ=1, else False
    if use_live_groq:
        # Test with real API
    else:
        # Test with mock
```

---

## 2. Whisper Server Testing (Integration)


### ✅ NEW: Custom Faster-Whisper Service (small.en Model)

**Status**: Production-ready and tested
**Performance**: ~400-700ms per 10-second audio file
**GPU Memory**: 1.3GB (vs 2.7GB for large-v3)
**Model**: `small.en` (English-only, optimized)

This is a custom Docker service built from the `faster-whisper` source code at `/external/faster-whisper/`. It provides:
- ✅ 25-50x faster transcription than the previous large-v3 setup
- ✅ Proper environment variable model selection
- ✅ GPU acceleration (CUDA 12.3 + cuDNN 9)
- ✅ VAD (Voice Activity Detection) to skip silence
- ✅ OpenAI-compatible API endpoint

### Summary of Previous Attempts and Current Solution

#### 1. Enhanced docker-compose.yml
Updated `/docker/docker-compose.yml` with debugging and performance tuning:
- **LOG_LEVEL=DEBUG** - Enable detailed logging
- **PYTHONUNBUFFERED=1** - Real-time log output
- **WHISPER__COMPUTE_TYPE=float32** - Performance tuning for RTX 2080
- **WHISPER__NUM_WORKERS=1** - Single worker for consistent GPU usage

#### 2. Test Scripts Created

##### Option A: Bash Test Script (Lightweight)
```bash
./test_whisper.sh [audio_file] [model_name]
```

**Usage:**
```bash
# Test with default file (test.wav) and model (whisper-1)
./test_whisper.sh

# Test with custom audio file
./test_whisper.sh my_audio.wav

# Test with custom audio and model
./test_whisper.sh my_audio.wav Systran/faster-whisper-large-v3
```

##### Option B: Python Test Script (Advanced)
```bash
python3 test_whisper_api.py [--audio FILE] [--model MODEL] [--url URL]
```

**Usage:**
```bash
# Test with defaults
python3 test_whisper_api.py

# Custom audio file
python3 test_whisper_api.py --audio my_recording.wav

# Custom model
python3 test_whisper_api.py --model Systran/faster-whisper-large-v3

# Custom URL
python3 test_whisper_api.py --url http://192.168.1.100:9090/v1/audio/transcriptions
```

##### Option C: Simple Curl Command
```bash
curl http://localhost:9090/v1/audio/transcriptions \
    -F "file=@test_audio.wav" \
    -F "model=whisper-1"
```

### GPU Monitoring Commands

#### Monitor GPU in Real-Time
```bash
watch -n 1 nvidia-smi
```

#### Monitor Only Whisper Process
```bash
docker stats whisper-server
```

#### Monitor GPU Memory Usage
```bash
nvidia-smi --query-gpu=memory.used,memory.total --format=csv,noheader
```

#### Check Docker Container GPU Access
```bash
docker exec whisper-server nvidia-smi
```

### Environment Variables Reference

The whisper-server supports these environment variables (from `config.py`):

| Variable | Purpose | Example |
|----------|---------|---------|
| `LOG_LEVEL` | Logging verbosity | `DEBUG`, `INFO`, `WARNING`, `ERROR` |
| `WHISPER_MODEL` | Model to load | `Systran/faster-whisper-large-v3` |
| `WHISPER__COMPUTE_TYPE` | Precision type | `int8`, `float16`, `float32` |
| `WHISPER__NUM_WORKERS` | Worker threads | `1`, `2`, `4` |
| `PYTHONUNBUFFERED` | Unbuffered output | `1` |

### Troubleshooting

#### Server Not Responding
```bash
# Check if container is running
docker ps | grep whisper-server

# View logs with full timestamp
docker logs -f --timestamps whisper-server

# Restart the service
docker-compose -f docker/docker-compose.yml restart whisper
```

#### GPU Not Detected in Container
```bash
# Verify GPU is available on host
nvidia-smi

# Check NVIDIA container toolkit is installed
docker run --rm --gpus all nvidia/cuda:12.2.2-runtime-ubuntu22.04 nvidia-smi

# Verify docker-compose GPU support
docker-compose -f docker/docker-compose.yml config | grep -A5 nvidia
```

#### Out of Memory Errors
Try reducing compute type:
```yaml
# In docker-compose.yml whisper service
environment:
  - WHISPER__COMPUTE_TYPE=int8  # More memory efficient
  # or
  - WHISPER__COMPUTE_TYPE=float16  # Balanced
```

#### Slow Transcription
```bash
# Monitor GPU utilization during transcription
watch -n 1 'nvidia-smi | grep whisper'

# Check if running on CPU instead of GPU
docker logs whisper-server | grep -i "cuda\|cpu"
```

### API Endpoint Reference

#### Transcription Endpoint
**POST** `/v1/audio/transcriptions`

**Parameters:**
- `file` (required) - Audio file (multipart/form-data)
- `model` (required) - Model name (e.g., "whisper-1" or "Systran/faster-whisper-large-v3")

**Response:**
```json
{
  "text": "Transcribed text from audio file"
}
```

**Example with jq parsing:**
```bash
curl -X POST http://localhost:9090/v1/audio/transcriptions \
  -F "file=@test.wav" \
  -F "model=whisper-1" | jq '.text'
```

### Performance Tuning

#### For RTX 2080 (8GB VRAM)
```yaml
environment:
  - WHISPER__COMPUTE_TYPE=float32    # Default, good quality
  - WHISPER__NUM_WORKERS=1            # Single worker
```

#### For Better Quality (if VRAM allows)
```yaml
environment:
  - WHISPER_MODEL=Systran/faster-whisper-large-v3  # Already set
  - WHISPER__COMPUTE_TYPE=float32
```

#### For Faster Processing (if quality acceptable)
```yaml
environment:
  - WHISPER__COMPUTE_TYPE=int8        # Fastest
  - WHISPER_MODEL=Systran/faster-whisper-medium    # Smaller model
```

### Updating docker-compose Configuration

To apply changes to docker-compose.yml:
```bash
cd docker
docker-compose up -d whisper  # Restart just the whisper service
```

To see the running configuration:
```bash
docker-compose config | grep -A20 "whisper:"
```

### Sources & References

- [Faster Whisper Server GitHub](https://github.com/fedirz/faster-whisper-server)
- [NVIDIA Container Toolkit Docs](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/)
- [Docker GPU Support](https://docs.docker.com/compose/how-tos/gpu-support/)
- [NVIDIA CUDA Documentation](https://docs.nvidia.com/cuda/)
---
Last Updated: 2026-01-28
