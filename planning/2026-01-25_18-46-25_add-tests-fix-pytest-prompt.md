# Spec: Add Unit Tests & Fix pytest

**Date:** 2026-01-25
**Status:** Under Review

## User Request
- Add more unit tests with focus on **critical paths only**
- Fix `pytest` (currently broken - not installed)
- Use mocked external services by default
- Optional integration testing with `-P integration` flag

## Current State
- 8 test cases total (~15-20% coverage)
- Using unittest instead of pytest
- pytest not installed
- No pytest configuration files
- 85% of codebase untested

## Critical Paths to Test (User Priority)
1. Config loading and environment overrides
2. Audio processing (Groq, local Whisper)
3. LLM processing (Ollama, OpenRouter)
4. Audio recording basics
5. Mode initialization and switching

## Coverage Target
- **Config module:** Full coverage of loading/parsing
- **Processor module:** Core transcription and LLM paths
- **Recorder module:** Start/stop, device handling
- **Modes:** Initialization and selection logic
- **CLI:** Basic argument parsing and entry points

## Acceptance Criteria
- [ ] pytest is installed and configured
- [ ] All critical path functions have unit tests
- [ ] All external API calls are mocked by default
- [ ] Tests can run offline: `pytest` or `pytest -m "not integration"`
- [ ] Integration tests runnable with: `pytest -P integration`
- [ ] All tests pass
- [ ] Coverage report shows 60%+ coverage on critical modules
