# Cline CLI - Integration Guide (Supported)

**Status:** ✅ Supported

This guide describes how **Cline CLI** is integrated into this project as an LLM provider.

---

## Overview

**Cline** (https://github.com/UserName/cline) is a CLI tool for interacting with language models. In this project, Cline CLI serves as one of the available **LLM providers** for text processing tasks.

Unlike Claude Code or Aider (which are full IDE integrations), Cline is invoked programmatically by the `second_voice` application to process audio transcriptions through cleanup and transformation.

---

## Quick Start

### Installation

```bash
# Install Cline CLI (requires Node.js 16+)
npm install -g cline

# Or with pip (if available)
pip install cline-cli

# Verify installation
cline --version
```

### Configuration

Cline can be configured via:
1. Environment variables
2. Project configuration file (`~/.cline/config.json`)
3. Application config (`~/.config/second_voice/settings.json`)

### Using Cline as Second Voice's LLM Provider

Set Cline as your LLM provider in `~/.config/second_voice/settings.json`:

```json
{
    "llm_provider": "cline",
    "cline_llm_model": "gpt-4o",
    "cline_api_key": null,
    "cline_timeout": 120
}
```

Or set environment variables:

```bash
export LLM_PROVIDER=cline
export CLINE_LLM_MODEL=gpt-4o
export CLINE_API_KEY=your-api-key
export CLINE_TIMEOUT=120
```

---

## Architecture: How Cline Fits In

### Provider Pattern

Second Voice uses a **provider pattern** for LLM backend selection:

```
second_voice/core/processor.py
  │
  ├─ _process_ollama()     # Local LLM via Ollama
  ├─ _process_openrouter() # Cloud LLM via OpenRouter
  └─ _process_cline()      # CLI LLM via Cline CLI  ← You are here
```

### Processing Flow

```
Audio Transcription
    │
    ▼
[ AIProcessor.process_text() ]
    │
    ├─ Detect LLM provider (llm_provider config)
    │
    ├─ Route to appropriate handler:
    │   - Cline? → _process_cline()
    │
    ├─ Build system prompt (cleanup/transform)
    │
    ├─ Invoke Cline CLI via subprocess:
    │   cline generate --model gpt-4o --input "..."
    │
    ▼
[ Processed/Cleaned Text ]
    │
    ▼
[ Output to Obsidian or Editor ]
```

---

## Configuration Reference

### Environment Variables

| Variable | Default | Purpose |
|----------|---------|---------|
| `CLINE_LLM_MODEL` | `gpt-4o` | Which model to use |
| `CLINE_API_KEY` | (none) | API key for authenticated models |
| `CLINE_TIMEOUT` | `120` | Seconds to wait for response |

### Config File Options

In `~/.config/second_voice/settings.json`:

```json
{
    "llm_provider": "cline",
    "cline_llm_model": "gpt-4o",
    "cline_api_key": null,
    "cline_timeout": 120
}
```

### Supported Models

Depends on your Cline CLI installation and available backends:

- OpenAI: `gpt-4o`, `gpt-4`, `gpt-3.5-turbo`
- Anthropic Claude: `claude-3-opus`, `claude-3-sonnet`
- Open source: `llama2`, `mistral`, etc. (via local setup)

---

## Use Cases

### 1. Text Cleanup (Default)

Cline processes transcribed speech to:
- Remove stutters and repeated phrases
- Fix grammar and sentence structure
- Consolidate ideas into coherent statements
- Maintain original meaning and intent

```bash
# Example audio transcription
"um, so like, the thing is, the thing is we need to like,
refactor the, um, the API module to be more, you know, modular"

# After Cline processing
"We need to refactor the API module to be more modular"
```

### 2. Transformations

Cline recognizes special keywords for transformations:
- `outline` - Create an outline
- `summarize` - Create a summary
- `list` / `bullets` - Convert to bullet points
- `organize` - Organize into categories
- `reorder` / `rearrange` - Change structure

```bash
# Input with transformation keyword
"outline the steps for implementing authentication: first you need,
um, a user model, then you need login endpoint, then..."

# Output: Structured outline
```

### 3. Context-Aware Processing

Cline can use previous context for multi-turn interactions:

```bash
# First turn: cleanup text with context
"convert that into a list"  # "that" refers to previous output

# Cline processes with access to conversation history
```

---

## Common Patterns & Examples

### Pattern 1: Basic Text Cleanup in Application
```python
from second_voice.core.processor import AIProcessor
from second_voice.core.config import Config

config = Config.load()
config.llm_provider = "cline"
config.cline_llm_model = "gpt-4o"

processor = AIProcessor(config)

# Transcribed speech from audio
raw_text = "um, so like, we need to, uh, refactor the, um, the API module"

# Cline cleans it up
cleaned = processor.process_text(raw_text)
# Output: "We need to refactor the API module"
```

### Pattern 2: Transformation with Keywords
```python
# User speaks with intent keyword
transcript = "outline the authentication flow: first you have login, then session validation"

# Cline recognizes "outline" keyword and structures response
result = processor.process_text(transcript)
# Output: Formatted outline with numbered steps
```

### Pattern 3: Chained Processing
```python
# First pass: cleanup
step1 = processor.process_text(raw_transcript)

# Second pass: transformation (user adds intent)
step2 = processor.process_text(step1 + " | summarize this")

# Result: Structured summary of cleaned text
```

### Pattern 4: Custom System Prompt
```python
# Customize cleanup instructions for specific domain
custom_system_prompt = """
You are a technical documentation assistant. Clean up technical speech by:
1. Removing filler words and stutters
2. Preserving technical terms accurately
3. Converting to technical documentation style
"""

# Use custom prompt (if supported by processor implementation)
result = processor.process_text(transcript, system_prompt=custom_system_prompt)
```

---

## Comparison with Other Providers

| Feature | Cline CLI | Ollama | OpenRouter |
|---------|-----------|--------|-----------|
| **Setup** | CLI tool | Docker/Local | Cloud (API key) |
| **Models** | Any CLI backend | Local models | 100+ cloud models |
| **Speed** | Depends on backend | Fast (local) | Medium (cloud) |
| **Cost** | Free (if local) | Free | Pay-per-request |
| **Privacy** | High (local possible) | Highest (local) | Lower (cloud) |
| **Configuration** | Args + env vars | Port + model | API key |
| **Use Case** | Flexible, modular | Fast, local | Scalable, diverse |

---

## Workflow Integration with AGENTS.md

Cline CLI is used **internally** by the `second_voice` application, not as an interactive development tool. However, it respects the project's AGENTS.md workflow implicitly:

### How It Respects AGENTS.md Principles

1. **Quality Standards** - Uses the system prompt from Definition of Done
2. **Error Handling** - Follows error handling patterns from core workflow
3. **Logging** - Debug logs match project standards
4. **Timeouts** - Respects configured timeouts for reliability

### Example: Cleanup System Prompt

The system prompt embedded in Cline's processing reflects AGENTS.md quality standards:

```
"You are a speech cleanup assistant. Your job is to clean up
transcribed speech by:
1. Removing stutters and repeated phrases
2. Consolidating similar ideas into coherent statements
3. Fixing grammar and improving sentence structure
4. Maintaining the original meaning and intent

IMPORTANT: Do NOT answer questions or provide new information.
Only clean up the language."
```

This follows the **"Unbreakable Rule"** principle: *Code quality must be maintained. Only functional changes are allowed.*

---

## CLI Reference & Environment Variables

### Command-Line Invocation

```bash
# Basic invocation (used by second_voice internally)
cline generate --model gpt-4o --input "raw text here"

# With timeout
cline generate --model gpt-4o --input "text" --timeout 120

# With API key override
CLINE_API_KEY="sk-..." cline generate --model gpt-4o --input "text"
```

### Configuration Reference

| Environment Variable | Purpose | Example |
|---|---|---|
| `CLINE_LLM_MODEL` | Model to use | `gpt-4o`, `claude-3-opus` |
| `CLINE_API_KEY` | Authentication | `sk-ant-...` or API key |
| `CLINE_TIMEOUT` | Request timeout (seconds) | `120` |
| `CLINE_BASE_URL` | Custom endpoint | `http://localhost:8000` |

### Configuration File

`~/.config/second_voice/settings.json` (used by second_voice):

```json
{
    "llm_provider": "cline",
    "cline_llm_model": "gpt-4o",
    "cline_api_key": null,           // Read from CLINE_API_KEY env var
    "cline_timeout": 120
}
```

---

## Troubleshooting

### Issue: "cline: command not found"

**Solution:** Ensure Cline CLI is installed and in your PATH
```bash
# Reinstall
npm install -g cline

# Verify
which cline
cline --version
```

### Issue: "Cline CLI error: Invalid API key"

**Solution:** Check your API key configuration
```bash
# Verify environment variable
echo $CLINE_API_KEY

# Or check config file
cat ~/.config/second_voice/settings.json | grep cline_api_key
```

### Issue: "Cline CLI request timeout after 120s"

**Solution:** Increase timeout in config or check Cline CLI backend
```json
{
    "cline_timeout": 300
}
```

### Issue: Cline not processing correctly

**Solution:** Check logs for detailed error messages
```bash
# Enable debug logging
export DEBUG=second_voice:*
python3 src/cli/run.py
```

---

## Advanced Configuration

### Custom Models

Change the model Cline uses:

```json
{
    "llm_provider": "cline",
    "cline_llm_model": "claude-3-opus",
    "cline_api_key": "sk-ant-..."
}
```

### Custom System Prompt

(Currently embedded in processor.py, can be extended in future)

The cleanup system prompt can be modified in `src/second_voice/core/processor.py`:

```python
system_prompt = (
    "Your custom instructions here..."
)
```

### Disable Timeout

```json
{
    "cline_timeout": null
}
```

---

## Known Limitations

1. **Requires External CLI** - Cline must be installed separately on your system
2. **No Interactive Mode** - Used programmatically, not for interactive development
3. **Single-Purpose** - Focused on text cleanup/transformation in second_voice
4. **Model Availability** - Supported models depend on your Cline setup

---

## Verification Status

- ✅ Cline CLI provider implemented in processor.py
- ✅ Configuration support in config.py
- ✅ Example config in config.example.json
- ✅ Documentation in docs/providers.md
- ✅ Error handling and logging included
- ✅ Timeout and API key support implemented

---

## Next Steps

1. **Install Cline CLI** - Follow Quick Start section above
2. **Configure Second Voice** - Set `llm_provider` to `cline`
3. **Test Processing** - Run with audio input and verify cleanup
4. **Monitor Logs** - Check logs if issues occur

---

## Additional Resources

- **AGENTS.md** - Project workflow and quality standards
- **docs/providers.md** - All available LLM providers
- **docs/definition-of-done.md** - Quality standards for text processing
- **src/second_voice/core/processor.py** - Implementation details
- **src/second_voice/core/config.py** - Configuration management

---

## Related Tools

- **Claude Code** (`CLAUDE.md`) - Interactive development IDE
- **Aider** (`docs/system-prompts/tools/aider.md`) - Collaborative coding
- **Codex** (`docs/system-prompts/tools/codex.md`) - OpenAI code editor
- **Gemini** (`GEMINI.md`) - Google's agent integration
