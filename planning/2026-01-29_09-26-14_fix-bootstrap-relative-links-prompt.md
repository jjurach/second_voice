# Spec: Fix Bootstrap Relative Link Problem

**Status:** Completed
**Created:** 2026-01-29 09:26:14
**Completed:** 2026-01-29 09:35:57
**Workflow:** @logs-first

## Problem Statement

When `bootstrap.py` assembles `AGENTS.md` from component files in `docs/system-prompts/`, relative markdown links break because they're evaluated from a different directory context after assembly.

### Current Behavior

**Example of broken link:**
- Source file: `docs/system-prompts/mandatory-reading.md`
- Contains link: `[Definition of Done](../definition-of-done.md)`
- From source location: `../definition-of-done.md` → `docs/definition-of-done.md` ✓ WORKS
- After assembly into root-level `AGENTS.md`: `../definition-of-done.md` → tries to resolve outside project ✗ BROKEN
- Should become: `docs/definition-of-done.md` after assembly

### Impact

1. **Non-idempotent bootstrap:** Running `bootstrap.py` repeatedly produces the same broken state
2. **Broken links for agents:** AI agents reading `AGENTS.md` encounter broken links
3. **Document integrity failures:** `docscan.py` reports broken links in assembled `AGENTS.md`
4. **User confusion:** Links work in source files but not in assembled files

### Affected Files

Source files with relative links that break when assembled:
- `docs/system-prompts/mandatory-reading.md` (lines 20, 35, 49, 66-68)
- `docs/system-prompts/README.md` (lines 752-755)
- `docs/system-prompts/tools/claude-code.md` (lines 7, 10-12)
- `docs/system-prompts/tools/aider.md` (lines 7, 10-12)
- `docs/system-prompts/tools/cline.md` (lines 7, 10-12)
- `docs/system-prompts/tools/gemini.md` (lines 7, 10-12)
- `docs/system-prompts/processes/bootstrap-project.md` (lines 441, 751, 1028-1030)

## Root Cause Analysis

The `bootstrap.py` script:
1. Reads source files unchanged via `_read_file()` method (lines 60-66)
2. Injects content verbatim into `AGENTS.md` via `_update_section()`
3. **NO link rewriting happens** - this is the bug

The links that work relative to `docs/system-prompts/` don't work relative to the root-level `AGENTS.md`.

## Requirements

### Functional Requirements

1. **FR1:** Relative links in source files must work when clicked in their original location
2. **FR2:** The same links must work when assembled into `AGENTS.md` at the root level
3. **FR3:** Bootstrap process must be truly idempotent (can run multiple times safely)
4. **FR4:** External URLs must remain unchanged
5. **FR5:** Anchor fragments must be preserved (e.g., `file.md#section`)
6. **FR6:** Absolute paths must remain unchanged
7. **FR7:** Self-references (anchor-only links like `#section`) must remain unchanged

### Non-Functional Requirements

1. **NFR1:** Solution must not require changes to existing source file formats
2. **NFR2:** Implementation must be maintainable (<200 lines of additional code)
3. **NFR3:** Must handle edge cases gracefully with warnings
4. **NFR4:** Performance impact must be negligible (<100ms for typical bootstrap)
5. **NFR5:** Must preserve backward compatibility with existing workflows

## Success Criteria

1. ✅ All relative links in assembled `AGENTS.md` work correctly
2. ✅ All relative links in source files continue to work in their original location
3. ✅ Bootstrap process can run multiple times without producing different outputs
4. ✅ `python3 docs/system-prompts/docscan.py` reports 0 broken links in `AGENTS.md`
5. ✅ Unit tests pass with >90% code coverage for link transformation logic
6. ✅ No transformation warnings during normal bootstrap execution
7. ✅ External URLs, absolute paths, and anchors are preserved unchanged

## Out of Scope

- Fixing links in files not assembled by bootstrap
- Validating that link targets actually exist
- Converting existing absolute paths to relative paths
- Handling non-markdown file formats
- Implementing link validation during transformation

## Proposed Solution

**Approach:** Implement link rewriting during bootstrap assembly.

### Why This Approach

**Alternatives considered:**

1. **Use absolute paths in source files** - ❌ Breaks source file navigation
2. **Use .dat format instead of .md** - ❌ Loses readability and maintainability
3. **Custom link syntax** - ❌ Breaks standard markdown tools
4. **Link rewriting (RECOMMENDED)** - ✅ Preserves source integrity, fixes assembled output

### Solution Components

1. **LinkTransformer class:** Handles link transformation logic
   - Pattern detection for markdown links
   - Path resolution from source to target context
   - Anchor preservation
   - Edge case handling

2. **Modified _read_file() method:** Adds optional link transformation
   - New parameters: `transform_links`, `source_file_relative`, `target_file_relative`
   - Calls transformation helper when enabled

3. **Link transformation helper:** `_transform_links_in_content()`
   - Uses regex to find all markdown links
   - Transforms each relative link appropriately
   - Collects and reports warnings

4. **Updated load_system_prompt():** Enables transformation
   - Passes source and target file paths
   - Enables `transform_links=True` for all sections

## Dependencies

- Python 3.10+ (already in use)
- Standard library: `re`, `pathlib`, `os`
- No new external dependencies required

## Testing Strategy

### Unit Tests

Create `docs/system-prompts/tests/test_link_transformation.py`:
- Test parent directory links (`../file.md`)
- Test anchor preservation (`../file.md#section`)
- Test external URL preservation
- Test absolute path preservation
- Test self-reference preservation
- Test multiple parent traversal (`../../file.md`)
- Test edge cases and error handling

### Integration Tests

- Run bootstrap with transformation
- Verify `AGENTS.md` has correct links
- Verify source files unchanged
- Run docscan to verify 0 broken links

### Manual Testing

- Click links in source files to verify navigation works
- Click links in `AGENTS.md` to verify navigation works
- Run bootstrap multiple times and verify idempotency

## Risks and Mitigations

| Risk | Impact | Likelihood | Mitigation |
|------|--------|------------|------------|
| Breaking existing functionality | High | Low | Comprehensive test coverage, gradual rollout |
| Edge cases not covered | Medium | Medium | Extensive edge case testing, warnings for untransformable links |
| Performance degradation | Low | Low | Regex is O(n), negligible for markdown files |
| Complex maintenance | Medium | Low | Clear documentation, well-structured code with docstrings |

## Acceptance Criteria

Before marking as "Done":

1. All unit tests pass
2. All integration tests pass
3. Bootstrap runs successfully with no errors
4. `docscan.py` reports 0 broken links in `AGENTS.md`
5. Manual verification: links in both source and assembled files work
6. Documentation updated
7. Code reviewed for clarity and maintainability

## References

- Investigation results: Agent exploration report (in conversation context)
- Current bootstrap.py: `/home/phaedrus/AiSpace/second_voice/docs/system-prompts/bootstrap.py`
- Affected files: All markdown files in `docs/system-prompts/` subdirectories
- Plan file: `/home/phaedrus/.claude/plans/shimmering-knitting-tarjan.md`
