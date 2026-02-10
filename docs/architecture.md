# Second Voice Architecture

## Overview

Second Voice follows a **Local Capture / Remote Compute / Local Edit** pattern to bypass Intel MacBook performance bottlenecks by offloading heavy AI computation to a remote Ubuntu server with an RTX 2080 GPU.

## Agent Kernel & Workflow Layer

This project uses the **Agent Kernel** pattern with optional **Workflows** to govern how AI agents approach development tasks.

### Workflow System

**What it is:** A set of instructions that define how agents should handle requests (documentation requirements, approval processes, verification standards).

**How it works:**
- Workflows are stored as markdown documents in `docs/system-prompts/workflows/`
- The `bootstrap.py` tool injects workflow content into `AGENTS.md` based on project preference
- Each project can enable/disable workflows independently

**Current Project:** This project uses the **logs-first workflow**, which emphasizes:
- Detailed specification documents (user intentions)
- Approved project plans before implementation
- Comprehensive change documentation with verification
- Complete audit trail (intention → design → implementation)

**Flexibility:** Projects can:
- Enable/disable logs-first workflow via `python3 docs/system-prompts/bootstrap.py --enable-logs-first`
- Create custom workflows for different project needs
- Switch workflows as project characteristics change

See `docs/workflows.md` for detailed workflow information.

### Bootstrap Tool

The `docs/system-prompts/bootstrap.py` tool:
- **Auto-detects** recommended workflows based on project size, git history, structure
- **Manages state** by storing preferences as HTML comments in AGENTS.md
- **Injects/removes** workflow content as needed
- **Persists** workflow selection across runs

Example usage:
```bash
python3 docs/system-prompts/bootstrap.py --analyze-workflow
python3 docs/system-prompts/bootstrap.py --enable-logs-first --commit
```

---

## System Components

### Client (Any Machine)
- **Audio Capture:** Records audio using `sounddevice` + `soundfile` (NumPy based)
- **Interface Modes:** 
  - **GUI:** Tkinter-based interface (requires DISPLAY)
  - **TUI:** Rich-based terminal UI (SSH-friendly)
  - **Menu:** Simple text menu (minimal dependencies, SSH-friendly)
- **Local Editing:** Obsidian integration (GUI) or $EDITOR ($EDITOR)
- **LLM Processing:** Multi-provider architecture (Ollama or OpenRouter)
- **Network:** SSH tunnel for Ollama (optional), direct internet for OpenRouter

### Server (Ubuntu RTX 2080) - Optional for Ollama
- **Speech-to-Text:** faster-whisper-server using `small.en` model
- **LLM Processing:** Ollama running `llama-pro` model (or other local models)
- **Deployment:** Docker containers with GPU access

### Cloud Services - Optional for OpenRouter / Groq
- **STT Processing:** Groq Whisper API or local Whisper
- **LLM Processing:** OpenRouter API or Ollama
- **Models:** Claude, GPT-4, Llama 3, etc.

## Module Structure

The application is organized into functional modules:

```
src/
├── cli/
│   └── run.py            # CLI entry point
└── second_voice/
    ├── core/
    │   ├── config.py     # Configuration management
    │   ├── recorder.py   # Audio recording (sounddevice)
    │   └── processor.py  # AI processing (STT/LLM)
    └── modes/
        ├── __init__.py   # Mode factory & detection
        ├── base.py       # BaseMode abstract class
        ├── gui_mode.py   # GUI interface
        ├── tui_mode.py   # TUI interface
        └── menu_mode.py  # Menu interface
```

## Configuration

Settings are stored in `~/.config/second_voice/settings.json`:

```json
{
    "whisper_url": "http://localhost:9090/v1/audio/transcriptions",
    "ollama_url": "http://localhost:11434/api/generate",
    "whisper_model": "small.en",
    "ollama_model": "llama-pro",
    "vault_path": "~/Documents/Obsidian/VoiceInbox",
    "landing_editor": "obsidian",
    "mode": "auto"
}
```


