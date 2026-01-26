# System-Prompts Refactoring Proposal

**Date:** 2026-01-25
**Status:** Awaiting Review

## Problem Statement

The `docs/system-prompts/` directory contains generic, reusable templates intended for use across projects. However, they currently contain **project-specific references** and **implementation details** that tie them to `second_voice`. This violates the "independence" principle and makes them non-reusable.

## Issues Identified

### 1. Project-Specific Directory References

**File:** `workflow/core.md`

Current references to `dev_notes/` subdirectories:
- Line 18: `dev_notes/specs`
- Line 19: `dev_notes/specs/YYYY-MM-DD_HH-MM-SS_spec-description.md`
- Line 27: `dev_notes/project_plans/YYYY-MM-DD_HH-MM-SS_description.md`
- Line 38: `dev_notes/changes/`
- Line 46: `dev_notes/` MUST use filename format

**Issue:** These are organizational choices specific to `second_voice`. A generic kernel shouldn't prescribe where to store files—only that files should be stored *somewhere* with consistent naming.

**Impact:** Projects using this kernel must adopt the exact `dev_notes/` structure. No flexibility for alternatives like `docs/planning/`, `docs/specs/`, `.ai-plans/`, etc.

---

### 2. Missing/Non-Existent References

**File:** `workflow/core.md`

- Line 14: References `docs/overview.md` - **DOESN'T EXIST** in any project
- Line 25: References `docs/templates.md` - EXISTS but is PROJECT-SPECIFIC documentation created for `second_voice`
- Line 47: References `docs/file-naming-conventions.md` - **DOESN'T EXIST**

**Issue:** System-prompts shouldn't reference project documentation that doesn't exist or that they depend on being created first.

**Impact:** New projects trying to use the kernel see broken references immediately.

---

### 3. Python-Specific Content in Universal Definition of Done

**File:** `principles/definition-of-done.md`

Lines that should be in `languages/python/definition-of-done.md`:
- Line 32: `requirements.txt` AND `pyproject.toml` - Python-specific
- Lines 52-53: Checklist items for these files

**Issue:** Non-Python projects see irrelevant checklist items. Python-specific guidance should only appear in the Python language section.

---

### 4. Project-Specific Configuration Examples

**File:** `principles/definition-of-done.md`

- Line 34: Example uses `openrouter_llm_model` - This is a `second_voice` config key, not generic
- Line 36: References `config.example.json` - Generic concept but with `second_voice` naming convention
- Line 37: References `config.example.json` - Same issue

**Issue:** Examples should be generic (e.g., `my_api_key`) or bracketed (e.g., `[config-example-file]`).

---

### 5. Project-Specific Examples in Patterns

**File:** `patterns/prompt-patterns.md`

- Line 225: `pytest --cov=src/second_voice` - Should be generic like `pytest --cov=src/[your-package]`
- Line 420: `src/second_voice/core/processor.py` - Project-specific path
- Lines 632, 649: Mentions specific providers: "Groq", "Ollama" - Second-voice specific, should be generic like `[API Provider A]`

**Issue:** Patterns lose reusability when they use real project names instead of placeholders.

---

## Proposed Solutions

### Solution 1: Replace `dev_notes/` with Configurable Structure

**In `workflow/core.md`, change:**

```markdown
# BEFORE (line 18-19)
- When a prompt involves planning, represent the planning in `dev_notes/specs`
- Create a summary of what the user is asking for or what they want in `dev_notes/specs/YYYY-MM-DD_HH-MM-SS_spec-description.md`

# AFTER (generalized)
- When a prompt involves planning, represent the planning in your project's planning directory (e.g., `dev_notes/specs`, `docs/planning`, `.ai-plans`)
- Create a summary of what the user is asking for in `[PLANNING_DIR]/YYYY-MM-DD_HH-MM-SS_spec-description.md` (timestamp-based filename)
```

Apply similar changes to:
- Line 27: `dev_notes/project_plans/` → `[PLANNING_DIR]/project-plans/`
- Line 38: `dev_notes/changes/` → `[PLANNING_DIR]/changes/` or `[DOCUMENTATION_DIR]/changes/`
- Line 46: Reference the pattern but don't dictate the path

**Add a note:** This kernel uses `dev_notes/` as the default. Projects may customize this, but must maintain the subdirectory structure (specs/, project_plans/, changes/) and naming convention.

---

### Solution 2: Remove Non-Existent References

**Remove from `workflow/core.md`:**
- Line 14: Delete reference to `docs/overview.md`
  - Replace with inline definition or move "Trivial Change Definition" to this file
- Line 47: Delete reference to `docs/file-naming-conventions.md`
  - The naming pattern is already defined in the same file (line 46)

