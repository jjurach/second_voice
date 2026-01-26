# Project Plan: Amplify Sound Bar Signal in Menu Mode

## Objective
Improve the visual feedback of the VU meter (sound bar) during audio recording in menu mode by amplifying the amplitude signal to fill more of the available 10-character display.

## Status: Completed
## Completion Date: 2026-01-25
## Verification: Implementation tested, all mode-related tests pass (113/122 overall)

## Scope
1. Analyze current amplitude handling in menu mode recording
2. Adjust amplitude multiplier to increase visual responsiveness
3. Verify no impact on audio recording quality or functionality
4. Test with actual audio input

## Detailed Tasks

### Task 1: Analyze Current Implementation
**File:** `src/second_voice/modes/menu_mode.py`
**Current Code (lines 44-50):**
```python
while True:
    amp = self.recorder.get_amplitude()
    bar_len = int(amp * 10)
    vu_bar = "#" * bar_len + "-" * (10 - bar_len)
    sys.stdout.write(f"\rLevel: [{vu_bar}] ")
    sys.stdout.flush()
    time.sleep(0.1)
```

**Analysis:**
- Amplitude range appears to be 0.0-0.1 (normalized)
- Current multiplier: 10 (produces 0-1 character fill)
- Need to increase multiplier to 50-100 for better visual response

### Task 2: Update Amplitude Multiplier
**File:** `src/second_voice/modes/menu_mode.py`
**Change:**
- Modify line 46 to use a larger multiplier (e.g., 50x)
- Change from: `bar_len = int(amp * 10)`
- Change to: `bar_len = int(amp * 50)`
- Ensure the result doesn't exceed 10 characters (add min/max bounds)

**Implementation detail:**
```python
bar_len = min(int(amp * 50), 10)
```

### Task 3: Verify No Side Effects
- Confirm this only affects display, not audio data
- Verify recorder.get_amplitude() returns normalized values (0.0-1.0 range)
- Check that no other code depends on the VU meter calculation

### Task 4: Manual Testing
**Test Case 1: Silence**
- Record with no audio input
- Bar should show minimal or no fill

**Test Case 2: Normal Speech**
- Record normal speaking voice
- Bar should fill 30-80% of display
- Should be responsive to volume changes

**Test Case 3: Loud Audio**
- Record loud audio/noise
- Bar should fill toward full 10 characters
- Should not overflow (handled by min() clamping)

## Validation Criteria
- [ ] Sound bar fills noticeably more during normal speech recording
- [ ] Bar is responsive to audio level changes
- [ ] No visual artifacts or display issues
- [ ] Audio recording quality is unchanged
- [ ] Menu mode functions continue to work correctly

## Potential Risks
- None identified; this is purely a display change with no impact on audio processing

## Out of Scope
- Changes to other modes (TUI, GUI)
- Changes to audio processing or quality
- Changes to amplitude calculation in recorder module

## Dependencies
- None; isolated change to menu mode display logic

## Timeline
1. Implement the change in menu_mode.py
2. Manual testing with audio input
3. Verification that all existing functionality works

## Next Steps
1. Get approval for this project plan
2. Begin implementation
