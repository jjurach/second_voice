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
│       │   └── providers/
│       │       ├── __init__.py
│       │       ├── base.py         # BaseLLMProvider (abstract)
│       │       ├── ollama.py       # OllamaProvider implementation
│       │       └── openrouter.py   # OpenRouterProvider implementation
│       └── ui/
│           ├── __init__.py
│           ├── main_window.py      # Main Tkinter application
│           └── components.py       # VU meter components
├── scripts/
│   └── demo_second_voice.py        # Demo script for testing
├── tests/
│   ├── __init__.py
│   ├── test_config.py              # Configuration tests
│   ├── test_processor.py           # API processing tests
│   ├── test_recorder.py            # Audio recording tests
│   └── test_providers.py           # LLM provider tests
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
  - `get_default_config()` - Return default configuration dict with both providers
  - `save_config(config)` - Save configuration
  - `validate_config(config)` - Validate required fields
  - `get_llm_provider()` - Auto-detect provider (OpenRouter if API key, else Ollama)
- [ ] Add configuration path constants
- [ ] Support environment variable substitution (e.g., ${OPENROUTER_API_KEY})
- [ ] Default config structure includes both ollama and openrouter sections
- [ ] Add helper to check if provider is configured

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

This task is broken into subtasks for the provider pattern implementation.

##### Task 2.3a: Create src/second_voice/engine/providers/base.py
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

##### Task 2.3b: Create src/second_voice/engine/providers/ollama.py
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

##### Task 2.3c: Create src/second_voice/engine/providers/openrouter.py
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

##### Task 2.3d: Create provider factory and processor
- [ ] Create `get_provider(config, provider_name=None)` factory function:
  - If provider_name specified, use that
  - Else auto-detect: OpenRouter if API key exists, else Ollama
  - Instantiate and return appropriate provider
- [ ] Create src/second_voice/engine/processor.py:
  - `__init__(config)` - Initialize with configuration
  - `transcribe(audio_frames, rate=16000)` - Send to Whisper API
  - `process_with_llm(text, context="")` - Delegate to LLM provider
  - `_save_crash_log(stt_text, error)` - Save to tmp-crash-{timestamp}.txt
  - `_build_recursive_prompt(context, new_text)` - Shared prompt logic
- [ ] **CRITICAL:** Use `tmp-audio.wav` (not `/tmp/`) for temporary audio files per AGENTS.md Rule #5
- [ ] Wrap LLM calls with try/except, save crash log on failure
- [ ] Include original STT text, error details, and stack trace in crash log
- [ ] Support verbose/debug output modes

#### Task 2.4: Create src/second_voice/ui/components.py
- [ ] Create VUVisualizer class (tkinter.Canvas subclass)
  - `__init__(parent, **kwargs)` - Initialize canvas
  - `update_amplitude(amplitude)` - Update visual based on 0-1 amplitude
  - `reset()` - Return to standby state
- [ ] Implement core pulse rendering (circle with color interpolation)
- [ ] Implement lateral level bars (10 segments per side)
- [ ] Add taper effect for professional appearance
- [ ] Optimize using canvas.coords() for performance

#### Task 2.5: Create src/second_voice/ui/main_window.py
- [ ] Create MainWindow class for primary GUI
- [ ] Extract and refactor GUI logic from current script
- [ ] Integrate VUVisualizer component
- [ ] Implement recorder integration via volume queue
- [ ] Add 30ms refresh loop for VU meter
- [ ] Implement keyboard shortcuts (Space, Enter)
- [ ] Add context management (display, clear)
- [ ] Implement Obsidian integration
- [ ] Add error dialogs and user feedback

#### Task 2.6: Create src/second_voice/cli.py
- [ ] Create main() function as entry point
- [ ] Implement argument parsing with argparse:
  - `--verbose` - Show detailed information (URLs, responses, timings)
  - `--debug` - Show debug information (payloads, full traces)
  - `--config PATH` - Override default config file path
  - `--provider {ollama,openrouter}` - Override auto-detected provider
  - `--model MODEL` - Override model name for selected provider
  - `--api-key KEY` - Override OpenRouter API key
  - `--whisper-url URL` - Override Whisper API URL
  - `--vault-path PATH` - Override Obsidian vault path
- [ ] Initialize configuration with CLI overrides
- [ ] Validate provider configuration before launching GUI
- [ ] Display provider info in verbose mode (which provider, which model)
- [ ] Launch GUI (MainWindow)
- [ ] Add logging configuration based on verbose/debug flags

