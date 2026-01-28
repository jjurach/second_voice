# AI Prompts and Processing Logic

## System Prompts

### Primary Mode: Speech Cleanup Assistant

All LLM providers now use a unified speech cleanup prompt:

```
You are a speech cleanup assistant. Your job is to clean up transcribed speech by:
1. Removing stutters and repeated phrases
2. Consolidating similar ideas into coherent statements
3. Fixing grammar and improving sentence structure
4. Maintaining the original meaning and intent

IMPORTANT: Do NOT answer questions or provide new information. Only clean up the language.

OUTPUT FORMAT: Output ONLY the cleaned text. No preamble, no introduction, no quotation marks.
Just the cleaned speech itself.
```

### Meta-Operation Exception

If the user's text contains keywords indicating a transformation request, the LLM allows meta-operations:

```
EXCEPTION: If the user's text contains a request to transform their own words
(keywords: outline, summarize, reorder, rearrange, list, bullets, organize),
perform that transformation instead. Still output only the result, no preamble.
```

## LLM Provider Implementation

### Ollama

System prompt is prepended to the input. The full prompt structure:

```
{system_prompt}

Previous Context:
{context}

User's transcribed speech:
{text}
```

### OpenRouter

System prompt is sent as a separate message with role="system":

```json
{
  "messages": [
    {
      "role": "system",
      "content": "{system_prompt}"
    },
    {
      "role": "system",
      "content": "Previous conversation context: {context}"
    },
    {
      "role": "user",
      "content": "{text}"
    }
  ]
}
```

### Cline CLI

System prompt is prepended to the `--input` parameter:

```bash
cline generate --model {model} --input "{system_prompt}\n\n{text}"
```

## Meta-Operation Detection

The `_detect_meta_operation()` method checks for these keywords:
- `outline` - Create a bulleted or numbered outline
- `summarize` - Provide a summary of the text
- `reorder` - Rearrange ideas in a different order
- `rearrange` - Same as reorder
- `list` - Convert to a list format
- `bullets` - Convert to bullet points
- `organize` - Reorganize or structure the content

When any of these keywords are detected, the LLM is told it may perform the transformation as an exception to the cleanup-only rule.

## Examples

### Example 1: Basic Cleanup (No Meta-Operation)

**Input:**
```
Is this a test? Is this working? Is this a working test? Is this gonna work?
Is this just gonna go for 10 seconds, I think?
```

**Expected Output:**
```
Is this a working test? Will it last for 10 seconds?
```

### Example 2: Meta-Operation - Outline

**Input:**
```
The project has multiple components. First there's the frontend which handles the UI.
Then there's the backend API. And we also have the database layer. We need to make sure
they all communicate properly. Let me organize this as an outline.
```

**Expected Output:**
```
- Frontend (UI handling)
- Backend (API)
- Database layer
- Communication between components
```

### Example 3: Meta-Operation - Summarize

**Input:**
```
I talked about how we need better error handling, more unit tests, and improved documentation.
Could you summarize what I said?
```

**Expected Output:**
```
Three key improvements needed:
1. Better error handling
2. More unit tests
3. Improved documentation
```

## Context Management

### Context Preservation

Previous conversation context is maintained across iterations using:
- `save_context()` - Saves the current output to `tmp-context.txt`
- `load_context()` - Loads saved context from `tmp-context.txt`
- `clear_context()` - Clears saved context

Context is passed to the LLM to maintain conversational continuity.

### Context Flow

1. User transcribes speech → `process_text(transcription, context)`
2. LLM receives context (if available) + transcription
3. LLM outputs cleaned speech or transformation
4. Output is saved as new context for next iteration

## API Endpoint Summary

| Provider | Endpoint | Method | Key Parameter |
|----------|----------|--------|----------------|
| Ollama | `http://localhost:11434/api/generate` | POST | `prompt` |
| OpenRouter | `https://openrouter.ai/api/v1/chat/completions` | POST | `messages` |
| Groq (STT) | `https://api.groq.com/openai/v1/audio/transcriptions` | POST | `file` |
| Local Whisper | `http://localhost:9090/v1/audio/transcriptions` | POST | `file` |

---
Last Updated: 2026-01-28
