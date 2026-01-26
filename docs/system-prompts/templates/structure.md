# Templates for Project Documentation

This document defines the standard templates for Spec Files, Project Plans, and Change Documentation. All templates use the filename format: `YYYY-MM-DD_HH-MM-SS_description.md`

---

## 1. Spec File Template

**Purpose:** Capture user intentions, goals, and acceptance criteria. Used in `dev_notes/specs/`.

**When to create:** When a request requires planning (Step B of Core Workflow).

**Filename:** `dev_notes/specs/YYYY-MM-DD_HH-MM-SS_spec-description.md`

### Template

```markdown
# Spec: [Feature/Task Name]

**Date:** YYYY-MM-DD
**Status:** [Under Review | Approved | In Progress]

## User Request
[Summarize what the user is asking for in bullet points]
- Item 1
- Item 2
- Item 3

## Current State
[Describe the existing situation]
- What exists now
- What's broken or missing
- Current metrics or baseline

## Goals
[What should be achieved]
- Primary goal
- Secondary goals
- Success indicators

## Scope
[Define what's included and excluded]
- **Included:** Components/features to address
- **Excluded:** Out of scope for this task
- **Related:** Adjacent work that might be affected

## Acceptance Criteria
- [ ] Criterion 1
- [ ] Criterion 2
- [ ] Criterion 3
- [ ] All tests pass
- [ ] Documentation updated

## Notes
[Optional: Technical notes, constraints, assumptions, or dependencies]
```

### Minimal Example

```markdown
# Spec: Add Unit Tests & Fix pytest

**Date:** 2026-01-25
**Status:** Under Review

## User Request
- Add more unit tests with focus on **critical paths only**
- Fix `pytest` (currently broken - not installed)
- Use mocked external services by default

## Current State
- 8 test cases total (~15-20% coverage)
- Using unittest instead of pytest
- pytest not installed

## Acceptance Criteria
- [ ] pytest is installed and configured
- [ ] All critical path functions have unit tests
- [ ] All external API calls are mocked by default
- [ ] Tests can run offline
- [ ] Coverage report shows 60%+ coverage on critical modules
```

---

## 2. Project Plan Template

**Purpose:** Detailed, step-by-step implementation plan. Used in `dev_notes/project_plans/`.

**When to create:** After spec approval, before implementation (Step C of Core Workflow).

**Filename:** `dev_notes/project_plans/YYYY-MM-DD_HH-MM-SS_description.md`

### Template

```markdown
# Project Plan: [Feature/Task Name]

**Created:** YYYY-MM-DD HH-MM-SS
**Status:** [Draft | Approved | In Progress | Completed]
**Implementation Reference:** `dev_notes/changes/YYYY-MM-DD_HH-MM-SS_description.md` (if completed)

## Overview
[2-3 sentence description of what this plan accomplishes]

## Phase 1: [Phase Name]
**Goal:** [What this phase achieves]

### 1.1 [Specific Task]
- Detailed step 1
- Detailed step 2
- Success indicator

### 1.2 [Specific Task]
- [Repeat]

## Phase 2: [Next Phase]
[Repeat structure as needed]

## Implementation Order
1. Phase 1 (dependency reasoning if applicable)
2. Phase 2 (why it depends on Phase 1)
3. etc.

## Files to Create/Modify

**New Files:**
- `path/to/new_file.py` - Brief description
- `path/to/config.json` - Brief description

**Modified Files:**
- `path/to/existing.py` - What changes and why
- `requirements.txt` - Add/update dependencies

**Not Modified:**
- Source files that won't be touched

## Success Criteria
✅ Criterion 1
✅ Criterion 2
✅ Criterion 3
✅ All tests pass
✅ Code follows project patterns
✅ Documentation updated

## Risk Assessment
- **Low Risk:** [Why this is low risk]
- **Medium Risk:** [Potential issues and mitigation]
- **High Risk:** [Critical dependencies or complex changes]

## Estimated Scope
- **New code:** ~X lines
- **Configuration changes:** ~X lines
- **Documentation:** ~X lines
- **Test code:** ~X lines

## Test Infrastructure (if applicable)
[Description of mocking strategy, test markers, fixtures, etc.]

## Miscellaneous Notes
[Optional: Known limitations, future improvements, tricky implementation details]
```

### Minimal Example (Pytest Plan)

