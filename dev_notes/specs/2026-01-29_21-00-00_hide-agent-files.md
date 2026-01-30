# Spec: Reorganize Agent Context Files

**Workflow:** @logs-first

## Background

The project root currently contains multiple agent-specific documentation files:
- `AIDER.md`
- `CLINE.md`
- `CODEX.md`
- `GEMINI.md`
- `CLAUDE.md`

These files create clutter. The goal is to move them to more "subtle" or "hidden" locations (e.g., dotfiles like `.clinerules`) that are standard or well-supported by the respective tools.

## Requirements

1.  **Investigate & Relocate:**
    *   **Cline:** Move `CLINE.md` to `.clinerules` (or similar standard).
    *   **Aider:** Move `AIDER.md` to a hidden location (e.g., `.aider.md` or similar) and configure `.aider.conf.yml` to read it.
    *   **Codex:** Determine the standard for `CODEX.md` and hide if possible.
    *   **Gemini:** specific to the Gemini CLI. Determine if it can be moved (e.g., to `.gemini/GEMINI.md` or similar).
    *   **Claude:** Investigate if `CLAUDE.md` can be hidden (e.g. `.claude.md`) without losing functionality. If not, keep it but document why.

2.  **Update Configuration:**
    *   Update `bootstrap.py` or any other scripts that generate/reference these files.
    *   Update `.aider.conf.yml` if necessary.

3.  **Documentation:**
    *   Update `AGENTS.md` or `docs/` to reflect the new locations.

## Goals

- Reduce root directory clutter.
- Maintain strong context inclusion for all agents.
- Use standard conventions where available (e.g., `.clinerules`).