## LLM Provider Architecture

Second Voice uses a provider pattern to support multiple LLM backends:

### Provider Selection Logic

1. **Auto-Detection (Default):**
   - If `OPENROUTER_API_KEY` environment variable is set → OpenRouter
   - If `openrouter.api_key` in config file → OpenRouter
   - Otherwise → Ollama

2. **Manual Override:**
   - CLI flag: `--provider {ollama,openrouter}`
   - Overrides auto-detection

### Provider Classes

**Base Provider (`BaseLLMProvider`):**
- Abstract class defining the provider interface
- Methods: `process()`, `validate_config()`, `is_available()`
- Standard exception hierarchy

**OllamaProvider:**
- Connects to local/tunneled Ollama instance
- Uses Ollama's `/api/generate` endpoint
- Supports all Ollama-compatible models

**OpenRouterProvider:**
- Connects to OpenRouter cloud API
- Uses OpenAI-compatible `/v1/chat/completions` endpoint
- Requires API key authentication
- Supports 100+ models

### Provider Factory

The `get_provider(config, provider_name=None)` factory function:
- Instantiates the correct provider based on configuration
- Handles auto-detection logic
- Validates provider configuration

See `docs/providers.md` for detailed provider documentation.

---

## Data Flow

1. **Capture:** User records audio via PyAudio (16kHz, mono, 16-bit)
2. **Transcribe:** Audio sent to Whisper service via HTTP (local/tunneled)
3. **Process:** Transcription sent to LLM provider with recursive context
   - **Ollama:** SSH-tunneled to local GPU server
   - **OpenRouter:** Direct HTTPS to cloud API
   - **On Failure:** Save crash log to `tmp-crash-{timestamp}.txt` with original STT text
4. **Review:** Output written to `.review_buffer.md` in Obsidian vault
5. **Edit:** User edits in Obsidian, clicks OK to confirm
6. **Store:** Final result becomes context for next iteration, archived with timestamp

## Recursive Context Feature

The application maintains session memory for iterative refinement:

1. **Context Storage:** Previous output is saved to `tmp-context.txt` after each iteration
2. **Context Retrieval:** On next recording, the context is loaded and passed to the LLM via the prompt
3. **LLM Processing:** The LLM receives ONLY the processed/cooked output from the previous iteration (NOT the original raw text)
4. **System Prompt:** Contains instructions for speech cleanup: removing stutters, consolidating ideas, improving grammar

**Current Limitation:** The LLM does NOT currently receive both the original raw text AND the processed text. Only the processed text from the previous iteration is available in context. This is a key architectural limitation identified for future enhancement.

This enables voice-driven iteration, but without visibility into the original raw speech from previous rounds.

---

## Editor Integration

**Single-Editor Launch (Currently Implemented):**
- After LLM processing, output is written to a temporary file
- User launches `$EDITOR` (or configured editor like Obsidian) to review the output
- Edited content becomes the new context for the next iteration
- Menu mode shows context alongside output for review

**Dual-Pane Interactive UI (Planned - Not Implemented):**
- Documented in this architecture but NOT yet implemented
- Would allow real-time chat-based refinement alongside text editing
- Requires significant UI rewrite and architectural changes

---

## Current Workflow Summary

The actual implemented workflow is:

```
1. Record audio (user speaks)
   ↓
2. Transcribe audio → raw text (via Whisper)
   ↓
3. Process with LLM → cooked text
   - System prompt cleans up speech
   - Optional context from previous iteration is included
   - Output is processed/formatted text
   ↓
4. Review in editor (user edits if desired)
   ↓
5. Save to context (cooked text only)
   ↓
6. [Loop back to 1]
```

**Key Point:** Steps 2→3 happen automatically. Step 4 (editor review) is optional but recommended for quality control.

---
Last Updated: 2026-02-09
