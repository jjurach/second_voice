# Project Plan: Fix Bootstrap Relative Link Problem

**Status:** Completed
**Created:** 2026-01-29 09:26:14
**Completed:** 2026-01-29 09:35:57
**Spec:** [2026-01-29_09-26-14_fix-bootstrap-relative-links.md](../specs/2026-01-29_09-26-14_fix-bootstrap-relative-links.md)
**Change Log:** [2026-01-29_09-35-57_bootstrap-link-transformation.md](../changes/2026-01-29_09-35-57_bootstrap-link-transformation.md)

## Overview

Implement link rewriting in `bootstrap.py` to fix relative links when assembling `AGENTS.md` from component files.

## Implementation Steps

### Step 1: Create LinkTransformer Class

**File:** `docs/system-prompts/bootstrap.py` (add after line 14)

**Actions:**
1. Add `LinkTransformer` class with static/class methods
2. Implement `extract_anchor()` to handle `#fragment` preservation
3. Implement `transform_link()` with comprehensive logic:
   - Skip external URLs (`http://`, `https://`, `ftp://`)
   - Skip self-references (`#anchor`)
   - Skip absolute paths (`/absolute/path`)
   - Transform relative paths (`../file.md`, `./file.md`)
   - Handle path resolution using `pathlib.Path`
   - Preserve anchors during transformation
   - Return tuple `(transformed_link, warning_message)`

**Estimated lines:** ~60 lines

**Edge cases to handle:**
- External URLs: preserve unchanged
- Anchor-only links: preserve unchanged
- Absolute paths: preserve unchanged
- Links with anchors: preserve anchor after transformation
- Links outside project: warn but preserve
- Malformed links: warn and skip transformation

### Step 2: Add Link Transformation Helper

**File:** `docs/system-prompts/bootstrap.py` (add method to Bootstrap class after line 66)

**Actions:**
1. Create `_transform_links_in_content(content, source_file, target_file)` method
2. Use regex to find all markdown links matching pattern `\[([^\]]+)\]\(([^)]+)\)`
3. For each link:
   - Call `LinkTransformer.transform_link()`
   - Collect warnings
   - Replace link in content
4. Print all warnings after transformation
5. Return transformed content

**Estimated lines:** ~25 lines

### Step 3: Modify _read_file() Method

**File:** `docs/system-prompts/bootstrap.py` (replace lines 60-66)

**Actions:**
1. Add optional parameters:
   - `transform_links: bool = False`
   - `source_file_relative: str = None`
   - `target_file_relative: str = None`
2. Add conditional transformation:
   ```python
   if transform_links and source_file_relative and target_file_relative:
       content = self._transform_links_in_content(
           content, source_file_relative, target_file_relative
       )
   ```
3. Update docstring to document new parameters

**Estimated lines:** ~15 lines (replaces 7 lines)

### Step 4: Update load_system_prompt() Method

**File:** `docs/system-prompts/bootstrap.py` (around line 160-183)

**Actions:**
1. Calculate source and target relative paths:
   ```python
   source_relative = os.path.join("docs", "system-prompts", section_map[section_name])
   target_relative = "AGENTS.md"
   ```
2. Update `_read_file()` call to pass transformation parameters:
   ```python
   content = self._read_file(
       file_path,
       transform_links=True,
       source_file_relative=source_relative,
       target_file_relative=target_relative
   )
   ```

**Estimated lines:** ~10 lines added

### Step 5: Create Unit Tests

**File:** `docs/system-prompts/tests/test_link_transformation.py` (new file)

**Actions:**
1. Create test class `TestLinkTransformer`
2. Implement tests:
   - `test_parent_directory_link()`: `../file.md` → `docs/file.md`
   - `test_anchor_preservation()`: `../file.md#section` → `docs/file.md#section`
   - `test_external_url_unchanged()`: `https://example.com` preserved
   - `test_anchor_only_unchanged()`: `#section` preserved
   - `test_absolute_path_unchanged()`: `/absolute/path` preserved
   - `test_multiple_parent_traversal()`: `../../file.md` transformation
   - `test_warning_for_outside_project()`: verify warning issued
3. Add test execution block for `python3 -m unittest`

**Estimated lines:** ~100 lines

### Step 6: Update Documentation

**File:** `docs/system-prompts/README.md`

**Actions:**
1. Add new section "## Link Transformation"
2. Document how transformation works
3. Provide examples:
   - Before: `[DoD](../definition-of-done.md)` in source
   - After: `[DoD](docs/definition-of-done.md)` in AGENTS.md
4. List what gets transformed vs. preserved
5. Add note about automatic transformation during bootstrap

**Estimated lines:** ~30 lines added

