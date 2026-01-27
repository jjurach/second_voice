# Specification: AAC Support & Whisper Output Recovery

**Date:** 2026-01-26
**Status:** Pending Review
**Priority:** High

## Overview

This specification addresses three enhancements to the Second Voice application:

1. **AAC Audio Format Support** - Enable processing of `.aac` audio files
2. **Whisper Output Recovery** - Preserve intermediate transcription results for debugging and fallback
3. **Output Headers** - Add structured metadata headers to text outputs for tracking and context

## Requirements

### R1: AAC Audio File Support

**Current Issue:**
```
$ python src/cli/run.py --file tmp/recording-2.aac --no-edit
Error: Invalid audio file: Error opening '/home/phaedrus/AiSpace/second_voice/tmp/recording-2.aac': Format not recognised.
```

**Requirement:**
- Accept `.aac` audio files via `--file` argument
- Auto-detect AAC format by file extension (`.aac`, `.m4a` variations)
- Use robust library that handles AAC decoding
- Maintain compatibility with existing audio format support

**Recommended Libraries:**
- **Mutagen** (v1.46+) - For AAC metadata reading
- **pydub** (v0.25+) - For AAC audio manipulation (uses FFmpeg backend)
- **FFmpeg** - System dependency for actual AAC decoding

**Strategy:**
- Keep `soundfile` as primary format handler (WAV, FLAC, OGG, MP3, AIFF, etc.)
- Add optional AAC support layer that converts AAC → WAV internally before processing
- Fallback: If FFmpeg not available, return helpful error directing user to install it

### R2: Whisper Output Recovery

**Current Behavior:**
- Intermediate `.wav` recordings are stored in `tmp/tmp-audio-*.wav` but lack timestamps
- Whisper transcription output is computed in-memory and discarded on failure
- On LLM failure, there's no way to recover the original transcription

**Requirement:**
- Create timestamped audio file: `tmp/recording-YYYY-MM-DD_HH-MM-SS.aac` or `.wav`
- Create corresponding raw whisper output: `tmp/whisper-YYYY-MM-DD_HH-MM-SS.txt`
- Preserve these files on:
  - Crash or exception
  - When `--keep-files` flag is used
  - When LLM processing fails
- Remove both files on normal successful operation
- On LLM failure, fall back to using raw whisper text as output

**File Lifecycle:**

```
Normal Flow (Success):
  recording-YYYY-MM-DD_HH-MM-SS.aac → [Whisper] → whisper-YYYY-MM-DD_HH-MM-SS.txt
                                       ↓
                                     [LLM]
                                       ↓
                              Final Output (DELETED)
  [Both audio & txt files deleted after LLM succeeds]

Failure Flow (LLM Error):
  recording-YYYY-MM-DD_HH-MM-SS.aac → [Whisper] → whisper-YYYY-MM-DD_HH-MM-SS.txt
                                       ↓                    ↓
                                     [LLM fails]     [Output as fallback]
  [Both files RETAINED for recovery]

Keep-Files Flow:
  [Same as failure, but intentional]
```

### R3: Output Headers with Metadata

**Raw Whisper Text Header (Input):**
```
**Source**: tmp/recording-1.aac
**Date:** 2026-01-25 22:46:00
**Status:** Awaiting transformation
```

**LLM Output Header (After Processing):**
```
**Source**: second-voice from tmp/recording-1.aac
**Date:** 2026-01-25 22:48:00
**Status:** Awaiting ingest
**Title:** <Something reasonable> (up to 60 characters to summarize intent)
**Project:** <something-reasonable> (best guess from text; default to "unknown")
```

**Requirements:**
- System prompt must clarify these are metadata headers, not user content
- LLM should preserve/enhance these headers in output
- If headers missing from LLM output, Second Voice should inject them (with warning)
- Title should be max 60 chars, auto-generated from transcribed content
- Project name should be inferred from text or default to "unknown"

## Implementation Approach

### Phase 1: AAC Support
- Add `mutagen` to `requirements.txt`
- Modify `src/second_voice/core/recorder.py` to accept AAC files
- Update `src/cli/run.py` validation to recognize `.aac` extension
- Add conversion layer: AAC → WAV (using FFmpeg via pydub if needed)

### Phase 2: Whisper Output Recovery
- Modify `src/second_voice/core/recorder.py` to create timestamped files
- Update whisper transcription call to write raw output to `.txt` file
- Implement fallback logic in LLM processor
- Add cleanup logic that respects `--keep-files` and crash scenarios

### Phase 3: Output Headers
- Update system prompt to explain header semantics
- Modify LLM processor to add headers to inputs
- Add post-processing to verify and inject headers if missing
- Implement title/project inference logic

## Success Criteria

- [ ] AAC files process without error using `--file tmp/recording.aac`
- [ ] Timestamped recording files created in `tmp/recording-*.aac`
- [ ] Whisper output saved to `tmp/whisper-*.txt` with correct timestamps
- [ ] Files retained on crash and with `--keep-files` flag
- [ ] Files deleted on successful completion
- [ ] Output headers present in LLM input and output
- [ ] Title auto-generated, max 60 chars
- [ ] Project name inferred or defaults to "unknown"
- [ ] All tests pass
- [ ] No regression in existing functionality

## Dependencies

- `mutagen>=1.46` - AAC metadata support
- `pydub>=0.25` - Audio conversion (optional, with FFmpeg)
- `FFmpeg` - System binary for AAC decoding (optional but recommended)
- Existing: `soundfile`, `numpy`, `requests`

## Risks

| Risk | Mitigation |
|------|-----------|
| FFmpeg not installed | Graceful error message directing user to install FFmpeg |
| AAC conversion overhead | Only convert if needed; keep original flow for native formats |
| Header injection conflicts | Validate headers before injecting; check for existing headers first |
| Timestamp collisions | Use microseconds in filename if needed (unlikely but possible) |
| Orphaned temporary files | Implement cleanup script; document in troubleshooting |

## Out of Scope

- Support for other container formats (`.m4b`, `.3ga`, etc.) in this iteration
- Custom header formats or database storage
- Batch processing of multiple files
- Integration with external audio editing tools
