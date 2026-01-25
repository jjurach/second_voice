Here is the comprehensive deployment plan for **Second Voice**. This plan codifies the architecture we've developed to offload the heavy computational lifting to your Ubuntu RTX 2080 while maintaining a fluid, integrated experience on your MacBook.

---

# Second Voice: Remote AI Transcription & Refinement Plan

## 1. System Architecture

The system follows a **Local Capture / Remote Compute / Local Edit** pattern to bypass Intel MacBook performance bottlenecks.

* **Client (MacBook):** Handles GUI, audio recording, and Markdown editing.
* **Server (Ubuntu RTX 2080):** Handles Speech-to-Text (STT) via `small.en` and LLM refinement via `llama-pro`.
* **Bridge:** Secured via SSH Tunneling (Ports 8000 and 11434).
* **Storage:** Volatile edits happen in a local "Shadow Buffer"; permanent notes are synced via Syncthing to an Obsidian Vault.

---

## 2. Server-Side Setup (Ubuntu)

### A. Docker Configuration

Update your `docker-compose.yml` to include the faster-whisper-server. Using the `small.en` model ensures it stays resident in VRAM alongside Ollama.

```yaml
services:
  whisper:
    image: fedirz/faster-whisper-server:latest-cuda
    container_name: whisper-server
    ports:
      - "8000:8000"
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
    restart: unless-stopped

  ollama:
    image: ollama/ollama:latest
    container_name: ollama
    ports:
      - "11434:11434"
    volumes:
      - ./ollama:/root/.ollama
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: 1
              capabilities: [gpu]

```

---

## 3. Client-Side Setup (MacBook)

### A. Dependencies

Install the system-level Tkinter library and Python requirements.

```bash
brew install python-tk
pip install pyaudio requests

```

### B. Configuration File

Create `~/.config/second_voice/settings.json`:

```json
{
    "whisper_url": "http://localhost:8000/v1/audio/transcriptions",
    "ollama_url": "http://localhost:11434/api/generate",
    "whisper_model": "small.en",
    "ollama_model": "llama-pro",
    "vault_path": "/Users/james.jurach/Documents/Obsidian/VoiceInbox",
    "landing_editor": "obsidian"
}

```

---

## 4. The Core Script: `second_voice.py`

