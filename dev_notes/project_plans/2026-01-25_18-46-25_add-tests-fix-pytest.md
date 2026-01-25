# Project Plan: Add Unit Tests & Fix pytest

**Created:** 2026-01-25 18:46:25
**Status:** Awaiting Approval

## Overview
Install and configure pytest, then add unit tests for critical code paths (config, processor, recorder, modes, CLI) with mocked external services. Focus on offline-first testing with optional integration mode.

## Phase 1: Setup & Configuration
**Goal:** Get pytest installed and configured, establish test infrastructure

### 1.1 Install pytest and dependencies
- Add pytest to `requirements.txt` or install via `pip install pytest pytest-cov`
- Verify installation: `python -m pytest --version`

### 1.2 Create pytest configuration file
- Create `pytest.ini` with:
  - Test discovery patterns
  - Mock markers for integration tests
  - Coverage thresholds
  - Output formatting

### 1.3 Create conftest.py
- Add fixtures for:
  - Mock config loader
  - Mock Groq/Whisper API clients
  - Mock Ollama/OpenRouter clients
  - Temporary test directories
  - Integration test markers

### 1.4 Verify existing tests work with pytest
- Migrate `tests/test_modes.py` if needed (currently uses unittest)
- Run: `pytest` (should pass 8 tests)
- Verify isolation and no side effects

---

## Phase 2: Config Module Tests
**File:** `tests/test_config.py`
**Target Module:** `src/second_voice/core/config.py` (81 lines)

### 2.1 Test config loading
- Load default config
- Load from file
- Load from environment variables
- Override hierarchy (env > file > defaults)

### 2.2 Test config validation
- Valid provider names
- Invalid provider names raise errors
- Missing required fields detected

### 2.3 Test config methods
- `get_provider_config()`
- `get_llm_config()`
- `save()` method if it exists

---

## Phase 3: Processor Module Tests
**File:** `tests/test_processor.py`
**Target Module:** `src/second_voice/core/processor.py` (221 lines)

### 3.1 Test transcription - Groq provider
- Mock successful transcription
- Mock API error handling
- Test with different audio formats

### 3.2 Test transcription - Local Whisper
- Mock Whisper service response
- Test timeout handling
- Test service unavailable

### 3.3 Test LLM processing - Ollama
- Mock successful LLM response
- Mock API error
- Test prompt construction

### 3.4 Test LLM processing - OpenRouter
- Mock successful response
- Mock API key validation failure
- Test rate limiting

### 3.5 Test context management
- Save/load conversation context
- Context file cleanup

---

## Phase 4: Recorder Module Tests
**File:** `tests/test_recorder.py` (expand existing minimal test)
**Target Module:** `src/second_voice/core/recorder.py` (173 lines)

### 4.1 Test recorder initialization
- Default device selection
- List available devices
- Invalid device handling

### 4.2 Test recording operations
- Start/stop recording (already exists, expand)
- Cancel recording
- Save recorded audio

### 4.3 Test cleanup
- Temporary file deletion
- Resource cleanup

---

## Phase 5: Modes Module Tests
**File:** `tests/test_modes_extended.py`
**Target Modules:**
- `src/second_voice/modes/__init__.py` (82 lines)
- `src/second_voice/modes/base.py` (120 lines)
- `src/second_voice/modes/menu_mode.py` (214 lines)
- `src/second_voice/modes/tui_mode.py` (233 lines)
- `src/second_voice/modes/gui_mode.py` (164 lines)

### 5.1 Test base mode
- Initialization
- Editor launch functionality
- Temporary file creation/cleanup

### 5.2 Test mode selection (expand existing)
- GUI mode detection
- TUI mode detection
- Menu mode detection
- Invalid config handling

### 5.3 Test mode instantiation
- Menu mode initialization
- TUI mode initialization
- GUI mode initialization

---

## Phase 6: CLI Entry Point Tests
**File:** `tests/test_cli.py`
**Target Module:** `src/cli/run.py` (76 lines)

### 6.1 Test CLI argument parsing
- Default arguments
- Custom mode selection
- Config file override
- Provider selection

### 6.2 Test CLI error handling
- Missing required dependencies
- Invalid mode
- Missing config file

---

## Phase 7: Integration & Polish
**Goal:** Finalize and verify

### 7.1 Run full test suite
- `pytest` - All offline tests pass
- `pytest -P integration` - Integration tests run (mocks can be disabled)
- `pytest --cov` - Coverage report

### 7.2 Update test configuration
- Set coverage threshold (target: 60%+)
- Add pytest plugins if needed
- Configure CI/CD markers

### 7.3 Documentation
- Update README with test instructions
- Document how to run mocked vs integration tests
- Document fixture usage for future tests

---

## Implementation Order
1. Phase 1 (Setup) - Must complete first
2. Phase 2 (Config) - Simplest, builds foundation
3. Phase 4 (Recorder) - Expand existing tests
4. Phase 3 (Processor) - Most complex, many mocks
5. Phase 5 (Modes) - Expand existing tests
6. Phase 6 (CLI) - Final integration
7. Phase 7 (Polish) - Verification and documentation

## Files to Create/Modify

**New Files:**
- `pytest.ini`
- `tests/conftest.py`
- `tests/test_config.py`
- `tests/test_processor.py`
- `tests/test_recorder.py` (expand existing)
- `tests/test_modes_extended.py`
- `tests/test_cli.py`

**Modified Files:**
- `tests/test_modes.py` - Ensure pytest compatibility
- `requirements.txt` - Add pytest, pytest-cov
- `pyproject.toml` - May need test markers config

**Not Modified:**
- Source files in `src/` - No changes to implementation

## Test Infrastructure Details

### Mocking Strategy
- Use `unittest.mock` (built-in, no extra dependencies)
- Mock all external API calls (Groq, Ollama, OpenRouter, Whisper) by default
- Tests check for environment variables to enable live API access
- If `ENABLE_LIVE_API=1` or `ENABLE_LIVE_GROQ=1` etc., use real APIs instead of mocks
- Create fixtures for common mocks

### Running Tests
```bash
pytest                           # All unit tests with mocks
pytest --cov=src -v             # Verbose with coverage
pytest --co                      # List all tests

# Enable live API testing:
ENABLE_LIVE_API=1 pytest        # Use real APIs (requires valid config/keys)
ENABLE_LIVE_GROQ=1 pytest       # Enable only Groq live testing
ENABLE_LIVE_WHISPER=1 pytest    # Enable only Whisper live testing
ENABLE_LIVE_OLLAMA=1 pytest     # Enable only Ollama live testing
```

## Risk Assessment
- **Low Risk:** Setup and config tests
- **Medium Risk:** Processor tests (many API mocks)
- **Medium Risk:** Mode tests (UI interaction mocking)
- **Low Risk:** Recorder tests (device mocking)
- **Low Risk:** CLI tests (argument parsing)

## Success Criteria
✅ pytest installed and working
✅ All tests pass offline
✅ Config module 100% tested
✅ Processor critical paths covered (transcription, LLM)
✅ Modes initialization tested
✅ Recorder operations tested
✅ CLI entry point tested
✅ Coverage report shows 60%+ on critical modules
✅ Integration test mode available but not required

## Estimated Scope
- **New test code:** ~1500-2000 lines
- **Configuration files:** ~50 lines
- **Documentation updates:** ~100 lines
