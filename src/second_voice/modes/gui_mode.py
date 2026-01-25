import tkinter as tk
from tkinter import messagebox
import subprocess
import urllib.parse
import threading
import os
from .base import BaseMode

class GUIMode(BaseMode):
    """
    GUI Mode implementation using Tkinter.
    Replicates the original Second Voice CLI interface but uses the shared engine.
    """

    def __init__(self, config, recorder, processor):
        super().__init__(config, recorder, processor)
        self.root = None
        self.is_recording = False
        self.last_output = ""
        self.buffer_file = os.path.join(self.config.get('vault_path', os.path.expanduser("~/Documents/Obsidian/VoiceInbox")), ".review_buffer.md")
        
        # Ensure vault path exists if we are going to use it
        os.makedirs(os.path.dirname(self.buffer_file), exist_ok=True)

    def start_recording(self) -> str:
        """
        Start recording audio.
        In GUI mode, this is triggered by the toggle button/key.
        Returns the path to the temp file being recorded to (or None).
        """
        return self.recorder.start_recording()

    def show_transcription(self, text: str):
        """Display transcription (not used directly in this GUI flow, but part of interface)."""
        print(f"Transcription: {text}")

    def review_output(self, text: str, context: str = None) -> str:
        """
        Open Obsidian for review.
        """
        with open(self.buffer_file, "w") as f: 
            f.write(text)
        
        # Open in Obsidian
        try:
            subprocess.run(["open", f"obsidian://open?path={urllib.parse.quote(str(self.buffer_file))}"])
            messagebox.showinfo("Review", "Refine in Obsidian. Click OK to set as next round's context.")
        except Exception as e:
            messagebox.showerror("Error", f"Could not open Obsidian: {e}\nFalling back to default editor.")
            self._launch_editor(self.buffer_file)
            
        with open(self.buffer_file, "r") as f:
            return f.read()

    def show_status(self, message: str):
        if self.root and hasattr(self, 'status_label'):
            self.status_label.config(text=message)
            self.root.update()

    def run(self):
        """Start the GUI main loop."""
        self.root = tk.Tk()
        self.root.title("Second Voice (Recursive Mode)")
        self.root.geometry("400x350")
        
        self._build_ui()
        self.root.mainloop()

    def _build_ui(self):
        # UI Build
        self.status_label = tk.Label(self.root, text="Ready", font=("Arial", 12))
        self.status_label.pack(pady=10)
        
        # VU Meter Canvas
        self.vu_canvas = tk.Canvas(self.root, width=300, height=40, bg="black")
        self.vu_canvas.pack(pady=5)
        self.vu_bar = self.vu_canvas.create_rectangle(0, 0, 0, 40, fill="green")
        
        self.context_indicator = tk.Label(self.root, text="Context: Empty", fg="gray")
        self.context_indicator.pack()

        self.btn_rec = tk.Button(self.root, text="Start Recording (Space)", command=self.toggle, width=30)
        self.btn_rec.pack(pady=10)
        
        self.btn_sub = tk.Button(self.root, text="Process & Edit (Enter)", command=self.submit, state=tk.DISABLED)
        self.btn_sub.pack(pady=5)

        self.btn_clear = tk.Button(self.root, text="Clear Context", command=self.clear_context)
        self.btn_clear.pack(pady=5)

        self.root.bind("<space>", lambda e: self.toggle())
        self.root.bind("<Return>", lambda e: self.submit() if self.btn_sub['state'] == 'normal' else None)
        
        # Start update loop
        self._update_vu()

    def _update_vu(self):
        if self.is_recording:
            amp = self.recorder.get_amplitude()
            self.vu_canvas.coords(self.vu_bar, 0, 0, int(amp * 300), 40)
            # Color transition based on amplitude
            if amp > 0.8:
                self.vu_canvas.itemconfig(self.vu_bar, fill="red")
            elif amp > 0.5:
                self.vu_canvas.itemconfig(self.vu_bar, fill="yellow")
            else:
                self.vu_canvas.itemconfig(self.vu_bar, fill="green")
        else:
            self.vu_canvas.coords(self.vu_bar, 0, 0, 0, 40)
            
        self.root.after(50, self._update_vu)

    def clear_context(self):
        self.last_output = ""
        self.processor.clear_context()
        self.context_indicator.config(text="Context: Empty", fg="gray")

    def toggle(self):
        if not self.is_recording:
            self.is_recording = True
            self.btn_rec.config(text="Stop (Space)", fg="red")
            self.btn_sub.config(state=tk.DISABLED)
            self.start_recording()
            self.show_status("Recording...")
        else:
            self.is_recording = False
            self.btn_rec.config(text="Record Instruction / New Text", fg="black")
            self.btn_sub.config(state=tk.NORMAL)
            self.audio_file = self.recorder.stop_recording()
            self.show_status("Recording stopped. Ready to process.")

    def submit(self):
        if not hasattr(self, 'audio_file') or not self.audio_file:
            messagebox.showerror("Error", "No audio recorded")
            return

        self.show_status("⌛ Processing Iteration...")
        
        # Run processing in a separate thread to avoid freezing UI
        # But Tkinter is not thread-safe, so we need to be careful. 
        # For simplicity in this port, we'll keep it synchronous or use simple update() calls.
        
        try:
            # 1. Transcribe
            self.show_status("Transcribing...")
            text = self.processor.transcribe(self.audio_file)
            print(f"User: {text}")

            # 2. Process with LLM
            self.show_status("Thinking...")
            
            response = self.processor.process_text(text, context=self.last_output)
            
            # 3. Review
            self.last_output = self.review_output(response)
            print(self.last_output)

            # Update GUI indicator
            self.context_indicator.config(text=f"Context: {len(self.last_output)} chars", fg="blue")
            self.show_status("Ready for Next Round")

        except Exception as e:
            messagebox.showerror("Error", str(e))
            self.show_status("Error occurred")
