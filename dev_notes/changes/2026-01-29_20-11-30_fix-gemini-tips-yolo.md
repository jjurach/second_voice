# Change Documentation: Fix Gemini CLI Tips (YOLO Flag)

**Date:** 2026-01-29 20-11-30
**Status:** ad-hoc
**Type:** Documentation
**Related Project Plan:** N/A

## Summary
Corrected the Gemini CLI documentation and aliases to use the `--yolo` flag instead of `--dangerously-skip-permissions`. Research confirmed that `--yolo` is the correct flag for Gemini ("YOLO mode"), while `--dangerously-skip-permissions` is used by Claude Code.

## Changes Made

### 1. Updated Gemini Tips
**File:** `docs/system-prompts/tips/gemini.md`
- Replaced all instances of `--dangerously-skip-permissions` with `--yolo` in aliases and best practices.

### 2. Updated Shared Aliases
**File:** `docs/system-prompts/tips/aliases.sh`
- Updated `gemini-*` aliases to use `--yolo`.
- Verified `claude-*` aliases correctly use `--dangerously-skip-permissions`.

## Verification
- Verified file content of `docs/system-prompts/tips/gemini.md` shows `--yolo`.
- Verified file content of `docs/system-prompts/tips/aliases.sh` shows `--yolo` for Gemini and `--dangerously-skip-permissions` for Claude.

## Integration with Definition of Done
- ✅ Documentation updated
- ✅ No code changes requiring tests
