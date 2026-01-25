# Second Voice

Second Voice is a recursive AI assistant that allows you to refine text and code using voice instructions. It follows a **Local Capture / Remote Compute / Local Edit** pattern.

## Features

- **Multi-Mode Interface:**
  - **GUI:** Tkinter-based window with visual feedback.
  - **TUI:** Full-screen terminal interface using Rich.
  - **Menu:** Simple text-based menu for minimal environments and SSH.
- **Recursive Context:** Maintains session memory, allowing for iterative refinement ("Do X", "Now make it a class", "Add error handling").
- **Multi-Provider Support:**
  - **STT:** Local Whisper (via Docker) or Groq API.
  - **LLM:** Local Ollama or cloud-based OpenRouter (Claude, GPT-4, etc.).
- **Cross-Platform Audio:** Uses `sounddevice` and `soundfile` for robust audio I/O.
- **Editor Integration:** Review and edit outputs in Obsidian or your preferred `$EDITOR`.

## Installation

```bash
# Clone the repository
git clone https://github.com/youruser/second_voice.git
cd second_voice

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

## Usage

Run the main CLI entry point:

```bash
python3 src/cli/run.py
```

### Command Line Options

```bash
usage: run.py [-h] [--mode {auto,gui,tui,menu}] [--keep-files] [--file FILE]

Second Voice - AI Assistant

optional arguments:
  -h, --help            show this help message and exit
  --mode {auto,gui,tui,menu}
                        Interaction mode (default: auto)
  --keep-files          Keep temporary files (recordings, transcripts) after execution
  --file FILE           Process an existing .wav file instead of recording from microphone
```

## Testing

For automated testing and debugging, you can use the `samples/test.wav` file (or provide your own) and the `--file` flag to bypass the microphone. This allows for reproducible runs without needing to speak.

### Example: Running with an input file

```bash
# Process a test file in TUI mode
python3 src/cli/run.py --mode tui --file samples/test.wav

# Process a test file in Menu mode
python3 src/cli/run.py --mode menu --file samples/test.wav
```

### Running the Demo Script

A standalone demo script is available to quickly verify the installation and audio processing without the full recursive loop:

```bash
python3 scripts/demo_second_voice.py
```

### Inspecting Intermediate Files

Use the `--keep-files` flag to inspect the recorded audio, intermediate transcripts, and context buffers.

```bash
python3 src/cli/run.py --keep-files
```

Temporary files will be preserved in the `tmp/` and `tmp/mode_tmp/` directories.

## Configuration

Configuration is stored in `~/.config/second_voice/settings.json`.

Example configuration:

```json
{
    "whisper_url": "http://localhost:9090/v1/audio/transcriptions",
    "ollama_url": "http://localhost:11434/api/generate",
    "vault_path": "~/Documents/Obsidian/VoiceInbox",
    "mode": "auto"
}
```

## Development

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src/second_voice

# Run specific test file
pytest tests/test_config.py -v

# For more testing options, see TESTING.md
```

For comprehensive testing documentation, see [TESTING.md](TESTING.md).

### Architecture

See [docs/architecture.md](docs/architecture.md) for a detailed overview of the system architecture.

## AI Tool Support & Workflow

This project supports multiple AI tools for development. **All tools follow the same AGENTS.md workflow.**

### For Developers Using AI Tools

**Start here:**
1. Read [AGENTS.md](AGENTS.md) - Core development workflow (mandatory)
2. Choose your tool below and read its guide
3. Reference [docs/PROMPT-PATTERNS.md](docs/PROMPT-PATTERNS.md) for effective prompting

### Supported Tools

#### 🎯 Claude Code (Primary)
**Status:** ✅ Fully Supported

- Official Anthropic CLI tool
- Built-in approval gates for plans
- Task tracking (TaskCreate/TaskUpdate)
- MCP server integration
- Web search and fetch

**Setup:**
```bash
pip install anthropic-claude-code
cd /path/to/second_voice
claude-code
```

