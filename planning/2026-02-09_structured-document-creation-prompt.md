# Specification: Structured Document Creation Workflow

**Source:** dev_notes/inbox/second-voice-enhancements.md
**Status:** 🔵 Ready for Review
**Priority:** HIGH
**Timestamp:** 2026-02-09_17-00-00

---

## Overview

Enable users to create well-structured markdown documents from unstructured voice input. Instead of iterative refinement, the workflow focuses on organizing spoken content directly into a properly formatted document with headers, bullet points, and logical sections.

**Use Case:** User wants to capture brainstorming, meeting notes, or article outlines by speaking. Second Voice receives the unstructured speech, then structures it into clean markdown with proper organization.

---

## Problem Statement

Currently, second-voice processes transcribed speech into "cleaned" text (fixing grammar, removing stutters). However:

1. **No Output Specification:** Users cannot specify where output should go before recording
2. **Single-Pass Processing:** Output is flat text, not hierarchically structured
3. **Manual Organization:** Users must manually format the result into markdown sections
4. **Same System Prompt:** Uses generic cleanup prompt, not document-organization prompt
5. **No Document Mode:** All recordings follow the same iterative refinement loop

**Impact:** Brainstorming or note-taking sessions require post-recording manual formatting work.

---

## Core Requirements

### FR-1: Document Mode CLI Flag
```
second_voice --document-mode --output /path/to/output.md
```
- New CLI flag: `--document-mode` activates document creation workflow
- Requires `--output` flag specifying target file path
- Incompatible with interactive loop (one recording → one document)
- If output file exists, user is asked to confirm overwrite

### FR-2: Output File Specification
- User must specify `--output <filepath>` when using `--document-mode`
- Output filepath can be absolute or relative
- Directory is created if it doesn't exist
- File extension suggests document type (`.md` for markdown, `.txt` for plaintext)

