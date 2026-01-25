# Revised Mode Selection Architecture Plan

## Change Type
Documentation - Project Plan Revision

## Date
2026-01-25 00:47:20

## Summary
Revised the mode selection architecture plan to address four critical issues: shared component extraction, task dependencies, /tmp violation fix, and proper task ordering.

## What Changed

### 1. Added Phase 1: Shared Engine Components
**New Tasks:**
- **M.0:** Create core/config.py - Configuration management
- **M.1:** Create core/recorder.py - Audio recording with PyAudio
- **M.2:** Create core/processor.py - STT + LLM processing pipeline

**Rationale:** All three modes (GUI, TUI, Menu) need to share the same recording and processing logic. Extracting these components first prevents code duplication and ensures consistency.

### 2. Added Explicit Task Dependencies
**Changes:**
- Each task now lists its dependencies explicitly
- Added "Task Dependency Graph" section with ASCII visualization
- Added "Task Execution Order" section with numbered sequence

**Example:**
```
Task M.3 (modes/base.py)
Dependencies: M.0, M.1, M.2
```

**Rationale:** Prevents implementation errors from doing tasks out of order. Another agent (or developer) can follow the plan without guessing what needs to be done first.

### 3. Fixed /tmp Violation
**Changes:**
- M.0 (config.py): NO /tmp USAGE - use CWD for temporary files
- M.1 (recorder.py): Change from `/tmp/sv_audio.wav` to `./tmp-audio.wav`
- M.4 (menu_mode.py): Use `tmp-review.md` in CWD for editor
- M.5 (tui_mode.py): Use `tmp-review.md` in CWD for editor
- M.6 (gui_mode.py): Fix buffer file location from hardcoded to use config or CWD
- Added Critical Implementation Note #7 about mandatory /tmp prohibition

**Rationale:** AGENTS.md Rule #5 prohibits `/tmp` usage. All temporary files must use CWD with patterns: `tmp-*`, `*.tmp`, or `tmp/*`.

### 4. Updated Module Structure
**Added:**
```
src/second_voice/
├── core/
│   ├── __init__.py
│   ├── config.py
│   ├── recorder.py
│   └── processor.py
```

**Rationale:** Separates shared engine logic from mode-specific UI logic.

### 5. Renumbered Tasks
**Old:** M.1 through M.9 (9 tasks)
**New:** M.0 through M.11 (12 tasks)

**Changes:**
- M.0, M.1, M.2: New shared component tasks
- M.3-M.6: Renumbered from M.1-M.4 (modes)
- M.7: Renumbered from M.5 (modes/__init__)
- M.8: Renumbered from M.6 (cli.py)
- M.9: Renumbered from M.7 (dependencies)
- M.10: Renumbered from M.8 (tests)
- M.11: Renumbered from M.9 (docs)

## Files Modified
- `dev_notes/project_plans/2026-01-25_00-32-27_mode-selection-architecture.md` (revised)

## Current Status
Plan revised and awaiting approval for implementation.

## Next Steps (After Approval)
1. Execute tasks M.0 through M.11 in dependency order
2. Document each implementation step in dev_notes/changes/
3. Test each component as it's completed
4. Integration test all modes after M.8 (CLI integration)

## Verification Checklist
After implementation, verify:
- [ ] No /tmp usage anywhere in the codebase
- [ ] All three modes use shared recorder and processor
- [ ] All task dependencies are satisfied
- [ ] Each mode can complete full workflow
- [ ] Auto-detection works correctly
- [ ] Graceful degradation works (gui → tui → menu)
- [ ] Temporary files are cleaned up properly

## Notes
This revision addresses developer feedback requesting:
1. Shared component extraction before mode implementation
2. /tmp violation fixes
3. Explicit task dependencies
4. Proper task ordering

The plan is now ready for implementation with clear dependencies and proper architecture.