### Step 7: Testing and Verification

**Actions:**
1. Run unit tests:
   ```bash
   python3 -m pytest docs/system-prompts/tests/test_link_transformation.py -v
   ```
   Expected: All tests pass

2. Run bootstrap with transformation:
   ```bash
   python3 docs/system-prompts/bootstrap.py --commit
   ```
   Expected: No errors, no warnings (or only expected warnings)

3. Run document integrity scan:
   ```bash
   python3 docs/system-prompts/docscan.py
   ```
   Expected: 0 broken links in `AGENTS.md`

4. Manual verification:
   - Open `AGENTS.md` and click links → should work
   - Open `docs/system-prompts/mandatory-reading.md` and click links → should work
   - Run bootstrap again → output identical (idempotent)

## File Changes Summary

### Files to Modify

1. **`docs/system-prompts/bootstrap.py`**
   - Add `LinkTransformer` class (~60 lines)
   - Add `_transform_links_in_content()` method (~25 lines)
   - Modify `_read_file()` method (~15 lines)
   - Update `load_system_prompt()` method (~10 lines)
   - **Total:** ~110 lines added/modified

2. **`docs/system-prompts/README.md`**
   - Add "Link Transformation" section (~30 lines)

### Files to Create

1. **`docs/system-prompts/tests/test_link_transformation.py`**
   - New test file (~100 lines)

### Files to Verify (no changes)

- `AGENTS.md` - verify assembled links work after bootstrap
- `docs/system-prompts/mandatory-reading.md` - verify source links still work
- All other source files in `docs/system-prompts/` - verify unchanged

## Critical Paths

1. **LinkTransformer.transform_link()** - Core transformation logic
   - Must handle all edge cases correctly
   - Must preserve anchors
   - Must warn on errors without failing

2. **_read_file() modification** - Integration point
   - Must be backward compatible (default `transform_links=False`)
   - Must pass correct relative paths

3. **load_system_prompt() update** - Activation point
   - Must enable transformation for all sections
   - Must calculate correct source/target paths

## Dependencies

- **Internal:** Python standard library (`re`, `pathlib`, `os`)
- **External:** None (no new dependencies)
- **Prerequisite knowledge:** Markdown link syntax, relative path resolution

## Rollback Plan

If implementation fails or causes issues:

1. Revert commit: `git revert HEAD`
2. Regenerate AGENTS.md from last known good state
3. Investigate failures using warnings collected during transformation
4. Fix issues and retry

## Success Metrics

### Must-Have (P0)

- [ ] All relative links in `AGENTS.md` work correctly
- [ ] Source files remain navigable in original location
- [ ] Bootstrap is idempotent (can run multiple times)
- [ ] Unit tests pass with >90% coverage
- [ ] `docscan.py`: 0 broken links in `AGENTS.md`
- [ ] No transformation warnings during normal use

### Should-Have (P1)

- [ ] Warnings issued for untransformable links
- [ ] Documentation complete and clear
- [ ] Edge cases tested and handled

### Nice-to-Have (P2)

- [ ] Link validation during transformation
- [ ] Configuration flags for transformation behavior
- [ ] Auto-fix suggestions for broken links

## Timeline Estimate

- **Step 1-4 (Implementation):** 4-5 hours
- **Step 5 (Tests):** 2-3 hours
- **Step 6 (Documentation):** 1 hour
- **Step 7 (Verification):** 1-2 hours
- **Total:** ~8-11 hours (1-1.5 days)

## Approval Checklist

Before starting implementation:

- [ ] Spec reviewed and approved
- [ ] Approach validated
- [ ] Edge cases identified
- [ ] Test strategy defined
- [ ] Rollback plan documented

## Definition of Done

Per [docs/definition-of-done.md](../../docs/definition-of-done.md):

1. **Functionality:**
   - [ ] All requirements from spec met
   - [ ] All edge cases handled
   - [ ] Bootstrap runs without errors

2. **Testing:**
   - [ ] Unit tests written and passing
   - [ ] Integration tests passing
   - [ ] Manual testing completed

3. **Documentation:**
   - [ ] README.md updated with link transformation section
   - [ ] Code docstrings complete
   - [ ] Change log entry added (if applicable)

4. **Verification:**
   - [ ] Links in source files work
   - [ ] Links in assembled AGENTS.md work
   - [ ] Document integrity scan passes
   - [ ] Bootstrap is idempotent

5. **Code Quality:**
   - [ ] Code follows project style
   - [ ] No code smells or anti-patterns
   - [ ] Maintainable and well-structured

## Notes

- Original investigation saved in conversation context
- Plan approved via ExitPlanMode
- User requested spec and project plan creation
- This plan follows logs-first workflow structure
