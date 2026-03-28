# Spec: Amplify Sound Bar Signal in Menu Mode

## Problem Statement
During audio recording in menu mode, the VU meter (sound bar) only jumps between 0.0 and 0.1 amplitude levels, causing it to barely register visually. The bar needs to be amplified to utilize the full 10-character display range.

## Current Behavior
- Audio amplitude is multiplied by 10 to calculate bar length: `bar_len = int(amp * 10)`
- With amplitude range of 0.0-0.1, bar only shows 0-1 characters filled
- User cannot effectively see recording levels

## Desired Behavior
- Sound bar should fill more of the available 10-character display
- Signal should be amplified by a multiplier factor (e.g., 50-100x) to make use of full range
- Visual feedback should be more informative during recording

## Acceptance Criteria
- [ ] Sound bar fills more of the display during normal speech recording
- [ ] VU meter becomes more responsive and visually informative
- [ ] No changes to other recording functionality
- [ ] No changes to audio data or file output quality
