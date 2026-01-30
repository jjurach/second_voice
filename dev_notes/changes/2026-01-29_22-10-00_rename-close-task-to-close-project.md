# Change Log: Rename Close Task to Close Project

**Source:** Ad-hoc
**Status:** Completed
**Timestamp:** 2026-01-29_22-10-00
**Last Updated:** 2026-01-29

---

## 📋 Executive Summary
Renamed the "Close Task" process to "Close Project" to better reflect its scope and maintain consistency with other project-level processes. Updated all references across system prompts, tips, and documentation.

## 🏗️ Changes

### Process Rename
- Renamed `docs/system-prompts/processes/close-task.md` to `docs/system-prompts/processes/close-project.md`.
- Updated internal content of `close-project.md` to use the new terminology.
- Added a note to `close-project.md` to interpret "close task" as "close project".

### Documentation & Tips Updates
- **`docs/system-prompts/processes/README.md`**: Updated references and descriptions.
- **`docs/system-prompts/docscan.py`**: Updated `ALLOWED_BACK_REFERENCES` to use the new filename.
- **`docs/system-prompts/tips/aliases.sh`**: Updated examples in comments.
- **`docs/system-prompts/tips/claude-code.md`**: Global update of "close-task" to "close-project" in tables, descriptions, and examples.
- **`docs/system-prompts/tips/cline.md`**: Updated process names and examples.
- **`docs/system-prompts/tips/codex.md`**: Updated process names and examples.
- **`docs/system-prompts/tips/gemini.md`**: Updated examples.

---

## ✅ Verification Results

### Document Integrity Scan
```bash
python3 docs/system-prompts/docscan.py
# Output: ✅ All checks passed!
```

### Regression Tests
```bash
pytest tests/ -v
# Output: 190 passed
```

---

## 🔗 Related Work
- Follow-up to `2026-01-29_21-56-34_agent-cleanup-and-fixes.md` to complete the terminology alignment.