```markdown
# Project Plan: Add Unit Tests & Fix pytest

**Created:** 2026-01-25 18:46:25
**Status:** Approved

## Overview
Install and configure pytest, then add unit tests for critical code paths (config, processor, recorder, modes, CLI) with mocked external services.

## Phase 1: Setup & Configuration
**Goal:** Get pytest installed and configured

### 1.1 Install pytest and dependencies
- Add pytest to `requirements.txt`
- Verify installation: `python -m pytest --version`

### 1.2 Create pytest configuration file
- Create `pytest.ini` with test discovery patterns and coverage thresholds

### 1.3 Create conftest.py
- Add fixtures for mock config, mock API clients, temporary directories

## Phase 2: Config Module Tests
**File:** `tests/test_config.py`

### 2.1 Test config loading
- Load default config
- Load from file
- Load from environment variables

### 2.2 Test config validation
- Valid provider names
- Invalid provider names raise errors

## Implementation Order
1. Phase 1 (Setup) - Must complete first
2. Phase 2 (Config) - Simplest module

## Files to Create/Modify
**New Files:**
- `pytest.ini`
- `tests/conftest.py`
- `tests/test_config.py`

**Modified Files:**
- `requirements.txt` - Add pytest, pytest-cov

## Success Criteria
✅ pytest installed and working
✅ All tests pass offline
✅ Config module 100% tested
✅ Coverage report shows 60%+ on critical modules

## Risk Assessment
- **Low Risk:** Setup and config tests
- **Medium Risk:** Processor tests (many API mocks)

## Estimated Scope
- **New test code:** ~1500-2000 lines
- **Configuration files:** ~50 lines
```

---

## 3. Change Documentation Template

**Purpose:** Document what was actually implemented and verify it works. Used in `dev_notes/changes/`.

**When to create:** After completing implementation steps (Step E of Core Workflow).

**Filename:** `dev_notes/changes/YYYY-MM-DD_HH-MM-SS_description.md`

### Template

```markdown
# Change Documentation: [What Changed]

**Date:** YYYY-MM-DD HH-MM-SS
**Status:** [In Progress | Completed]
**Type:** [Feature | Bug Fix | Refactor | Testing | Infrastructure | Documentation]
**Related Project Plan:** `dev_notes/project_plans/YYYY-MM-DD_HH-MM-SS_description.md` (if applicable)

## Summary
[1-2 sentences of what was accomplished and the impact]

## Changes Made

### 1. [Component/Module Name]

**Files:**
- `path/to/file1.py` - What changed
- `path/to/file2.py` - What changed

**Details:**
- What was added/modified/removed
- Why this approach was chosen
- Any relevant code patterns or constraints

### 2. [Another Component]
[Repeat structure]

## Test Execution

### Running [Test Suite Name]
```bash
pytest                    # Command 1
pytest --cov            # Command 2
```

### Test Results
```
========================= test session starts ==========================
collected 94 items

tests/test_config.py ................................ [ 27%]
tests/test_processor.py ............................. [ 67%]
tests/test_recorder.py .............................. [ 93%]
tests/test_modes.py .................................. [100%]

========================= 94 passed in 2.34s ==========================
```

## Coverage Results

| Module | Statements | Coverage | Status |
|--------|-----------|----------|--------|
| config.py | 33 | 100% | ✅ Complete |
| processor.py | 89 | 100% | ✅ Complete |
| **TOTAL** | **597** | **49%** | ✅ Critical paths 100% |

## Files Modified/Created

### Created
- `file1.py` - Brief description
- `file2.py` - Brief description

### Modified
- `existing.py` - What changed
- `requirements.txt` - Dependencies added

### Not Modified
- Source files that weren't touched

## Verification

✅ All tests pass
✅ Coverage meets targets
✅ Code follows project patterns
✅ No hardcoded credentials
✅ Dependencies in requirements.txt
✅ Configuration updated if applicable

## Integration with Definition of Done

This change satisfies:
- ✅ Testing requirements (all critical paths tested)
- ✅ Code quality (follows project patterns)
- ✅ Documentation (updated in docs/)
- ✅ Dependencies (in requirements.txt and pyproject.toml)

## Known Issues

[Optional section for caveats, limitations, or future improvements]

Example:
- GUI mode not tested (TBD - requires X11)
- Recorder module 86% coverage (edge case exceptions in stream init untested)

## Next Steps (Optional)

[Any follow-up work or recommendations]
```

### Minimal Example (Pytest Changes)

```markdown
# Change Documentation: pytest Setup & Unit Tests

**Date:** 2026-01-25 18:50:00
**Status:** Completed
**Type:** Testing Infrastructure

## Summary
Successfully installed pytest and created 94 comprehensive unit tests for critical code paths. Achieved 49% overall coverage with 100% coverage on critical modules (config, processor).

## Changes Made

### 1. pytest Installation & Configuration

**Files:**
- `requirements.txt` - Added pytest, pytest-cov, requests-mock
- `pytest.ini` - Created pytest configuration file
- `tests/conftest.py` - Created shared test fixtures

**Details:**
- Installed pytest 9.0.2, pytest-cov 7.0.0, requests-mock 1.12.1
- Created comprehensive test fixtures for mock API clients
- Configured pytest to discover and run tests from `tests/` directory

### 2. Config Module Tests (25 tests)

**File:** `tests/test_config.py`
**Coverage:** 100% of config.py (33 statements)

**Details:**
- Config file loading and merging
- Environment variable overrides
- Configuration access methods
- Save/load roundtrip functionality

## Test Execution

### Running All Tests
```bash
pytest
```

### Results
```
========================= test session starts ==========================
collected 94 items

