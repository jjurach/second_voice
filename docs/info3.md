This refined specification integrates a **dynamic VU (Volume Unit) meter** into the "throbbing red light" logic. Instead of a simple timed pulse, the GUI will now react to the **RMS (Root Mean Square)** amplitude of the incoming audio stream from your MacBook's microphone, providing real-time visual confirmation that your voice is being captured.

---

## 1. Network & Backend Bridge (Port 9090)

All AI traffic is routed through the 9090/11434 tunnel to your RTX 2080.

* **SSH Tunnel:** `ssh -N -L 9090:localhost:9090 -L 11434:localhost:11434 192.168.0.157`
* **Target Engine:** `faster-whisper-server` (Model: `small.en`)

---

## 2. Dynamic UI & Visual Specifications

The GUI transitions from a static "Standby" state to an "Active" state where the center light and lateral "level lines" expand and contract based on decibel input.

### ASCII Layout: Dynamic Recording State

```text
+------------------------------------------+
|           [  ● RECORDING  ]              | 
+------------------------------------------+
|                                          |
|                03:42                     | 
|                                          |
+------------------------------------------+
|  <---[||||]      ( ● )      [||||]--->   | <-- Dynamic VU Meter
|  (Left Level)   (Core)    (Right Level)  |
+------------------------------------------+
|                                          |
|    [ STOP (Space) ]    [ CLEAR MEM ]     | 
|                                          |
|    [        SUBMIT & EDIT        ]       | 
|                                          |
+------------------------------------------+
| Context: 1240 chars                      | 
| File: /tmp/sv/.review_buffer.md          | 
+------------------------------------------+

```

### Visual Logic & Implementation Patterns

* **The Core Pulse:** A central circle (`Canvas.create_oval`) that changes radius and color saturation based on the current volume.
* **Quiet:** Small diameter, Dark Maroon (`#440000`).
* **Loud:** Large diameter, Bright Neon Red (`#FF0000`).


* **Lateral Level Lines:** Horizontal bars extending from the center.
* **Implementation:** A series of rectangles in a `for` loop. The number of visible segments is calculated by `int(amplitude * max_segments)`.


* **Font Specs:**
* **Timer:** 32pt Courier Bold (Red during recording).
* **Path Footer:** 10pt Consolas (Bottom-left).
* **Context Info:** 10pt Grey (Bottom-right).



---

## 3. Python Module & Directory Structure

To support real-time audio analysis without lagging the UI, we decouple the "Analyzer" from the "GUI".

```text
second_voice/
├── __init__.py
├── cli.py                # CLI Entry: handles `second_voice -m tkinter`
├── config.py             # Loads settings.json from ~/.config/second_voice/
├── engine/
│   ├── __init__.py
│   ├── recorder.py       # PyAudio stream + RMS amplitude calculation
│   └── processor.py      # Requests to 9090 (Whisper) & 11434 (Ollama)
└── ui/
    ├── __init__.py
    ├── main_window.py    # Primary Tkinter Class
    └── components.py     # Custom Canvas classes for "Pulse" & "Level Lines"

```

---

## 4. Callback Mapping & Volume Integration

The `recorder.py` module uses a thread-safe Queue to pass volume levels to the `main_window.py`.

| Action | Callback / Method | Pattern |
| --- | --- | --- |
| **Microphone Input** | `recorder._stream_callback` | Calculates RMS amplitude of the current 1024-frame buffer. |
| **UI Update** | `ui._refresh_meter` | Runs every 30ms via `root.after()`. Pulls RMS from queue and resizes Canvas objects. |
| **Stop Recording** | `gui.on_toggle_record` | Stops the pulse loop; sets Core to static Grey; enables Submit. |
| **Submit** | `engine.submit_to_gpu` | Disables UI; executes `POST`; launches Obsidian via URI. |

---

## 5. System Prompts & Iterative Logic

### A. Initial "Clean & Form" Prompt

Sent to `llama-pro` for the first pass or if context is cleared.

> "Clean up the following STT transcript. Remove stutters, filler words, and fix grammar. Format as professional Markdown with logical headers."

### B. "Retry/Redo" Recursive Prompt

Sent to `llama-pro` when `self.last_output` is populated.

> "ORIGINAL_TEXT: {last_output} | NEW_INSTRUCTION: {new_stt}.
> **Logic:** If NEW_INSTRUCTION references the ORIGINAL_TEXT (e.g. 'it', 'shorter', 'bullets'), modify ORIGINAL_TEXT. If not, treat as a fresh request and ignore ORIGINAL_TEXT. Output only the final result."

---

## 6. Pre-Flight Checklist

1. **SSH Tunnel:** Confirm port 9090 and 11434 are mapped to `192.168.0.157`.
2. **Obsidian:** Ensure `VoiceInbox` exists and Syncthing ignore patterns are set for `.review_buffer.md`.
3. **Python:** Run `python3 -m tkinter` to verify GUI availability.
4. **Audio:** Verify MacBook "Input Device" is set to the correct microphone.