#### Task 2.7: Create src/second_voice/__init__.py
- [ ] Define __version__
- [ ] Import and expose main classes (AudioRecorder, AudioProcessor, MainWindow, Config)
- [ ] Add package-level documentation

---

### Phase 3: Demo Script Enhancement

#### Task 3.1: Refactor scripts/demo_second_voice.py
- [ ] Update imports to use new second_voice package modules
- [ ] Use samples/test.wav as default input file
- [ ] Add argparse for command-line options:
  - `--audio PATH` - Path to audio file (default: samples/test.wav)
  - `--verbose` - Show detailed information
  - `--debug` - Show debug information
  - `--provider {ollama,openrouter}` - Override auto-detected provider
  - `--model MODEL` - Override model name
  - `--api-key KEY` - Override OpenRouter API key
  - `--whisper-url URL` - Override Whisper API URL
- [ ] Add timing measurements (start time, end time, duration)
- [ ] Display active provider and model in output
- [ ] Add detailed output for verbose mode:
  - Active LLM provider
  - Request URL
  - Request payload/files
  - Response status code
  - Response body
  - Timing information
- [ ] Add debug mode output:
  - Full request headers
  - Full response headers
  - Raw response content
- [ ] Add GPU status checks (if nvidia-smi available, for Ollama)
- [ ] Ensure demo uses refactored AudioProcessor module with provider pattern
- [ ] Add error handling and user-friendly messages
- [ ] Test with both Ollama and OpenRouter if configured

---

### Phase 4: Testing Infrastructure

#### Task 4.1: Create tests/test_config.py
- [ ] Test default configuration loading
- [ ] Test configuration file creation
- [ ] Test configuration validation
- [ ] Test configuration overrides
- [ ] Mock file system operations
- [ ] Test error handling for invalid configs

#### Task 4.2: Create tests/test_providers.py
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
- [ ] Test provider factory (get_provider):
  - Test auto-detection with OPENROUTER_API_KEY env var
  - Test auto-detection without API key (defaults to Ollama)
  - Test explicit provider selection
  - Test invalid provider name handling

#### Task 4.3: Create tests/test_processor.py
- [ ] Test AudioProcessor initialization with different providers
- [ ] Mock Whisper API requests
- [ ] Test successful transcription
- [ ] Test LLM processing delegates to provider correctly
- [ ] Test crash log creation on LLM failure
- [ ] Verify crash log contains STT text, error, and stack trace
- [ ] Test crash log file naming (tmp-crash-{timestamp}.txt)
- [ ] Test timeout handling
- [ ] Test connection error handling

#### Task 4.4: Create tests/test_recorder.py
- [ ] Test AudioRecorder initialization
- [ ] Test RMS calculation with sample data
- [ ] Mock PyAudio interactions
- [ ] Test volume queue functionality
- [ ] Test start/stop recording
- [ ] Test resource cleanup

#### Task 4.5: Setup pytest configuration
- [ ] Create pytest.ini or add to pyproject.toml
- [ ] Configure test discovery
- [ ] Configure coverage reporting
- [ ] Add test markers if needed

---

### Phase 5: Documentation

#### Task 5.1: Create README.md
- [ ] Project title and description
- [ ] Features list (multi-provider LLM, remote compute, recursive context, Obsidian integration, etc.)
- [ ] System requirements
- [ ] Installation instructions:
  - Mention brew install python-tk for macOS
  - venv creation and activation
  - pip install -e .
- [ ] Configuration section:
  - settings.json location and format
  - Both Ollama and OpenRouter configuration
  - Environment variable usage for API keys
  - Provider auto-detection explanation
- [ ] Provider setup:
  - Ollama setup (Docker compose, SSH tunnel)
  - OpenRouter setup (API key acquisition)
  - How to switch between providers
- [ ] Usage examples:
  - Basic usage: `second_voice` (auto-detects provider)
  - With Ollama: `second_voice --provider ollama --model llama-pro`
  - With OpenRouter: `second_voice --provider openrouter --model anthropic/claude-3.5-sonnet`
  - Demo script: `demo_second_voice --audio samples/test.wav --verbose`
- [ ] Crash log recovery section
- [ ] Architecture overview (reference docs/architecture.md and docs/providers.md)
- [ ] Development section:
  - Running tests: `pytest`
  - Running with coverage: `pytest --cov`
- [ ] Troubleshooting section:
  - Provider connection issues
  - API key problems
  - Crash log interpretation
