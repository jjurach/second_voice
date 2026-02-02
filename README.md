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
usage: run.py [-h] [--mode {auto,gui,tui,menu}]
              [--input-provider {default,google-drive}] [--keep-remote]
              [--record-only | --transcribe-only | --translate-only]
              [--keep-files] [--file FILE] [--audio-file AUDIO_FILE]
              [--text-file TEXT_FILE] [--output-file OUTPUT_FILE]
              [--no-edit] [--editor-command CMD] [--debug] [--verbose]

Second Voice - AI Assistant

optional arguments:
  -h, --help            show this help message and exit
  --mode {auto,gui,tui,menu}
                        Interaction mode (default: menu)

Input Provider:
  --input-provider {default,google-drive}
                        Input source: 'default' (record), 'google-drive' (fetch from Drive)
  --keep-remote         Keep remote file after download (only with --input-provider google-drive)

Pipeline Modes:
  --record-only         Record audio and exit (no transcription or translation)
  --transcribe-only     Transcribe existing audio file (requires --audio-file)
  --translate-only      Translate/process existing text file (requires --text-file)

File Options:
  --file FILE           Input audio file to process (bypasses recording)
  --audio-file FILE     Audio file path (input for --transcribe-only, output for --record-only)
  --text-file FILE      Text file path (input for --translate-only, output for --transcribe-only)
  --output-file FILE    Output file path (for --translate-only)

Editor Options:
  --no-edit             Skip editor after processing (default: invoke editor)
  --editor-command CMD  Specify custom editor command (e.g., 'code --wait', 'emacs')

General Options:
  --keep-files          Keep temporary files (recordings, transcripts) after execution
  --debug               Enable debug logging
  --verbose             Enable verbose output
```

### Pipeline Modes

For automation and integration with other tools, use pipeline modes to execute isolated workflow stages:

#### Record-Only Mode
Record audio and exit immediately:

```bash
# Record to default temp file
python3 src/cli/run.py --record-only

# Record to specific file
python3 src/cli/run.py --record-only --audio-file recording.wav
```

#### Transcribe-Only Mode
Transcribe existing audio without editing or translation:

```bash
# Transcribe audio to temp file
python3 src/cli/run.py --transcribe-only --audio-file recording.wav

# Transcribe to specific file
python3 src/cli/run.py --transcribe-only --audio-file recording.wav --text-file transcript.txt
```

#### Translate-Only Mode
Process/translate existing text without recording or transcription:

```bash
# Process text to temp file
python3 src/cli/run.py --translate-only --text-file transcript.txt

# Process to specific file
python3 src/cli/run.py --translate-only --text-file transcript.txt --output-file final.md
```

### Google Drive Input Provider

Second Voice can automatically fetch voice recordings from Google Drive instead of recording from your microphone. This is useful for processing recordings made on mobile devices.

#### Prerequisites

1. Set up Google authentication using [google-personal-mcp](https://github.com/anthropics/mcp-google):
   ```bash
   # Install google-personal-mcp
   npm install -g @anthropic/google-personal-mcp

   # Follow setup instructions to create OAuth credentials
   # This will create credentials in ~/.config/google-personal-mcp/profiles/default/
   ```

2. Upload voice recordings to a Google Drive folder (default: `/Voice Recordings`)

#### Usage

Fetch and process the earliest file from Google Drive:

```bash
# Fetch from Google Drive and process
python3 src/cli/run.py --input-provider google-drive

# Keep the remote file after download
python3 src/cli/run.py --input-provider google-drive --keep-remote
```

#### How It Works

1. **Fetch:** Downloads the lexicographically earliest file from the configured Google Drive folder
2. **Archive:** Moves the file to `dev_notes/inbox-archive/` with timestamp from the remote file
3. **Process:** Transcribes and processes the audio through the normal workflow
4. **Output:** Saves the final .md file to `dev_notes/inbox/` with matching timestamp
5. **Cleanup:** Deletes the remote file (unless `--keep-remote` is specified)

#### Configuration

Configure Google Drive settings in `~/.config/second_voice/settings.json`:

```json
{
  "google_drive": {
    "profile": "default",
    "folder": "/Voice Recordings",
    "inbox_dir": "dev_notes/inbox",
    "archive_dir": "dev_notes/inbox-archive"
  }
}
```

Or use environment variables:
- `SECOND_VOICE_GOOGLE_PROFILE`: Google authentication profile name
- `SECOND_VOICE_GOOGLE_FOLDER`: Google Drive folder path
- `SECOND_VOICE_INBOX_DIR`: Local inbox directory for output files
- `SECOND_VOICE_ARCHIVE_DIR`: Archive directory for downloaded audio

#### Full Pipeline Example

Chain pipeline modes for complete workflow:

```bash
# Step 1: Record audio
python3 src/cli/run.py --record-only --audio-file recording.wav

# Step 2: Transcribe audio
python3 src/cli/run.py --transcribe-only --audio-file recording.wav --text-file transcript.txt

# Step 3: Process/translate text
python3 src/cli/run.py --translate-only --text-file transcript.txt --output-file final.md
```

### Editor Behavior

**Default:** Editor is invoked by default. To skip editor:

```bash
# Skip editor after processing
python3 src/cli/run.py --no-edit

# Specify custom editor
python3 src/cli/run.py --editor-command "code --wait"
python3 src/cli/run.py --editor-command "emacs"
```

**Editor Resolution:** The following command sources are checked in order:
1. `--editor-command` flag from CLI
2. `editor_command` setting in config file
3. `$EDITOR` environment variable
4. System default (`nano`)

## Testing

For automated testing and debugging, you can use the `samples/test.wav` file (or provide your own) and the `--file` flag to bypass the microphone. This allows for reproducible runs without needing to speak.

### Example: Running with an input file

A test audio file is included at `samples/test.wav`:

```bash
# Process the test file in TUI mode
python3 src/cli/run.py --mode tui --file samples/test.wav

