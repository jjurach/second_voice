# Change: Align System Prompts with Project Standards

**Date:** 2026-01-26
**Description:** Standardized the Agent Kernel system prompts to explicitly use `dev_notes/` directory structure, removing generic placeholders. Synced `AGENTS.md` to match these updated templates, resolving "locally modified" warnings from `bootstrap.py`.

## Changes

1.  **docs/system-prompts/workflows/core.md**:
    - Replaced `[PLANNING_DIR]` placeholders with `dev_notes/`.
    - Standardized subdirectories to `dev_notes/specs/`, `dev_notes/project_plans/`, and `dev_notes/changes/`.

2.  **docs/system-prompts/principles/definition-of-done.md**:
    - Replaced generic "your change documentation" references with specific `dev_notes/changes/` paths.
    - Updated project plan references to `dev_notes/project_plans/`.

3.  **docs/system-prompts/languages/python/definition-of-done.md**:
    - Updated temporary script documentation to reference `dev_notes/changes/`.

4.  **AGENTS.md**:
    - Force-synced with the updated templates using `bootstrap.py`.

## Verification

- **Bootstrap Check:** Ran `python3 docs/system-prompts/bootstrap.py`.
    - Result: "No changes needed." (Confirmed `AGENTS.md` is in sync).
- **Docscan:** Ran `python3 docs/system-prompts/docscan.py`.
    - Result: No new violations introduced.

## Rationale

This project serves as a reference implementation for the Logs-First workflow. By standardizing the system prompts to use the recommended `dev_notes` structure, we ensure `AGENTS.md` remains compliant with the source templates while providing specific, actionable instructions for agents.
