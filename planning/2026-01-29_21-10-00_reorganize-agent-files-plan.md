# Project Plan: Reorganize Agent Context Files

**Status:** Completed

**Workflow:** @logs-first

## Goal
Reduce clutter in the project root by moving or removing agent-specific markdown files (`AIDER.md`, `CLINE.md`, `CODEX.md`, etc.) while ensuring agents still receive their necessary context.

## Motivation
The project root currently contains multiple agent-specific documentation files. This creates noise. The goal is to use "hidden" or standard configuration files where possible, or rely on native `AGENTS.md` support.

## Proposed Changes

### 1. Cline (`CLINE.md` -> `.clinerules`)
-   **Current:** `CLINE.md` in root.
-   **Target:** `.clinerules` in root.
-   **Reason:** Cline natively supports `.clinerules` as a configuration/context file. This hides it from default directory listings.

### 2. Aider (`AIDER.md` -> `.aider.md`)
-   **Current:** `AIDER.md` in root.
-   **Target:** `.aider.md` in root (hidden).
-   **Configuration:** Update `.aider.conf.yml` to include `.aider.md` in the `read` list (if needed) or rely on `AGENTS.md`. 
    -   *Correction:* The current `AIDER.md` is an anemic entry point mainly for humans or explicit loading. Aider reads `AGENTS.md` by default via `.aider.conf.yml`. We will rename `AIDER.md` to `.aider.md` and ensure `.aider.conf.yml` references it if it contains Aider-specific instructions not in `AGENTS.md`. If it's just a pointer, we might delete it and rely on `AGENTS.md`.
    -   *Decision:* Move to `.aider.md` and add to `.aider.conf.yml` `read` list to ensure Aider sees it if it contains specific instructions.

### 3. Codex (`CODEX.md` -> Remove)
-   **Current:** `CODEX.md` in root.
-   **Target:** Remove.
-   **Reason:** Codex natively discovers and reads `AGENTS.md`. The `CODEX.md` file is redundant if it just points to docs. Humans should start with `AGENTS.md` or `README.md`.

### 4. Gemini (`GEMINI.md` -> Keep)
-   **Current:** `GEMINI.md` in root.
-   **Target:** Keep as `GEMINI.md`.
-   **Reason:** The Gemini CLI looks for `GEMINI.md` or `~/.gemini/GEMINI.md`. There is no hidden project-level default (like `.gemini.md`) documented. Moving it to `~` is not project-specific.

### 5. Claude (`CLAUDE.md` -> Keep)
-   **Current:** `CLAUDE.md` in root.
-   **Target:** Keep as `CLAUDE.md`.
-   **Reason:** Claude Code looks for `CLAUDE.md`. No hidden project-level default documented.

## Implementation Steps

1.  **Update `bootstrap.py`:**
    -   Modify `regenerate_tool_entries` to:
        -   Generate `.clinerules` instead of `CLINE.md`.
        -   Generate `.aider.md` instead of `AIDER.md`.
        -   Stop generating `CODEX.md`.
    -   Update `validate_tool_entry_point` to check new paths.
    -   Update `report_gaps` to check new paths.

2.  **Update `.aider.conf.yml`:**
    -   Add `.aider.md` to the `read` list.

3.  **Migration Script:**
    -   Delete `CLINE.md`, `AIDER.md`, `CODEX.md` from root.
    -   Run `bootstrap.py --regenerate-tool-entries --commit` to create new files.

4.  **Documentation Updates:**
    -   Update `docs/system-prompts/tools/cline.md` to mention `.clinerules`.
    -   Update `docs/system-prompts/tools/aider.md` to mention `.aider.md`.
    -   Update `docs/system-prompts/tools/codex.md` to remove `CODEX.md` reference.
    -   Update `docs/system-prompts/processes/tool-entry-points.md`.
    -   Update `docs/file-naming-conventions.md`.

## Verification
-   Verify `.clinerules` is created and contains correct content.
-   Verify `.aider.md` is created and `.aider.conf.yml` is updated.
-   Verify `CODEX.md` is gone.
-   Verify `bootstrap.py --analyze` reports correctly.
