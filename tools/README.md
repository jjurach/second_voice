# Tools

## Status Query Tool (`query_status.py`)

This tool helps track the progress of specifications and project plans by parsing standard headers in markdown files.

### Usage

```bash
python tools/query_status.py [options]
```

### Options

- `--summary`: Show overall status summary (default)
- `--next`: Show the next unimplemented project plan (based on timestamp)
- `--oldest`: Show the oldest pending project plan
- `--incomplete`: List all plans that are not "Complete"
- `--orphans`: List plans that reference missing source specifications

### Header Requirements

The tool expects files in `dev_notes/specs/`, `dev_notes/project_plans/`, and `dev_notes/changes/` to have a standardized YAML-like header:

```markdown
**Source:** path/to/source
**Status:** 🔵 Ready for Implementation
**Timestamp:** 2026-01-27_10-00-00
```

See `docs/header-standard.md` for full details on the header format.
