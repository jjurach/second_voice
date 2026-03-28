# Project Plan: CLI Options for Testing & File Input

**Status:** ✅ COMPLETE
**Last Updated:** 2026-01-25 (All 5 phases implemented)

## Goal
Enable automated testing and reproducible runs by adding CLI options to preserve temporary files and inject audio input.

## Current State (Discovered via Code Exploration)

### ✅ Already Implemented
1. **CLI Arguments** (`src/cli/run.py:19-21`):
   - `--keep-files` flag exists and is passed to config
   - `--file FILE` argument exists and is passed to config as `input_file`
   - Cleanup logic respects `keep_files` (lines 69-74)

2. **TUI Mode Support** (`src/second_voice/modes/tui_mode.py:158-216`):
   - Checks for `config.get('input_file')` on startup
   - Processes input file on first run (bypasses recording)
   - Protects input file from deletion: `if audio_path != input_file` (line 207)
   - Respects `keep_files` for generated temp files

3. **Menu Mode Support** (`src/second_voice/modes/menu_mode.py:128-137`):
   - Checks for `config.get('input_file')` on startup
   - Processes input file directly (bypasses menu)
   - **⚠️ MISSING:** File protection (doesn't check if file is input_file before cleanup)

4. **Base Mode Cleanup** (`src/second_voice/modes/base.py:106-120`):
   - Already checks `config.get('keep_files')` before cleanup
   - Cleans up `mode_tmp/` directory when `keep_files=False`

5. **Recorder Cleanup** (`src/second_voice/core/recorder.py:154-166`):
   - Cleanup targets `tmp-audio-*.wav` pattern only
   - Age-based cleanup (24 hours default)
   - Naturally avoids deleting user files (different naming pattern)

6. **Test Infrastructure** (Verified):
   - `tests/conftest.py` - Mock fixtures exist
   - `tests/test_*.py` - Unit tests exist for config, processor, recorder
   - `samples/test.wav` - Real test audio file exists (1.7MB)
   - `TESTING.md` - Comprehensive testing documentation

7. **Documentation** (`README.md:56-86`):
   - Testing section exists
   - Documents `--file` and `--keep-files` flags
   - Explains temporary file locations
   - References `scripts/demo_second_voice.py`

### ❌ Not Yet Implemented
1. **Input File Validation** (`src/cli/run.py`):
   - No check that file exists before passing to modes
   - No check that file is readable
   - No validation of file format

2. **Menu Mode File Protection** (`src/second_voice/modes/menu_mode.py`):
   - Missing explicit check to protect input_file from cleanup
   - Unlike TUI mode, doesn't verify `audio_path != input_file`

3. **GUI Mode Support** (`src/second_voice/modes/gui_mode.py`):
   - No support for `input_file` config option
   - No error/warning when `--file` used with GUI mode
   - Unclear behavior when auto-detection picks GUI with `--file` arg

4. **Integration Tests**:
   - No end-to-end tests for `--file` workflow
   - No tests verifying file protection logic
   - No tests for `--keep-files` behavior

## Design Clarifications (From User Requirements)

### File Lifecycle Rules
1. **User-provided files** (via `--file`): **NEVER** delete under any circumstances
2. **Generated files** (by recorder/modes): Delete unless `--keep-files=True`
3. **When `--file` is used**: `--keep-files` flag becomes irrelevant (input file already protected)
4. **`--keep-files` scope**: Preserves ALL temp files:
   - Audio recordings in `tmp/` (from recorder)
   - Editor temp files in `tmp/mode_tmp/` (from modes)

### Audio Format Support
- **Supported Formats**: Whatever `soundfile.read()` supports (verified: WAV, FLAC, OGG, MP3, AIFF, AU, and 25+ others)
- **Validation**: If file is corrupted or unreadable, fail with clear error message
- **No size limits** for now

### Editor Compatibility
- **User responsibility**: Users should test their editor command supports file arguments
- **Example limitation**: Some editors may only support stdin/stdout, not `--file` flag
- **Strategy**: Document limitations as discovered during testing; no preemptive restrictions

### GUI Mode with `--file`
- **Current**: GUI mode doesn't check for input_file
- **Recommendation**: Show error or warning if `--file` used with GUI mode
- **Alternative**: Auto-downgrade to TUI/menu mode when `--file` detected

## Implementation Plan

### Phase 1: Input File Validation (High Priority)
**File:** `src/cli/run.py`

Add validation after argument parsing (around line 36):
```python
if args.file:
    input_file_path = os.path.abspath(args.file)

    # Validate file exists
    if not os.path.exists(input_file_path):
        print(f"Error: Input file not found: {input_file_path}")
        sys.exit(1)

    # Validate file is readable
    if not os.access(input_file_path, os.R_OK):
        print(f"Error: Input file not readable: {input_file_path}")
        sys.exit(1)

    # Validate file format (try to open with soundfile)
    try:
        import soundfile as sf
        info = sf.info(input_file_path)
        if args.verbose:
            print(f"Detected audio: {info.samplerate}Hz, {info.channels}ch, {info.duration:.1f}s")
    except Exception as e:
        print(f"Error: Invalid audio file: {e}")
        sys.exit(1)

    config.set('input_file', input_file_path)
```

**Success Criteria:**
- File existence checked before modes execute
- Clear error messages for missing/unreadable/corrupt files
- Verbose mode shows audio file info

### Phase 2: Menu Mode File Protection (High Priority)
**File:** `src/second_voice/modes/menu_mode.py`

Add file protection to cleanup logic (need to identify where cleanup happens):
```python
# After processing audio_path
if audio_path and os.path.exists(audio_path):
    # Protect user-provided input file
    input_file = self.config.get('input_file')
    if audio_path != input_file:
        if not self.config.get('keep_files'):
            os.unlink(audio_path)
    # else: Never delete user's input file
```

**Success Criteria:**
- Input file never deleted in menu mode
- Generated files still cleaned up when `keep_files=False`
- Behavior matches TUI mode

### Phase 3: GUI Mode Compatibility (Medium Priority)
**File:** `src/second_voice/modes/gui_mode.py` or `src/cli/run.py`

**Option A:** Error in run.py before mode instantiation:
```python
# After mode detection
if mode_name == 'gui' and config.get('input_file'):
    print("Warning: --file not supported in GUI mode. Use --mode tui or --mode menu instead.")
    print("Falling back to menu mode...")
    mode_name = 'menu'
```

**Option B:** Error in gui_mode.py:
```python
def __init__(self, config, recorder, processor):
    if config.get('input_file'):
        raise ValueError("GUI mode does not support --file input. Use TUI or Menu mode instead.")
    super().__init__(config, recorder, processor)
```

**Decision:** Option A preferred (cleaner UX, automatic fallback)

**Success Criteria:**
- Clear warning when `--file` used with GUI mode
- Automatic fallback to menu mode
- No crash or undefined behavior

### Phase 4: Integration Tests (Medium Priority)
**File:** `tests/test_cli_integration.py` (new file)

Create end-to-end tests:
```python
def test_file_input_menu_mode(temp_dir):
    """Test --file flag with menu mode"""
    # Use samples/test.wav
    # Run menu mode with input file
    # Verify file still exists after run
    # Verify output was generated

def test_file_input_tui_mode(temp_dir):
    """Test --file flag with TUI mode"""
    # Similar to menu mode test

def test_keep_files_preserves_temps(temp_dir):
    """Test --keep-files flag"""
    # Run with --keep-files
    # Verify tmp/ and mode_tmp/ still exist

def test_file_input_protection(temp_dir):
    """Test that input file is never deleted"""
    # Create test file
    # Run without --keep-files
    # Verify input file still exists

def test_invalid_file_handling():
    """Test error handling for invalid files"""
    # Test missing file
    # Test corrupted file
    # Test unreadable file
```

**Success Criteria:**
- All integration tests pass
- File protection verified
- Error handling verified

### Phase 5: Documentation Updates (Low Priority)
**Files:** `README.md`, `TESTING.md`

Minor updates needed:
1. **README.md**:
   - Clarify that `samples/test.wav` already exists (line 58)
   - Add note about editor compatibility testing
   - Document supported audio formats (reference soundfile)

2. **TESTING.md**:
   - Add section on integration testing with `--file`
   - Document test audio fixtures location

**Success Criteria:**
- Documentation accurate and complete
- Examples work as written

## Task Dependencies

```
Phase 1 (Validation) ─┬─> Phase 2 (Menu Protection)
                      │
                      ├─> Phase 3 (GUI Compatibility)
                      │
                      └─> Phase 4 (Integration Tests)
                                │
                                └─> Phase 5 (Documentation)
```

**Recommended Order:** 1 → 2 → 3 → 4 → 5

## Verification Checklist

After implementation, verify:
- [ ] `python src/cli/run.py --file nonexistent.wav` → Clear error
- [ ] `python src/cli/run.py --file samples/test.wav --mode menu` → File processed, not deleted
- [ ] `python src/cli/run.py --file samples/test.wav --mode tui` → File processed, not deleted
- [ ] `python src/cli/run.py --file samples/test.wav --mode gui` → Warning + fallback or error
- [ ] `python src/cli/run.py --keep-files` → Temp files preserved in `tmp/` and `tmp/mode_tmp/`
- [ ] `python src/cli/run.py` → Normal recording, temp files cleaned up
- [ ] `pytest tests/test_cli_integration.py -v` → All integration tests pass

## Audio Format Support

The `soundfile` library (used by the recorder) supports reading:
- **WAV** (primary format for generated recordings)
- **FLAC, OGG, MP3** (compressed formats)
- **AIFF, AU, CAF** (Apple/Unix formats)
- **And 25+ additional formats**

See full list: `python -c "import soundfile; print(soundfile.available_formats())"`

## Risks & Mitigations

| Risk | Mitigation | Status |
|------|-----------|--------|
| Deleting user input file | Explicit checks in TUI/menu modes; different naming pattern for generated files | ✅ COMPLETE (both modes protected) |
| Corrupted file crashes app | Validate with soundfile before processing | ✅ COMPLETE |
| GUI mode undefined behavior with --file | Auto-fallback to menu/TUI mode | ✅ COMPLETE |
| Test fixtures missing | samples/test.wav already exists | ✅ COMPLETE |

## Deliverables

- [x] CLI arguments (--keep-files, --file) - Already done
- [x] TUI mode input file support - Already done
- [x] Menu mode input file support - ✅ COMPLETE (protection added)
- [x] Input file validation in run.py - ✅ COMPLETE Phase 1
- [x] Menu mode file protection - ✅ COMPLETE Phase 2
- [x] GUI mode compatibility - ✅ COMPLETE Phase 3
- [x] Integration tests - ✅ COMPLETE Phase 4
- [x] Documentation polish - ✅ COMPLETE Phase 5
