# Change: Additional Formatting Fixes

**Date:** 2026-01-26
**Description:** Addressed remaining plain text reference formatting issues in `docs/system-prompts/tools/README.md` to further clean up the document integrity scan output.

## Changes

1.  **docs/system-prompts/tools/README.md**:
    - Replaced plain text reference "AGENTS.md" with backticks.
    - Replaced plain text references "AGENTS.md", "CLAUDE.md", "GEMINI.md", "AIDER.md" with backticks in the tool instructions section.

## Verification

- **Docscan:** Ran `python3 docs/system-prompts/docscan.py`.
    - Warnings related to `docs/system-prompts/tools/README.md` plain text references have been resolved.
    - Overall warning count reduced to 277.

## Notes

- Some warnings remain in `AGENTS.md`, `docs/workflows.md`, and `dev_notes/` files. These are deemed lower priority or acceptable for now as they are outside the core `docs/system-prompts` definitions or are note files.
