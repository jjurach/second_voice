# AI Prompts and Processing Logic

## System Prompts

### Initial "Clean & Form" Prompt

Used for the first pass or when context is cleared:

```
Clean up the following STT transcript. Remove stutters, filler words, and fix grammar.
Format as professional Markdown with logical headers.
```

### "Retry/Redo" Recursive Prompt

Used when `last_output` context exists:

```
ORIGINAL_TEXT: {last_output}

NEW_INSTRUCTION: {new_stt}

Logic: If NEW_INSTRUCTION references the ORIGINAL_TEXT (e.g. 'it', 'shorter', 'bullets'),
modify ORIGINAL_TEXT. If not, treat as a fresh request and ignore ORIGINAL_TEXT.
Output only the final result.
```

## Current Implementation

The current system prompt used in the application:

```python
system_rules = (
    "If the NEW INSTRUCTION mentions the ORIGINAL TEXT (using 'it', 'this', 'that', "
    "'bullets', 'shorter', etc.), transform the ORIGINAL TEXT accordingly. "
    "If it does not, ignore the ORIGINAL TEXT and process a fresh answer."
)

combined_prompt = f"ORIGINAL TEXT: {self.last_output}\n\nNEW INSTRUCTION: {new_text}"
```

## LLM Request Format

### Ollama API Call

```python
requests.post(ollama_url, json={
    "model": "llama-pro",
    "prompt": combined_prompt,
    "stream": False,
    "system": system_rules
})
```

### Whisper API Call

```python
requests.post(whisper_url,
    files={'file': audio_file},
    data={'model': 'small.en'}
)
```

## Iterative Workflow Examples

### Example 1: Fresh Content

**Recording 1:**
- Input: "Write a python function to calculate fibonacci numbers"
- Context: Empty
- Output: Complete fibonacci function
- Context after: Stored function code

**Recording 2:**
- Input: "Write a test for binary search"
- Context: Previous fibonacci function
- Detected: No reference to previous content
- Output: New binary search test (ignores fibonacci context)

### Example 2: Iterative Refinement

**Recording 1:**
- Input: "Write a python function to calculate fibonacci numbers"
- Context: Empty
- Output: Complete fibonacci function
- Context after: Stored function code

**Recording 2:**
- Input: "Convert that to use a class"
- Context: Previous fibonacci function
- Detected: "that" references previous content
- Output: Class-based fibonacci implementation
- Context after: New class version stored

**Recording 3:**
- Input: "Add error handling for negative inputs"
- Context: Class-based version
- Detected: Implicit reference to previous content
- Output: Enhanced class with error handling
- Context after: Updated class stored

### Example 3: Mixed Usage

**Recording 1:**
- Input: "Create a shopping list: milk, bread, eggs"
- Output: Formatted markdown list
- Context after: Shopping list

**Recording 2:**
- Input: "Make it shorter"
- Detected: "it" references previous
- Output: Abbreviated list (e.g., bullet points without descriptions)

**Recording 3:**
- Input: "What's the weather like?"
- Detected: No reference to shopping list
- Output: Fresh response about weather (context ignored)

## Detection Keywords

The LLM is trained to detect these reference patterns:

- **Pronouns:** it, this, that, those, these
- **Modification verbs:** change, update, modify, transform, convert
- **Style instructions:** shorter, longer, bullets, numbered, format
- **Actions on previous:** add to, remove from, expand, condense

## Context Management

### Clear Context Button

Resets `last_output = ""` to start fresh without references to previous iterations.

### Context Indicator

Shows character count of current context:
- "Context: Empty" (gray) when no context
- "Context: 1240 chars" (blue) when context exists

## Output Handling

1. **LLM Response:** Received from Ollama
2. **Buffer Write:** Written to `.review_buffer.md`
3. **Human Edit:** User edits in Obsidian
4. **Context Update:** Edited version becomes new `last_output`
5. **STDOUT:** Final version printed for CLI integration
6. **Archive:** Moved to `voice_note_<timestamp>.md`

## Pre-Flight Validation

Before processing, the system checks:

1. **SSH Tunnel:** Ports 9090 and 11434 are mapped
2. **Obsidian Vault:** VoiceInbox directory exists
3. **Syncthing:** Ignore patterns set for `.review_buffer.md`
4. **Audio Input:** MacBook microphone is selected
5. **Docker Services:** whisper-server and ollama are running

## Error Handling

- **Connection errors:** Display error dialog with connection details
- **Timeout:** 120s timeout for transcription requests
- **GPU OOM:** Model selection ensures `small.en` + `llama-pro` fit in 8GB VRAM
- **File errors:** Graceful handling of missing vault directory
