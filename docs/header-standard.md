# Standard Document Header Format

**Purpose:** Ensure consistent metadata across all generated project documents to enable automated status tracking and traceability.

---

## Standard Header Block

All markdown files in `dev_notes/specs/`, `dev_notes/project_plans/`, and `dev_notes/changes/` must begin with this YAML-like header block:

```markdown
# [Title of Document]

**Source:** [path/to/source/file]
**Original File:** [original-filename-if-applicable]
**Status:** [Current-Status]
**Timestamp:** [YYYY-MM-DD_HH-MM-SS]
**Last Updated:** [YYYY-MM-DD]
**Estimated Phases:** [Number-if-applicable]
**Priority:** [High/Medium/Low]

---
```

## Field Definitions

| Field | Description | Example |
|-------|-------------|---------|
| **Source** | Path to the document that triggered this one | `dev_notes/specs/2026-01-27_feature.md` |
| **Original File** | Name of the original user input file (if any) | `feature-request.md` |
| **Status** | Current lifecycle state (see below) | `🔵 Ready for Implementation` |
| **Timestamp** | Creation time (ISO-8601-like) | `2026-01-27_14-30-00` |
| **Last Updated** | Date of last modification | `2026-01-28` |
| **Estimated Phases** | Number of implementation phases (plans only) | `4` |
| **Priority** | Urgency level (High, Medium, Low) | `High` |

## Status Values

Use these exact strings (including emojis) to ensure correct parsing by the status query tool.

| Status | Meaning |
|--------|---------|
| `🔵 Ready for Implementation` | Document created but work not started |
| `🟡 In Progress` | Implementation is actively underway |
| `🟢 Awaiting Approval` | Implementation done, waiting for review |
| `✅ Complete` | Fully approved and merged |

## Automation Compatibility

- The status query tool (`tools/query_status.py`) uses regex to parse these fields.
- **Do not** change the bolding or colon format (e.g., maintain `**Status:**`).
- Status values are case-sensitive for the tool.

## Example: Specification

```markdown
# Spec: Add Dark Mode

**Source:** dev_notes/inbox/dark-mode-request.md
**Original File:** dark-mode-request.md
**Status:** 🔵 Ready for Implementation
**Timestamp:** 2026-01-27_10-00-00
**Last Updated:** 2026-01-27
**Priority:** Medium

---
```

## Example: Project Plan

```markdown
# Project Plan: Dark Mode Implementation

**Source:** dev_notes/specs/2026-01-27_10-00-00_dark-mode.md
**Original File:** dark-mode-request.md
**Status:** 🟡 In Progress
**Timestamp:** 2026-01-27_10-05-00
**Last Updated:** 2026-01-27
**Estimated Phases:** 3
**Priority:** Medium

---
```
