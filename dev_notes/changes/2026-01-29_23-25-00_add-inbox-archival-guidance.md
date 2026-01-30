# Change Documentation: Add Inbox Archival Guidance

**Status:** ad-hoc
**Related Plan:** N/A
**Session:** Close Project Documentation

---

## Summary

Added detailed guidance for archiving handled inbox requests in the Close Project process documentation (section 3.3), including standardized renaming with timestamps and integration with Phase 4 commit examples.

---

## Changes Made

### Documentation Updates

**File:** `docs/system-prompts/processes/close-project.md`

- **Added Section 3.3:** "Archive Inbox Requests" with complete checklist and rationale
  - Guidelines for identifying handled inbox items
  - Instructions for moving files to `dev_notes/inbox-archive/`
  - Timestamp format specification: `YYYY-MM-DD_HH-MM-SS_original-name.md`
  - Verification steps for clean inbox state
  - Noted as backstop for logs-first workflow

- **Updated Phase 4 Commit Examples:** Added three code examples showing how to stage inbox directories:
  - For code changes with change documentation
  - For documentation-only changes
  - For project plan updates
  - Pattern: `git add dev_notes/inbox/ dev_notes/inbox-archive/  # If inbox items were archived`

---

## Files Modified

- `docs/system-prompts/processes/close-project.md` (+13 lines)

---

## Verification

**Command:** `git show f3b69b0`

**Output:**
```
commit f3b69b0 docs: add inbox archival guidance to Close Project process
Author: Anthropic Claude <claude@anthropic.com>
Date:   Wed Jan 29 23:25:19 2026 +0000

    docs: add inbox archival guidance to Close Project process

    Add section 3.3 to document archiving handled inbox requests with timestamps, and update Phase 4 commit examples to include inbox directories.

    Co-Authored-By: Claude Haiku 4.5 <noreply@anthropic.com>

 docs/system-prompts/processes/close-project.md | 13 +++++++++++++
 1 file changed, 13 insertions(+)

diff --git a/docs/system-prompts/processes/close-project.md b/docs/system-prompts/processes/close-project.md
index a7d2995..1052682 100644
--- a/docs/system-prompts/processes/close-project.md
+++ b/docs/system-prompts/processes/close-project.md
@@ -196,6 +196,16 @@ Check that the change documentation includes:
 - [ ] **Known Issues:** Any caveats, limitations, or future work noted
 - [ ] **Integration with DoD:** Explicit checklist against Definition of Done

+#### 3.3 Archive Inbox Requests
+
+**Goal:** Ensure handled inbox requests are properly archived.
+
+- [ ] Identify any `dev_notes/inbox/` files addressed by this session
+- [ ] Move them to `dev_notes/inbox-archive/`
+- [ ] Rename with timestamp: `YYYY-MM-DD_HH-MM-SS_original-name.md`
+- [ ] Verify `dev_notes/inbox/` is clean (or only contains unrelated items)
+- [ ] *Note: This serves as a backstop if the logs-first workflow didn't already archive them.*
+
 ---

 ### Phase 4: Commit Changes
@@ -228,6 +238,7 @@ git add src/
 git add tests/
 git add requirements.txt
 git add dev_notes/changes/YYYY-MM-DD_HH-MM-SS_description.md
+git add dev_notes/inbox/ dev_notes/inbox-archive/  # If inbox items were archived
 ```

 **For documentation-only changes:**
@@ -235,12 +246,14 @@ git add dev_notes/changes/YYYY-MM-DD_HH-MM-SS_description.md
 # Stage docs and change documentation together
 git add docs/
 git add dev_notes/changes/YYYY-MM-DD_HH-MM-SS_description.md
+git add dev_notes/inbox/ dev_notes/inbox-archive/  # If inbox items were archived
 ```

 **For project plan updates:**
 ```bash
 # Stage completed plan status update
 git add dev_notes/project_plans/YYYY-MM-DD_HH-MM-SS_description.md
+git add dev_notes/inbox/ dev_notes/inbox-archive/  # If inbox items were archived
 ```
```

Git status confirms clean working tree.

---

## Definition of Done

✅ **Documentation-Specific Criteria:**
- ✅ File naming: lowercase-kebab.md (process document)
- ✅ Reference formatting: Uses markdown links and backticks correctly
- ✅ Content clarity: Complete section with examples and rationale
- ✅ Integration: Properly integrated into existing process flow (Phase 3.3)

✅ **Documentation Quality:**
- ✅ Section title and goal clearly stated
- ✅ Checklist format for easy reference
- ✅ Integrated with both Phase 3 and Phase 4
- ✅ Added code examples showing integration points

---

## Known Issues

None. This is a straightforward documentation addition with no breaking changes or limitations.
