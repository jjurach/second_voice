# Change Documentation: Fixed OpenRouter 404 and Config Key Mismatch

## Date: 2026-01-25 03:10:00

## Description
Resolved issues where the application failed to process LLM requests due to invalid model names and configuration key precedence issues.

## Changes

### Configuration
- **User Config (`settings.json`)**:
    - Renamed `llm_model` to `openrouter_llm_model` to align with the new schema.
    - Updated the model from the invalid `openai/gpt-oss-120b:free` to `google/gemini-2.0-flash-exp:free`.

### Debugging
- Added and subsequently removed debug prints in `src/second_voice/core/processor.py` to diagnose the issue.

## Verification Results
- Ran `EDITOR=cat timeout 20 python3 src/cli/run.py --mode menu --file samples/test.wav <<< 4`.
- Confirmed full end-to-end success:
    - Audio input loaded.
    - Transcription successful (Groq).
    - LLM processing successful (OpenRouter/Gemini).
    - Output displayed correctly.
