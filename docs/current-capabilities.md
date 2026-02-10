# Second Voice - Current Capabilities Inventory

**Purpose:** This document distinguishes between features that are currently implemented vs. those that are documented/planned but not yet built.

**Last Updated:** 2026-02-09

---

## Implemented Features ✅

### Core Audio Pipeline
- ✅ **Audio Recording:** Via `sounddevice` + `soundfile` (NumPy-based) with VU meter and Ctrl+C stop
- ✅ **Whisper Transcription:** Via local Whisper service or Groq API with configurable timeouts
- ✅ **Audio File Archival:** Timestamped WAV files saved to `tmp/` with recovery capability
- ✅ **Transcription Recovery:** Raw transcripts saved separately for recovery if LLM fails

### LLM Processing
- ✅ **Multi-Provider Support:** Ollama, OpenRouter, Groq, Cline CLI
- ✅ **Provider Auto-Detection:** Environment variables and config-file based selection
- ✅ **OpenRouter Fallback Chain:** 18-model fallback chain for free models
- ✅ **System Prompt Injection:** Speech cleanup + meta-operation detection
- ✅ **Meta-Operations:** Keywords (outline, summarize, reorder, etc.) trigger transformation mode
- ✅ **Timeout Handling:** Configurable timeouts per provider with graceful errors

### Context & Session Management
- ✅ **Single Context File:** `tmp-context.txt` stores processed output for next iteration
- ✅ **Context Loading/Saving:** Load context from previous iteration, save current output
- ✅ **Max Context Length:** Configurable truncation to prevent context explosion
- ✅ **Context Clearing:** Menu option to clear and start fresh

### User Interfaces
- ✅ **Menu Mode:** Text-based menu (record → transcribe → process → edit → loop)
- ✅ **TUI Mode:** Rich terminal UI (not fully documented but present in codebase)
- ✅ **GUI Mode:** Tkinter-based interface (requires DISPLAY environment)
- ✅ **Mode Auto-Detection:** Detects environment and chooses appropriate mode

### Editor Integration
- ✅ **$EDITOR Support:** Launches configured editor for output review
- ✅ **Obsidian Integration:** Special support for Obsidian vault paths
- ✅ **File Editing:** User can edit output before it becomes context for next iteration
- ✅ **Context Display:** Shows previous context alongside current output in editor

### YAML Header System
- ✅ **Header Parsing:** Extracts source, status, title, project from YAML headers
- ✅ **Header Injection:** Auto-generates headers for output if missing
- ✅ **Header Preservation:** Maintains headers across context iterations
- ✅ **Metadata Tracking:** Source file, status, title, project name automatically set

### Google Drive Inbox Integration
- ✅ **Inbox Directory:** Auto-saves processed output to `dev_notes/inbox/`
- ✅ **Archive Directory:** Original audio stored in `dev_notes/inbox-archive/`
- ✅ **Timestamped Filenames:** YYYY-MM-DD_HH-MM-SS_name.md format
- ✅ **Input File Processing:** `--input-file` flag to process existing audio files
- ✅ **Output File Saving:** `--output-file` flag to specify output location

### Configuration
- ✅ **Config File:** `~/.config/second_voice/settings.json`
- ✅ **Environment Variable Overrides:** API keys via `OPENROUTER_API_KEY`, `GROQ_API_KEY`, etc.
- ✅ **Per-Mode Configuration:** Config applies across all modes
- ✅ **Debug Flag:** `--debug` enables verbose logging

### Development & Debugging
- ✅ **Temporary File Preservation:** `--keep-files` flag for debugging
- ✅ **No-Edit Mode:** `--no-edit` flag skips editor review
- ✅ **Debug Logging:** Structured logging throughout pipeline
- ✅ **Crash Recovery:** Failed LLM calls save transcriptions for recovery

---

## Documented but NOT Implemented ❌

### Dual-Text Looping (mentioned in architecture.md)
- ❌ **Original Raw + Processed Text:** LLM does NOT receive both texts on each iteration
- ❌ **Current State:** Only processed/cooked text from previous iteration is in context
- ❌ **Archive of Originals:** No preserved history of original raw transcriptions
- **Impact:** Users cannot see evolution from raw speech → processed output across multiple iterations

### Two-Pane Interactive Interface (mentioned in architecture.md)
- ❌ **Split-Pane UI:** Architecture mentions but is NOT implemented
- ❌ **Top Pane Target Text:** Proposed but no code
- ❌ **Bottom Pane Chat:** Proposed but no code
- ❌ **Real-Time LLM Collaboration:** Not in current implementation
- **Current State:** Single editor launch after processing completes