```python
#!/usr/bin/env python3
import tkinter as tk
from tkinter import messagebox
import pyaudio, wave, requests, os, json, time, subprocess, urllib.parse, sys
from pathlib import Path

# --- CONSTANTS ---
CONFIG_PATH = Path.home() / ".config/second_voice/settings.json"
BUFFER_FILENAME = ".review_buffer.md"

class SecondVoice:
    def __init__(self, root):
        self.root = root
        self.root.title("Second Voice")
        self.root.geometry("400x350")
        self.config = self.load_config()
        self.vault_path = Path(self.config["vault_path"]).expanduser()
        self.buffer_file = self.vault_path / BUFFER_FILENAME
        
        # State
        self.is_recording = False
        self.frames = []
        self.p = pyaudio.PyAudio()
        self.last_output = ""  # Recursive memory
        
        # UI
        self.status = tk.Label(root, text="Ready to Record", font=("Arial", 14))
        self.status.pack(pady=10)
        
        self.context_label = tk.Label(root, text="Context: Empty", fg="gray")
        self.context_label.pack()

        self.btn_rec = tk.Button(root, text="Start Recording (Space)", command=self.toggle, width=30, height=2)
        self.btn_rec.pack(pady=10)
        
        self.btn_sub = tk.Button(root, text="Process & Edit (Enter)", command=self.submit, state=tk.DISABLED)
        self.btn_sub.pack(pady=5)

        self.btn_clear = tk.Button(root, text="Clear Context", command=self.clear_context)
        self.btn_clear.pack(pady=5)

        root.bind("<space>", lambda e: self.toggle())
        root.bind("<Return>", lambda e: self.submit() if self.btn_sub['state'] == 'normal' else None)

    def load_config(self):
        if not CONFIG_PATH.exists():
            CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
            with open(CONFIG_PATH, 'w') as f:
                json.dump({
                    "whisper_url": "http://localhost:8000/v1/audio/transcriptions",
                    "ollama_url": "http://localhost:11434/api/generate",
                    "whisper_model": "small.en",
                    "ollama_model": "llama-pro",
                    "vault_path": "~/Documents/Obsidian/VoiceInbox"
                }, f, indent=4)
        return json.load(open(CONFIG_PATH))

    def clear_context(self):
        self.last_output = ""
        self.context_label.config(text="Context: Empty", fg="gray")

    def toggle(self):
        if not self.is_recording:
            self.is_recording = True
            self.frames = []
            self.btn_rec.config(text="STOP (Space)", fg="red")
            self.btn_sub.config(state=tk.DISABLED)
            self.stream = self.p.open(format=pyaudio.paInt16, channels=1, rate=16000, input=True, frames_per_buffer=1024)
            self.record_loop()
        else:
            self.is_recording = False
            self.btn_rec.config(text="RE-RECORD (Space)", fg="black")
            self.btn_sub.config(state=tk.NORMAL)
            self.stream.stop_stream()
            self.stream.close()

    def record_loop(self):
        if self.is_recording:
            self.frames.append(self.stream.read(1024, exception_on_overflow=False))
            self.root.after(1, self.record_loop)

    def submit(self):
        temp_wav = "/tmp/sv_audio.wav"
        with wave.open(temp_wav, "wb") as wf:
            wf.setnchannels(1); wf.setsampwidth(self.p.get_sample_size(pyaudio.paInt16)); wf.setframerate(16000)
            wf.writeframes(b"".join(self.frames))
        
        self.status.config(text="⌛ Processing AI Loop...")
        self.root.update()

        try:
            # 1. Remote Whisper
            with open(temp_wav, 'rb') as f:
                r = requests.post(self.config['whisper_url'], files={'file': f}, data={'model': self.config['whisper_model']})
            new_text = r.json()['text']

            # 2. Remote Ollama with Recursive Context
            combined_prompt = f"ORIGINAL TEXT: {self.last_output}\n\nNEW INSTRUCTION: {new_text}"
            system_rules = (
                "If NEW INSTRUCTION refers to ORIGINAL TEXT (using 'it', 'this', 'that', 'bullets', 'shorten'), "
                "transform the ORIGINAL TEXT. Otherwise, process the NEW INSTRUCTION as a fresh prompt."
            )
            
            o = requests.post(self.config['ollama_url'], json={
                "model": self.config['ollama_model'], "prompt": combined_prompt, "stream": False, "system": system_rules
            })
            processed_text = o.json()['response']

            # 3. Shadow Buffer Promotion
            self.vault_path.mkdir(parents=True, exist_ok=True)
            with open(self.buffer_file, "w") as f: f.write(processed_text)
            
            # 4. Obsidian Landing
            subprocess.run(["open", f"obsidian://open?path={urllib.parse.quote(str(self.buffer_file))}"])
            
            messagebox.showinfo("Review", "Edit in Obsidian. Click OK to capture the result.")
            
            with open(self.buffer_file, "r") as f:
                self.last_output = f.read()
            
            # Final Output to STDOUT for CLI/Claude integration
            sys.stdout.write(self.last_output)
            sys.stdout.flush()

            # 5. Permanent Archive
            perm_note = self.vault_path / f"voice_note_{int(time.time())}.md"
            os.rename(self.buffer_file, perm_note)
            
            self.context_label.config(text=f"Context: {len(self.last_output)} chars", fg="blue")
            self.status.config(text="Ready for Refinement")

        except Exception as e:
            messagebox.showerror("Error", str(e))

if __name__ == "__main__":
    root = tk.Tk()
    app = SecondVoice(root)
    root.mainloop()

```

---

## 5. Deployment and Integration

### A. The SSH Tunnel (Permanent Bridge)

Run this in a dedicated terminal tab on your MacBook. This maps your local ports to the Ubuntu AI services.

```bash
ssh -N -L 8000:localhost:8000 -L 11434:localhost:11434 james.jurach@192.168.0.157

```

### B. Syncthing Ignore Patterns

To prevent the `.review_buffer.md` from triggering sync cycles, add this to the Syncthing "Ignore Patterns" for the VoiceInbox folder:

```text
.review_buffer.md
*.sync-conflict-*

```

### C. CLI/Claude Integration

To use this with a hotkey (like `Ctrl+G`), wrap the script call so it handles the output redirection:

```bash
# Example wrapper to copy result to clipboard
second_voice | pbcopy

```

---

## 6. Theory of Validation

1. **Hardware:** `nvidia-smi` on Ubuntu should show ~2.5GB VRAM used by `whisper` and `ollama`.
2. **Network:** `lsof -i :8000` on Mac should show `ssh` as the listener.
3. **Recursion:** Record "hello", edit to "HELLO WORLD" in Obsidian, hit OK, then record "translate to French". Obsidian should pop up with "BONJOUR LE MONDE".
