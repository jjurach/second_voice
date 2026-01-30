# Change Log: Reorganize Agent Context Files

**Status:** Completed

## Changes
-   **Regorganized Agent Entry Points:** Moved `AIDER.md` to `.aider.md` and `CLINE.md` to `.clinerules` to reduce project root clutter.
-   **Removed `CODEX.md`:** Codex natively discovers `AGENTS.md`, making a separate entry point redundant.
-   **Updated `docs/system-prompts/bootstrap.py`:**
    -   Modified `regenerate_tool_entries` to support the new hidden/native filenames.
    -   Shortened templates to ensure they remain anemic (under 25 lines).
    -   Updated `validate_tool_entry_point` and `report_gaps` to track the new locations.
-   **Updated `.aider.conf.yml`:** Added `.aider.md` to the `read` list to ensure Aider receives its specific instructions.
-   **Updated `docs/system-prompts/docscan.py`:** Updated Layer 4 validation to check the new hidden/native filenames.
-   **Documentation Updates:**
    -   `README.md`: Updated links and descriptions for Aider, Cline, and Codex.
    -   `docs/file-naming-conventions.md`: Updated the naming convention table and tool-specific sections.
    -   `docs/system-prompts/tools/cline.md`: Reflected the move to `.clinerules`.
    -   `docs/system-prompts/tools/aider.md`: Reflected the move to `.aider.md`.
    -   `docs/system-prompts/processes/tool-entry-points.md`: Updated process documentation with new filenames.
    -   `docs/system-prompts/processes/document-integrity-scan.md`: Updated safe entry point list.
    -   `docs/system-prompts/processes/bootstrap-project.md`: Updated informational references.

## Verification Results

### Tool Entry Point Validation
```bash
python3 docs/system-prompts/bootstrap.py --validate-tool-entries
```
Output:
```
Validating tool entry points...
✓ CLAUDE.md: Valid anemic format (21 lines)
✓ .aider.md: Valid anemic format (21 lines)
✓ .clinerules: Valid anemic format (21 lines)
✓ GEMINI.md: Valid anemic format (21 lines)

✅ All tool entry points are valid!
```

### Document Integrity Scan
```bash
python3 docs/system-prompts/docscan.py --check tool-entries
```
Output:
```
[Layer 4: Tool Entry Points]
  ✓ CLAUDE.md (Valid)
  ✓ .aider.md (Valid)
  ✓ .clinerules (Valid)
  ✓ GEMINI.md (Valid)

✅ All checks passed!
```

## Known Issues
-   None.
