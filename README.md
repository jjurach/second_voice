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

Second Voice - AI Assistant

optional arguments:
  -h, --help            show this help message and exit
  --mode {auto,gui,tui,menu}
                        Interaction mode (default: auto)
```

## Configuration

Configuration is stored in `~/.config/second_voice/settings.json`.

Example configuration:

```json
{
    "whisper_url": "http://localhost:8000/v1/audio/transcriptions",
    "ollama_url": "http://localhost:11434/api/generate",
    "vault_path": "~/Documents/Obsidian/VoiceInbox",
    "mode": "auto"
}
```

## Development

### Running Tests

```bash
python3 tests/test_modes.py
```

### Architecture

See [docs/architecture.md](docs/architecture.md) for a detailed overview of the system architecture.

## License

MIT