# Process the test file in Menu mode
python3 src/cli/run.py --mode menu --file samples/test.wav

# Display audio info in verbose mode
python3 src/cli/run.py --file samples/test.wav --verbose
```

**Supported Audio Formats:**
- WAV, FLAC, OGG, MP3 (common formats)
- **AAC, M4A** (via FFmpeg conversion)
- AIFF, AU, CAF (legacy formats)
- And 25+ additional formats supported by `soundfile`

**AAC Support Requirements:**
To process AAC files, install FFmpeg:
- Linux: `apt-get install ffmpeg`
- macOS: `brew install ffmpeg`
- Windows: `choco install ffmpeg` or download from ffmpeg.org

See [docs/test-guide.md](docs/test-guide.md) for comprehensive testing documentation.

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

### Whisper Output Recovery

On failure or with the `--keep-files` flag, Second Voice preserves:
- **Recording files**: `tmp/recording-YYYY-MM-DD_HH-MM-SS.{format}`
- **Whisper transcripts**: `tmp/whisper-YYYY-MM-DD_HH-MM-SS.txt`

This allows you to:
1. Review raw transcriptions if LLM processing fails
2. Recover transcripts from crashes
3. Audit the processing pipeline

**Example recovery:**
```bash
# Keep files with --keep-files flag
python3 src/cli/run.py --file recording.aac --keep-files

# Later, recover the whisper output
python3 scripts/recover_whisper_output.py --recover
```

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

# For more testing options, see docs/test-guide.md
```

For comprehensive testing documentation, see [docs/test-guide.md](docs/test-guide.md).

### Architecture

See [docs/architecture.md](docs/architecture.md) for a detailed overview of the system architecture.

## AI Tool Support & Workflow

This project supports multiple AI tools for development. **All tools follow the same AGENTS.md workflow.**

### For Developers Using AI Tools

**Start here:**
1. Read [AGENTS.md](AGENTS.md) - Core development workflow (mandatory)
2. Choose your tool below and read its guide
3. Reference [docs/prompt-patterns.md](docs/prompt-patterns.md) for effective prompting

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
- Entry point: [.claude/CLAUDE.md](.claude/CLAUDE.md)
- Complete guide: [docs/system-prompts/tools/claude-code.md](docs/system-prompts/tools/claude-code.md)

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
- Configuration: `.aider.conf.yml` (see [docs/system-prompts/tools/aider.md](docs/system-prompts/tools/aider.md))
- Complete guide: [docs/system-prompts/tools/aider.md](docs/system-prompts/tools/aider.md)

---

#### 🔧 Cline
**Status:** ✅ Supported

- Open-source code editor CLI
- Multi-file editing with automatic commits
- Flexible approval modes (suggest, auto, conversational)
- Shell integration for testing and debugging

**Setup:**
```bash
npm install -g cline
cd /path/to/second_voice
cline
```

**Documentation:**
- Entry point: `.clinerules` in project root
- Complete guide: [docs/system-prompts/tools/cline.md](docs/system-prompts/tools/cline.md)

---

#### 🔬 Google Gemini
**Status:** ⏳ Experimental (Testing in progress)

- Fast multimodal AI
- Lower context window (~32k tokens)
- Function calling support
- Web search integration

**Documentation:**
- Entry point: [.gemini/GEMINI.md](.gemini/GEMINI.md)
- Status & guide: [docs/system-prompts/tools/gemini.md](docs/system-prompts/tools/gemini.md)
- Help us test! See guide for how to contribute.

---

#### 💻 OpenAI Codex/GPT-4
**Status:** ⏳ Experimental (Investigation needed)

- Excellent code understanding
- No official CLI tool (needs custom integration)
- Lower context window (~8k tokens)
- Function calling support

**Documentation:**
- Status & guide: [docs/system-prompts/tools/codex.md](docs/system-prompts/tools/codex.md)
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
| [.claude/CLAUDE.md](.claude/CLAUDE.md) | Claude Code entry point |
| [.gemini/GEMINI.md](.gemini/GEMINI.md) | Gemini CLI entry point |
| [docs/tools-capabilities.md](docs/tools-capabilities.md) | What each tool can do |
| [docs/workflow-mapping.md](docs/workflow-mapping.md) | How AGENTS.md maps to each tool |
| [docs/prompt-patterns.md](docs/prompt-patterns.md) | Universal prompt structures |
| [docs/file-naming-conventions.md](docs/file-naming-conventions.md) | Which file names matter |
| [docs/system-prompts/tools/](docs/system-prompts/tools/) | Generic tool workflow guides |

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
2. **Document** - Update guide in `docs/tool-specific-guides/`
3. **Reference** - Update [docs/tools-capabilities.md](docs/tools-capabilities.md)
4. **Configure** - Create tool config file (e.g., `.aider.conf`)
5. **Submit** - PR with documentation and config

## Documentation

### For AI Agents
- **[AGENTS.md](AGENTS.md)** - Mandatory workflow for AI agents
- **[Definition of Done](docs/definition-of-done.md)** - Quality standards
- **[Workflows](docs/workflows.md)** - Development workflows

### For Developers
- **[Documentation Index](docs/README.md)** - Complete documentation navigation
- **[Architecture](docs/architecture.md)** - System architecture
- **[Implementation Reference](docs/implementation-reference.md)** - Code patterns

## License

MIT

---
Last Updated: 2026-01-29