**Handle `docs/templates.md`:**
- Option A: Move it into system-prompts as `system-prompts/templates.md` (if it's truly generic)
- Option B: Keep it in projects' `docs/` and update reference to note it's project-maintained
- **Recommendation:** Option A - Move templates into system-prompts so the kernel is self-contained

---

### Solution 3: Move Python-Specific Content

**In `principles/definition-of-done.md`:**

Remove these lines and move to `languages/python/definition-of-done.md`:
```markdown
Line 32: If any new library is imported, the task is **NOT DONE** until both `requirements.txt` AND `pyproject.toml` are updated.
Line 52: - [ ] `requirements.txt` & `pyproject.toml` updated (if applicable).
```

**In `languages/python/definition-of-done.md`, add if missing:**
```markdown
## 1. Python Environment & Dependencies

- [ ] All new imports are added to `requirements.txt`
- [ ] All new imports are added to `pyproject.toml`
- [ ] Dependencies verified: `python -m venv test_venv && pip install -r requirements.txt`
```

The universal `principles/definition-of-done.md` should say:
```markdown
*   **Dependencies:**
    *   Language/framework specific checklist applies (see language-specific DoD).
```

---

### Solution 4: Generalize Configuration Examples

**In `principles/definition-of-done.md`, change:**

```markdown
# BEFORE (line 34)
If you add or modify a configuration key (e.g., `openrouter_llm_model`):

# AFTER
If you add or modify a configuration key (e.g., `api_key`, `timeout_seconds`):
```

```markdown
# BEFORE (line 36)
Update `config.example.json` to include the new key...

# AFTER
Update your project's configuration example/template file to document the new key...
(Common names: `config.example.json`, `.env.example`, `config.sample.yaml`, etc.)
```

---

### Solution 5: Generalize Prompt Patterns Examples

**In `patterns/prompt-patterns.md`:**

```markdown
# Line 225 - BEFORE
pytest --cov=src/second_voice

# AFTER
pytest --cov=src/[your-package-name]
```

```markdown
# Line 420 - BEFORE
Context:
- In src/second_voice/core/processor.py
- Saves conversation history to temp file

# AFTER
Context:
- In `src/[project]/core/processor.py` (or equivalent)
- Saves conversation history to temp file
```

```markdown
# Lines 632, 649 - BEFORE
2. Transcriber processes it (mocked Groq API)
...
- Groq API endpoint
- Ollama API endpoint

# AFTER
2. Transcriber processes it (mocked API)
...
- [External API A] endpoint
- [External API B] endpoint
```

---

## Implementation Approach

### Phase 1: Make System-Prompts Self-Contained
1. Move `docs/templates.md` → `docs/system-prompts/templates/structure.md`
2. Add a README or INDEX to `docs/system-prompts/` explaining the structure
3. Update all cross-references within system-prompts to be relative

### Phase 2: Generalize References
1. Replace `dev_notes/` with `[PLANNING_DIR]` or generic description
2. Remove references to `docs/overview.md`, `docs/file-naming-conventions.md` (non-existent)
3. Move Python-specific checks to `languages/python/`

### Phase 3: Generalize Examples
1. Replace `second_voice` with `[your-package]` or generic placeholders
2. Replace provider names (Groq, Ollama) with `[API Provider A]`, `[External Service]`
3. Replace `openrouter_llm_model` with generic `api_key` or `[config-key-name]`

### Phase 4: Document the Customization
1. Add a "Customization Guide" to `docs/system-prompts/README.md`
2. Show how projects can:
   - Keep `dev_notes/` structure or use an alternative
   - Reference their own config format
   - Populate their own project-specific docs

---

## Files to Modify

| File | Changes | Priority |
|------|---------|----------|
| `workflow/core.md` | 1. Replace `dev_notes/` with generic refs<br>2. Remove refs to non-existent docs | HIGH |
| `principles/definition-of-done.md` | 1. Remove Python-specific checklist items<br>2. Generalize config examples | HIGH |
| `patterns/prompt-patterns.md` | 1. Replace project paths with placeholders<br>2. Generalize provider names | MEDIUM |
| `languages/python/definition-of-done.md` | Add Python-specific dependency checks | HIGH |
| `docs/system-prompts/README.md` | Add customization guide | MEDIUM |

---

## Expected Outcome

After refactoring:
- ✅ System-prompts are **self-contained** (don't reference missing files)
- ✅ System-prompts are **generic** (reusable across projects)
- ✅ System-prompts are **documented** (projects know what to customize)
- ✅ No project-specific paths or provider names leak into generic templates
- ✅ Language-specific guidance stays in language-specific files
- ✅ Projects can adopt the kernel with minimal customization

---

## Questions for Review

1. Should `dev_notes/` be truly optional, or is the naming convention mandatory?
2. Should templates.md move into system-prompts, or stay in project docs?
3. Any other project-specific references I missed?
4. Should we add a "Customization Checklist" for new projects adopting the kernel?
