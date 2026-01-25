# Second Voice Refactor - Project Plan
**Created:** 2026-01-24
**Status:** Awaiting Approval
**Spec Reference:** dev_notes/specs/2026-01-24_23-27-34_second-voice-refactor.md

---

## Executive Summary

This plan transforms the existing Second Voice proof-of-concept into a professional, publishable Python project. The current working scripts (`src/cli/second_voice.py` and `scripts/demo_second_voice.py`) will be refactored into a modular architecture with proper packaging, testing, and documentation.

**Key Documentation Created:**
- `docs/architecture.md` - System architecture and data flow
- `docs/gui-design.md` - GUI specifications and visual design
- `docs/prompts.md` - AI prompting strategies and workflows

These documents consolidate information from the previous info1-5.md files and will serve as architectural reference throughout development.

---

## Goals

1. Create a professional Python project structure suitable for publication
2. Separate functional logic into reusable modules
3. Add comprehensive CLI options with verbose/debug modes
4. Implement pytest test coverage for core functionality
5. Create installable entry points via pyproject.toml
6. Provide professional documentation (README.md, LICENSE)
7. Ensure all tests and demos run cleanly before completion

---

## Project Structure

```
second_voice/
├── LICENSE                          # MIT License
├── README.md                        # Professional project documentation
├── pyproject.toml                   # Modern Python packaging
├── requirements.txt                 # Dependencies (venv required)
├── .gitignore                       # Python-specific ignores
├── tmp/                             # Temporary files (crash logs, audio)
├── src/
│   └── second_voice/
│       ├── __init__.py             # Package initialization
│       ├── cli.py                  # CLI entry point with argparse
│       ├── config.py               # Configuration management
│       ├── engine/
│       │   ├── __init__.py
│       │   ├── recorder.py         # Audio recording + RMS analysis
│       │   ├── processor.py        # Orchestrates STT + LLM processing
│       │   ├── llm_providers/
│       │   │   ├── __init__.py
│       │   │   ├── base.py         # BaseLLMProvider (abstract)
│       │   │   ├── ollama.py       # OllamaProvider implementation
│       │   │   └── openrouter.py   # OpenRouterProvider implementation
│       │   └── stt_providers/
│       │       ├── __init__.py
│       │       ├── base.py         # BaseSTTProvider (abstract)
│       │       ├── local_whisper.py # Local faster-whisper-server
│       │       ├── groq.py         # Groq Whisper API
│       │       └── openai.py       # OpenAI Whisper API
│       └── ui/
│           ├── __init__.py
│           ├── main_window.py      # Main Tkinter application
│           └── components.py       # VU meter components
├── scripts/
│   └── demo_second_voice.py        # Demo script for testing
├── tests/
│   ├── __init__.py
│   ├── test_config.py              # Configuration tests
│   ├── test_processor.py           # Orchestration tests
│   ├── test_recorder.py            # Audio recording tests
│   ├── test_llm_providers.py       # LLM provider tests
│   └── test_stt_providers.py       # STT provider tests
├── samples/
│   └── test.wav                    # Sample audio for testing
├── docs/
│   ├── architecture.md             # System architecture (created)
│   ├── gui-design.md               # GUI specifications (created)
│   ├── prompts.md                  # AI prompts reference (created)
│   ├── implementation-reference.md # Code templates (created)
│   └── providers.md                # LLM provider guide (to be created)
└── dev_notes/
    ├── specs/
    ├── project_plans/
    └── changes/
```

---

## Tasks Breakdown

### Phase 0: Critical Fixes (Pre-Refactor)

#### Task 0.1: Fix temporary file location violation
- [ ] Update `src/cli/second_voice.py` line 78
- [ ] Change from `/tmp/sv_audio.wav` to `tmp-audio.wav`
- [ ] Ensure tmp directory or tmp-* files are used per AGENTS.md Rule #5
- [ ] Test that the fix works with current script
- [ ] Commit the fix before proceeding with refactoring

**Rationale:** The current code violates AGENTS.md Rule #5 which prohibits using `/tmp` or system temporary directories. All temporary files must use `tmp-*`, `*.tmp`, or `tmp/*` patterns in the current working directory.

---

### Phase 1: Project Foundation (Setup & Structure)

#### Task 1.1: Create LICENSE file
- [ ] Add MIT License with appropriate copyright year
- [ ] Include standard MIT License text

