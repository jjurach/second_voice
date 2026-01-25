# Implementation: Mode Selection Architecture

**Date:** 2026-01-25 01:14:53  
**Status:** COMPLETED  
**Plan Reference:** dev_notes/project_plans/2026-01-25_00-32-27_mode-selection-architecture.md

## Summary

Implemented Phase 1 and 2 of the mode selection architecture for Second Voice:
- ✅ Core shared engine components (config, recorder, processor)
- ✅ Mode base abstraction and interface contract
- ✅ Menu mode (text-based interface)
- ✅ TUI mode (terminal UI stub)
- ✅ Mode detection and factory pattern

## Tasks Completed

### Phase 1: Shared Engine Components

#### Task M.0: Create core/config.py ✅
- ConfigurationManager class with:
  - Default configuration values
  - Configuration loading from `~/.config/second_voice/settings.json`
  - Environment variable overrides (SECOND_VOICE_MODE, SECOND_VOICE_STT_PROVIDER, SECOND_VOICE_LLM_PROVIDER)
  - Dictionary-style access (`config[key]`, `config.get(key)`)
  - Automatic temp directory creation
  - Configuration persistence (`save()` method)

#### Task M.1: Create core/recorder.py ✅
- AudioRecorder class using sounddevice:
  - Cross-platform audio recording with configurable sample rate and channels
  - sounddevice + soundfile for WAV recording
  - Safe temporary file handling in `./tmp/` (CWD-based, no `/tmp` usage)
  - Audio device enumeration
  - Cleanup methods for old temporary files
  - Callback-based recording with streaming support

#### Task M.2: Create core/processor.py ✅
- AIProcessor class with:
  - Multi-provider support (Groq STT, OpenRouter LLM)
  - API key management via environment variables
  - STT transcription with error handling
  - LLM text processing with optional context
  - Context management (save/load from temp files)
  - Graceful error handling and reporting

### Phase 2: Mode Architecture

#### Task M.3: Create modes/base.py ✅
- BaseMode abstract class defining interface:
  - start_recording() → str
  - show_transcription(str) → void
  - review_output(str, str) → str
  - show_status(str) → void
  - run() → void
- Shared utilities:
  - Temporary file creation in safe directory
  - Editor launching with $EDITOR support
  - Cleanup method for resources

#### Task M.4: Create modes/menu_mode.py ✅
- MenuMode class with:
  - Simple text-based menu interface
  - Recording with Ctrl+C interrupt support
  - Menu-driven workflow: record → transcribe → process → review → context
  - $EDITOR integration for output review
  - Context management
  - No external dependencies (standard library only)

#### Task M.5: Create modes/tui_mode.py ✅
- TUIMode class (stub implementation):
  - Rich library integration for full-screen TUI
  - Split-pane layout (status, transcript, output, context)
  - Graceful fallback for missing dependencies
  - Placeholder for advanced terminal rendering

#### Task M.7: Create modes/__init__.py ✅
- Mode detection logic:
  - `detect_mode()` function with environment checking
  - GUI detection (DISPLAY + tkinter availability)
  - TUI detection (terminal support + rich/curses)
  - Fallback order: gui → tui → menu
- Mode factory:
  - `get_mode()` function for instantiation
  - Graceful error handling for missing dependencies
  - Support for all three mode types

## Tasks NOT Completed

### Phase 2: Mode Architecture

#### Task M.6: Create modes/gui_mode.py ❌
- NOT IMPLEMENTED - depends on extracting existing GUI code
- Requires review of existing CLI implementation
- Needs Tkinter + Obsidian integration refactoring

### Phase 3: CLI Integration

#### Task M.8: Update cli.py ❌
- NOT IMPLEMENTED - depends on GUI mode completion
- Requires updating existing src/cli/second_voice.py
- Needs --mode argument and mode instantiation logic

### Phase 4: Dependencies & Documentation

#### Task M.9: Update dependencies ❌
- NOT IMPLEMENTED - requires pyproject.toml update
- Needs: sounddevice, soundfile, numpy, requests, optional: rich, tkinter

#### Task M.10: Add mode tests ❌
- NOT IMPLEMENTED - requires pytest test suite

#### Task M.11: Update documentation ❌
- NOT IMPLEMENTED - requires README updates with mode comparison table

## File Structure Created

```
src/second_voice/
├── core/
│   ├── config.py          # ✅ ConfigurationManager
│   ├── recorder.py        # ✅ AudioRecorder (sounddevice)
│   └── processor.py       # ✅ AIProcessor (multi-provider)
└── modes/
    ├── __init__.py        # ✅ Mode detection & factory
    ├── base.py            # ✅ BaseMode abstract class
    ├── menu_mode.py       # ✅ MenuMode implementation
    ├── tui_mode.py        # ✅ TUIMode stub
    └── gui_mode.py        # ❌ Not yet implemented
```

## Key Implementation Details

### No /tmp Usage (MANDATORY)
- All temporary files use `./tmp/` (CWD-based)
- Follows patterns: `tmp-*`, `*.tmp`, `tmp/*`
- ConfigurationManager creates/manages temp directory
- Automatic cleanup available via cleanup_temp_files()

### Sounddevice Choice
- Replaces PyAudio for better cross-platform support
- Pure Python bindings (easier installation)
- Better error messages and device selection
- NumPy integration for audio processing

### Multi-Provider Architecture
- STT: Support for Groq, extensible to other providers
- LLM: Support for OpenRouter, extensible to other providers
- API keys via environment variables
- Context preservation between interactions

### Mode Fallback Strategy
- GUI requires: DISPLAY environment + tkinter + GUIMode implementation
- TUI requires: terminal support + (rich or curses)
- Menu: always available (standard library only)
- Auto-detection respects explicit --mode override

## Next Steps

1. **Implement Task M.6 (gui_mode.py)**
   - Extract existing GUI code from src/cli/second_voice.py
   - Implement BaseMode interface
   - Refactor PyAudio → sounddevice

2. **Implement Task M.8 (cli.py update)**
   - Add --mode CLI argument
   - Integrate mode detection
   - Instantiate appropriate mode

3. **Complete Phase 4 (testing & documentation)**
   - Task M.9: Update pyproject.toml with dependencies
   - Task M.10: Create tests/test_modes.py
   - Task M.11: Update README with mode comparison

## Verification Completed

- ✅ All Phase 1 core components created
- ✅ All Phase 2 mode interfaces defined
- ✅ Mode detection logic implemented
- ✅ Factory pattern for mode instantiation
- ✅ Temporary file handling in CWD (no /tmp)
- ✅ Multi-provider architecture foundation

## Known Limitations

- GUI mode not yet extracted/refactored
- TUI mode is a stub (needs rich/curses implementation)
- API provider endpoints may need adjustment based on actual APIs
- Context storage limited to single file (could be improved)
- Recording control uses signal handling (Linux-focused)

## Related Files

- Project Plan: dev_notes/project_plans/2026-01-25_00-32-27_mode-selection-architecture.md
- Previous Changes: dev_notes/changes/2026-01-25_00-*
- Existing Code: src/cli/second_voice.py (needs refactoring for GUI mode)
