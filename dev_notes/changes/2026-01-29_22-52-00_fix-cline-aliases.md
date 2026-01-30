# Change: Fix Cline aliases and documentation

**Date:** 2026-01-29  
**Author:** AI Assistant  
**Status:** ad-hoc  

## Change Description
Fixed Cline CLI aliases and documentation to use correct command-line syntax:
1. Remove incorrect `task new`, `task open`, `task chat` subcommands (not supported by CLI)
2. Use correct syntax: `cline --yolo --mode act 'description'`
3. Remove unsupported `--no-interactive` flag
4. Add new `cline-quick` alias for quick task creation
5. Add new `cline-ask` alias for one-shot commands
6. Keep task management commands (`cline task list`, `cline task open`) without flags
7. Ensure consistency with working command format across all Cline aliases

## Files Modified
- `docs/system-prompts/tips/cline.md` - Corrected alias definitions and examples
- `docs/system-prompts/tips/aliases.sh` - Fixed all Cline alias implementations

## Changes Made

### Correct Cline CLI Syntax
The Cline CLI uses a simplified command structure where the task description is passed directly as an argument:
```bash
# CORRECT - Direct description passing
cline --yolo --mode act 'what is 2+2?'

# INCORRECT - These subcommands don't exist in Cline CLI
cline --yolo --mode act task new 'description'
cline --yolo --mode act --no-interactive 'description'
```

### aliases.sh Updates
- Simplified all auto-approved alias definitions: `cline --yolo --mode act`
- Removed incorrect `task new`, `task open`, `task chat` subcommands
- Removed unsupported `--no-interactive` flag
- Added `cline-quick` alias for quick task creation (same as `cline-dev`)
- Added `cline-ask` alias for one-shot commands
- Kept task management aliases (`cline-list`, `cline-resume`, `cline-view`) without auto-approval flags
- Updated usage examples with correct command format

### Affected Aliases
| Alias | Command | Update |
|-------|---------|--------|
| `cline-list` | `cline task list` | ✅ Removed invalid flags |
| `cline-resume` | `cline task open` | ✅ Removed invalid flags |
| `cline-view` | `cline task view` | ✅ Kept without flags |
| `cline-dev` | `cline --yolo --mode act` | ✅ Fixed syntax |
| `cline-quick` | `cline --yolo --mode act` | ✨ NEW |
| `cline-sys` | `cline --yolo --mode act` | ✅ Fixed syntax |
| `cline-ask` | `cline --yolo --mode act` | ✨ NEW (one-shot) |

### Documentation Updates (cline.md)
- Updated Task Aliases section with correct syntax
- Added clear flag explanations
- Provided usage examples showing:
  - Creating development tasks
  - Applying system-prompts processes
  - Running one-shot commands
  - Managing tasks (without auto-approval)

## Verification
✅ All auto-approved aliases use: `cline --yolo --mode act`
✅ Task management commands don't include auto-approval flags
✅ Both `cline-dev` and `cline-quick` implement same syntax
✅ Syntax matches working test: `cline --yolo --mode act 'what is 2+2?'`
✅ Documented in both aliases.sh and tips/cline.md