#### Task 1.2: Create .gitignore
- [ ] Add Python-specific ignores (__pycache__, *.pyc, *.pyo, *.pyd)
- [ ] Add environment ignores (venv/, .env)
- [ ] Add IDE ignores (.vscode/, .idea/)
- [ ] Add build artifacts (dist/, build/, *.egg-info/)
- [ ] Add tmp files (tmp/*, *.tmp, tmp-*)
- [ ] Add crash logs pattern (tmp-crash-*.txt)

#### Task 1.2b: Create tmp/ directory structure
- [ ] Create tmp/ directory in project root
- [ ] Add tmp/.gitkeep to ensure directory exists in git
- [ ] Verify .gitignore properly excludes tmp/* contents but keeps directory

#### Task 1.3: Create pyproject.toml
- [ ] Configure build system (setuptools)
- [ ] Set project metadata (name, version, description, authors)
- [ ] Define dependencies (pyaudio, requests, numpy)
- [ ] Create console script entry points:
  - `second_voice` → `second_voice.cli:main`
  - `demo_second_voice` → `scripts.demo_second_voice:main`
- [ ] Specify Python version requirement (>=3.8)

#### Task 1.4: Update requirements.txt
- [ ] List all runtime dependencies with versions:
  - pyaudio
  - requests
  - numpy
  - (tkinter is standard library but note brew install python-tk in docs)
- [ ] Add dev dependencies section:
  - pytest
  - pytest-cov

---

### Phase 2: Module Refactoring

#### Task 2.1: Create src/second_voice/config.py
- [ ] Extract configuration loading logic from current script
- [ ] Create Config class with methods:
  - `load_config()` - Load from ~/.config/second_voice/settings.json
  - `get_default_config()` - Return default configuration dict with all providers
  - `save_config(config)` - Save configuration
  - `validate_config(config)` - Validate required fields
  - `get_llm_provider()` - Auto-detect LLM provider (OpenRouter if API key, else Ollama)
  - `get_stt_provider()` - Auto-detect STT provider (Groq if API key, else OpenAI if API key, else local)
- [ ] Add configuration path constants
- [ ] Support environment variable substitution (e.g., ${GROQ_API_KEY}, ${OPENROUTER_API_KEY})
- [ ] Default config structure includes:
  - STT providers: local_whisper, groq, openai
  - LLM providers: ollama, openrouter
- [ ] Add helper methods to check if providers are configured

#### Task 2.2: Create src/second_voice/engine/recorder.py
- [ ] Extract audio recording logic from current script
- [ ] Create AudioRecorder class with methods:
  - `__init__(rate=16000, chunk=1024)` - Initialize PyAudio
  - `_calculate_rms(audio_data)` - Calculate RMS amplitude
  - `_stream_callback(...)` - PyAudio callback for recording
  - `start()` - Start recording
  - `stop()` - Stop recording and return frames
  - `get_volume_queue()` - Return thread-safe queue for GUI
- [ ] Implement thread-safe volume queue for VU meter
- [ ] Add proper resource cleanup

#### Task 2.3: Create LLM Provider Architecture

This task is broken into subtasks for the LLM provider pattern implementation.

##### Task 2.3a: Create src/second_voice/engine/llm_providers/base.py
- [ ] Create BaseLLMProvider abstract class with methods:
  - `process(prompt, system_prompt="", context="")` - Abstract method
  - `validate_config()` - Abstract method to check configuration
  - `is_available()` - Abstract method to test connectivity
  - `get_provider_name()` - Return provider name string
- [ ] Define standard exception classes:
  - `ProviderError` - Base exception
  - `ProviderConfigError` - Configuration issues
  - `ProviderConnectionError` - Network/connection issues
  - `ProviderAuthError` - Authentication failures
- [ ] Add docstrings explaining the contract

##### Task 2.3b: Create src/second_voice/engine/llm_providers/ollama.py
- [ ] Create OllamaProvider(BaseLLMProvider) class
- [ ] Implement `__init__(config)` - Extract ollama config section
- [ ] Implement `process(prompt, system_prompt, context)`:
  - Build recursive prompt if context exists
  - POST to Ollama API (/api/generate endpoint)
  - Handle streaming vs non-streaming
  - Extract response from Ollama's JSON format
- [ ] Implement `validate_config()` - Check url and model are set
- [ ] Implement `is_available()` - Test connection to Ollama URL
- [ ] Add timeout handling (120s default)
- [ ] Add connection error handling
- [ ] Support verbose/debug output modes

##### Task 2.3c: Create src/second_voice/engine/llm_providers/openrouter.py
- [ ] Create OpenRouterProvider(BaseLLMProvider) class
- [ ] Implement `__init__(config)` - Extract openrouter config section
- [ ] Implement `process(prompt, system_prompt, context)`:
  - Build recursive prompt if context exists
  - Use OpenAI-compatible format (chat/completions)
  - Add API key to Authorization header
  - Handle response in OpenAI format
- [ ] Implement `validate_config()` - Check API key and model are set
- [ ] Implement `is_available()` - Test connection to OpenRouter
- [ ] Add timeout handling (120s default)
- [ ] Add authentication error handling
- [ ] Add rate limit error handling
- [ ] Support verbose/debug output modes

##### Task 2.3d: Create LLM provider factory
- [ ] Create `get_llm_provider(config, provider_name=None)` factory function in llm_providers/__init__.py:
  - If provider_name specified, use that
  - Else auto-detect: OpenRouter if API key exists, else Ollama
  - Instantiate and return appropriate provider
- [ ] Add provider registry/mapping
- [ ] Validate provider name
- [ ] Return initialized provider instance

#### Task 2.4: Create STT Provider Architecture

This task creates the STT provider pattern parallel to LLM providers.

##### Task 2.4a: Create src/second_voice/engine/stt_providers/base.py
- [ ] Create BaseSTTProvider abstract class with methods:
  - `transcribe(audio_file_path)` - Abstract method, returns transcribed text
  - `transcribe_frames(audio_frames, rate=16000)` - Alternative interface for in-memory audio
  - `validate_config()` - Abstract method to check configuration
  - `is_available()` - Abstract method to test connectivity
  - `get_provider_name()` - Return provider name string
- [ ] Define standard exception classes:
  - `STTProviderError` - Base exception
  - `STTProviderConfigError` - Configuration issues
  - `STTProviderConnectionError` - Network/connection issues
  - `STTProviderAuthError` - Authentication failures
- [ ] Add docstrings explaining the contract

##### Task 2.4b: Create src/second_voice/engine/stt_providers/local_whisper.py
- [ ] Create LocalWhisperProvider(BaseSTTProvider) class
- [ ] Implement `__init__(config)` - Extract local_whisper config section
- [ ] Implement `transcribe(audio_file_path)`:
  - POST file to local Whisper server
  - Parse response for text field
- [ ] Implement `transcribe_frames(audio_frames, rate)`:
  - Save frames to tmp-audio.wav
  - Call transcribe()
- [ ] Implement `validate_config()` - Check url and model are set
- [ ] Implement `is_available()` - Test connection to local Whisper URL
- [ ] Add timeout handling (120s default)
- [ ] Add connection error handling
- [ ] Support verbose/debug output modes

##### Task 2.4c: Create src/second_voice/engine/stt_providers/groq.py
- [ ] Create GroqProvider(BaseSTTProvider) class
- [ ] Implement `__init__(config)` - Extract groq config section
- [ ] Implement `transcribe(audio_file_path)`:
  - Use OpenAI-compatible Whisper API format
  - POST to https://api.groq.com/openai/v1/audio/transcriptions
  - Add API key to Authorization header
  - Parse response for text field
- [ ] Implement `transcribe_frames(audio_frames, rate)`:
  - Save frames to tmp-audio.wav
  - Call transcribe()
- [ ] Implement `validate_config()` - Check API key and model are set
- [ ] Implement `is_available()` - Test connection to Groq API
- [ ] Add timeout handling (120s default)
- [ ] Add authentication error handling
- [ ] Add rate limit error handling
- [ ] Support verbose/debug output modes
- [ ] Note in docstring: Groq offers generous free tier

##### Task 2.4d: Create src/second_voice/engine/stt_providers/openai.py
- [ ] Create OpenAIProvider(BaseSTTProvider) class
- [ ] Implement `__init__(config)` - Extract openai config section
- [ ] Implement `transcribe(audio_file_path)`:
  - Use OpenAI Whisper API format
  - POST to https://api.openai.com/v1/audio/transcriptions
  - Add API key to Authorization header
  - Parse response for text field
- [ ] Implement `transcribe_frames(audio_frames, rate)`:
  - Save frames to tmp-audio.wav
  - Call transcribe()
- [ ] Implement `validate_config()` - Check API key and model are set
- [ ] Implement `is_available()` - Test connection to OpenAI API
- [ ] Add timeout handling (120s default)
- [ ] Add authentication error handling
- [ ] Add rate limit error handling
- [ ] Support verbose/debug output modes
- [ ] Note pricing in docstring: ~$0.006/minute

##### Task 2.4e: Create STT provider factory
- [ ] Create `get_stt_provider(config, provider_name=None)` factory function in stt_providers/__init__.py:
  - If provider_name specified, use that
  - Else auto-detect: Groq if GROQ_API_KEY, else OpenAI if OPENAI_API_KEY, else local
  - Instantiate and return appropriate provider
- [ ] Add provider registry/mapping
- [ ] Validate provider name
- [ ] Return initialized provider instance

#### Task 2.5: Create src/second_voice/engine/processor.py (Orchestration Layer)
- [ ] Create AudioProcessor class that orchestrates STT + LLM processing:
  - `__init__(config)` - Initialize with configuration
  - `set_stt_provider(provider)` - Set STT provider instance
  - `set_llm_provider(provider)` - Set LLM provider instance
  - `transcribe(audio_frames, rate=16000)` - Delegate to STT provider
  - `process_with_llm(text, context="")` - Delegate to LLM provider
  - `process_audio(audio_frames, context="", rate=16000)` - Full pipeline: STT → LLM
  - `_save_crash_log(stt_text, error, provider_info)` - Save to tmp-crash-{timestamp}.txt
  - `_build_recursive_prompt(context, new_text)` - Shared prompt logic
- [ ] **CRITICAL:** Use `tmp-audio.wav` (not `/tmp/`) for temporary audio files per AGENTS.md Rule #5
- [ ] Wrap both STT and LLM calls with try/except
- [ ] Save crash log on LLM failure (preserves STT text)
- [ ] Save crash log on STT failure (preserves audio file path)
- [ ] Include original data, error details, provider info, and stack trace in crash logs
- [ ] Support verbose/debug output modes (show which providers are being used)

#### Task 2.6: Create src/second_voice/ui/components.py
- [ ] Create VUVisualizer class (tkinter.Canvas subclass)
  - `__init__(parent, **kwargs)` - Initialize canvas
  - `update_amplitude(amplitude)` - Update visual based on 0-1 amplitude
  - `reset()` - Return to standby state
- [ ] Implement core pulse rendering (circle with color interpolation)
- [ ] Implement lateral level bars (10 segments per side)
- [ ] Add taper effect for professional appearance
- [ ] Optimize using canvas.coords() for performance

#### Task 2.7: Create src/second_voice/ui/main_window.py
- [ ] Create MainWindow class for primary GUI
- [ ] Extract and refactor GUI logic from current script
- [ ] Integrate VUVisualizer component
- [ ] Implement recorder integration via volume queue
- [ ] Add 30ms refresh loop for VU meter
- [ ] Implement keyboard shortcuts (Space, Enter)
- [ ] Add context management (display, clear)
- [ ] Implement Obsidian integration
- [ ] Add error dialogs and user feedback

#### Task 2.8: Create src/second_voice/cli.py
- [ ] Create main() function as entry point
- [ ] Implement argument parsing with argparse (bifurcated STT/LLM options):

  **General options:**
  - `--verbose` - Show detailed information (URLs, responses, timings, provider selection)
  - `--debug` - Show debug information (payloads, full traces)
  - `--config PATH` - Override default config file path
  - `--vault-path PATH` - Override Obsidian vault path

  **STT (Speech-to-Text) options:**
  - `--stt-provider {local,groq,openai}` - Override auto-detected STT provider
  - `--stt-model MODEL` - Override STT model name (e.g., whisper-large-v3, whisper-1)
  - `--stt-api-key KEY` - Override STT API key (for Groq/OpenAI)
  - `--stt-url URL` - Override local Whisper URL (for local provider)

  **LLM (Language Model) options:**
  - `--llm-provider {ollama,openrouter}` - Override auto-detected LLM provider
  - `--llm-model MODEL` - Override LLM model name
  - `--llm-api-key KEY` - Override LLM API key (for OpenRouter)
  - `--llm-url URL` - Override Ollama URL (for local provider)

- [ ] Initialize configuration with CLI overrides
- [ ] Instantiate STT provider using get_stt_provider()
- [ ] Instantiate LLM provider using get_llm_provider()
- [ ] Validate both provider configurations before launching GUI
- [ ] Display provider info in verbose mode:
  - STT provider name and model
  - LLM provider name and model
  - Connection status for both
- [ ] Launch GUI (MainWindow) with configured providers
- [ ] Add logging configuration based on verbose/debug flags

#### Task 2.9: Create src/second_voice/__init__.py
- [ ] Define __version__
- [ ] Import and expose main classes (AudioRecorder, AudioProcessor, MainWindow, Config)
- [ ] Add package-level documentation

---

### Phase 3: Demo Script Enhancement

#### Task 3.1: Refactor scripts/demo_second_voice.py
- [ ] Update imports to use new second_voice package modules
- [ ] Use samples/test.wav as default input file
- [ ] Add argparse for command-line options (bifurcated):

  **General:**
  - `--audio PATH` - Path to audio file (default: samples/test.wav)
  - `--verbose` - Show detailed information
  - `--debug` - Show debug information

  **STT options:**
  - `--stt-provider {local,groq,openai}` - Override auto-detected STT provider
  - `--stt-model MODEL` - Override STT model name
  - `--stt-api-key KEY` - Override STT API key

  **LLM options:**
  - `--llm-provider {ollama,openrouter}` - Override auto-detected LLM provider
  - `--llm-model MODEL` - Override LLM model name
  - `--llm-api-key KEY` - Override LLM API key

- [ ] Add timing measurements (start time, end time, duration for both STT and LLM)
- [ ] Display active providers and models in output:
  - STT provider and model
  - LLM provider and model
- [ ] Add detailed output for verbose mode:
  - Active STT provider and endpoint
  - Active LLM provider and endpoint
  - Request URLs
  - Request payload/files
  - Response status codes
  - Response bodies
  - Timing information (STT time, LLM time, total time)
- [ ] Add debug mode output:
  - Full request headers (with API keys masked)
  - Full response headers
  - Raw response content
- [ ] Add GPU status checks (if nvidia-smi available, for local Ollama/Whisper)
- [ ] Ensure demo uses refactored AudioProcessor module with dual provider pattern
- [ ] Add error handling and user-friendly messages
- [ ] Test with all provider combinations if configured:
  - local STT + local LLM
  - Groq STT + OpenRouter LLM
  - All four combinations

---

### Phase 4: Testing Infrastructure

#### Task 4.1: Create tests/test_config.py
- [ ] Test default configuration loading
- [ ] Test configuration file creation
- [ ] Test configuration validation
- [ ] Test configuration overrides
- [ ] Mock file system operations
- [ ] Test error handling for invalid configs

#### Task 4.2: Create tests/test_llm_providers.py
- [ ] Test BaseLLMProvider interface
- [ ] Test OllamaProvider:
  - Mock Ollama API requests
  - Test successful LLM processing
  - Test recursive prompt building with context
  - Test timeout handling
  - Test connection error handling
  - Test response validation
  - Test is_available() check
- [ ] Test OpenRouterProvider:
  - Mock OpenRouter API requests
  - Test successful LLM processing with OpenAI format
  - Test recursive prompt building with context
  - Test API key authentication
  - Test auth error handling
  - Test rate limit handling
  - Test is_available() check
- [ ] Test LLM provider factory (get_llm_provider):
  - Test auto-detection with OPENROUTER_API_KEY env var
  - Test auto-detection without API key (defaults to Ollama)
  - Test explicit provider selection
  - Test invalid provider name handling

#### Task 4.3: Create tests/test_stt_providers.py
- [ ] Test BaseSTTProvider interface
- [ ] Test LocalWhisperProvider:
  - Mock local Whisper API requests
  - Test successful transcription from file
  - Test successful transcription from frames
  - Test timeout handling
  - Test connection error handling
  - Test response validation
  - Test is_available() check
- [ ] Test GroqProvider:
  - Mock Groq API requests
  - Test successful transcription with OpenAI-compatible format
  - Test API key authentication
  - Test auth error handling
  - Test rate limit handling
  - Test is_available() check
- [ ] Test OpenAIProvider:
  - Mock OpenAI API requests
  - Test successful transcription
  - Test API key authentication
  - Test auth error handling
  - Test rate limit handling
  - Test is_available() check
- [ ] Test STT provider factory (get_stt_provider):
  - Test auto-detection with GROQ_API_KEY env var
  - Test auto-detection with OPENAI_API_KEY env var
  - Test auto-detection without API keys (defaults to local)
  - Test explicit provider selection
  - Test invalid provider name handling

#### Task 4.4: Create tests/test_processor.py
- [ ] Test AudioProcessor initialization with different provider combinations
- [ ] Test set_stt_provider() and set_llm_provider()
- [ ] Test transcribe() delegates to STT provider correctly
- [ ] Test process_with_llm() delegates to LLM provider correctly
- [ ] Test full process_audio() pipeline (STT → LLM)
- [ ] Test crash log creation on STT failure
- [ ] Test crash log creation on LLM failure
- [ ] Verify crash logs contain appropriate data:
  - STT failure: audio file path, error, stack trace
  - LLM failure: STT text, error, provider info, stack trace
- [ ] Test crash log file naming (tmp-crash-{timestamp}.txt)
- [ ] Test timeout handling for both STT and LLM
- [ ] Test connection error handling for both providers
- [ ] Test with different provider combinations

#### Task 4.5: Create tests/test_recorder.py
- [ ] Test AudioRecorder initialization
- [ ] Test RMS calculation with sample data
- [ ] Mock PyAudio interactions
- [ ] Test volume queue functionality
- [ ] Test start/stop recording
- [ ] Test resource cleanup

#### Task 4.6: Setup pytest configuration
- [ ] Create pytest.ini or add to pyproject.toml
- [ ] Configure test discovery
- [ ] Configure coverage reporting
- [ ] Add test markers if needed

---

### Phase 5: Documentation

#### Task 5.1: Create README.md (Privacy-Positive Messaging)
- [ ] Project title and description
- [ ] Features list:
  - Multi-provider architecture (STT + LLM)
  - Privacy-first option (full local processing)
  - Zero-infrastructure option (free cloud APIs)
  - Recursive context, Obsidian integration, VU meter
- [ ] System requirements
- [ ] **Quick Start Section:**
  - Zero-infrastructure setup (2 minutes):
    ```bash
    export GROQ_API_KEY="..." OPENROUTER_API_KEY="..."
    pip install -e . && second_voice
    ```
  - Privacy-conscious setup (local processing)
- [ ] Installation instructions:
  - Mention brew install python-tk for macOS
  - venv creation and activation
  - pip install -e .
- [ ] Configuration section:
  - settings.json location and format
  - All provider configurations (STT: local/groq/openai, LLM: ollama/openrouter)
  - Environment variable usage for API keys
  - Dual provider auto-detection explanation
- [ ] Provider setup (Privacy-Positive Framing):
  - **Privacy-First (Recommended for sensitive work):**
    - Local Whisper + Ollama setup
    - Docker compose, SSH tunnel
    - Complete data sovereignty
  - **Quick Start (Free tier available):**
    - Groq + OpenRouter setup
    - API key acquisition
    - No infrastructure needed
  - **Hybrid Options:**
    - Local Whisper + OpenRouter
    - Groq + Ollama
- [ ] Usage examples (bifurcated CLI):
  - Auto-detect: `second_voice`
  - Privacy-first: `second_voice --stt-provider local --llm-provider ollama`
  - Cloud quick start: `second_voice --stt-provider groq --llm-provider openrouter`
  - Specific models: `second_voice --stt-model whisper-large-v3 --llm-model anthropic/claude-3.5-sonnet`
  - Demo script: `demo_second_voice --audio samples/test.wav --verbose`
- [ ] Crash log recovery section
- [ ] Architecture overview (reference docs/architecture.md and docs/providers.md)
- [ ] Development section:
  - Running tests: `pytest`
  - Running with coverage: `pytest --cov`
- [ ] Troubleshooting section:
  - STT provider connection issues
  - LLM provider connection issues
  - API key problems
  - Crash log interpretation
- [ ] Privacy & Security section:
  - Local processing benefits
  - API key security best practices
  - Data flow transparency
- [ ] License section (MIT)
- [ ] Contributing guidelines (if applicable)

#### Task 5.1b: Create docs/providers.md (Privacy-Positive Framing)
- [ ] Overview of dual provider architecture (STT + LLM)
- [ ] **Privacy-first messaging:** Position local providers as the privacy-conscious choice

  **STT Providers:**
  - [ ] **Local Whisper (Privacy-First):**
    - Complete data sovereignty - audio never leaves your network
    - Ideal for sensitive conversations, medical/legal use
    - Configuration options and Docker setup
    - Model selection and performance tuning
  - [ ] **Groq (Free Tier, Cloud):**
    - Excellent for getting started quickly
    - Generous free tier
    - Setup instructions and API key
    - Model selection (whisper-large-v3 recommended)
  - [ ] **OpenAI (Paid, Official):**
    - Most reliable commercial option
    - Pricing (~$0.006/min)
    - Configuration options

  **LLM Providers:**
  - [ ] **Ollama (Privacy-First):**
    - Complete privacy - data stays local
    - Perfect for proprietary/confidential work
    - Full control over model selection
    - Configuration options and Docker setup
  - [ ] **OpenRouter (Pay-as-you-go, Cloud):**
    - Access to 100+ models
    - Good for occasional use or testing
    - Configuration and API key setup
    - Cost considerations and model selection

- [ ] Provider auto-detection logic explanation
- [ ] Comparison tables:
  - STT providers (Local Whisper vs Groq vs OpenAI)
  - LLM providers (Ollama vs OpenRouter)
  - Emphasize privacy benefits of local options
- [ ] Zero-infrastructure quick start (Groq + OpenRouter)
- [ ] Privacy-conscious setup (Local Whisper + Ollama)
- [ ] How to add new providers (for contributors)

#### Task 5.2: Add docstrings to all modules
- [ ] Add module-level docstrings
- [ ] Add class-level docstrings
- [ ] Add method-level docstrings
- [ ] Use Google or NumPy docstring format
- [ ] Document parameters, return values, exceptions

#### Task 5.3: Create/Update inline documentation
- [ ] Add comments for complex logic
- [ ] Document configuration options
- [ ] Document API endpoints and formats
- [ ] Add usage examples in docstrings

---

### Phase 6: Integration & Validation

#### Task 6.1: Install package in development mode
- [ ] Create/activate venv
- [ ] Run `pip install -e .`
- [ ] Verify second_voice command is available
- [ ] Verify demo_second_voice command is available

#### Task 6.2: Run full test suite
- [ ] Execute `pytest` with all tests
- [ ] Verify all tests pass
- [ ] Check code coverage report
- [ ] Fix any failing tests

#### Task 6.3: Run demo script with provider combinations
- [ ] Test with local STT + local LLM (if configured):
  - `demo_second_voice --audio samples/test.wav --stt-provider local --llm-provider ollama --verbose`
- [ ] Test with cloud STT + cloud LLM (if configured):
  - `demo_second_voice --audio samples/test.wav --stt-provider groq --llm-provider openrouter --verbose`
- [ ] Test with auto-detection:
  - `demo_second_voice --audio samples/test.wav --verbose`
- [ ] Verify successful transcription and LLM processing
- [ ] Check verbose output shows both providers being used
- [ ] Verify timing information for both STT and LLM
- [ ] Verify error handling for both providers

#### Task 6.4: Manual GUI testing with providers
- [ ] Launch `second_voice` (test auto-detection)
- [ ] Verify status shows active STT and LLM providers
- [ ] Test recording with Space key
- [ ] Verify VU meter responds to audio
- [ ] Test stop and submit
- [ ] Verify STT transcription completes
- [ ] Verify LLM processing completes
- [ ] Verify Obsidian integration
- [ ] Test context persistence
- [ ] Test clear context button
- [ ] Test keyboard shortcuts
- [ ] Test with different provider combinations using CLI flags

#### Task 6.5: Final test run
- [ ] Run pytest one more time
- [ ] Run demo script one more time with --verbose
- [ ] Document any issues
- [ ] Ensure clean exit with no errors

---

### Phase 7: Cleanup & Polish

#### Task 7.1: Code quality review
- [ ] Remove any debug print statements
- [ ] Ensure consistent code style
- [ ] Check for TODO/FIXME comments
- [ ] Verify all imports are used
- [ ] Remove unused code

#### Task 7.2: Verify documentation consolidation
- [x] Delete docs/info1.md through docs/info5.md (COMPLETED in initial commit)
- [x] Verify consolidated documentation is complete (COMPLETED)
- [ ] Final review of all documentation for accuracy

#### Task 7.3: Final documentation review
- [ ] Proofread README.md
- [ ] Verify all links work
- [ ] Check code examples in docs
- [ ] Ensure consistency across documentation

---

## Dependencies

### Runtime Dependencies
- Python >= 3.8
- pyaudio (audio recording)
- requests (API communication with Whisper, Ollama, OpenRouter)
- numpy (RMS calculation)
- tkinter (GUI - standard library but requires system package on macOS)

### Optional Runtime Dependencies
- None (all providers use standard requests library)

### System Dependencies (macOS)
```bash
brew install python-tk
```

### Development Dependencies
- pytest (testing framework)
- pytest-cov (coverage reporting)

---

## Success Criteria

The project is considered complete when:

1. ✅ All tasks above are marked complete
2. ✅ Package can be installed via `pip install -e .`
3. ✅ Both CLI commands (`second_voice` and `demo_second_voice`) are available
4. ✅ All pytest tests pass (including STT and LLM provider-specific tests)
5. ✅ **STT provider auto-detection works:**
   - Groq if GROQ_API_KEY exists
   - OpenAI if OPENAI_API_KEY exists
   - Local Whisper otherwise
6. ✅ **LLM provider auto-detection works:**
   - OpenRouter if OPENROUTER_API_KEY exists
   - Ollama otherwise
7. ✅ All provider combinations work when configured:
   - Local Whisper + Ollama (privacy-first)
   - Groq + OpenRouter (zero-infrastructure)
   - Mixed combinations (e.g., Local Whisper + OpenRouter)
8. ✅ Demo script successfully processes samples/test.wav with all available providers
9. ✅ GUI launches and responds to user input
10. ✅ VU meter displays real-time audio levels
11. ✅ Crash logs are created correctly on both STT and LLM failures
12. ✅ Crash logs preserve appropriate data (STT text for LLM failures, audio path for STT failures)
13. ✅ Verbose mode shows both STT and LLM provider information
14. ✅ Bifurcated CLI flags work correctly (--stt-* and --llm-* options)
15. ✅ README.md provides clear instructions for:
    - Zero-infrastructure quick start (Groq + OpenRouter)
    - Privacy-conscious setup (Local Whisper + Ollama)
    - All provider configurations
16. ✅ Documentation frames local providers as privacy-first choice, not as burden
17. ✅ Code follows consistent style and includes proper documentation
18. ✅ API keys are masked in verbose/debug output

---

## Risk Assessment

### Low Risk
- Configuration management refactoring
- Documentation creation
- Test writing
- Crash log implementation
- Groq STT integration (OpenAI-compatible API, well-documented)

### Medium Risk
- GUI refactoring (ensure VU meter performance on Intel MacBook)
- Audio recording module (PyAudio threading complexity)
- Entry point configuration (pyproject.toml setup)
- Dual provider abstraction (STT + LLM, ensuring all combinations work)
- Dual auto-detection logic (two independent detection systems)
- Local Whisper provider (existing dependency, should work)

### Higher Risk (but manageable)
- OpenRouter LLM API integration (new external dependency)
- OpenAI STT API integration (new external dependency)
- API key security (ensure keys aren't logged or exposed across 3 cloud providers)
- Provider combination testing (4+ combinations to validate)

### Mitigation Strategies
- Test VU meter performance early with 30ms refresh rate
- Use threading best practices for audio (callback-based, non-blocking queue)
- Verify entry points work immediately after pyproject.toml creation
- Keep existing working code as reference during refactoring
- Test on actual hardware (MacBook) throughout development
- **Provider-specific:**
  - Mock all providers thoroughly in tests (3 STT + 2 LLM = 5 provider mocks)
  - Test provider combinations systematically
  - Test auto-detection with all API key combinations
  - Document API key handling clearly for all providers
  - Implement API key masking early and verify in all output modes
  - Start with Groq (free tier) for zero-cost testing
  - Test local providers first (known working state)
  - Test cloud providers incrementally

---

## Timeline Estimate

This is an informational breakdown only (no time estimates per policy):

- **Phase 0:** Critical bug fix (temporary file location)
- **Phase 1:** Foundation setup
- **Phase 2:** Core refactoring (largest phase)
- **Phase 3:** Demo enhancement
- **Phase 4:** Test creation
- **Phase 5:** Documentation
- **Phase 6:** Integration testing
- **Phase 7:** Polish and cleanup

---

## Notes

1. **CRITICAL:** Phase 0 must complete first - fixes temporary file location violation in current code
2. The existing code is working and will serve as the reference implementation
3. Refactoring should maintain all existing functionality (currently local Whisper + Ollama only)
4. Hard-coded values should become CLI options with current values as defaults
5. The VU meter is a new visual enhancement to be added
6. Testing focuses on core logic (config, processor, recorder, **STT providers, LLM providers**) rather than GUI
7. Documentation references should point to consolidated docs/ files
8. Final validation requires clean test and demo runs with multiple provider combinations
9. All refactored code must use `tmp-*` or `*.tmp` patterns, never `/tmp/`
10. **Dual provider architecture (STT + LLM):**
    - **STT auto-detection:** Groq if GROQ_API_KEY → OpenAI if OPENAI_API_KEY → Local Whisper
    - **LLM auto-detection:** OpenRouter if OPENROUTER_API_KEY → Ollama
    - All providers (3 STT + 2 LLM = 5 total) must be fully implemented in initial refactor
    - Crash logs save appropriate data based on failure point:
      - STT failure: preserves audio file path
      - LLM failure: preserves STT transcription text
    - API keys can be in config file or environment variables
    - No API keys should appear in logs (even verbose mode must mask them)
    - CLI flags are bifurcated: `--stt-*` and `--llm-*`
11. **Privacy-positive documentation:**
    - Frame local providers (Local Whisper, Ollama) as **privacy-first choice**, not as barrier
    - Promote benefits: data sovereignty, no external dependencies, ideal for sensitive work
    - Position cloud providers (Groq, OpenRouter, OpenAI) as **convenience option**
    - Emphasize zero-infrastructure quick start for users without local GPU
    - Support all combinations (privacy-first, convenience, hybrid)
12. **Configuration migration:**
    - Old single-provider config will be migrated to new multi-provider format
    - Existing local Whisper + Ollama users will continue to work without changes
    - Cloud providers are opt-in via API key configuration
13. **Target audiences:**
    - Privacy-conscious professionals (medical, legal, proprietary work)
    - Quick-start users without infrastructure (Groq free tier + OpenRouter)
    - Developers who want full control (all local)

---

## Approval Required

This plan must be approved before implementation begins. Upon approval, work will proceed phase by phase with change documentation created concurrently in `dev_notes/changes/`.

**Instructions after approval:**
- Execute tasks sequentially within each phase
- Mark tasks complete as they finish
- Create change documentation entries for significant modifications
- Stop and ask for guidance if any uncertainties arise
- Update this plan file to track progress
