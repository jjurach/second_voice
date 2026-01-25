# Testing Guide

## Quick Start

Run all tests with:
```bash
pytest
```

Run with verbose output:
```bash
pytest -v
```

## Test Coverage

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

## Test Organization

### Config Module Tests (`tests/test_config.py`)
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

### Processor Module Tests (`tests/test_processor.py`)
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

### Recorder Module Tests (`tests/test_recorder.py`)
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

### Mode Tests (`tests/test_modes.py`)
8 existing tests (unchanged):
- GUI mode detection
- TUI mode detection
- Menu mode detection
- Mode instantiation

## Mocking Strategy

All external services are mocked by default for fast, offline testing:

### Services Mocked
- **Groq API** - Speech-to-text transcription
- **Local Whisper** - HTTP service for transcription
- **Ollama** - Local LLM inference
- **OpenRouter** - Cloud LLM API
- **Audio devices** - Device enumeration and recording

### Enabling Live API Testing

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

## Common Test Commands

### Run specific test file
```bash
pytest tests/test_config.py
```

### Run specific test class
```bash
pytest tests/test_config.py::TestConfigurationDefaults
```

### Run specific test
```bash
pytest tests/test_config.py::TestConfigurationDefaults::test_default_config_contains_required_keys
```

### Run tests matching a pattern
```bash
pytest -k "config"
pytest -k "groq"
pytest -k "whisper"
```

### Show test collection without running
```bash
pytest --collect-only
pytest -q --collect-only
```

### Run with short traceback format
```bash
pytest --tb=short
```

### Run with detailed output
```bash
pytest -vv
```

### Run in parallel (install pytest-xdist)
```bash
pip install pytest-xdist
pytest -n auto
```

## Test Infrastructure

### pytest.ini
Located in project root, configures:
- Test discovery in `tests/` directory
- Python module naming conventions
- Markers for test classification
- Output formatting

### conftest.py
Located in `tests/` directory, provides:
- Mock fixtures for API clients (Groq, OpenRouter)
- HTTP service mocks (Whisper, Ollama)
- Temporary directory fixtures
- Mock audio file fixtures
- Environment variable control fixtures

### Fixtures Available

#### Temporary Directories
```python
def test_something(temp_dir):
    # temp_dir is a Path object pointing to a temporary directory
    config_file = temp_dir / "config.json"
```

#### Mock Audio Files
```python
def test_recording(mock_audio_file):
    # mock_audio_file is a valid WAV file path
    result = processor.transcribe(str(mock_audio_file))
```

#### API Control Flags
```python
def test_groq(use_live_groq):
    # use_live_groq is True if ENABLE_LIVE_GROQ=1, else False
    if use_live_groq:
        # Test with real API
    else:
        # Test with mock
```

## Continuous Integration

To run tests in CI/CD:
```bash
pytest --cov=src/second_voice --cov-report=term --cov-report=xml -v
```

Coverage threshold can be set in `pytest.ini` or enforced in CI.

## Troubleshooting

### Tests fail due to missing modules
```bash
pip install -r requirements.txt
```

### Coverage report not generated
```bash
pip install pytest-cov
pytest --cov=src/second_voice
```

### Import errors from tests
Ensure current directory has `src/` in path:
```bash
export PYTHONPATH="${PWD}:${PYTHONPATH}"
pytest
```

### Slow tests
Tests should complete in < 2 seconds. If slower:
- Check for accidental live API calls
- Verify mocks are working
- Profile with `pytest --profile` (requires pytest-profiling)

## Development Workflow

When adding new tests:
1. Create test file in `tests/test_*.py`
2. Use existing fixtures from `conftest.py`
3. Run tests frequently during development
4. Check coverage: `pytest --cov=src/second_voice`
5. Commit with tests passing

When adding new features:
1. Write tests first (TDD approach)
2. Implement feature
3. Run full test suite
4. Verify coverage hasn't decreased
5. Commit with both code and tests
