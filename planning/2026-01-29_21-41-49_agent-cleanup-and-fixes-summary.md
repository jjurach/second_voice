# Agent Cleanup And Fixes - Implementation Summary

**Plan:** `planning/2026-01-29_21-41-49_agent-cleanup-and-fixes-plan-plan.md`
**Changes Doc:** `dev_notes/changes/2026-01-29_21-56-34_agent-cleanup-and-fixes.md`
**Status:** ✓ Implemented
**Date:** 2026-01-29

## Implementation Details



## 📋 Executive Summary
Cleaned up agent-specific configuration files from the root directory, updated tooling to support namespaced locations, and fixed Gemini CLI aliases to use valid models and correct argument passing.

## 🏗️ Changes

### Phase 1: File Relocation & Tooling Updates

#### File Moves
- Moved `GEMINI.md` to `.gemini/GEMINI.md`.
- Moved `CLAUDE.md` to `.claude/CLAUDE.md`.
- Confirmed `.aider.md` and `.clinerules` were already in correct locations.

#### Tooling Updates
- **`docs/system-prompts/bootstrap.py`**:
    - Updated `regenerate_tool_entries` to write to new paths.
    - Updated `validate_tool_entry_point` to check new paths.
    - Updated `report_gaps` to check new paths.
    - Updated templates to use correct relative links (e.g., `../AGENTS.md`) for nested files.
- **`docs/system-prompts/docscan.py`**:
    - Updated `ENTRY_POINTS` and `tool_files` mapping.
    - Updated reference checking logic to support directory-nested entry points.
    - Fixed regex patterns for file detection.

#### Documentation Updates
- Updated `README.md` to point to new entry point locations.
- Updated `docs/system-prompts/README.md` and `docs/system-prompts/tools/README.md`.
- Updated `docs/system-prompts/tools/gemini.md` and `docs/system-prompts/tools/claude-code.md` to reflect new paths.
- Updated `docs/system-prompts/tips/gemini.md` and `docs/system-prompts/tips/claude-code.md`.
- Updated `docs/system-prompts/processes/tool-entry-points.md`.

### Phase 2: CLI Fixes

#### Gemini Aliases
- Updated `docs/system-prompts/tips/aliases.sh`.
- Set valid models: `gemini-3-flash-preview` and `gemini-3-pro-preview`.
- Added `--prompt` flag to all Gemini aliases to correctly handle user arguments.
- Updated usage examples in comments.



---
*Summary generated from dev_notes/changes/ documentation*
