# Change Documentation: Added --keep-files and --file CLI Options

## Date: 2026-01-25 02:20:00

## Description
Added support for preserving temporary files and injecting audio files directly via CLI to facilitate automated testing and debugging.

## Changes

### CLI & Configuration
- **`src/cli/run.py`**:
    - Added `--keep-files` and `--file FILE` arguments to the argument parser.
    - Updated `ConfigurationManager` to store these values.
    - Modified global cleanup logic to respect the `keep_files` flag.

### Core Modes
- **`src/second_voice/modes/base.py`**:
    - Updated `cleanup()` method to skip file deletion if `keep_files` is set in the configuration.
- **`src/second_voice/modes/tui_mode.py`**:
    - Modified the `run()` loop to check for `input_file` on startup.
    - If present, the application processes the file immediately without triggering the microphone.
    - Added protection to ensure the user's input file is never deleted during per-loop cleanup.
- **`src/second_voice/modes/menu_mode.py`**:
    - Added a startup check for `input_file`.
    - If found, it automatically transcribes and processes the file before entering the interactive menu.

### Documentation
- **`README.md`**:
    - Updated the "Command Line Options" section with the new flags.
    - Added a "Testing" section with examples on how to use the `--file` and `--keep-files` flags for debugging and automation.

## Verification Results
- Ran `EDITOR=cat python3 src/cli/run.py --mode menu --file samples/test.wav --keep-files`.
- Confirmed "Processing input file" message appeared.
- Confirmed "Keeping temporary files" messages appeared at exit.
- Verified that the main menu was still accessible after file processing.
