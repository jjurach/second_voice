# Specification: CLI Options for Testing & File Input

## Context
The Second Voice application currently requires interactive recording and cleans up temporary files automatically. To facilitate "agentic testing" (automated testing and debugging), we need to allow:
1.  Preserving temporary files (`.wav` recordings, etc.) to inspect intermediate outputs.
2.  Injecting an existing audio file (`.wav`) as input to bypass the microphone recording step, allowing for reproducible test cases.

## Requirements

### 1. New CLI Option: `--keep-files`
-   **Flag:** `--keep-files`
-   **Behavior:** When set, the application **must not** delete temporary files (audio recordings, context buffers) upon exit or after processing.
-   **Scope:** Affects `run.py` cleanup and individual mode cleanup routines (TUI, Menu, etc.).

### 2. New CLI Option: `--file FILE`
-   **Flag:** `--file <path_to_wav_file>`
-   **Behavior:**
    -   When provided, the application should use this file as the *initial* input audio.
    -   It should bypass the `recorder.start_recording()` step for the first turn.
    -   It should proceed to transcribe the file, process it with the LLM, and display the output.
    -   After processing the input file, the application should either exit (if in a non-interactive context) or fall back to the normal interactive loop (recording from mic). For this iteration, falling back to the loop (or just processing one turn) is acceptable, but the primary goal is to process the injected file.
    -   **Constraint:** The application must not delete the user-provided input file during cleanup.

### 3. Documentation
-   Update `README.md` to include:
    -   Testing instructions.
    -   Usage of `scripts/demo_second_voice.py`.
    -   Usage of new flags `--keep-files` and `--file`.

## Technical Impact
-   **`src/cli/run.py`**: Add `argparse` arguments, update `ConfigurationManager`.
-   **`src/second_voice/modes/`**: Update `run()` methods in `tui_mode.py` and `menu_mode.py` (and potentially `gui_mode.py` if feasible) to consume the `input_file` from config.
-   **`src/second_voice/modes/base.py`**: Update `cleanup()` to respect `keep_files`.

## Acceptance Criteria
-   `python src/cli/run.py --file samples/test.wav` processes `test.wav` and outputs the result.
-   `python src/cli/run.py --keep-files` leaves `tmp/` files intact after execution.
-   `README.md` contains a clear "Testing" section.
