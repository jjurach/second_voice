# GUI Design Specification

## Visual Requirements

The GUI provides real-time visual feedback during audio recording using a dynamic VU (Volume Unit) meter that responds to microphone input amplitude.

## Layout

### ASCII Layout: Recording State

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

## Visual Components

### Core Pulse (Center Circle)

The central visual element that responds to audio amplitude:

- **Implementation:** `Canvas.create_oval`
- **Quiet State:** Small diameter (~20px), Dark Maroon (`#440000`)
- **Loud State:** Large diameter (up to ~70px), Bright Neon Red (`#FF0000`)
- **Animation:** Radius and color saturation both scale with RMS amplitude

### Lateral Level Lines

Horizontal bars extending from both sides of the core pulse:

- **Implementation:** Series of rectangles in a loop
- **Segments:** 10 bars per side
- **Behavior:** Number of visible/bright segments = `int(amplitude * max_segments)`
- **Taper:** Bars further from center are progressively smaller (creates professional hardware aesthetic)
- **Colors:**
  - Active segments: Match core pulse color (dark red → bright red)
  - Inactive segments: Dark gray (`#222222`)

### Typography

- **Timer:** 32pt Courier Bold, Red during recording
- **Status Label:** 14pt Arial, Standard font color
- **Path Footer:** 10pt Consolas, Bottom-left
- **Context Info:** 10pt Standard, Grey, Bottom-right

## Implementation Details

### VU Meter Audio Analysis

The VU meter is driven by real-time RMS (Root Mean Square) amplitude calculation:

```python
def _calculate_rms(audio_data):
    """Calculate RMS amplitude from raw bytes, returns 0.0-1.0"""
    samples = np.frombuffer(audio_data, dtype=np.int16).astype(np.float32)
    rms = np.sqrt(np.mean(samples**2))
    normalized = min(1.0, rms / 3000.0)  # Normalize to 0-1 range
    return normalized
```

### Threading Architecture

- **Audio Thread:** PyAudio callback runs in separate thread, calculates RMS
- **Queue:** Thread-safe queue passes amplitude values to GUI thread
- **GUI Thread:** Tkinter main loop pulls from queue every 30ms (≈33fps)
- **Pattern:** Pull-based to prevent GUI blocking

### Visual Update Loop

```python
def refresh_loop(self):
    try:
        amplitude = self.recorder.volume_queue.get_nowait()
        self.viz.update_amplitude(amplitude)
    except queue.Empty:
        pass

    if self.is_recording:
        self.root.after(30, self.refresh_loop)  # 30ms = ~33fps
    else:
        self.viz.reset()
```

### Color Interpolation

The pulse color interpolates from dark to bright red based on amplitude:

```python
red_val = int(68 + (amplitude * 187))  # Range: 68 (#44) to 255 (#FF)
color = f'#{red_val:02x}0000'
```

### Performance Optimizations

1. **Object Reuse:** Use `canvas.coords()` to move existing shapes rather than delete/recreate
2. **Amplitude Scaling:** Logarithmic-ish scaling (`rms / 3000.0`) makes UI reactive to normal speech volumes
3. **Frame Drop Tolerance:** Non-blocking queue ensures audio capture continues even if GUI stutters
4. **Intel MacBook Friendly:** Separate threads keep audio stable on thermally-constrained hardware

## Keyboard Shortcuts

- **Space:** Toggle recording on/off
- **Enter:** Submit and edit (when recording stopped)

## States

### Standby
- Core: Small, dark maroon
- Level bars: Dark gray
- Status: "Ready"

### Recording
- Core: Pulsing with audio amplitude
- Level bars: Dancing with audio levels
- Status: "● RECORDING"
- Timer: Running

### Stopped (Ready to Submit)
- Core: Static, last size
- Level bars: Static
- Status: "Ready for Next Round"
- Submit button: Enabled

### Processing
- Status: "⌛ Processing AI Loop..."
- All controls: Disabled

## Obsidian Integration

When processing completes:
1. Output written to `.review_buffer.md` in vault
2. Obsidian opened via URI: `obsidian://open?path=<url-encoded-path>`
3. Modal dialog: "Refine in Obsidian. Click OK to set as next round's context."
4. On OK: Read buffer back into `last_output` memory
5. Archive buffer to `voice_note_<timestamp>.md`

---
Last Updated: 2026-01-28
