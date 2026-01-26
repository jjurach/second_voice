# Project Plan: Refactor System-Prompts for Independence

**Created:** 2026-01-25 23:00:00
**Status:** Draft
**Related Spec:** `dev_notes/system-prompts-refactor-proposal.md`

## Overview

Remove all project-specific references from `docs/system-prompts/` to make the Agent Kernel reusable across projects. Replace hardcoded paths (`dev_notes/`, `second_voice`) with generic placeholders, eliminate references to non-existent files, and move Python-specific guidance to language-specific sections. Result: a self-contained, zero-dependency kernel that new projects can adopt with minimal customization.

---

## Phase 1: Analyze & Prepare

**Goal:** Document current state and prepare for systematic refactoring.

### 1.1 Verify all problematic references
- Read each system-prompts file
- Confirm issues identified in proposal
- Note any additional project-specific references
- Document line numbers and context

### 1.2 Create refactoring checklist
- List all specific changes required
- Prioritize by impact (HIGH/MEDIUM/LOW)
- Identify ripple effects (e.g., bootstrap.py references)

### 1.3 Verify bootstrap.py compatibility
- Check if bootstrap.py needs updates (unlikely, it just syncs content)
- Confirm it doesn't hardcode project-specific expectations

---

## Phase 2: Generalize `workflow/core.md`

**Goal:** Remove all `dev_notes/` prescriptions and project-specific directory references.

### 2.1 Replace directory structure references
**Lines to change:** 18, 19, 27, 38, 46

**Before:**
```markdown
- When a prompt involves planning, represent the planning in `dev_notes/specs`
- Create a summary of what the user is asking for or what they want in `dev_notes/specs/YYYY-MM-DD_HH-MM-SS_spec-description.md`
- Save the plan to `dev_notes/project_plans/YYYY-MM-DD_HH-MM-SS_description.md`
- After each logical change, create or update a **Change Documentation** entry in `dev_notes/changes/`
- All Project Plans and Change Documentation in `dev_notes/` MUST use the `YYYY-MM-DD_HH-MM-SS_description.md` format.
```

**After:**
```markdown
- When a prompt involves planning, represent the planning in your project's planning directory (e.g., `dev_notes/specs`, `docs/planning`, `.ai-plans/`)
- Create a summary of what the user is asking for in `[PLANNING_DIR]/specs/YYYY-MM-DD_HH-MM-SS_spec-description.md` (timestamp-based filename)
- Save the plan to `[PLANNING_DIR]/project_plans/YYYY-MM-DD_HH-MM-SS_description.md`
- After each logical change, create or update a **Change Documentation** entry in `[PLANNING_DIR]/changes/`
- All Project Plans and Change Documentation MUST use the `YYYY-MM-DD_HH-MM-SS_description.md` filename format. (See your project's implementation for the directory location.)
```

### 2.2 Remove references to non-existent files
**Lines to change:** 14, 47

**Line 14 - Remove invalid reference to `docs/overview.md`:**
- Current: `> **Trivial Change Definition:** Non-functional changes like fixing typos in comments or code formatting. The full definition and examples are in `docs/overview.md`.`
- Change to: Move the definition inline (full text already provided above in the list)
- New text: `> **Trivial Change Definition:** Non-functional changes like fixing typos in comments or code formatting.`

**Line 47 - Remove invalid reference to `docs/file-naming-conventions.md`:**
- Current: `All new documentation files in `docs/` MUST use `lowercase-kebab.md` naming convention (see `docs/file-naming-conventions.md`).`
- Change to: `All new documentation files in `docs/` MUST use `lowercase-kebab.md` naming convention.`

### 2.3 Update reference to `docs/templates.md`
**Lines to change:** 25, 38

- Current reference assumes `docs/templates.md` is project-maintained
- Change to reference a path within system-prompts OR note this is project-maintained
- Recommended: `Use the Project Plan Structure in your project's templates documentation (e.g., `docs/templates.md`, `.ai-templates/plans.md`)` or keep if truly moving it into system-prompts

---

## Phase 3: Generalize `principles/definition-of-done.md`

**Goal:** Remove Python-specific items and project-specific examples.

### 3.1 Remove Python-specific dependency checks
**Lines to change:** 32, 52

**Line 32 - Remove Python-specific mandate:**
- Current: `If any new library is imported, the task is **NOT DONE** until both `requirements.txt` AND `pyproject.toml` are updated.`
- Change to: `If any new library is imported, the task is **NOT DONE** until all dependency files are updated (language-specific).`