- [ ] License section (MIT)
- [ ] Contributing guidelines (if applicable)

#### Task 5.1b: Create docs/providers.md
- [ ] Overview of provider architecture
- [ ] Ollama provider documentation:
  - Configuration options
  - Setup instructions
  - Model selection
  - Troubleshooting
- [ ] OpenRouter provider documentation:
  - Configuration options
  - API key setup
  - Model selection (link to OpenRouter model list)
  - Cost considerations
  - Rate limits
  - Troubleshooting
- [ ] Provider auto-detection logic explanation
- [ ] How to add new providers (for contributors)
- [ ] Comparison table (Ollama vs OpenRouter)

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

#### Task 6.3: Run demo script
- [ ] Execute `demo_second_voice --audio samples/test.wav --verbose`
- [ ] Verify successful transcription
- [ ] Check verbose output contains expected details
- [ ] Verify error handling

#### Task 6.4: Manual GUI testing
- [ ] Launch `second_voice`
- [ ] Test recording with Space key
- [ ] Verify VU meter responds to audio
- [ ] Test stop and submit
- [ ] Verify Obsidian integration
- [ ] Test context persistence
- [ ] Test clear context button
- [ ] Test keyboard shortcuts

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
- None (both Ollama and OpenRouter use standard requests library)

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
4. ✅ All pytest tests pass (including provider-specific tests)
5. ✅ Demo script successfully transcribes samples/test.wav with both providers
6. ✅ Provider auto-detection works correctly (OpenRouter if API key, else Ollama)
7. ✅ GUI launches and responds to user input
8. ✅ VU meter displays real-time audio levels
9. ✅ Crash logs are created correctly on LLM failure
10. ✅ Both Ollama and OpenRouter providers work when configured
11. ✅ Verbose and debug modes show provider information
12. ✅ README.md provides clear installation and usage instructions for both providers
13. ✅ Code follows consistent style and includes proper documentation
14. ✅ CLI flags for provider selection work correctly

---

## Risk Assessment

### Low Risk
- Configuration management refactoring
- Documentation creation
- Test writing
- Crash log implementation

### Medium Risk
- GUI refactoring (ensure VU meter performance on Intel MacBook)
- Audio recording module (PyAudio threading complexity)
- Entry point configuration (pyproject.toml setup)
- Provider abstraction (ensuring both providers work correctly)
- Auto-detection logic (API key detection, fallback behavior)

### Higher Risk (but manageable)
- OpenRouter API integration (new external dependency, requires testing without local setup)
- API key security (ensure keys aren't logged or exposed)

### Mitigation Strategies
- Test VU meter performance early with 30ms refresh rate
- Use threading best practices for audio (callback-based, non-blocking queue)
- Verify entry points work immediately after pyproject.toml creation
- Keep existing working code as reference during refactoring
- Test on actual hardware (MacBook) throughout development
- **Provider-specific:**
  - Mock both providers thoroughly in tests
  - Test provider switching manually with both services
  - Document API key handling clearly
  - Add warnings if API keys appear in verbose output
  - Test auto-detection with and without API keys

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
3. Refactoring should maintain all existing functionality (currently Ollama-only)
4. Hard-coded values should become CLI options with current values as defaults
5. The VU meter is a new visual enhancement to be added
6. Testing focuses on core logic (config, processor, recorder, **providers**) rather than GUI
7. Documentation references should point to consolidated docs/ files
8. Final validation requires clean test and demo runs
9. All refactored code must use `tmp-*` or `*.tmp` patterns, never `/tmp/`
10. **Provider architecture:**
    - Default behavior: auto-detect (OpenRouter if API key exists, else Ollama)
    - Both providers must be fully implemented in initial refactor
    - Crash logs save unprocessed STT text when LLM fails
    - API keys can be in config file or environment variables
    - No API keys should appear in logs (even verbose mode should mask them)
11. **Configuration migration:**
    - Old single-provider config will be migrated to new dual-provider format
    - Existing Ollama users will continue to work without changes
    - OpenRouter is opt-in via API key configuration

---

## Approval Required

This plan must be approved before implementation begins. Upon approval, work will proceed phase by phase with change documentation created concurrently in `dev_notes/changes/`.

**Instructions after approval:**
- Execute tasks sequentially within each phase
- Mark tasks complete as they finish
- Create change documentation entries for significant modifications
- Stop and ask for guidance if any uncertainties arise
- Update this plan file to track progress
