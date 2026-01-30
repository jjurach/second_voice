# Change Documentation: Create Close-Task Process

**Date:** 2026-01-29 18-48-41
**Status:** ad-hoc
**Type:** Documentation
**Related Project Plan:** N/A

## Summary
Created comprehensive close-task.md process document that provides a detailed checklist and procedures for properly completing work before ending an agentic session. Includes Definition of Done verification, test execution, change documentation, git commit procedures, and abort criteria for when human intervention is needed.

## Changes Made

### 1. New Process Document

**Files Created:**
- `docs/system-prompts/processes/close-task.md` - Comprehensive 600+ line process guide

**Details:**
The close-task process document covers:

**Phase 1: Verify Definition of Done**
- Universal DoD criteria checklist
- Language-specific DoD criteria (Python)
- Project-specific DoD criteria
- Stop if any criteria not met

**Phase 2: Run Tests**
- Execute test suite
- Decision tree for test results:
  - ✅ Pass → Continue
  - ❌ Trivial failures → Fix and rerun
  - ❌ Non-trivial failures → ABORT and request human intervention
- Explicit abort scenarios with example messages
- Clear rationale for why to abort on non-trivial failures

**Phase 3: Document Changes**
- Check for change documentation existence
- Verify quality and completeness
- Create if missing (with proper ad-hoc or completed status)
- Ensure all required sections included

**Phase 4: Commit Changes**
- Review git status for unexpected files
- Stage changes (code + change docs together)
- Create properly formatted commit message
- Verify commit success

**Phase 5: Final Status Report**
- Provide clear summary to user
- List what was accomplished
- Clean up temporary files

**Abort Scenarios:**
- Tests fail (non-trivial) - Detailed guidance on when and how to abort
- Unexpected files in source tree - Ask user for guidance
- Missing change documentation - Create before committing
- Definition of Done not met - Fix before proceeding

**Common Patterns:**
- Standard code change
- Documentation-only change (ad-hoc)
- Tests failing
- Multi-file refactoring

**Examples:**
- Successful code change close (complete walkthrough)
- Abort on test failure (with example output)
- Documentation change (ad-hoc)

### 2. Updated Process Index

**Files Modified:**
- `docs/system-prompts/processes/README.md` - Added close-task to Available Processes section

**Details:**
- Listed close-task process alongside document-integrity-scan
- Provided summary of what it covers
- Indicated when to use the process

## Files Created

- `docs/system-prompts/processes/close-task.md` (614 lines)
- `dev_notes/changes/2026-01-29_18-48-41_create-close-task-process.md` (this file)

## Files Modified

- `docs/system-prompts/processes/README.md` - Added close-task reference

## Verification

✅ File follows lowercase-kebab.md naming convention
✅ Markdown formatting validated
✅ All internal links verified (pointing to existing docs)
✅ Examples are clear and actionable
✅ Abort criteria are explicit and well-reasoned
✅ Integration with other processes documented

## Integration with Definition of Done

This change satisfies:
- ✅ Documentation quality standards (comprehensive, clear structure)
- ✅ File naming conventions (lowercase-kebab.md)
- ✅ Reference formatting correct (hyperlinks and backticks used properly)
- ✅ No broken links
- ✅ Change documentation created (this file, marked as ad-hoc)

## Rationale

**Problem:** Agents lacked clear guidance on how to properly close out work before ending a session. This led to:
- Incomplete Definition of Done verification
- Committing code with failing tests
- Missing change documentation
- Unclear git commit practices
- Not knowing when to abort and request human help

**Solution:** Created a comprehensive close-task process that:
- Provides step-by-step checklist
- Explicitly defines abort criteria (especially for non-trivial test failures)
- Covers all aspects: DoD verification, testing, documentation, committing
- Includes detailed examples for different scenarios
- Explains WHEN and WHY to stop and ask for human intervention

**Key Features:**
1. **Abort on non-trivial test failures** - Prevents committing broken code
2. **Change documentation verification** - Ensures audit trail is complete
3. **Git hygiene** - Check for unexpected files before committing
4. **Clear examples** - Shows what success and abort scenarios look like
5. **Integration documentation** - Links to related processes and workflows

**Impact:**
- Agents now have clear guidance on "landing the plan"
- Reduces risk of committing broken or incomplete work
- Ensures all work is properly documented
- Provides clear decision points for when to stop and ask for help
- Maintains quality standards through explicit DoD verification

## Known Issues

None - process documentation is complete. Future refinements may include:
- Automated close-task checklist script
- Integration with CI/CD pipelines
- Project-specific close-task extensions

## Next Steps

None required. The close-task process is ready for use. Agents can now reference it when wrapping up work sessions.