**Line 52 - Remove Python-specific checklist:**
- Current: `- [ ] `requirements.txt` & `pyproject.toml` updated (if applicable).`
- Change to: `- [ ] Dependencies updated in language-specific formats (if applicable).`

### 3.2 Generalize configuration example
**Lines to change:** 34, 35, 36, 37

**Before:**
```markdown
If you add or modify a configuration key (e.g., `openrouter_llm_model`):
    1.  Update `docs/implementation-reference.md` (or relevant doc).
    2.  Update `config.example.json` to include the new key with a safe default or placeholder.
*   **Secrets:** Never hardcode secrets. Ensure they are read from env vars or config, and documented in `config.example.json`.
```

**After:**
```markdown
If you add or modify a configuration key (e.g., `api_timeout`, `max_retries`):
    1.  Update your project's implementation documentation (e.g., `docs/implementation-reference.md`, `docs/config.md`).
    2.  Update your project's configuration example/template file (e.g., `config.example.json`, `.env.example`, `config.sample.yaml`) to include the new key with a safe default or placeholder.
*   **Secrets:** Never hardcode secrets. Ensure they are read from env vars or config, and documented in your configuration example/template file.
```

### 3.3 Add reference to language-specific DoD
**After line 54, add:**
```markdown
## Language-Specific Requirements

- **Python projects:** See `docs/system-prompts/languages/python/definition-of-done.md` for pytest, requirements.txt, and type hint requirements.
- **JavaScript projects:** (When available)
- **Other languages:** Language-specific DoD will be provided.
```

---

## Phase 4: Generalize `languages/python/definition-of-done.md`

**Goal:** Ensure all Python-specific requirements are in the right place.

### 4.1 Verify Python-specific content exists
- Confirm file contains pytest requirements
- Confirm it documents requirements.txt and pyproject.toml
- Confirm it covers type hints, docstrings, etc.

### 4.2 Add dependency update requirements (if missing)
**Add new section if not present:**
```markdown
## 1. Python Environment & Dependencies

**Mandatory Checks:**
- [ ] All new imports are added to `requirements.txt`
- [ ] All new imports are added to `pyproject.toml` (if project uses it)
- [ ] Dependencies are pinned to specific versions (e.g., `pytest==9.0.2`)
- [ ] Virtual environment can be recreated cleanly: `python -m venv /tmp/test_venv && pip install -r requirements.txt`
```

### 4.3 Verify no universal DoD duplication
- Ensure sections are not duplicated from `principles/definition-of-done.md`
- If duplicated, remove from this file (keep only in universal)

---

## Phase 5: Generalize `patterns/prompt-patterns.md`

**Goal:** Replace all project-specific paths and provider names with generic placeholders.

### 5.1 Replace project package name
**Lines to change:** 225, 420

**Line 225 - Replace in example:**
- Before: `pytest --cov=src/second_voice`
- After: `pytest --cov=src/[your-package-name]`

**Line 420 - Replace in example:**
- Before: `- In src/second_voice/core/processor.py`
- After: `- In `src/[project-name]/core/processor.py` (or equivalent)`

### 5.2 Replace provider-specific names
**Lines to change:** 632, 639, 649, 656, 657

**Line 632 - Generalize API reference:**
- Before: `2. Transcriber processes it (mocked Groq API)`
- After: `2. Transcriber processes it (mocked [External API A])`

**Line 639 - Generalize provider:**
- Before: `- Groq API - (mocked, returns transcript)`
- After: `- [External API A] - (mocked, returns result)`

**Line 649 - Generalize endpoint:**
- Before: `- Groq API endpoint`
- After: `- [External API A] endpoint`

**Line 649 - Generalize endpoint:**
- Before: `- Ollama API endpoint`
- After: `- [External API B] endpoint`

**Lines 656-657 - Generalize failures:**
- Before: `- What if Groq returns error?` and `- What if Ollama is unreachable?`
- After: `- What if [External API A] returns error?` and `- What if [External API B] is unreachable?`

### 5.3 Add note about examples
**At top of patterns document, add:**
```markdown
**Note:** Examples in this document use placeholder names like `[your-package]` and `[External API]`. Replace these with your actual project names and service names.
```

---

## Phase 6: Handle `docs/templates.md`

