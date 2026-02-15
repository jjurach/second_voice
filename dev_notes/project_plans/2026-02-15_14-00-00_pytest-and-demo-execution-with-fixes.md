# Project Plan: Pytest and Demo Script Execution with Fixes

**Status:** Draft
**Created:** 2026-02-15
**Last Updated:** 2026-02-15
**Owner:** Planner
**Ready for Review:** YES

---

## Overview

Create and execute a bead that runs pytest test suite and demo scripts, identifies failures and errors, and applies targeted fixes to resolve all issues. This ensures code quality and correctness of both test coverage and demo workflows.

---

## Objectives

1. **Execute pytest** - Run full test suite with verbose output
2. **Execute demo scripts** - Run any demonstration/example scripts in the project
3. **Identify failures** - Capture all failures, errors, and warnings
4. **Apply fixes** - Make targeted code changes to fix identified issues
5. **Verify resolution** - Re-run tests/demos to confirm all issues resolved
6. **Document results** - Create change documentation with verification proof

---

## Scope

### In Scope
- Running `pytest tests/ -v` with full output capture
- Running identified demo scripts (if any exist in `scripts/demo/` or similar)
- Analyzing pytest output for failures and errors
- Making targeted code fixes to address root causes
- Re-running tests after fixes to verify success
- Documenting all changes and verification results

### Out of Scope
- Adding new tests
- Refactoring code beyond bug fixes
- Changing project architecture
- Modifying configuration files (unless necessary to fix broken tests)

---

## Execution Steps

### Step 1: Discover Tests and Demo Scripts
**Deliverable:** List of all test files and demo scripts

- Use `pytest --collect-only` to get comprehensive test inventory
- Search for demo scripts in:
  - `scripts/demo/`
  - `examples/`
  - `docs/examples/`
  - Any `*_demo.py` files
- Document locations and purposes

### Step 2: Run Pytest Test Suite
**Deliverable:** Full pytest output, categorized by status

```bash
pytest tests/ -v --tb=short 2>&1
```

- Capture all output (both stdout and stderr)
- Categorize results:
  - ✅ Passed tests
  - ❌ Failed tests
  - ⚠️ Errors (import, setup, etc.)
  - 🔕 Skipped tests
- Note any deprecation warnings

### Step 3: Run Demo Scripts
**Deliverable:** Demo script execution results

For each discovered demo script:
```bash
cd project-root
python scripts/demo/<script_name>.py 2>&1
```

- Capture output and any error messages
- Note expected vs. actual behavior

### Step 4: Analyze Failures
**Deliverable:** Root cause analysis document

For each failure/error:
1. **Read the error message** - Extract traceback and assertion details
2. **Identify root cause** - File, function, and type of issue
3. **Classify issue:**
   - Missing dependency
   - Logic error
   - Configuration issue
   - API incompatibility
   - Other
4. **Prioritize** - Order fixes by impact

### Step 5: Apply Targeted Fixes
**Deliverable:** Code changes fixing identified issues

For each issue:
1. **Read affected file(s)** - Understand current implementation
2. **Apply minimal fix** - Change only what's necessary
3. **Follow code patterns** - Match existing style and conventions
4. **Add no extra changes** - Avoid refactoring or improvements
5. **Document change** - Note what changed and why

### Step 6: Verify Fixes
**Deliverable:** Re-run test output showing resolution

```bash
pytest tests/ -v --tb=short 2>&1
```

For each demo:
```bash
python scripts/demo/<script_name>.py 2>&1
```

- Confirm all previously failing tests now pass
- Confirm all demo scripts execute without error
- Capture final output for documentation

### Step 7: Create Change Documentation
**Deliverable:** Entry in `dev_notes/changes/`

- Filename: `2026-02-15_HH-MM-SS_pytest-and-demo-fixes.md`
- Document:
  - Summary of issues found
  - Each fix applied (file, change, reason)
  - Before/after test counts
  - Full verification output
  - Known issues (if any)

---

## Success Criteria

- [ ] All pytest tests pass (or known skips documented)
- [ ] All demo scripts execute without errors
- [ ] Each fix is documented with proof of resolution
- [ ] Change documentation created with verification output
- [ ] Project Plan marked as `Status: Completed`

---

## Risks & Mitigations

| Risk | Mitigation |
|------|-----------|
| Large number of failures | Process systematically, fix root causes first |
| Breaking existing functionality | Run full suite after each fix, revert if needed |
| Missing demo scripts | Search thoroughly, ask if unclear |
| External dependencies down | Document environment setup needed, skip if unavoidable |

---

## Notes for Execution

- **Be minimal** - Fix only what's broken, no refactoring
- **Follow patterns** - Match existing code style
- **Test after each fix** - Verify fixes work before moving on
- **Document as you go** - Update change log with each fix
- **Stop if blocked** - If uncertain about a fix, ask first

---

## Files to Monitor

Key files likely involved:
- `tests/` - Test suite files
- `src/` - Source code being tested
- `scripts/` - Demo scripts
- `requirements.txt` / `pyproject.toml` - Dependencies
- `conftest.py` - Pytest configuration and fixtures

---

## Related Documentation

- `docs/definition-of-done.md` - Python DoD requirements
- `AGENTS.md` - Workflow and quality standards
- `pytest.ini` or `pyproject.toml` - Test configuration
