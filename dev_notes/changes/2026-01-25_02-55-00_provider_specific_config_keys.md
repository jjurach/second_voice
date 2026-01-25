# Change Documentation: Provider-Specific Configuration Keys

## Date: 2026-01-25 02:55:00

## Description
Refactored the configuration system to use provider-prefixed keys for model selection. This improves clarity and prevents ambiguity as more providers are added.

## Changes

### Configuration
- **`src/second_voice/core/config.py`**:
    - Added `openrouter_llm_model` (default: `openai/gpt-oss-120b:free`) to `DEFAULT_CONFIG`.
    - Added `groq_stt_model` (default: `whisper-large-v3`) to `DEFAULT_CONFIG`.

### Processing
- **`src/second_voice/core/processor.py`**:
    - Updated `_transcribe_groq` to use the `groq_stt_model` configuration key instead of a hardcoded value.
    - Updated `_process_openrouter` to use the `openrouter_llm_model` configuration key, with a fallback to the legacy `llm_model` key.

## Verification Results
- Ran `python3 src/cli/run.py --mode menu --file samples/test.wav`.
- Confirmed transcription still works (using `groq_stt_model` default).
- Verified that configuration precedence works correctly.