### FR-3: Specialized System Prompt
- System prompt is different from generic cleanup prompt
- Focuses on document structure instead of just language cleanup
- Instructions for creating headers (## Topic), bullet lists, sections
- Example prompt structure:
  ```
  You are a document structuring assistant. The user has spoken freely about a topic.
  Your job is to:
  1. Extract the main topic (becomes the H1 title)
  2. Identify key sections (become H2 headers)
  3. List important points under each section (become bullet points)
  4. Organize chronologically or by importance as appropriate
  5. Fix grammar and remove stutters while preserving intent

  Output ONLY the structured markdown. No preamble or explanation.
  ```

### FR-4: Document Structure Output
- Output includes:
  - H1 title (generated from content)
  - H2 section headers
  - Bullet points under each section
  - Proper markdown formatting
  - YAML metadata headers (source, status, title, project)

### FR-5: No Iterative Loop in Document Mode
- Single recording session per document
- User records once, LLM structures, document is saved
- No "review and refine" cycle in document mode
- Optional: `--review` flag to allow editing after generation

### FR-6: Direct File Saving
- On successful LLM processing, output is saved directly to `--output` file
- No temporary file, no editor wait
- Confirmation message: `✓ Document created: /path/to/output.md`
- On failure: transcription is saved instead with warning message

### FR-7: Metadata Headers
- Output includes YAML header with:
  - `source`: audio file name
  - `status`: "Structured from voice"
  - `title`: extracted from document content
  - `project`: inferred from content or `--project` CLI flag

### FR-8: Error Handling
- If LLM processing fails, save raw transcription with error message
- If file write fails, suggest alternative location
- Timeout errors include recovery instructions

---

## Architecture

### Data Flow (Document Mode)

```
Record audio
    ↓
Transcribe → raw text
    ↓
Apply DOCUMENT system prompt (NOT cleanup prompt)
    ↓
LLM processes → structured markdown
    ↓
Inject YAML headers
    ↓
Save to --output file directly
    ↓
[Exit - no editor, no loop]
```

### Files to Modify

**1. `src/cli/run.py`** - CLI argument parsing
- Add `--document-mode` flag
- Make `--output` required when `--document-mode` is set
- Add `--project` optional flag
- Add `--review` optional flag (for future enhancement)
- Validate combination of flags

**2. `src/second_voice/core/processor.py`** - Document processing
- Add `process_document_creation()` method
- Takes: raw transcription, system prompt
- Returns: structured markdown text
- Separate system prompt for document mode vs. cleanup mode

**3. `src/second_voice/modes/base.py`** - Document mode interface
- Add new abstract method: `run_document_mode()` (optional default implementation)
- Or add logic to existing `run()` to detect document-mode flag

**4. `src/second_voice/modes/menu_mode.py`** - Implement document mode
- Check for `document_mode` flag in config
- If set, execute document workflow instead of menu loop
- After LLM processing, save directly to output file
- Exit cleanly without editor

### System Prompt for Document Mode

```python
DOCUMENT_SYSTEM_PROMPT = """You are a document structuring assistant.
The user has spoken freely about a topic or ideas.

Your job is to:
1. Extract the main topic (becomes document title)
2. Identify 3-5 key sections or themes
3. List specific points under each section as bullet points
4. Organize logically (chronologically, by importance, or by theme)
5. Clean up grammar and remove speech artifacts (ums, ahs, stutters)
6. Keep the user's original meaning and intent intact

OUTPUT FORMAT:
- Use markdown formatting
- Start with # Title (one H1)
- Use ## Section Headers for each topic (H2)
- Use - bullet points for details
- Use paragraphs when topic needs explanation
- No metadata, no preamble, just the document

IMPORTANT: Output ONLY the markdown document.
Do not include explanations or instructions.
The document should be ready to save immediately."""
```

### Configuration

No new config keys needed. Behavior controlled entirely by CLI flags:
- `--document-mode`: enables mode
- `--output`: specifies output path
- `--project`: specifies project name (optional)
- `--review`: enable post-generation editing (future)

---

## Implementation Approach

### Step 1: Add CLI Flags
File: `src/cli/run.py`
- Parse `--document-mode` flag
- Validate `--output` is present when document-mode is used
- Store flags in config dict

### Step 2: Create Document Processor
File: `src/second_voice/core/processor.py`
- Add `process_document_creation()` method
- Use document-specific system prompt (defined above)
- Call existing `_process_ollama()`, `_process_openrouter()`, etc. with custom prompt
- Handle failures gracefully

### Step 3: Implement Document Mode in Menu
File: `src/second_voice/modes/menu_mode.py`
- In `run()` method, check `self.config.get('document_mode')`
- If True:
  - Record audio
  - Transcribe
  - Process with `process_document_creation()`
  - Save directly to `--output` file
  - Print success message
  - Exit (no editor loop)
- If False: use existing menu loop logic

### Step 4: Error Recovery
- If LLM fails: save transcription to output file with error header
- If file write fails: suggest alternative path and exit with status code
- All errors logged to debug output

### Step 5: Testing (for future agents)
- Test document-mode with various inputs (brainstorm, meeting notes, article outline)
- Verify markdown formatting is valid
- Verify YAML headers are present
- Test with `--output` in existing directory vs. new directory
- Test permission errors gracefully

---

## Success Criteria

### User Perspective
- [ ] User can run: `second_voice --document-mode --output ~/Documents/notes.md`
- [ ] After speaking, a well-structured markdown document appears at `~/Documents/notes.md`
- [ ] Document includes:
  - YAML metadata header
  - H1 title derived from content
  - H2 section headers
  - Bullet points under each section
  - Clean, grammatically correct text

### Developer Perspective
- [ ] `--document-mode` and `--output` flags parsed correctly
- [ ] Document system prompt is distinct from cleanup prompt
- [ ] `process_document_creation()` method exists and is tested
- [ ] Menu mode detects document-mode flag and executes correct workflow
- [ ] File saving succeeds with proper error handling
- [ ] Debug logging shows document mode activation

### Quality Gates
- [ ] No breaking changes to existing menu/loop mode
- [ ] Existing tests still pass
- [ ] Document-mode documents are valid markdown
- [ ] Headers are properly injected

---

## Integration with Existing Workflows

### Backward Compatibility
- ✅ Existing `second_voice` (no flags) → uses menu mode, unchanged
- ✅ Existing `second_voice --input file.aac` → file processing mode, unchanged
- ⚠️ `second_voice --output file.md` without `--document-mode` → still uses menu mode, output flag ignored (or error)

### Future Enhancements (Out of Scope)
- `--review` flag to edit structured document before saving
- `--template` flag to use custom markdown templates
- `--auto-tags` flag to add topic tags based on content
- Document mode that saves incrementally across multiple recordings

---

## References

### Related Documents
- `docs/current-capabilities.md` - Current feature inventory
- `docs/architecture.md` - System architecture overview
- `src/second_voice/core/processor.py` - LLM processing logic

### Similar Features
- Menu mode (single-pass from recording → processing → output)
- Google Drive inbox workflow (auto-saves to specified directory)
- Header injection system (already implemented in `process_with_headers_and_fallback()`)

### Dependencies
- None - uses existing LLM providers and audio pipeline
- Requires only CLI flag parsing and conditional mode selection

---

## Specifications for Future

Once this spec is implemented, consider:

1. **Redundancy Removal Spec** - Add explicit deduplication for brainstorm documents
2. **Document Templates Spec** - User can specify document format (meeting notes, brainstorm, article)
3. **Multi-Recording Documents** - Accumulate multiple voice inputs into single document
4. **Review + Refine** - Allow editing and re-structuring after initial generation
