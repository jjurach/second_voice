# Specification: Provider-Specific Configuration Keys

## Context
Currently, the application uses generic configuration keys like `llm_model` which are ambiguous when multiple providers are supported. To improve clarity and support multiple providers simultaneously, we will move to provider-prefixed configuration keys.

## Requirements

### 1. Rename `llm_model` to `openrouter_llm_model`
-   **Old Key:** `llm_model`
-   **New Key:** `openrouter_llm_model`
-   **Default:** `openai/gpt-oss-120b:free`
-   **Behavior:** The `OpenRouter` processor should look for `openrouter_llm_model`.

### 2. Introduce `groq_stt_model`
-   **New Key:** `groq_stt_model`
-   **Default:** `whisper-large-v3`
-   **Behavior:** The `Groq` transcriber should look for `groq_stt_model` instead of the hardcoded value.

### 3. Backward Compatibility (Optional but recommended)
-   For `llm_model`, the system should check `openrouter_llm_model` first. If not found, check `llm_model`. If neither, use default.

## Impact Analysis
-   **`src/second_voice/core/processor.py`**:
    -   Update `_process_openrouter` to use `openrouter_llm_model`.
    -   Update `_transcribe_groq` to use `groq_stt_model`.
-   **`src/second_voice/core/config.py`**:
    -   Update `DEFAULT_CONFIG` to reflect these new keys if they are present there (currently they are not, but good to add).

## Deliverables
-   Updated `processor.py`.
-   Updated `config.py` with better defaults.
