# Switch from PyAudio to sounddevice

## Change Type
Documentation - Project Plan Revision (Breaking Change)

## Date
2026-01-25 00:56:24

## Summary
Updated the mode selection architecture plan to use `sounddevice` + `soundfile` instead of PyAudio for audio recording, solving cross-platform installation issues.

## Problem

PyAudio has significant cross-platform installation issues:

### Ubuntu/Linux Issues:
- Requires system packages: `portaudio19-dev`, `python3-dev`
- Needs manual apt-get installation before pip install
- ALSA/PulseAudio configuration issues
- User may need to be in `audio` group

### macOS Issues:
- Requires Homebrew: `brew install portaudio`
- Microphone permission prompts
- Apple Silicon compatibility issues (partially fixed in 0.2.13)

### General Issues:
- Requires C compilation - fails if system dependencies missing
- Python 3.13 compatibility problems
- Last updated 2021 (not actively maintained)
- Poor error messages when dependencies missing

## Solution

Replace PyAudio with **sounddevice + soundfile**:

### Benefits:
- ✅ Pure Python bindings (easier installation)
- ✅ Active maintenance (vs PyAudio abandoned in 2021)
- ✅ Better cross-platform support (no PortAudio compilation)
- ✅ Works on Ubuntu, macOS, Windows via pip install only
- ✅ Better error messages and device selection
- ✅ NumPy integration for audio processing
- ✅ Same functionality, cleaner API

### Dependencies Added:
- **sounddevice** - Cross-platform audio I/O
- **soundfile** - WAV file read/write
- **numpy** - Required by sounddevice (also useful for audio processing)

## Changes Made to Plan

### Task M.1 (core/recorder.py):
**Before:**
- Wrap PyAudio for audio capture

**After:**
- Use sounddevice + soundfile (NOT PyAudio)
- Wrap sounddevice for audio capture
- Return audio frames as bytes or NumPy array
- Support device selection
- Provide helpful error messages if sounddevice not installed

### Task M.6 (modes/gui_mode.py):
**Added:**
- REPLACE PyAudio with sounddevice: Refactor existing PyAudio code to use shared recorder component

### Task M.9 (dependencies):
**Added:**
- sounddevice - Cross-platform audio I/O (replaces PyAudio)
- soundfile - Audio file read/write support
- numpy - Required by sounddevice
- Note about better cross-platform support

### New Section Added:
"Why sounddevice instead of PyAudio?" with rationale and benefits

## Migration Notes

### Existing Code Impact:
Current code in `src/cli/second_voice.py` uses PyAudio:
```python
import pyaudio
self.p = pyaudio.PyAudio()
self.stream = self.p.open(format=pyaudio.paInt16, channels=1, rate=16000, ...)
```

### Will be replaced with sounddevice:
```python
import sounddevice as sd
import soundfile as sf
recording = sd.rec(frames, samplerate=16000, channels=1, dtype='int16')
sf.write('tmp-audio.wav', recording, 16000)
```

### API Differences:
- **PyAudio:** Callback-based streaming, requires manual buffer management
- **sounddevice:** NumPy-based, simpler API, built-in file writing

## Files Modified
- `dev_notes/project_plans/2026-01-25_00-32-27_mode-selection-architecture.md` (v3)

## Testing Implications

### Must Test:
- [ ] Installation on fresh Ubuntu system (pip install only)
- [ ] Installation on fresh macOS system (pip install only)
- [ ] Audio recording works on both platforms
- [ ] Device selection works
- [ ] Error messages helpful when sounddevice missing
- [ ] VU meter still works with sounddevice audio levels
- [ ] WAV file format compatible with STT APIs

## Current Status
Plan updated to v3. Awaiting approval for implementation.

## References
- sounddevice documentation: https://python-sounddevice.readthedocs.io/
- soundfile documentation: https://python-soundfile.readthedocs.io/
- PyAudio installation issues: See web search results on cross-platform problems

## Next Steps (After Approval)
1. Implement M.0 (config.py)
2. Implement M.1 (recorder.py) using sounddevice API
3. Test on both Ubuntu and macOS
4. Refactor existing GUI code (M.6) from PyAudio to sounddevice
