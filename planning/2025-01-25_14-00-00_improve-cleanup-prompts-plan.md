# Project Plan: Improve Language Cleanup Prompts

**Status:** Completed

**Objective:** Modify LLM system prompts to focus on cleaning up transcribed speech (grammar, structure, redundancy removal) rather than answering/responding to the user's questions. Include support for meta-operations (outline, summarize, reorder) based on keyword detection.

---

## Background

Current behavior: When users transcribe speech that's rambling or stuttered, the LLM interprets the content and provides answers rather than cleaning up the language. For example:
- Input: "Is this working? Is this a working test? Is this gonna work?"
- Current output: *LLM answers* "Yes, it's working..."
- Desired output: "Is this working?" (stutters and redundancy removed)

---

## Requirements

1. **Language Cleanup Mode (Primary)**
   - Remove stutters and repeated phrases
   - Consolidate similar ideas into one coherent statement
   - Fix grammar and rearrange for clarity
   - Do NOT answer or interpret the user's question
   - Preserve the user's original intent and meaning

2. **Meta-Operation Support (Exception)**
   - Detect keywords indicating transformations: "outline", "summarize", "reorder", "rearrange", "list", "bullets", "organize"
   - When detected, allow the LLM to perform the transformation
   - Example: "rearrange what I said in outline format" → outputs a bulleted outline
   - Only applies when user explicitly requests a transformation of their own text

3. **Preserve Context**
   - Maintain previous conversation context for iterative refinement
   - Don't lose information from prior iterations

---

## Implementation Scope

### Files to Modify

1. **`src/second_voice/core/processor.py`**
   - Modify `_process_ollama()` (lines 237-284) to add system prompt
   - Modify `_process_openrouter()` (lines 286-342) to improve system prompt
   - Optionally modify `_process_cline()` (lines 174-235) if Cline support is desired
   - Add helper method to detect meta-operation keywords

2. **`docs/prompts.md`**
   - Update documentation to reflect new cleanup-focused prompts
   - Document the meta-operation keyword detection logic
   - Provide examples of expected behavior

### New/Updated System Prompts

#### Ollama (local)
Change from generic context injection to explicit cleanup instructions:
```
Previous Context: {context}

You are a speech cleanup assistant. Your job is to clean up transcribed speech by:
1. Removing stutters and repeated phrases
2. Consolidating similar ideas into coherent statements
3. Fixing grammar and improving sentence structure
4. Maintaining the original meaning and intent

IMPORTANT: Do NOT answer questions or provide new information. Only clean up the language.

User's transcribed speech: {text}
```

#### OpenRouter
Change system prompt from context-only to explicit cleanup instructions:
```
You are a speech cleanup assistant. Your job is to clean up transcribed speech by:
1. Removing stutters and repeated phrases
2. Consolidating similar ideas into coherent statements
3. Fixing grammar and improving sentence structure
4. Maintaining the original meaning and intent

IMPORTANT: Do NOT answer questions or provide new information. Only clean up the language.

If the user's text contains a request to transform their own words (keywords: outline, summarize, reorder, rearrange, list, bullets, organize), perform that transformation instead.
```

#### Cline
Modify the CLI arguments to include explicit instructions in the input.

---

## Implementation Steps

### Step 1: Add Meta-Operation Detection
Create a helper method in `processor.py`:
```python
def _detect_meta_operation(self, text: str) -> bool:
    """
    Detect if user is asking for a transformation of their own text.
    Returns True if keywords like 'outline', 'summarize', 'rearrange', etc. are detected.
    """
    keywords = {'outline', 'summarize', 'reorder', 'rearrange', 'list', 'bullets', 'organize'}
    text_lower = text.lower()
    return any(keyword in text_lower for keyword in keywords)
```

### Step 2: Modify Ollama Processing
Update `_process_ollama()` to include system prompt with conditional meta-operation handling.

### Step 3: Modify OpenRouter Processing
Update `_process_openrouter()` system prompt to be explicit about cleanup-only behavior and meta-operations.

### Step 4: Optionally Update Cline Processing
If Cline is used as an LLM provider, prepend system instructions to the input text.

### Step 5: Update Documentation
Update `docs/prompts.md` to reflect new behavior and examples.

### Step 6: Verification
Test with the exact input from the spec to ensure:
- Input: "Is this a test? Is this working? Is this a working test? Is this gonna work? Is this just gonna go for 10 seconds, I think?"
- Expected output: Something like "Is this a working test? Is this going to work for 10 seconds?"
- NOT the previous answer-oriented response

---

## Testing Strategy

1. Test cleanup-only mode with the example from the spec
2. Test meta-operation detection:
   - "rearrange what I said in outline format" → should produce outline
   - "summarize what I just said" → should produce summary
3. Test context preservation across iterations
4. Test with all configured LLM providers (Ollama, OpenRouter, Cline)

---

## Success Criteria

- [ ] LLM produces cleaned-up text instead of answers for normal prompts
- [ ] Meta-operations work when keywords are detected
- [ ] All existing functionality continues to work
- [ ] Documentation updated and accurate
- [ ] Tested with all three LLM providers (or subset available)

---

## Risks & Considerations

- **Ambiguity:** Some user inputs might be unclear whether they're asking a question or wanting it cleaned up. The prompt should lean toward cleanup unless meta-operation keywords are present.
- **Cline Provider:** May require additional testing if using external CLI tool
- **Context Ordering:** Ensure context is presented before the new instructions for clarity

---

## Dependencies

- No new libraries required
- Works with existing provider configuration
