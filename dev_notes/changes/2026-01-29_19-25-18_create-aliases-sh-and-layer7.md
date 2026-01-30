# Change Documentation: Create Aliases Shell Script and Add Layer 7 to Document Scan

**Date:** 2026-01-29 19-25-18
**Status:** ad-hoc
**Type:** Documentation
**Related Project Plan:** N/A

## Summary
Created a unified shell aliases script (`aliases.sh`) consolidating all AI coding tool aliases from tips documentation. Extended the document-integrity-scan process with Layer 7: Alias Verification to ensure aliases referenced in tips documents are defined in aliases.sh.

## Changes Made

### 1. Created Unified Shell Aliases Script

**File:** `docs/system-prompts/tips/aliases.sh` (new)

**Content:**
- Shell script with proper shebang (`#!/usr/bin/env bash`)
- Sourcing instructions for bash and zsh
- Three alias categories:
  - **Claude Code aliases:** claude-sys, claude-quick, claude-dev, claude-think
  - **Codex CLI aliases:** codex-sys, codex-quick, codex-dev, codex-think
  - **Cline aliases:** cline-list, cline-resume, cline-view, cline-new, cline-chat, cline-sys, cline-dev
- Usage examples in comments
- Session resumption examples
- Optional print-on-load message

**Alias definitions:**
```bash
# Claude Code
alias claude-sys='claude --model sonnet --dangerously-skip-permissions'
alias claude-quick='claude --model haiku --dangerously-skip-permissions'
alias claude-dev='claude --model sonnet --dangerously-skip-permissions'
alias claude-think='claude --model opus --dangerously-skip-permissions'

# Codex CLI
alias codex-sys='codex'
alias codex-quick='codex --model gpt-5-mini'
alias codex-dev='codex --model gpt-5.1-codex-max'
alias codex-think='codex --model gpt-5.2-codex'

# Cline
alias cline-list='cline task list'
alias cline-resume='cline task open'
alias cline-view='cline task view'
alias cline-new='cline task new'
alias cline-chat='cline task chat'
alias cline-sys='cline task new "apply system-prompts process"'
alias cline-dev='cline task new "development task"'
```

**Sourcing instructions:**
```bash
# Source in ~/.bashrc or ~/.zshrc:
source /path/to/docs/system-prompts/tips/aliases.sh

# Or add to shell config:
echo "source $(pwd)/docs/system-prompts/tips/aliases.sh" >> ~/.bashrc
echo "source $(pwd)/docs/system-prompts/tips/aliases.sh" >> ~/.zshrc
```

### 2. Extended Document Integrity Scan with Layer 7

**File:** `docs/system-prompts/processes/document-integrity-scan.md` (modified)

**Added Layer 7: Alias Verification** (lines 221-277)

**Purpose:** Ensure all shell aliases referenced in tips documents are defined in aliases.sh to prevent drift between documentation and the sourceable script.

**Verification process:**
1. Scan all `.md` files in `docs/system-prompts/tips/` directory
2. Extract alias references from markdown (both alias definitions in code blocks and usage examples)
3. Read `docs/system-prompts/tips/aliases.sh`
4. Parse alias definitions from the shell script
5. Compare referenced aliases against defined aliases
6. Report any missing aliases

**Patterns detected:**
- Alias definitions in code blocks: `` `alias name='command'` ``
- Alias usage in examples: `` `name 'arguments'` ``
- Both bash and markdown code fence formats

**Example violations:**
```markdown
VIOLATION: Alias "claude-experimental" referenced in claude-code.md but not defined in aliases.sh
VIOLATION: Alias "codex-debug" referenced in codex.md but not defined in aliases.sh
```

**Added Rule 7: Alias Consistency** (lines 380-401)

**Rule text:**
> All shell aliases referenced in tips/ documents must be defined in aliases.sh.
>
> Verification process:
> 1. Scan all markdown files in docs/system-prompts/tips/
> 2. Extract alias references (alias definitions and usage examples)
> 3. Verify each alias exists in docs/system-prompts/tips/aliases.sh
> 4. Report missing aliases

