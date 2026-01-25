# Implementation Reference

This document contains complete code templates and implementation patterns extracted from the original design specifications. These serve as reference implementations for the refactoring work.

---

## Audio Recorder Module

Complete reference implementation for `engine/recorder.py`:

```python
import pyaudio
import numpy as np
import threading
import queue

class AudioRecorder:
    def __init__(self, rate=16000, chunk=1024):
        self.rate = rate
        self.chunk = chunk
        self.p = pyaudio.PyAudio()
        self.frames = []
        self.is_recording = False
        self.stream = None

        # Thread-safe queue to pass volume levels to the GUI
        self.volume_queue = queue.Queue(maxsize=1)

    def _calculate_rms(self, audio_data):
        """
        Calculates Root Mean Square (RMS) amplitude from raw bytes.
        Returns a float between 0 and 1 (normalized).
        """
        # Convert buffer to 16-bit integers
        samples = np.frombuffer(audio_data, dtype=np.int16).astype(np.float32)

        if len(samples) == 0:
            return 0.0

        # RMS Formula: sqrt(sum(s^2) / n)
        rms = np.sqrt(np.mean(samples**2))

        # Normalize based on 16-bit max (32767)
        # We use a log-ish scaling or a multiplier to make the UI reactive
        normalized = min(1.0, rms / 3000.0)
        return normalized

    def _stream_callback(self, in_data, frame_count, time_info, status):
        """PyAudio callback for non-blocking recording."""
        if self.is_recording:
            self.frames.append(in_data)

            # Calculate volume for the GUI
            volume = self._calculate_rms(in_data)

            # Update the queue (non-blocking, drop if GUI is slow)
            try:
                if not self.volume_queue.full():
                    self.volume_queue.put_nowait(volume)
            except queue.Full:
                pass

        return (in_data, pyaudio.paContinue)

    def start(self):
        self.is_recording = True
        self.frames = []
        self.stream = self.p.open(
            format=pyaudio.paInt16,
            channels=1,
            rate=self.rate,
            input=True,
            frames_per_buffer=self.chunk,
            stream_callback=self._stream_callback
        )
        self.stream.start_stream()

    def stop(self):
        self.is_recording = False
        if self.stream:
            self.stream.stop_stream()
            self.stream.close()
        return self.frames
```

### Implementation Notes

- **Decoupling:** Keep `pyaudio` logic strictly in `recorder.py`. The GUI should never know how the audio is sampled; it should only care about the normalized `0.0` to `1.0` float coming out of the queue.
- **Threading:** PyAudio's `stream_callback` runs in a separate thread by default. This is perfect for Intel MacBook because it keeps the audio capture stable even if the Tkinter GUI thread stutters momentarily.

---

## VU Visualizer Component

Complete reference implementation for `ui/components.py`:

```python
import tkinter as tk

class VUVisualizer(tk.Canvas):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, highlightthickness=0, **kwargs)
        self.config(bg="#1e1e1e") # Dark background for high-contrast red

        # Geometry constants
        self.center_x = 200
        self.center_y = 50
        self.base_radius = 15
        self.max_extra_radius = 35
        self.num_bars = 10
        self.bar_spacing = 8
        self.bar_width = 12

        # Create Core Circle (The "Throbber")
        self.core = self.create_oval(0, 0, 0, 0, fill="#440000", outline="#660000", width=2)

        # Create Lateral Bars (Level Lines)
        self.left_bars = []
        self.right_bars = []
        for i in range(self.num_bars):
            # Left side bars (extending left)
            l_bar = self.create_rectangle(0, 0, 0, 0, fill="#330000", outline="")
            self.left_bars.append(l_bar)

            # Right side bars (extending right)
            r_bar = self.create_rectangle(0, 0, 0, 0, fill="#330000", outline="")
            self.right_bars.append(r_bar)

    def update_amplitude(self, amplitude):
        """
        Updates the UI based on 0.0 - 1.0 amplitude.
        """
        # 1. Update Core Pulse
        # Increase radius and brighten color based on volume
        current_r = self.base_radius + (amplitude * self.max_extra_radius)
        self.coords(self.core,
                    self.center_x - current_r, self.center_y - current_r,
                    self.center_x + current_r, self.center_y + current_r)

        # Map amplitude to a hex color from Dark Red to Neon Red
        red_val = int(68 + (amplitude * 187)) # Range ~68 to 255
        color = f'#{red_val:02x}0000'
        self.itemconfig(self.core, fill=color)

        # 2. Update Lateral Bars
        active_bars = int(amplitude * self.num_bars * 1.5) # Over-scale slightly for "sensitivity"

        for i in range(self.num_bars):
            # Calculate bar heights - further out = smaller/tapered
            taper = (self.num_bars - i) / self.num_bars
            h = (10 + (amplitude * 30)) * taper

            # Left Bar positions
            lx0 = self.center_x - (self.base_radius + 15) - (i * (self.bar_width + self.bar_spacing))
            self.coords(self.left_bars[i], lx0 - self.bar_width, self.center_y - h, lx0, self.center_y + h)

            # Right Bar positions
            rx0 = self.center_x + (self.base_radius + 15) + (i * (self.bar_width + self.bar_spacing))
            self.coords(self.right_bars[i], rx0, self.center_y - h, rx0 + self.bar_width, self.center_y + h)

            # Color logic for bars
            bar_color = color if i < active_bars else "#222222"
            self.itemconfig(self.left_bars[i], fill=bar_color)
            self.itemconfig(self.right_bars[i], fill=bar_color)

    def reset(self):
        """Return to standby state."""
        self.update_amplitude(0)
        self.itemconfig(self.core, fill="#440000")
```

