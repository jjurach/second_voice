# Change Documentation: Simple Mandatory Reading Lists Implementation

**Date:** 2026-01-28 10:36:41
**Status:** Completed
**Type:** Documentation & Infrastructure
**Related Project Plan:** `dev_notes/project_plans/2026-01-28_10-36-41_simple-mandatory-reading-lists.md`

---

## Summary

Successfully implemented a simple mandatory reading system that ensures agents see mandatory content at session start. The solution uses explicit reading lists in AGENTS.md and tool-specific guides rather than complex assembly machinery, respecting bootstrap.py's anemic entry point architecture.

---

## Changes Made

### 1. Created Project-Specific Mandatory Instructions

**File:** `docs/mandatory.md`

**Content:**
- Second Voice project overview
- Key directory structure
- Documentation references
- Development guidelines (Python, dependencies, configuration, code style, testing)
- Prohibited actions
- When to stop and ask for help
- Definition of Done quick reference

**Purpose:** Provides project-specific rules separate from workflow-generic content.

---

### 2. Created Mandatory Reading List Section

**File:** `docs/system-prompts/mandatory-reading.md`

**Content:**
- Title: "MANDATORY READING - READ FIRST, EVERY SESSION"
- Why these files are mandatory (with clear reasoning)
- The three mandatory files with descriptions:
  1. Core Workflow (logs-first.md) - Step-by-step workflow
  2. Definition of Done (definition-of-done.md) - Completion criteria
  3. Project Guidelines (mandatory.md) - Second Voice specific rules
- Optional resources (architecture, implementation reference, workflows)
- Self-check verification questions (7 questions)
- Emphasis that reading is REQUIRED, not suggested

**Purpose:** Creates a single authoritative list of mandatory reading, injected into AGENTS.md by bootstrap.py.

---

### 3. Updated bootstrap.py for Automatic Injection

**File:** `docs/system-prompts/bootstrap.py`

**Changes:**
- Added section mapping: `"MANDATORY-READING": "mandatory-reading.md"` (line 135)
- Added to sections sync list: `("MANDATORY-READING", "mandatory-reading.md")` (line 313)
- MANDATORY-READING is first section (ensures it appears before other content)

**Result:**
- `bootstrap.py --commit` now injects the mandatory reading section into AGENTS.md automatically
- AGENTS.md now contains the MANDATORY READING section at the top
- Future edits to mandatory-reading.md will be synced automatically

---

### 4. Updated Tool-Specific Guides

**Files Updated:**
- `docs/system-prompts/tools/claude-code.md`
- `docs/system-prompts/tools/aider.md`
- `docs/system-prompts/tools/gemini.md`
- `docs/system-prompts/tools/cline.md`

**Changes:** Added prominent section immediately after title:
```markdown
## 🚨 MANDATORY READING FIRST 🚨

**STOP!** Before reading this guide, you MUST first read the files listed in the
"MANDATORY READING" section of [AGENTS.md](../../../AGENTS.md#mandatory-reading---read-first-every-session).

**Quick links to mandatory files:**
1. [Core Workflow](../workflows/logs-first.md) - How to approach all tasks
2. [Definition of Done](../../definition-of-done.md) - Completion criteria
3. [Project Guidelines](../../mandatory.md) - Second Voice specific rules

**Have you read all three?** ✓ Yes, continue. ✗ No, read them now.
```

**Purpose:** Emphasizes mandatory reading at the start of each tool guide, directing agents to AGENTS.md before proceeding with tool-specific content.

---

## Verification Results

### Content Verification

✅ All mandatory files exist:
- docs/mandatory.md - Created
- docs/system-prompts/mandatory-reading.md - Created
- AGENTS.md - Has MANDATORY READING section injected
- Tool guides - All have prominent mandatory reading section

✅ Bootstrap.py injection working:
```bash
$ python docs/system-prompts/bootstrap.py --commit
✓ Updated section: MANDATORY-READING
✓ Wrote: /home/phaedrus/AiSpace/second_voice/AGENTS.md
✓ Successfully synced /home/phaedrus/AiSpace/second_voice/AGENTS.md
```

✅ AGENTS.md contains mandatory reading:
```bash
$ grep -A 5 "MANDATORY READING" AGENTS.md | head -20
# MANDATORY READING - READ FIRST, EVERY SESSION

**CRITICAL:** Before starting ANY task in this project, you MUST read these files in this exact order.

## Why These Files Are Mandatory
```

✅ All tool guides updated:
```bash
$ grep -c "MANDATORY READING" docs/system-prompts/tools/claude-code.md
2
$ grep -c "MANDATORY READING" docs/system-prompts/tools/aider.md
2
$ grep -c "MANDATORY READING" docs/system-prompts/tools/gemini.md
2
$ grep -c "MANDATORY READING" docs/system-prompts/tools/cline.md
2
```

### Testing Verification

✅ Tested bootstrap.py integration:
- Section injection working correctly
- MANDATORY-READING appears as first section in AGENTS.md
- MANDATORY-READING section mapping properly configured

✅ Cross-reference links verified:
- AGENTS.md → mandatory-reading.md (injected content)
- mandatory-reading.md → tool guides
- Tool guides → AGENTS.md mandatory section (with anchor link)
- Tool guides → core workflow, definition of done, project guidelines

✅ File paths all relative and correct:
- Links in guides point to actual files
- Relative paths work from various locations

---

## Files Modified/Created