**Rationale:**
- **User convenience:** Single file to source for all workflow aliases
- **Consistency:** Prevents documentation drift from actual available aliases
- **Maintenance:** Easy to audit what aliases exist across all tools
- **Onboarding:** New users can source one file to get all recommended aliases

## Files Created

- `docs/system-prompts/tips/aliases.sh` (97 lines)
- `dev_notes/changes/2026-01-29_19-25-18_create-aliases-sh-and-layer7.md` (this file)

## Files Modified

- `docs/system-prompts/processes/document-integrity-scan.md` - Added Layer 7 and Rule 7

## Verification

✅ All aliases from claude-code.md included in aliases.sh
✅ All aliases from codex.md included in aliases.sh
✅ All aliases from cline.md included in aliases.sh
✅ Shell script has proper shebang and sourcing instructions
✅ Usage examples included in comments
✅ Layer 7 documentation added to document-integrity-scan.md
✅ Rule 7 added to integrity rules list
✅ No drift between tips documentation and aliases.sh

## Integration with Definition of Done

This change satisfies:
- ✅ Documentation quality standards (comprehensive, well-organized)
- ✅ File naming conventions (lowercase-kebab.sh)
- ✅ Consistent formatting (bash best practices)
- ✅ Change documentation created (this file, marked as ad-hoc)
- ✅ Extends document-integrity-scan with automated verification

## Rationale

**User request:** "create docs/system-prompts/tips/aliases.sh with all of these aliases so it is easy to load these into my zsh and bash sessions. update document-integrity-scan.md to scan across all of these tips files and to ensure that all the referenced aliases are present in the aliases.sh file."

**Approach:**
1. **Centralized alias management** - Single source of truth for all workflow aliases
2. **Automated verification** - Layer 7 ensures documentation stays synchronized with aliases.sh
3. **User convenience** - One command to source all aliases instead of copying them individually
4. **Cross-platform support** - Works with both bash and zsh

**Impact:**
- Users can load all recommended aliases with one source command
- Documentation integrity scan will catch any drift between tips docs and aliases.sh
- Easier onboarding for new users following workflow optimization tips
- Prevents stale or incorrect alias examples in documentation

## Known Issues

**Note:** Layer 7 is documented in document-integrity-scan.md but the actual implementation in `scripts/docscan.py` has not been updated yet. The documentation describes the intended behavior and verification process, but the Python script needs to be enhanced to execute Layer 7 checks.

**Next steps if implementing Layer 7 in docscan.py:**
1. Add alias extraction logic for markdown files
2. Add alias parsing logic for shell scripts
3. Add comparison and reporting logic
4. Add Layer 7 to the execution flow

## Usage

**To load aliases in your shell:**

```bash
# One-time sourcing
source docs/system-prompts/tips/aliases.sh

# Add to shell config (bash)
echo "source $(pwd)/docs/system-prompts/tips/aliases.sh" >> ~/.bashrc
source ~/.bashrc

# Add to shell config (zsh)
echo "source $(pwd)/docs/system-prompts/tips/aliases.sh" >> ~/.zshrc
source ~/.zshrc
```

**Using the aliases:**

```bash
# System-prompts processes
claude-sys 'apply document-integrity-scan process'
codex-sys 'apply close-task process'
cline-sys

# Quick exploration
claude-quick 'find all TODO comments'
codex-quick 'list all API endpoints'

# Development work
claude-dev 'implement OAuth authentication'
codex-dev 'refactor database layer'
cline-dev

# Deep reasoning
claude-think 'design caching architecture'
codex-think 'review security vulnerabilities'

# Session resumption (Claude Code)
claude-dev --continue
claude-sys --resume my-session

# Session resumption (Codex CLI)
codex-dev resume --last
codex-quick resume <SESSION_ID>

# Task management (Cline)
cline-list
cline-resume <TASK_ID>
cline-view <TASK_ID>
```

## Next Steps

None required. The aliases.sh file is ready for use and Layer 7 is documented for future implementation in the docscan.py script.