### Integration Pattern

In your `main_window.py`, initialize this component and create a "tick" that updates it:

```python
# Inside MainWindow.__init__
self.viz = VUVisualizer(self.root, width=400, height=100)
self.viz.pack()

def refresh_loop(self):
    try:
        # Pull the RMS value we calculated in recorder.py
        amp = self.recorder.volume_queue.get_nowait()
        self.viz.update_amplitude(amp)
    except queue.Empty:
        pass

    # 30ms refresh rate is smooth for the eye (approx 33fps)
    if self.is_recording:
        self.root.after(30, self.refresh_loop)
    else:
        self.viz.reset()
```

### Key Implementation Details

- **Coordinate Math:** The lateral bars taper (`taper`) as they move away from the center, which gives it a "professional hardware" look.
- **Color Interpolation:** The `red_val` logic ensures the core doesn't just grow—it actually "glows" brighter as you get louder.
- **Performance:** We use `self.coords()` to move existing objects rather than deleting and recreating them. This is essential for the Intel MacBook to keep the UI fluid while PyAudio is busy recording.

---

## Callback Mapping & Integration Table

| Action | Callback / Method | Pattern |
| --- | --- | --- |
| **Microphone Input** | `recorder._stream_callback` | Calculates RMS amplitude of the current 1024-frame buffer. |
| **UI Update** | `ui._refresh_meter` | Runs every 30ms via `root.after()`. Pulls RMS from queue and resizes Canvas objects. |
| **Stop Recording** | `gui.on_toggle_record` | Stops the pulse loop; sets Core to static Grey; enables Submit. |
| **Submit** | `engine.submit_to_gpu` | Disables UI; executes `POST`; launches Obsidian via URI. |

---

## Original Working Script Reference

The current working implementation from `src/cli/second_voice.py` serves as the baseline. Key sections:

### Configuration Loading Pattern

```python
CONFIG_PATH = Path.home() / ".config/second_voice/settings.json"

def load_config(self):
    if not CONFIG_PATH.exists():
        CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
        with open(CONFIG_PATH, 'w') as f:
            json.dump({
                "whisper_url": "http://localhost:8000/v1/audio/transcriptions",
                "ollama_url": "http://localhost:11434/api/generate",
                "ollama_model": "llama-pro",
                "whisper_model": "small.en"
            }, f, indent=4)
    return json.load(open(CONFIG_PATH))
```

### Recording Toggle Pattern

```python
def toggle(self):
    if not self.is_recording:
        self.is_recording = True
        self.frames = []
        self.btn_rec.config(text="Stop (Space)", fg="red")
        self.btn_sub.config(state=tk.DISABLED)
        self.stream = self.p.open(
            format=pyaudio.paInt16,
            channels=1,
            rate=16000,
            input=True,
            frames_per_buffer=1024
        )
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
```

### Submit and Process Pattern