**Goal:** Ensure templates.md is either self-contained or properly documented as project-maintained.

### 6.1 Decide on templates.md location
**Two options:**

**Option A: Move into system-prompts** (RECOMMENDED)
- Move `docs/templates.md` → `docs/system-prompts/templates/structure.md`
- Pros: Makes kernel self-contained; new projects get templates immediately
- Cons: Adds another file to system-prompts

**Option B: Keep in project docs, update references**
- Keep `docs/templates.md` in project
- Update `workflow/core.md` to note: "Your project should maintain `docs/templates.md` (template structure examples)"
- Pros: Keeps system-prompts minimal
- Cons: New projects must create templates.md from scratch

**Recommendation:** Option A for true independence. Execute if Option A chosen:
- Create directory: `docs/system-prompts/templates/`
- Move file: `docs/templates.md` → `docs/system-prompts/templates/structure.md`
- Update reference in `workflow/core.md` line 25 to: `docs/system-prompts/templates/structure.md`

### 6.2 Update README if moved
If templates.md is moved to system-prompts:
- Update `docs/system-prompts/README.md` to reference the new location
- Add to "What's Included" section

---

## Phase 7: Update System-Prompts README

**Goal:** Document how new projects should customize the kernel.

### 7.1 Add Customization Guide section
**Add to `docs/system-prompts/README.md`:**

```markdown
## Customizing for Your Project

This Agent Kernel is **generic and reusable**. To adopt it in your project:

### 1. Choose Your Planning Directory
The kernel references `[PLANNING_DIR]`. Choose your naming:
- Option A: `dev_notes/` (recommended, matches examples)
- Option B: `docs/planning/`
- Option C: `.ai-plans/`
- Option D: Any other directory

Update references in your `AGENTS.md` after syncing kernel content.

### 2. Create Project-Specific Documentation
After adopting the kernel, create:
- `docs/templates.md` - Document templates (copy from `docs/system-prompts/templates/structure.md`)
- `docs/file-naming-conventions.md` - Your project's file naming rules (optional)
- `docs/implementation-reference.md` - Patterns and examples for your specific tech stack

### 3. Language-Specific Setup
- **Python projects:** Use `languages/python/definition-of-done.md` as-is; no customization needed
- **JavaScript projects:** Language-specific DoD coming soon
- **Other languages:** Create similar structure in `docs/system-prompts/languages/[your-language]/definition-of-done.md`

### 4. Provider/Service Names
Replace placeholders in `patterns/prompt-patterns.md` examples with your actual:
- External API names (e.g., Groq → replace with `[External API A]` or your service name)
- Package names (e.g., `second_voice` → replace with `[your-package]`)
```

### 7.2 Add Index of Included Content
**Add section explaining what's generic vs. project-specific:**

```markdown
## Generic vs. Project-Specific Content

### Generic (Use As-Is)
- `workflow/core.md` - Core workflow steps (applies to all projects)
- `principles/definition-of-done.md` - Universal acceptance criteria
- `patterns/prompt-patterns.md` - Prompt structures (customize examples)
- `languages/python/definition-of-done.md` - Python-specific checks

### Project-Maintained (You Create)
- `AGENTS.md` - Sync with kernel, then customize for your project
- `dev_notes/` (or your chosen planning dir) - Your planning files
- `docs/templates.md` - Your template documentation
- `docs/implementation-reference.md` - Your tech stack patterns
```

---

## Implementation Order

1. **Phase 1** - Analyze & Prepare (foundational)
2. **Phase 2** - Generalize `workflow/core.md` (foundational, most references)
3. **Phase 3** - Generalize `principles/definition-of-done.md` (foundational)
4. **Phase 4** - Generalize `languages/python/definition-of-done.md` (consolidation)
5. **Phase 5** - Generalize `patterns/prompt-patterns.md` (examples)
6. **Phase 6** - Handle `docs/templates.md` (optional, depends on decision)
7. **Phase 7** - Update System-Prompts README (documentation)

---

## Files to Create/Modify

**Modified Files:**
- `docs/system-prompts/workflow/core.md` - Generalize directory refs, remove broken links
- `docs/system-prompts/principles/definition-of-done.md` - Remove Python-specific, generalize examples
- `docs/system-prompts/languages/python/definition-of-done.md` - Add dependency requirements section
- `docs/system-prompts/patterns/prompt-patterns.md` - Replace project paths and provider names
- `docs/system-prompts/README.md` - Add customization guide and index

