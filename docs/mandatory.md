# Second Voice: Project-Specific Mandatory Instructions

This file contains mandatory instructions specific to the Second Voice project.

## Project Overview

Second Voice is a voice-to-text processing tool with AI integration. It processes audio recordings, transcribes them with optional AI enhancement, and supports multiple AI provider backends.

## Project Structure

**Key directories:**
- `src/second_voice/` - Main source code
  - `core/` - Configuration, modes, and core functionality
  - `providers/` - AI provider integrations
  - `cli/` - Command-line interface
- `tests/` - Unit tests
- `docs/` - Documentation
- `dev_notes/` - Development logs and planning

## Key Documentation References

**Understanding the codebase:**
- `README.md` - Project overview and quick start
- `docs/architecture.md` - System design and components
- `docs/implementation-reference.md` - Implementation patterns and conventions
- `docs/workflows.md` - Development workflows and processes
- `config.example.json` - Configuration schema (source of truth for config keys)

**System prompts framework:**
- `docs/system-prompts/` - Agent kernel and workflow definitions
- See [AGENTS.md](../AGENTS.md) for workflow details.

## Development Guidelines

### Language & Dependencies
- **Python version:** 3.8+
- **Dependency management:** Update BOTH `requirements.txt` AND `pyproject.toml`
- **Imports:** All new imports must be in requirements.txt before task is "Done"

### Configuration
- **Never hardcode secrets** - Use `config.json` or environment variables
- **Configuration schema:** `config.example.json` is the source of truth
- **Adding new config keys:** Update `config.example.json` with safe defaults
- **Reading config:** See `src/second_voice/core/config.py`

### Code Style
- Follow existing code patterns in the codebase
- New code should look like old code
- Type hints on function signatures
- Docstrings follow project conventions

### Testing
- **Framework:** pytest (use mocked external services)
- **Target coverage:** 60%+ on critical paths
- **Running tests:** `pytest tests/ -v`
- **All external APIs must be mocked** - Tests must run offline

## Prohibited Actions

**Do NOT:**
- ❌ Edit files in `docs/system-prompts/` unless explicitly instructed (they're auto-generated)
- ❌ Refactor code unless it's part of the stated task
- ❌ Add features beyond what's requested
- ❌ Use `/tmp` for temporary files (use current directory with `tmp-*` pattern)
- ❌ Commit secrets or hardcoded credentials
- ❌ Modify tests just to make them pass (fix the code instead)
- ❌ Update git config or use force push

## When You're Uncertain

**STOP immediately and ask the user rather than:**
- Making architectural changes
- Adding new dependencies
- Breaking existing APIs
- Touching security-sensitive code
- Refactoring beyond the task scope

**Good question:** "I'm uncertain about how X should work - should I approach it this way?"
**Bad action:** Guessing and hoping it works

## Definition of Done Quick Reference

Every task is "Done" only when:
✅ Code follows project patterns
✅ New imports in requirements.txt & pyproject.toml
✅ Tests pass: `pytest tests/ -v`
✅ Configuration changes in config.example.json
✅ `dev_notes/changes/` entry created with verification results
✅ Related project plan marked as `Status: Completed`

See `docs/definition-of-done.md` for complete checklist.

## Quick Commands

```bash
# Run tests
pytest tests/ -v

# Check code coverage
pytest --cov=src tests/

# View example config
cat config.example.json
```

---

**Remember:** When in doubt, read the mandatory files first. They exist for a reason.

---
Last Updated: 2026-01-28