```python
def submit(self):
    temp_wav = "/tmp/sv_audio.wav"
    with wave.open(temp_wav, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(self.p.get_sample_size(pyaudio.paInt16))
        wf.setframerate(16000)
        wf.writeframes(b"".join(self.frames))

    self.status.config(text="⌛ Processing Iteration...")
    self.root.update()

    try:
        # 1. Whisper
        with open(temp_wav, 'rb') as f:
            r = requests.post(
                self.config['whisper_url'],
                files={'file': f},
                data={'model': self.config['whisper_model']}
            )
        new_text = r.json()['text']

        # 2. Iterative Prompt Logic
        combined_prompt = f"ORIGINAL TEXT: {self.last_output}\n\nNEW INSTRUCTION: {new_text}"

        system_rules = (
            "If the NEW INSTRUCTION mentions the ORIGINAL TEXT (using 'it', 'this', "
            "'that', 'bullets', 'shorter', etc.), transform the ORIGINAL TEXT accordingly. "
            "If it does not, ignore the ORIGINAL TEXT and process a fresh answer."
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
        with open(BUFFER_FILE, "w") as f:
            f.write(processed_text)
        subprocess.run([
            "open",
            f"obsidian://open?path={urllib.parse.quote(str(BUFFER_FILE))}"
        ])

        messagebox.showinfo(
            "Review",
            "Refine in Obsidian. Click OK to set as next round's context."
        )

        with open(BUFFER_FILE, "r") as f:
            self.last_output = f.read()
            print(self.last_output)  # Output to STDOUT for CLI integration

        # Update GUI indicator
        self.context_indicator.config(
            text=f"Context: {len(self.last_output)} chars",
            fg="blue"
        )
        self.status.config(text="Ready for Next Round")

    except Exception as e:
        messagebox.showerror("Error", str(e))
```

---

## Pre-Flight Checklist

Before running the application, verify:

1. **SSH Tunnel:** Confirm ports 8000 and 11434 are mapped to `192.168.0.157`
   ```bash
   lsof -i :8000  # Should show ssh as listener
   ```

2. **Obsidian:** Ensure `VoiceInbox` exists and Syncthing ignore patterns are set for `.review_buffer.md`
   ```text
   .review_buffer.md
   *.sync-conflict-*
   ```

3. **Python:** Run `python3 -m tkinter` to verify GUI availability

4. **Audio:** Verify MacBook "Input Device" is set to the correct microphone

5. **GPU Status:** On Ubuntu server, verify GPU usage
   ```bash
   nvidia-smi  # Should show ~2.5GB VRAM used by whisper and ollama
   ```

---

## Workflows

### Workflow A: The "Voice Inbox" (Standard Mode)

- **Goal:** Capture long-form thoughts or "stutter talk" into your permanent vault.
- **Process:** Record → Transcribe → Professional Cleanup → Edit in Obsidian → Save as timestamped file in `VoiceInbox`.

### Workflow B: The "Ctrl-G" CLI (Modal Mode)

- **Goal:** Use voice to input commands or text directly into a terminal or Claude session.
- **Process:** Invoke script → Record instruction → Edit/Refine in Obsidian → Output to `stdout` upon closing.

---

## Error Handling Patterns

### Connection Errors
```python
try:
    response = requests.post(url, ...)
except requests.exceptions.ConnectionError:
    messagebox.showerror("Connection Error", f"Cannot connect to {url}")
except requests.exceptions.Timeout:
    messagebox.showerror("Timeout", f"Request timed out after {timeout}s")
```

### GPU Memory Management

Using `small.en` model ensures it stays resident in RTX 2080's 8GB VRAM alongside `llama-pro` (~4.9GB) without causing OOM errors.

### File System Errors
```python
try:
    self.vault_path.mkdir(parents=True, exist_ok=True)
    with open(buffer_file, "w") as f:
        f.write(content)
except IOError as e:
    messagebox.showerror("File Error", f"Cannot write to vault: {e}")
```

---

## Testing Patterns

### Mock PyAudio for Testing

```python
import pytest
from unittest.mock import Mock, patch

def test_recorder_initialization():
    with patch('pyaudio.PyAudio'):
        recorder = AudioRecorder()
        assert recorder.rate == 16000
        assert recorder.chunk == 1024

def test_rms_calculation():
    recorder = AudioRecorder()
    # Create sample audio data (silence)
    silence = b'\x00' * 2048
    rms = recorder._calculate_rms(silence)
    assert rms == 0.0
```

### Mock API Requests for Testing

```python
import pytest
from unittest.mock import Mock, patch
import requests

def test_transcription_success():
    with patch('requests.post') as mock_post:
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {'text': 'test transcription'}

        processor = AudioProcessor(config)
        result = processor.transcribe(audio_frames)

        assert result == 'test transcription'
        mock_post.assert_called_once()
```

---

## Reference: Demo Script Pattern

The enhanced demo script should follow this pattern:

```python
def main():
    import argparse
    parser = argparse.ArgumentParser(description="Test Whisper transcription")
    parser.add_argument("--audio", default="samples/test.wav")
    parser.add_argument("--verbose", action="store_true")
    parser.add_argument("--debug", action="store_true")
    args = parser.parse_args()

    if args.verbose:
        print(f"Using audio file: {args.audio}")
        print(f"Target URL: {url}")

    start_time = time.time()

    # ... perform transcription ...

    duration = time.time() - start_time

    if args.verbose:
        print(f"Duration: {duration:.2f}s")
        print(f"Response: {result}")
```
