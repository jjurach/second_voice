import tkinter as tk
from tkinter import messagebox
import pyaudio, wave, requests, os, json, time, subprocess, urllib.parse
from pathlib import Path

# --- CONFIG ---
CONFIG_PATH = Path.home() / ".config/second_voice/settings.json"
DEFAULT_VAULT = Path.home() / "Documents/Obsidian/VoiceInbox"
BUFFER_FILE = DEFAULT_VAULT / ".review_buffer.md"

class SecondVoice:
    def __init__(self, root):
        self.root = root
        self.root.title("Second Voice (Recursive Mode)")
        self.root.geometry("400x350")
        self.config = self.load_config()
        
        # State
        self.is_recording = False
        self.frames = []
        self.p = pyaudio.PyAudio()
        self.last_output = ""  # Persistent memory for the session
        
        # UI Build
        self.status = tk.Label(root, text="Ready", font=("Arial", 12))
        self.status.pack(pady=10)
        
        self.context_indicator = tk.Label(root, text="Context: Empty", fg="gray")
        self.context_indicator.pack()

        self.btn_rec = tk.Button(root, text="Start Recording (Space)", command=self.toggle, width=30)
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
                json.dump({"whisper_url": "http://localhost:8000/v1/audio/transcriptions", 
                          "ollama_url": "http://localhost:11434/api/generate",
                          "ollama_model": "llama-pro", 
                          "whisper_model": "small.en"}, f, indent=4)
        return json.load(open(CONFIG_PATH))

    def clear_context(self):
        self.last_output = ""
        self.context_indicator.config(text="Context: Empty", fg="gray")

    def toggle(self):
        if not self.is_recording:
            self.is_recording = True
            self.frames = []
            self.btn_rec.config(text="Stop (Space)", fg="red")
            self.btn_sub.config(state=tk.DISABLED)
            self.stream = self.p.open(format=pyaudio.paInt16, channels=1, rate=16000, input=True, frames_per_buffer=1024)
            self.record_loop()
        else:
            self.is_recording = False
            self.btn_rec.config(text="Record Instruction / New Text", fg="black")
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
        
        self.status.config(text="⌛ Processing Iteration...")
        self.root.update()

        try:
            # 1. Whisper
            with open(temp_wav, 'rb') as f:
                r = requests.post(self.config['whisper_url'], files={'file': f}, data={'model': self.config['whisper_model']})
            new_text = r.json()['text']

            # 2. Iterative Prompt Logic
            combined_prompt = f"ORIGINAL TEXT: {self.last_output}\n\nNEW INSTRUCTION: {new_text}"
            
            system_rules = (
                "If the NEW INSTRUCTION mentions the ORIGINAL TEXT (using 'it', 'this', 'that', 'bullets', 'shorter', etc.), "
                "transform the ORIGINAL TEXT accordingly. If it does not, ignore the ORIGINAL TEXT and process a fresh answer."
            )

            # 3. Ollama
            o = requests.post(self.config['ollama_url'], json={
                "model": self.config['ollama_model'],
                "prompt": combined_prompt,
                "stream": False,
                "system": system_rules
            })
            processed_text = o.json()['response']

            # 4. Obsidian Review
            with open(BUFFER_FILE, "w") as f: f.write(processed_text)
            subprocess.run(["open", f"obsidian://open?path={urllib.parse.quote(str(BUFFER_FILE))}"])
            
            messagebox.showinfo("Review", "Refine in Obsidian. Click OK to set as next round's context.")
            
            with open(BUFFER_FILE, "r") as f:
                self.last_output = f.read()
                print(self.last_output) # Output to STDOUT for CLI integration

            # Update GUI indicator
            self.context_indicator.config(text=f"Context: {len(self.last_output)} chars", fg="blue")
            self.status.config(text="Ready for Next Round")

        except Exception as e:
            messagebox.showerror("Error", str(e))

if __name__ == "__main__":
    root = tk.Tk()
    app = SecondVoice(root)
    root.mainloop()
