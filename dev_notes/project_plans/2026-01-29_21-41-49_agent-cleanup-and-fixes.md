# Project Plan: Agent Configuration Cleanup and Fixes

**Source:** `dev_notes/specs/2026-01-29_21-00-00_hide-agent-files.md`, `dev_notes/inbox/fix-gemini.md`
**Status:** Completed
**Timestamp:** 2026-01-29_21-41-49
**Estimated Phases:** 2
**Priority:** Medium

---

## 📋 Executive Summary
This plan addresses two related objectives: improving the project structure by moving agent-specific configuration files (like `CLINE.md`, `AIDER.md`) out of the root directory to reduced clutter, and fixing configuration/alias issues with the Gemini CLI and other agent wrappers to ensure reliable operation and documentation consistency.

## 🎯 Goals
1.  **Reduce Root Clutter:** Move agent context files to hidden or standard locations (e.g., `.clinerules`, `.aider.md`).
2.  **Maintain Context:** Ensure all agents continue to load their specific instructions from the new locations.
3.  **Fix Gemini CLI:** Resolve model selection errors and fix alias definitions (ensure trailing `--prompt`).
4.  **Standardize Usage:** Audit and align documentation with actual CLI capabilities for all agents.

## 🏗️ Implementation Plan

### Phase 1: File Relocation & Bootstrap Update
**Goal:** Clean up root directory and update generation scripts.

#### Task 1.1: Relocate Agent Files
**Files:** `CLINE.md`, `AIDER.md`, `GEMINI.md`, `CLAUDE.md`, `CODEX.md` (and potential targets like `.clinerules`, `.aider.md`)
- [ ] Move `CLINE.md` to `.clinerules` (Standard for Cline).
- [ ] Move `AIDER.md` to `.aider.md` and update `.aider.conf.yml` `read` setting to point to it.
- [ ] Move `GEMINI.md` to `.gemini/GEMINI.md` (Update `src/cli/run.py` or config if needed to ensure it's read).
- [ ] Investigate and move `CLAUDE.md` (e.g., to `.claude.md` or `.claude/config`).
- [ ] Investigate and move `CODEX.md`.

#### Task 1.2: Update Bootstrap Script
**Files:** `docs/system-prompts/bootstrap.py`
- [ ] Update the `bootstrap.py` script to generate/update these files in their new locations instead of the root.

#### Task 1.3: Update Documentation References
**Files:** `AGENTS.md`, `docs/`
- [ ] Update `AGENTS.md` to reflect the new file locations.
- [ ] Update any other docs referencing these root files.

**Acceptance Criteria:**
- [ ] Root directory does not contain `CLINE.md`, `AIDER.md`, `GEMINI.md`, `CLAUDE.md`, `CODEX.md`.
- [ ] `bootstrap.py` runs without error and updates the files in new locations.
- [ ] Aider starts and reads `.aider.md`.
- [ ] Cline detects `.clinerules`.

---

### Phase 2: CLI Fixes & Consistency Audit
**Goal:** Fix Gemini aliases and ensure docs match reality.

#### Task 2.1: Gemini Model & Alias Fixes
**Files:** `aliases.sh` (or source of aliases), `src/cli/run.py` (if applicable)
- [ ] Research valid models for Gemini Pro plan (using `context7` or search).
- [ ] Update Gemini aliases to use a working model.
- [ ] Ensure all `gemini-*` aliases end with `--prompt` to correctly handle user input.

#### Task 2.2: Documentation vs CLI Audit
**Files:** `docs/*.md`
- [ ] Run `egrep -i 'gemini|claude|aider|cline|codex' -r *.md docs` to find usage examples.
- [ ] For each agent, run `--help` to verify flags/arguments match documentation.
- [ ] Fix any discrepancies in the documentation or aliases.

**Acceptance Criteria:**
- [ ] `gemini` aliases work correctly (no 404 on model).
- [ ] `gemini-quick "query"` works as expected.
- [ ] Documentation examples for all agents are verifiable against their `--help` output.

## ✅ Definition of Done
- [ ] All tasks completed.
- [ ] Root directory is clean of agent MD files.
- [ ] Verification commands (to be recorded in changes) show agents loading context correctly.
- [ ] Gemini commands function without model errors.
- [ ] Documentation is updated and accurate.
