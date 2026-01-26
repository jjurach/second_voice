# Add Cline CLI Provider Implementation

## Overview
Added Cline CLI as a new Language Model (LLM) provider to the Second Voice project, extending provider flexibility and supporting CLI-based text processing.

## Key Changes
- Updated `src/second_voice/core/config.py` to include Cline CLI configuration keys
  - Added `cline_llm_model`
  - Added `cline_api_key`
- Updated `config.example.json` with Cline CLI example configuration
- Updated `docs/providers.md` to include Cline CLI provider documentation
- Modified `src/second_voice/core/processor.py` to support Cline CLI processing
  - Added `_process_cline()` method
  - Updated `process_text()` method to handle Cline CLI provider

## Configuration Details
```json
{
  "cline_llm_model": "default-model",
  "cline_api_key": null
}
```

## Implementation Notes
- Supports optional API key configuration
- Uses subprocess to invoke Cline CLI
- Implements timeout and error handling
- Allows context passing and model selection

## Verification Results
```bash
# Verify Cline CLI provider configuration
python -c "from second_voice.core.config import ConfigurationManager; config = ConfigurationManager(); print(config.get('cline_llm_model'))"
# Expected output: default-model
```

## Known Issues
- Requires the `cline` CLI tool to be installed
- Exact behavior depends on the specific Cline CLI implementation
- May require additional error handling based on specific CLI behavior

## Future Improvements
- Add more comprehensive CLI parameter support
- Implement advanced context management
- Add more robust error handling for different CLI scenarios

## Out of Scope
- Performance optimizations for the Cline CLI provider
- Extensive model backend configuration