### Created
- `docs/mandatory.md` - Project-specific mandatory instructions (64 lines)
- `docs/system-prompts/mandatory-reading.md` - Mandatory reading list (79 lines)

### Modified
- `docs/system-prompts/bootstrap.py` - Add section mapping and sync config (2 changes, +3 lines)
- `docs/system-prompts/tools/claude-code.md` - Add mandatory reading section (18 new lines at top)
- `docs/system-prompts/tools/aider.md` - Add mandatory reading section (18 new lines at top)
- `docs/system-prompts/tools/gemini.md` - Add mandatory reading section (18 new lines at top)
- `docs/system-prompts/tools/cline.md` - Add mandatory reading section (18 new lines at top)
- `AGENTS.md` - Now contains injected MANDATORY-READING section (managed by bootstrap.py)

---

## Definition of Done Verification

✅ Code follows project patterns
  - Bootstrap.py changes follow existing patterns
  - New markdown files follow project conventions
  - Section injection follows bootstrap.py architecture

✅ No new imports or dependencies
  - No external dependencies added
  - No Python package changes required

✅ Configuration changes handled
  - No new config keys added
  - config.example.json not affected

✅ Documentation complete
  - All files documented above
  - Purpose of each file explained
  - Cross-references documented

✅ Change documentation created
  - This file serves as complete change documentation
  - Verification results included
  - Known issues documented below

---

## How This Solution Works

### For Claude Code Users

1. User starts Claude Code in project: `claude-code`
2. Claude Code reads `CLAUDE.md` (anemic, 20 lines)
3. CLAUDE.md points to AGENTS.md as primary reference
4. AGENTS.md now starts with "MANDATORY READING" section
5. Agent reads the three mandatory files before proceeding
6. Agent reads tool-specific guide, which re-emphasizes mandatory reading
7. Agent is now fully informed with no gaps

### For Other Tools (Aider, Gemini, Cline)

Same flow:
1. Tool reads its entry point (AIDER.md, GEMINI.md, CLINE.md)
2. Entry point points to AGENTS.md
3. AGENTS.md contains mandatory reading
4. Tool guide re-emphasizes mandatory reading
5. Agent is prepared before implementing

### For Maintainers

- Edit `docs/system-prompts/mandatory-reading.md` to update the mandatory reading list
- Edit `docs/mandatory.md` for project-specific rules
- Edit `docs/system-prompts/bootstrap.py` section list to add/remove mandatory sections
- Run `python docs/system-prompts/bootstrap.py --commit` to sync AGENTS.md
- No manual editing of AGENTS.md (it's auto-generated)

---

## Known Issues

### Tool Entry Point Line Count

**Issue:** Tool entry points (CLAUDE.md, AIDER.md, CLINE.md, GEMINI.md) are 35 lines instead of the anemic maximum of 20 lines.

**Status:** Pre-existing (not caused by this implementation)

**Reason:** The templates in `bootstrap.py` `get_tool_entry_point_template()` method include extra sections (System Architecture, System-Prompts Processes) that exceed the anemic format constraint.

**Impact:** Per `docs/system-prompts/processes/tool-entry-points.md`, these files should be 20 lines max for anemic format. Current templates are 35 lines.

**Recommendation:** Future work to simplify entry point templates to meet anemic constraint.

**Verification:**
```bash
$ python docs/system-prompts/bootstrap.py --validate-tool-entries
⚠️  CLAUDE.md:
   - File is 35 lines (should be ≤20 for anemic format)
```

---

## Notes

### Design Choices

1. **Mandatory reading list in AGENTS.md** - Makes it visible to all agents regardless of entry point
2. **Tool guides emphasize first** - Reinforces importance before tool-specific content
3. **Three mandatory files** - Not more (avoids overwhelming), not less (ensures essentials covered)
4. **Bootstrap.py injection** - Respects existing architecture, no generated files to maintain
5. **Self-check questions** - Helps agents verify they've actually read the files

### Why This Approach Works

- **Simple:** No build steps, no complex machinery
- **Transparent:** Users see actual mandatory files, not compiled/generated content
- **Maintainable:** Changes to mandatory reading are immediate (no re-generation)
- **Respects architecture:** Works with bootstrap.py's section injection system
- **Effective:** Emphasizes mandatory reading at multiple points (AGENTS.md, each tool guide)

### Alternative Approaches Considered

- **Complex assembly system** (WONT-DO) - Over-engineered, too much complexity
- **No explicit lists** - Doesn't guarantee agents read mandatory content
- **Longer reading lists** - Overwhelms with non-essential content

This approach balances simplicity with effectiveness.

---

## Future Enhancements (Not Implemented)

These could be explored if real-world testing shows they're needed:
1. Make mandatory reading links more prominent (colors, styling in markdown)
2. Add verification confirmation ("I confirm I've read all mandatory files")
3. Create a quick checklist agents can copy/paste
4. Add estimated reading time for each mandatory file
5. Create a video walkthrough of the mandatory files

**Recommendation:** Don't implement until evidence shows they're needed.

---

## Implementation Status

✅ Phase 1: Create docs/mandatory.md
✅ Phase 2: Create docs/system-prompts/mandatory-reading.md
✅ Phase 3: Update bootstrap.py + AGENTS.md injection
✅ Phase 4: Update all tool-specific guides
✅ Phase 5: Verify entry points
✅ Phase 6: This change documentation

**All phases complete. Implementation successful.**

---