tests/test_config.py ........................................ [ 27%]
tests/test_processor.py .................................... [ 67%]
tests/test_recorder.py ...................................... [ 93%]
tests/test_modes.py ......................................... [100%]

========================= 94 passed in 2.34s ==========================
```

## Coverage Results

| Module | Coverage | Status |
|--------|----------|--------|
| config.py | 100% | ✅ Complete |
| processor.py | 100% | ✅ Complete |
| recorder.py | 86% | ✅ Critical paths |

## Files Created
- `pytest.ini`
- `tests/conftest.py`
- `tests/test_config.py` (25 tests)
- `tests/test_processor.py` (37 tests)
- `tests/test_recorder.py` (24 tests)

## Files Modified
- `requirements.txt` - Added pytest, pytest-cov, requests-mock

## Verification

✅ 94 tests all passing
✅ 100% coverage on critical modules
✅ All mocks working correctly
✅ Existing tests still pass
✅ No source code changes required

## Known Issues

Recorder module 86% coverage - lines 88-92, 106-107, 110-113 untested (exception handling in edge cases during stream initialization). These don't affect functionality in normal operation.
```

---

## 4. Best Practices for All Templates

### Naming & Dates
- **Format:** `YYYY-MM-DD_HH-MM-SS_description.md`
- **Example:** `2026-01-25_18-46-25_add-tests-fix-pytest.md`
- **How to generate:**
  ```bash
  # Python
  python3 -c "from datetime import datetime; print(datetime.now().strftime('%Y-%m-%d_%H-%M-%S'))"

  # Shell
  date "+%Y-%m-%d_%H-%M-%S"
  ```

### Status Field
- **Spec Files:** `Under Review`, `Approved`, `In Progress`
- **Project Plans:** `Draft`, `Approved`, `In Progress`, `Completed`
- **Change Documentation:** `In Progress`, `Completed`

### Cross-References
- Project Plans reference related Spec Files
- Change Documentation references related Project Plans
- Always use relative paths: `dev_notes/specs/YYYY-MM-DD_...md`

### Verification Section
Every Change Documentation must include:
- Exact commands used for testing
- Terminal output showing success
- Coverage metrics if applicable
- Checklist against Definition of Done

### Known Issues Section
Document limitations, edge cases, or future improvements:
- Be specific about what's not tested and why
- Explain any workarounds
- Link to related follow-up work

---

## 5. State Transition Rules

### Spec Files
```
Under Review → Approved → In Progress
```

### Project Plans
```
Draft → Approved → In Progress → Completed
```

When marking Complete:
1. Update `Status: Completed` header
2. Add `Completion Summary` section at end
3. Reference related Change Documentation file

### Change Documentation
```
In Progress → Completed
```

When marking Complete:
1. Update `Status: Completed` header
2. Include full verification results
3. Check all Definition of Done criteria

---

## 6. Integration with Definition of Done

Every completed Change Documentation must verify:

### Universal Requirements
- [ ] Code follows project patterns and style
- [ ] No hardcoded credentials or secrets
- [ ] Tests pass
- [ ] `dev_notes/changes/` entry created with verification
- [ ] Related Project Plan marked as `Completed`

### Python Specifics (if applicable)
- [ ] All new imports in `requirements.txt`
- [ ] Type hints present for function signatures
- [ ] Docstrings follow project conventions
- [ ] `requirements.txt` and `pyproject.toml` updated
- [ ] All tests pass: `pytest tests/ -v`
- [ ] Coverage measured and documented

### File Changes
- [ ] `config.example.json` updated if config keys added
- [ ] Documentation in `docs/` updated if needed
- [ ] Temporary test scripts deleted after verification

See `docs/definition-of-done.md` for complete checklist.

---

## 7. Quick Reference

| Document Type | Location | Triggers | Status Values | Example |
|---|---|---|---|---|
| **Spec File** | `dev_notes/specs/` | Step B of workflow | `Under Review`, `Approved` | `2026-01-25_18-46-25_add-tests.md` |
| **Project Plan** | `dev_notes/project_plans/` | Step C of workflow | `Draft`, `Approved`, `Completed` | `2026-01-25_18-46-25_test-plan.md` |
| **Change Doc** | `dev_notes/changes/` | Step E of workflow | `In Progress`, `Completed` | `2026-01-25_18-50-00_pytest-tests.md` |

---

## Notes

- **Spec files** can be lightweight if requirements are clear
- **Project Plans** should be detailed enough for another agent to execute
- **Change Documentation** is your proof that work was done correctly
- All three document types feed into audit trail and Definition of Done verification
