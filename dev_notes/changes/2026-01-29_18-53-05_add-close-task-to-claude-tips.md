# Change Documentation: Add Close-Task Process to Claude Tips

**Date:** 2026-01-29 18-53-05
**Status:** ad-hoc
**Type:** Documentation
**Related Project Plan:** N/A

## Summary
Updated claude-tips.md to include close-task process in the Available Processes table, added example commands for invoking the process, and created a new workflow pattern showing the complete development cycle ending with proper task closure.

## Changes Made

### 1. Available Processes Table

**File Modified:**
- `docs/system-prompts/claude-tips.md` - Added close-task to Available Processes table

**Details:**
Added new row to the processes table:
- Process: **close-task**
- Command: `claude-dev 'apply close-task process'`
- Description: Properly complete and land work before ending session

### 2. Common Process Commands Section

**File Modified:**
- `docs/system-prompts/claude-tips.md` - Added close-task example commands

**Details:**
Added two example invocations:
```bash
# Close task (wrap up work properly)
claude-dev 'apply close-task process'
claude-dev 'close this task and commit changes'
```

### 3. New Workflow Pattern

**File Modified:**
- `docs/system-prompts/claude-tips.md` - Added Pattern 4: Development → Close Task

**Details:**
Created comprehensive workflow pattern showing:

**Three-step development cycle:**
1. Implement the feature
2. Run tests and verify
3. Close the task properly

**What close-task does:**
- Verifies Definition of Done criteria
- Runs tests (aborts if non-trivial failures)
- Checks/creates change documentation
- Commits changes with proper attribution
- Reports final status

**When to use close-task:**
- At end of development sessions
- After completing a feature
- Before switching contexts
- When ready to commit work

**When close-task will abort:**
- Tests fail for non-trivial reasons (logic errors)
- Unexpected files in source tree
- Definition of Done criteria not met

## Files Modified

- `docs/system-prompts/claude-tips.md` - Added close-task references and workflow pattern

## Verification

✅ File maintains consistent formatting with existing patterns
✅ Markdown formatting validated
✅ Commands follow existing conventions (claude-dev for development tasks)
✅ Workflow pattern integrates with existing patterns 1-3
✅ All information is accurate and actionable

## Integration with Definition of Done

This change satisfies:
- ✅ Documentation quality standards (clear, consistent with existing content)
- ✅ File naming conventions (existing file, lowercase-kebab.md)
- ✅ Reference formatting correct
- ✅ Change documentation created (this file, marked as ad-hoc)

## Rationale

**Problem:** The claude-tips.md file documented system-prompts processes but didn't include the newly created close-task process, which is critical for proper session closure.

**Solution:** Added close-task to:
1. Available Processes table (for quick reference)
2. Common Process Commands (with example invocations)
3. New workflow pattern (showing complete dev cycle with proper closure)

**Impact:**
- Users now know how to invoke close-task
- Workflow pattern demonstrates when and why to use it
- Clear guidance on what close-task does and when it aborts
- Promotes proper task closure habits

## Known Issues

None - documentation update is complete and accurate.

## Next Steps

None required. Users can now reference claude-tips.md to learn about the close-task process and how to invoke it autonomously.
