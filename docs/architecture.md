# Second Voice Architecture

## Overview

Second Voice follows a **Local Capture / Remote Compute / Local Edit** pattern to bypass Intel MacBook performance bottlenecks by offloading heavy AI computation to a remote Ubuntu server with an RTX 2080 GPU.

## System Components

### Client (MacBook)
- **Audio Capture:** Records audio using PyAudio
- **GUI:** Tkinter-based interface with visual feedback
- **Local Editing:** Obsidian integration for human review
- **Network:** SSH tunnel to remote services

### Server (Ubuntu RTX 2080)
- **Speech-to-Text:** faster-whisper-server using `small.en` model
- **LLM Processing:** Ollama running `llama-pro` model
- **Deployment:** Docker containers with GPU access

### Bridge/Integration
- **SSH Tunnel:** Ports 8000 (Whisper) and 11434 (Ollama)
- **Storage:** Syncthing for Obsidian vault synchronization
- **Workflow:** Volatile edits in shadow buffer, permanent notes in vault

## Network Configuration

### Port Mapping
- **Port 8000:** Whisper transcription service
- **Port 11434:** Ollama LLM service
- **SSH Tunnel:** `ssh -N -L 8000:localhost:8000 -L 11434:localhost:11434 james.jurach@192.168.0.157`

### Docker Services

The Ubuntu server runs two containerized services sharing the GPU:

```yaml
services:
  whisper:
    image: fedirz/faster-whisper-server:latest-cuda
    ports: ["8000:8000"]
    environment:
      - WHISPER_MODEL=small.en
      - MODEL_MAP=whisper-1:small.en
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: 1
              capabilities: [gpu]

  ollama:
    image: ollama/ollama:latest
    ports: ["11434:11434"]
    volumes: ["./ollama:/root/.ollama"]
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: 1
              capabilities: [gpu]
```

## Module Structure

The application is organized into functional modules:

```
second_voice/
├── __init__.py
├── cli.py                # CLI entry point
├── config.py             # Configuration management
├── engine/
│   ├── __init__.py
│   ├── recorder.py       # Audio recording + RMS analysis
│   └── processor.py      # API communication (Whisper/Ollama)
└── ui/
    ├── __init__.py
    ├── main_window.py    # Main Tkinter application
    └── components.py     # VU meter and visual components
```

## Configuration

Settings are stored in `~/.config/second_voice/settings.json`:

```json
{
    "whisper_url": "http://localhost:8000/v1/audio/transcriptions",
    "ollama_url": "http://localhost:11434/api/generate",
    "whisper_model": "small.en",
    "ollama_model": "llama-pro",
    "vault_path": "~/Documents/Obsidian/VoiceInbox",
    "landing_editor": "obsidian"
}
```

## Data Flow

1. **Capture:** User records audio via PyAudio (16kHz, mono, 16-bit)
2. **Transcribe:** Audio sent to remote Whisper service via HTTP
3. **Process:** Transcription sent to Ollama with recursive context
4. **Review:** Output written to `.review_buffer.md` in Obsidian vault
5. **Edit:** User edits in Obsidian, clicks OK to confirm
6. **Store:** Final result becomes context for next iteration, archived with timestamp

## Recursive Context Feature

The application maintains session memory (`last_output`) for iterative refinement:

1. **Initial Input:** "Build a python script for X" → Result saved to context
2. **Refinement:** "Convert that to use a Class" → LLM receives both context and new instruction
3. **LLM Logic:** System prompt detects references to previous output ("it", "this", "that") and transforms accordingly

This enables voice-driven iteration without re-stating the entire context.
