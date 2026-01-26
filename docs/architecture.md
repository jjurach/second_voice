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

The application maintains session memory (`last_output`) for iterative refinement:

1. **Initial Input:** "Build a python script for X" → Result saved to context
2. **Refinement:** "Convert that to use a Class" → LLM receives both context and new instruction
3. **LLM Logic:** System prompt detects references to previous output ("it", "this", "that") and transforms accordingly

This enables voice-driven iteration without re-stating the entire context.
