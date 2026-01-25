# Project Plan: Provider-Specific Configuration

**Status:** ✅ COMPLETE (Already implemented in Mode Selection Architecture)

## Goal
Refactor configuration to use provider-specific keys (`openrouter_llm_model`, `groq_stt_model`) for better clarity and flexibility.

## Steps

1.  **Update `ConfigurationManager` (`src/second_voice/core/config.py`)**
    *   Update `DEFAULT_CONFIG` to include:
        *   `openrouter_llm_model`: `openai/gpt-oss-120b:free`
        *   `groq_stt_model`: `whisper-large-v3`
    *   This ensures these keys are always available in the config object.

2.  **Update `AIProcessor` (`src/second_voice/core/processor.py`)**
    *   **Method `_process_openrouter`**: Change `config.get('llm_model', ...)` to `config.get('openrouter_llm_model', ...)`.
        *   *Self-Correction*: To support the transition, I will make it look for `openrouter_llm_model` first, and fallback to `llm_model` if the specific one isn't set (or just rely on the default we added to `config.py`).
        *   *Decision*: Use `config.get('openrouter_llm_model', config.get('llm_model', 'openai/gpt-oss-120b:free'))`.
    *   **Method `_transcribe_groq`**: Change hardcoded `'model': 'whisper-large-v3'` to `config.get('groq_stt_model', 'whisper-large-v3')`.

3.  **Verification**
    *   Verify code compiles/runs.
    *   (Optional) Check if `settings.json` needs manual update guidance for the user.

## Deliverables
-   Modified `src/second_voice/core/config.py`
-   Modified `src/second_voice/core/processor.py`