### Ctrl+G Cloud Code Integration (NOT mentioned in current docs)
- ❌ **Keyboard Shortcut Trigger:** Not implemented
- ❌ **IDE Integration:** No Claude Code/Cline integration layer
- ❌ **Buffer Integration:** No mechanism to insert results into Claude Code buffer
- **Status:** Requires external integration research

### Structured Document Creation Mode (NOT in current code)
- ❌ **Document Mode:** No `--document-mode` or `--create-doc` flag
- ❌ **Output Specification:** Users cannot pre-specify output file for brainstorm→document workflow
- ❌ **Markdown Organization:** Output format is currently flat, not structured with headers/bullets/sections
- **Current State:** User must manually organize transcribed speech post-hoc

### Dedicated Redundancy Removal (NOT explicit in code)
- ❌ **Explicit Deduplication:** No dedicated pass for removing repeated ideas
- ⚠️ **Partial:** System prompt mentions "consolidating similar ideas" but this is LLM-based, not algorithmic
- ❌ **Repetition Detection:** No analysis of what user repeated across iterations
- ⚠️ **Current:** LLM handles via prompt, not explicit module

### Collaborative Refinement Session Mode (NOT in code)
- ❌ **Session Tracking:** No explicit "round" counter or session state
- ❌ **Collaborative UI:** No visual indication of iterations or evolution
- ⚠️ **Partial:** Menu loop IS collaborative (speak → process → edit → loop), but not named/formalized

---

## Known Limitations 🔴

1. **Context Asymmetry:** Only processed text is passed forward, not original raw text
2. **Editor is Blocking:** Must complete editor review before next recording can start
3. **No Parallel Editing:** Cannot chat with LLM while editing (single-threaded)
4. **Linear Context:** Only one previous output in context; no full history
5. **No UI Refresh:** Changes in config require restart to take effect
6. **File-Based Context:** Context stored in temp file, not database (limits queries)
7. **Stateless Across Sessions:** No persistent session data; clearing config loses all context

---

## Files by Capability

### Core Pipeline
- `src/second_voice/core/processor.py:process_text()` - LLM integration
- `src/second_voice/core/processor.py:process_with_headers_and_fallback()` - Full pipeline
- `src/second_voice/core/processor.py:save_context()/load_context()` - Context management
- `src/second_voice/core/recorder.py` - Audio capture

### Modes (UI implementations)
- `src/second_voice/modes/menu_mode.py:run()` - Main menu workflow (L174-387)
- `src/second_voice/modes/menu_mode.py:review_output()` - Editor integration (L74-100)
- `src/second_voice/modes/tui_mode.py` - Terminal UI variant
- `src/second_voice/modes/gui_mode.py` - Tkinter GUI variant

### Provider Integrations
- `src/second_voice/core/processor.py:_process_ollama()` - Ollama backend
- `src/second_voice/core/processor.py:_process_openrouter()` - OpenRouter with fallback
- `src/second_voice/core/processor.py:_transcribe_groq()` - Groq STT

### Configuration & Headers
- `src/second_voice/core/config.py` - Settings management
- `src/second_voice/utils/headers.py` - YAML header parsing/generation
- `src/second_voice/providers/google_drive_provider.py` - Google Drive integration

---

## Architecture Notes

### Current Context Loop
The actual implementation stores ONLY the processed output:

```python
# From processor.py lines 615-650
def save_context(self, context: str):
    # Saves processed text (the "cooked" version)
    context_path = os.path.join(temp_dir, 'tmp-context.txt')
    with open(context_path, 'w') as f:
        f.write(context)

def load_context(self):
    # Retrieves the processed text from previous iteration
    with open(context_path, 'r') as f:
        return f.read()
```

On next iteration in menu_mode.py (L325-329):
```python
edited_output = self.review_output(output, context)
context = edited_output  # Store ONLY edited output
self.processor.save_context(context)  # Context = processed text, not original
```

### What's NOT Saved
- ❌ Original raw transcription (only processed text saved)
- ❌ Previous original texts (no history archive)
- ❌ Round count or iteration metadata

### What WOULD be needed for Dual-Text Looping
- Modify `save_context()` to save `{"original": raw_text, "processed": processed_text}`
- Store context as JSON or structured format instead of plain text
- Load both texts and pass both to LLM in processor.py
- Update all modes to handle structured context

---

## Recommendations for Specifications

Based on this audit, the priority for specifications should be:

1. **HIGH:** Structured Document Creation - builds on existing pipeline, high user value
2. **HIGH:** Redundancy Removal - enhances existing LLM prompt, moderate complexity
3. **MEDIUM:** Dual-Text Looping - architectural prerequisite for collaborative features
4. **MEDIUM:** Two-Pane Interactive UI - significant UI work, depends on dual-text
5. **MEDIUM:** Collaborative Refinement - formalizes existing loop, low code complexity
6. **LOW:** Cloud Code Integration - requires external research first