**Possibly Created (Phase 6 decision):**
- `docs/system-prompts/templates/` - Directory for templates (if Option A chosen)
- `docs/system-prompts/templates/structure.md` - Moved from `docs/templates.md`

**Not Modified:**
- `bootstrap.py` - No changes needed; it only syncs content
- Source code files - No implementation changes

---

## Success Criteria

✅ All project-specific references removed from system-prompts
✅ No references to non-existent files remain
✅ All `dev_notes/` references replaced with `[PLANNING_DIR]` or generic descriptions
✅ All provider names (Groq, Ollama) replaced with placeholders
✅ All project paths (`second_voice`) replaced with `[your-package]`
✅ Python-specific requirements isolated in `languages/python/` section
✅ Configuration examples use generic names (not `openrouter_llm_model`)
✅ `docs/system-prompts/README.md` includes customization guide
✅ System-prompts are self-contained and zero-dependency
✅ New projects can adopt kernel and run `bootstrap.py` without modification

---

## Risk Assessment

- **Low Risk:** Generalization of references (mechanics are straightforward, low impact)
- **Low Risk:** Removal of broken links (they point nowhere anyway)
- **Medium Risk:** Moving Python-specific content (must not lose anything; verify duplication)
- **Medium Risk:** Decision on templates.md location (slight impact on bootstrap.py reference, easy to handle)
- **Low Risk:** README updates (purely documentation, no code impact)

**Mitigation:**
- Review each change against original proposal
- Use search/grep to verify all instances are caught
- Test bootstrap.py still works after modifications
- Verify existing projects' AGENTS.md still syncs correctly

---

## Estimated Scope

- **Documentation changes:** ~150-200 lines modified
- **File moves:** 1 file (templates.md, if Option A)
- **New content:** README additions (~80 lines)
- **Code changes:** 0 (system-prompts are markdown only)
- **Breaking changes:** None (only generalizations)

---

## Testing Strategy

### 1. Verify Syntax
```bash
# Check all markdown files are valid
find docs/system-prompts -name "*.md" -exec grep -l "^\[" {} \;  # Check for broken references
```

### 2. Verify No Project-Specific Content Remains
```bash
# Search for project-specific terms
grep -r "second_voice\|second-voice\|dev_notes/" docs/system-prompts/
# Should return only placeholder references like [PLANNING_DIR], [your-package]
```

### 3. Verify bootstrap.py Still Works
```bash
# Run bootstrap.py to ensure it still syncs correctly
python3 docs/system-prompts/bootstrap.py --analyze
# Should show all sections found and ready to sync
```

### 4. Verify Existing AGENTS.md Still Syncs
```bash
# Backup current AGENTS.md, then test sync
cp AGENTS.md AGENTS.md.backup
python3 docs/system-prompts/bootstrap.py --dry-run
# Should show what would be updated (or "No changes needed")
```

---

## Known Issues & Notes

- **Decision Required:** Should `docs/templates.md` move into system-prompts (Phase 6)?
  - This plan assumes Option A (move it), but can be skipped if staying in project docs
  - If keeping in project: Update reference in workflow/core.md line 25 to note it's project-maintained

- **Future Work:** Add language-specific DoD for JavaScript, Go, Rust, etc.
  - This plan focuses on generalizing existing Python guidance
  - Structure is in place for new language sections

- **bootstrap.py Compatibility:** The tool should need no changes
  - It only reads files from the standard paths
  - Generalizing content (not structure) doesn't affect it

---

## Definition of Done Checklist

- [ ] All 5 system-prompts files modified per plan
- [ ] No references to `docs/overview.md`, `docs/file-naming-conventions.md` remain
- [ ] All `dev_notes/` references replaced with `[PLANNING_DIR]` or generic equivalents
- [ ] All `second_voice` references replaced with `[your-package]` or removed
- [ ] All Groq/Ollama references replaced with `[External API A]` or `[External API B]`
- [ ] Python-specific content consolidated in `languages/python/` section
- [ ] README includes customization guide for new projects
- [ ] Templates.md decision made and implemented (Phase 6)
- [ ] No broken links remain in system-prompts
- [ ] bootstrap.py --analyze still works without errors
- [ ] Existing AGENTS.md still syncs correctly
- [ ] Verification: `grep -r "second_voice\|dev_notes/" docs/system-prompts/` returns no project-specific references
