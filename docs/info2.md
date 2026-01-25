Here is the comprehensive deployment and architectural plan for **Second Voice**. This plan integrates the hardware optimizations for your RTX 2080, the SSH tunneling strategy for your Intel MacBook, and the newly defined iterative "Recursive Context" workflow.

---

# Second Voice: Remote AI Transcription & Iterative Refinement Plan

## 1. Core Philosophy: The "Remote Brain" Bridge

To bypass the Intel MacBook's thermal and processing limitations, this system decouples audio capture from AI computation.

* **The Engine:** Your Ubuntu server (james-desktop) runs a high-performance **Whisper** engine (using the `small.en` model for VRAM efficiency) and **Ollama** (`llama-pro`).
* **The Workflow:** Audio is captured locally on the Mac, processed on the Ubuntu GPU, and then "promoted" to an Obsidian buffer for human review before final use.

---

## 2. Server-Side Infrastructure (Ubuntu RTX 2080)

### A. Docker Deployment

Using the `small.en` model allows it to stay resident in the RTX 2080's 8GB VRAM alongside your `llama-pro` model (~4.9GB) without causing Out-of-Memory (OOM) errors.

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

### A. The SSH Tunnel (The Permanent Bridge)

You must keep this tunnel active to allow the Mac to communicate with the Ubuntu containers.

```bash
ssh -N -L 8000:localhost:8000 -L 11434:localhost:11434 james.jurach@192.168.0.157

```

### B. Syncthing Ignore Patterns

To ensure the `buffer.md` used for editing doesn't create sync noise or conflicts, add this to your Obsidian folder's Ignore Patterns:

```text
.review_buffer.md
*.sync-conflict-*

```

---

## 4. The Unified Workflows

### Workflow A: The "Voice Inbox" (Standard Mode)

* **Goal:** Capture long-form thoughts or "stutter talk" into your permanent vault.
* **Process:** Record -> Transcribe -> Professional Cleanup -> Edit in Obsidian -> Save as timestamped file in `VoiceInbox`.

### Workflow B: The "Ctrl-G" CLI (Modal Mode)

* **Goal:** Use voice to input commands or text directly into a terminal or Claude session.
* **Process:** Invoke script -> Record instruction -> Edit/Refine in Obsidian -> Output to `stdout` upon closing.

---

## 5. The "Retry or Redo" Feature (Recursive Context)

This feature allows for iterative refinement. The script maintains a `last_output` variable during the session.

1. **Initial Input:** "Build a python script for X." -> Result saved to context.
2. **Refinement:** User hits "Record" again and says "Convert that to use a Class."
3. **LLM Logic:** The system prompt instructs the LLM: *If the new instruction mentions 'that', 'this', or 'it', use the context. Otherwise, start fresh.*

---

## 6. The Core Script: `second_voice.py`

```python
#!/usr/bin/env python3
import tkinter as tk
from tkinter import messagebox
import pyaudio, wave, requests, os, json, time, subprocess, urllib.parse, sys
from pathlib import Path

# --- CONFIG LOADING ---
CONFIG_PATH = Path.home() / ".config/second_voice/settings.json"
BUFFER_FILENAME = ".review_buffer.md"

class SecondVoice:
    def __init__(self, root):
        self.root = root
        self.root.title("Second Voice (Recursive Mode)")
        self.root.geometry("400x400")
        self.config = self.load_config()
        self.vault_path = Path(self.config["vault_path"]).expanduser()
        self.buffer_file = self.vault_path / BUFFER_FILENAME
        
        # State
        self.is_recording = False
        self.frames = []
        self.p = pyaudio.PyAudio()
        self.last_output = ""  # Memory for 'Redo/Retry' cycles
        
        # UI Elements
        self.status = tk.Label(root, text="Ready", font=("Arial", 14))
        self.status.pack(pady=10)
        
        self.context_info = tk.Label(root, text="Context: Empty", fg="gray")
        self.context_info.pack()

        self.btn_rec = tk.Button(root, text="Start Recording (Space)", command=self.toggle, width=30, height=2)
        self.btn_rec.pack(pady=10)
        
        self.btn_sub = tk.Button(root, text="Submit & Edit (Enter)", command=self.submit, state=tk.DISABLED)
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
        self.context_info.config(text="Context: Empty", fg="gray")

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
            self.btn_rec.config(text="RE-RECORD / ADD INSTRUCTION", fg="black")
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
            # 1. Remote Whisper STT
            with open(temp_wav, 'rb') as f:
                r = requests.post(self.config['whisper_url'], files={'file': f}, data={'model': self.config['whisper_model']})
            new_text = r.json()['text']

            # 2. Iterative LLM Prompting
            combined_prompt = f"ORIGINAL TEXT: {self.last_output}\n\nNEW INSTRUCTION: {new_text}"
            system_rules = (
                "If NEW INSTRUCTION refers to ORIGINAL TEXT (using 'it', 'this', 'that', 'bullets', 'shorten'), "
                "transform the ORIGINAL TEXT. Otherwise, process the NEW INSTRUCTION as a fresh prompt."
            )
            
            o = requests.post(self.config['ollama_url'], json={
                "model": self.config['ollama_model'], "prompt": combined_prompt, "stream": False, "system": system_rules
            })
            processed_text = o.json()['response']

            # 3. Obsidian Buffer Review
            self.vault_path.mkdir(parents=True, exist_ok=True)
            with open(self.buffer_file, "w") as f: f.write(processed_text)
            
            # Open Obsidian to the buffer file
            subprocess.run(["open", f"obsidian://open?path={urllib.parse.quote(str(self.buffer_file))}"])
            
            messagebox.showinfo("Review", "Edit in Obsidian. Click OK to confirm context.")
            
            with open(self.buffer_file, "r") as f:
                self.last_output = f.read()
            
            # Write to STDOUT for CLI/Claude pipe
            sys.stdout.write(self.last_output + "\n")
            sys.stdout.flush()

            # Archive permanent copy
            perm_note = self.vault_path / f"voice_note_{int(time.time())}.md"
            os.rename(self.buffer_file, perm_note)
            
            self.context_info.config(text=f"Context: {len(self.last_output)} chars", fg="blue")
            self.status.config(text="Ready for Refinement")

        except Exception as e:
            messagebox.showerror("Error", str(e))

if __name__ == "__main__":
    root = tk.Tk()
    app = SecondVoice(root)
    root.mainloop()

```