**Documentation:**
- Entry point: [CLAUDE.md](CLAUDE.md)
- Complete guide: [docs/TOOL-SPECIFIC-GUIDES/claude-code.md](docs/TOOL-SPECIFIC-GUIDES/claude-code.md)

---

#### 🤝 Aider
**Status:** ✅ Supported (Implicit approval)

- Collaborative AI coding tool
- Excellent code awareness
- Automatic git commits
- No built-in approval gates (conversational approval instead)

**Setup:**
```bash
pip install aider-chat
cd /path/to/second_voice
aider
```

**Documentation:**
- Configuration: `.aider.conf` (create from [docs/TOOL-SPECIFIC-GUIDES/aider.md](docs/TOOL-SPECIFIC-GUIDES/aider.md))
- Complete guide: [docs/TOOL-SPECIFIC-GUIDES/aider.md](docs/TOOL-SPECIFIC-GUIDES/aider.md)

---

#### 🔬 Google Gemini
**Status:** ⏳ Experimental (Testing in progress)

- Fast multimodal AI
- Lower context window (~32k tokens)
- Function calling support
- Web search integration

**Documentation:**
- Status & guide: [docs/TOOL-SPECIFIC-GUIDES/gemini.md](docs/TOOL-SPECIFIC-GUIDES/gemini.md)
- Help us test! See guide for how to contribute.

---

#### 💻 OpenAI Codex/GPT-4
**Status:** ⏳ Experimental (Investigation needed)

- Excellent code understanding
- No official CLI tool (needs custom integration)
- Lower context window (~8k tokens)
- Function calling support

**Documentation:**
- Status & guide: [docs/TOOL-SPECIFIC-GUIDES/codex.md](docs/TOOL-SPECIFIC-GUIDES/codex.md)
- Help us integrate! See guide for how to contribute.

### All Tools Use the Same Workflow

Regardless of tool, all development follows **AGENTS.md:**

1. **Analyze** - Understand the request
2. **Spec** - Create spec file in `dev_notes/specs/`
3. **Plan** - Create plan in `dev_notes/project_plans/` (if non-trivial)
4. **Approve** - Get explicit approval (tool-specific implementation)
5. **Implement** - Execute with concurrent documentation
6. **Verify** - Ensure all criteria are met

### Reference Documentation

| Document | Purpose |
|----------|---------|
| [AGENTS.md](AGENTS.md) | **Core workflow - READ FIRST** |
| [CLAUDE.md](CLAUDE.md) | Claude Code entry point |
| [docs/TOOLS-CAPABILITIES.md](docs/TOOLS-CAPABILITIES.md) | What each tool can do |
| [docs/WORKFLOW-MAPPING.md](docs/WORKFLOW-MAPPING.md) | How AGENTS.md maps to each tool |
| [docs/PROMPT-PATTERNS.md](docs/PROMPT-PATTERNS.md) | Universal prompt structures |
| [docs/FILE-NAMING-CONVENTIONS.md](docs/FILE-NAMING-CONVENTIONS.md) | Which file names matter |
| [docs/TOOL-SPECIFIC-GUIDES/](docs/TOOL-SPECIFIC-GUIDES/) | Per-tool complete guides |

### Quick Decision Tree

**Which tool should I use?**

```
Do I need explicit approval gates?
  YES → Use Claude Code
  NO  → Consider Aider

Do I need task tracking?
  YES → Use Claude Code
  NO  → Any tool works

Is the project large (full repo context)?
  YES → Use Claude Code (200k tokens)
  NO  → Aider or Gemini acceptable

Do I need multimodal input (images)?
  YES → Use Gemini
  NO  → Any tool works

Need MCP server integration?
  YES → Use Claude Code
  NO  → Any tool works
```

### Contributing to Tool Support

To add or improve tool support:

1. **Test** - Use tool on a simple task
2. **Document** - Update guide in `docs/TOOL-SPECIFIC-GUIDES/`
3. **Reference** - Update [docs/TOOLS-CAPABILITIES.md](docs/TOOLS-CAPABILITIES.md)
4. **Configure** - Create tool config file (e.g., `.aider.conf`)
5. **Submit** - PR with documentation and config

## License

MIT
