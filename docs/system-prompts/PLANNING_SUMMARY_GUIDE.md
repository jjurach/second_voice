# Planning Summary - Agent Guide

## Purpose

`planning-summary.py` displays the current status of all beads (tasks) in the project, showing what's completed, in progress, ready to work on, and blocked.

## How It Works

The script has a **two-tier architecture** for reliability:

1. **Primary:** Tries to use `bd list --json` (beads CLI command)
2. **Fallback:** Reads directly from `.beads/issues.jsonl` if `bd` isn't available

This means the script works regardless of whether the beads CLI is installed or available.

## Quick Start

### From Project Root

```bash
# Show all beads and their status
python3 docs/system-prompts/planning-summary.py

# Filter by status (ready, blocked, in-progress, closed)
python3 docs/system-prompts/planning-summary.py --status ready

# Filter by label (implementation, approval, failure, etc.)
python3 docs/system-prompts/planning-summary.py --label implementation

# Show with full descriptions
python3 docs/system-prompts/planning-summary.py --verbose

# Output as JSON (for scripting)
python3 docs/system-prompts/planning-summary.py --json

# Control how many closed beads to show (default: 5)
python3 docs/system-prompts/planning-summary.py --limit 10
```

## Output Format

The script displays beads in categories:

```
Ready to Work (3):
  ○ pitchjudge-2  Phase 7: Integration Testing  [implementation]

Blocked (2):
  ✗ pitchjudge-3  Phase 8: API Security  (blocked by: pitchjudge-1)

────────────────────────────────────────────────────────────

Total Beads: 5
  Closed:      1 (20%)
  Ready:       3 (60%)
  Blocked:     2 (40%)

Progress: ██░░░░░░░░░░░░░░░░░░ 20% complete
```

### Icons Meaning

- `✓` = Closed (completed)
- `→` = In Progress (someone is working on it)
- `○` = Ready (ready for work)
- `✗` = Blocked (waiting for dependency)
- `❌` = Failure (requires human review)
- `?` = Unknown status

## Status Values

The script understands two bead formats:

### BD CLI Format
- `closed` - Task is complete
- `in-progress` - Someone is actively working
- `ready` - Ready for someone to claim
- `not-ready` - Blocked by dependencies

### JSONL Format (Fallback)
- `open` - Open task (may be ready or blocked based on dependencies)
- Beads with `dependencies` array are treated as blocked
- Beads without dependencies are treated as ready

## For Claude Agents

When you want to check beads status:

```bash
python3 docs/system-prompts/planning-summary.py
```

This will:
1. Try to use the `bd` CLI if available
2. Automatically fall back to reading `.beads/issues.jsonl` if `bd` isn't available
3. Parse and display the results

**No venv activation needed** - the fallback mechanism ensures it always works.

### Example: Check for Ready Beads

```bash
python3 docs/system-prompts/planning-summary.py --status ready
```

### Example: Check if Your Task is Blocked

```bash
python3 docs/system-prompts/planning-summary.py --verbose | grep "pitchjudge-2"
```

## Closing a Bead After Work

After completing work on a bead, close it with:

```bash
# Using bd CLI (if available)
bd update pitchjudge-1 --close

# Or manually edit .beads/issues.jsonl
# Change status from "open" to "closed" and add closed_at timestamp
```

## Troubleshooting

### Script runs but shows "Unknown Status"

This happens if the bead format is unexpected. The script will still categorize it correctly based on dependencies.

### No beads appear

Check:
```bash
ls .beads/issues.jsonl
```

If it exists, ensure it has JSONL content (one JSON object per line).

## Architecture Details

The script handles format conversion automatically:

```
.beads/issues.jsonl (JSONL format)
         ↓
    load_beads()
    (with fallback)
         ↓
categorize_beads()
    (handles both formats)
         ↓
print_summary()
    (consistent output)
```

The fallback is transparent - agents don't need to know which format is being used.

---

**Last Updated:** 2026-02-15
**Status:** Reliable fallback implemented ✓
