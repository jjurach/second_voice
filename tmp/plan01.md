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
├── src/
│   └── second_voice/
│       ├── __init__.py             # Package initialization
│       ├── cli.py                  # CLI entry point with argparse
│       ├── config.py               # Configuration management
│       ├── engine/
│       │   ├── __init__.py
│       │   ├── recorder.py         # Audio recording + RMS analysis
│       │   └── processor.py        # API communication (Whisper/Ollama)
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
│   └── test_recorder.py            # Audio recording tests
├── samples/
│   └── test.wav                    # Sample audio for testing
├── docs/
│   ├── architecture.md             # System architecture (created)
│   ├── gui-design.md               # GUI specifications (created)
│   └── prompts.md                  # AI prompts reference (created)
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
  - `get_default_config()` - Return default configuration dict
  - `save_config(config)` - Save configuration
  - `validate_config(config)` - Validate required fields
- [ ] Add configuration path constants
- [ ] Support environment variable overrides

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

#### Task 2.3: Create src/second_voice/engine/processor.py
- [ ] Extract API communication logic
- [ ] Create AudioProcessor class with methods:
  - `__init__(config)` - Initialize with configuration
  - `transcribe(audio_frames, rate=16000)` - Send to Whisper API
  - `process_with_llm(text, context="", system_prompt="")` - Send to Ollama
  - `_build_recursive_prompt(context, new_text)` - Build prompt with context
- [ ] **CRITICAL:** Use `tmp-audio.wav` (not `/tmp/`) for temporary audio files per AGENTS.md Rule #5
- [ ] Add timeout handling (120s default)
- [ ] Add connection error handling
- [ ] Add response validation
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
  - `--whisper-url URL` - Override Whisper API URL
  - `--ollama-url URL` - Override Ollama API URL
  - `--vault-path PATH` - Override Obsidian vault path
  - `--model MODEL` - Override Ollama model name
- [ ] Initialize configuration with CLI overrides
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
  - `--whisper-url URL` - Override Whisper API URL
  - `--model MODEL` - Override model name
- [ ] Add timing measurements (start time, end time, duration)
- [ ] Add detailed output for verbose mode:
  - Request URL
  - Request payload/files
  - Response status code
  - Response body
  - Timing information
- [ ] Add debug mode output:
  - Full request headers
  - Full response headers
  - Raw response content
- [ ] Add GPU status checks (if nvidia-smi available)
- [ ] Ensure demo uses refactored AudioProcessor module
- [ ] Add error handling and user-friendly messages

---

### Phase 4: Testing Infrastructure

#### Task 4.1: Create tests/test_config.py
- [ ] Test default configuration loading
- [ ] Test configuration file creation
- [ ] Test configuration validation
- [ ] Test configuration overrides
- [ ] Mock file system operations
- [ ] Test error handling for invalid configs

#### Task 4.2: Create tests/test_processor.py
- [ ] Test AudioProcessor initialization
- [ ] Mock API requests (Whisper and Ollama)
- [ ] Test successful transcription
- [ ] Test successful LLM processing
- [ ] Test recursive prompt building
- [ ] Test timeout handling
- [ ] Test connection error handling
- [ ] Test response validation

#### Task 4.3: Create tests/test_recorder.py
- [ ] Test AudioRecorder initialization
- [ ] Test RMS calculation with sample data
- [ ] Mock PyAudio interactions
- [ ] Test volume queue functionality
- [ ] Test start/stop recording
- [ ] Test resource cleanup

#### Task 4.4: Setup pytest configuration
- [ ] Create pytest.ini or add to pyproject.toml
- [ ] Configure test discovery
- [ ] Configure coverage reporting
- [ ] Add test markers if needed

---

### Phase 5: Documentation

#### Task 5.1: Create README.md
- [ ] Project title and description
- [ ] Features list (remote compute, recursive context, Obsidian integration, etc.)
- [ ] System requirements
- [ ] Installation instructions:
  - Mention brew install python-tk for macOS
  - venv creation and activation
  - pip install -e .
- [ ] Configuration section (settings.json location and format)
- [ ] Server setup section (Docker compose reference)
- [ ] SSH tunnel setup
- [ ] Usage examples:
  - Basic usage: `second_voice`
  - With options: `second_voice --verbose --model llama-pro`
  - Demo script: `demo_second_voice --audio samples/test.wav --verbose`
- [ ] Architecture overview (reference docs/architecture.md)
- [ ] Development section:
  - Running tests: `pytest`
  - Running with coverage: `pytest --cov`
- [ ] Troubleshooting section
- [ ] License section (MIT)
- [ ] Contributing guidelines (if applicable)

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
- requests (API communication)
- numpy (RMS calculation)
- tkinter (GUI - standard library but requires system package on macOS)

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
4. ✅ All pytest tests pass
5. ✅ Demo script successfully transcribes samples/test.wav
6. ✅ GUI launches and responds to user input
7. ✅ VU meter displays real-time audio levels
8. ✅ Verbose and debug modes show expected output
9. ✅ README.md provides clear installation and usage instructions
10. ✅ Code follows consistent style and includes proper documentation

---

## Risk Assessment

### Low Risk
- Configuration management refactoring
- Documentation creation
- Test writing

### Medium Risk
- GUI refactoring (ensure VU meter performance on Intel MacBook)
- Audio recording module (PyAudio threading complexity)
- Entry point configuration (pyproject.toml setup)

### Mitigation Strategies
- Test VU meter performance early with 30ms refresh rate
- Use threading best practices for audio (callback-based, non-blocking queue)
- Verify entry points work immediately after pyproject.toml creation
- Keep existing working code as reference during refactoring
- Test on actual hardware (MacBook) throughout development

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
3. Refactoring should maintain all existing functionality
4. Hard-coded values should become CLI options with current values as defaults
5. The VU meter is a new visual enhancement to be added
6. Testing focuses on core logic (config, processor, recorder) rather than GUI
7. Documentation references should point to consolidated docs/ files
8. Final validation requires clean test and demo runs
9. All refactored code must use `tmp-*` or `*.tmp` patterns, never `/tmp/`

---

## Approval Required

This plan must be approved before implementation begins. Upon approval, work will proceed phase by phase with change documentation created concurrently in `dev_notes/changes/`.

**Instructions after approval:**
- Execute tasks sequentially within each phase
- Mark tasks complete as they finish
- Create change documentation entries for significant modifications
- Stop and ask for guidance if any uncertainties arise
- Update this plan file to track progress
