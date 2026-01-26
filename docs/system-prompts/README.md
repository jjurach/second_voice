# Agent Kernel: System Prompts Module

The **Agent Kernel** is a reusable, standardized collection of agentic workflow guidelines and patterns. It provides a foundation for consistent AI agent behavior across projects.

## Overview

This directory contains the "ideal state" documentation for:
- **Workflow Principles** - The core A-E workflow and unbreakable rules
- **Definition of Done** - Universal and language-specific completion criteria
- **Prompt Patterns** - Proven templates for effective AI prompts

## Directory Structure

```
docs/system-prompts/
├── bootstrap.py                 # Tool to inject/maintain sections in AGENTS.md
├── README.md                    # This file
├── principles/
│   └── definition-of-done.md    # Universal DoD criteria
├── workflow/
│   └── core.md                  # Core A-E workflow + Unbreakable Rules
├── patterns/
│   └── prompt-patterns.md       # Prompt templates for consistent results
└── languages/
    └── python/
        └── definition-of-done.md # Python-specific DoD (pytest, venv, etc.)
```

## Core Concept

The Agent Kernel separates **generic** guidance (applicable to all projects) from **language-specific** guidance (e.g., Python pytest, JavaScript npm). Each project maintains its own `AGENTS.md` file, which can be:

1. **Bootstrapped** with kernel content via `bootstrap.py`
2. **Extended** with project-specific rules
3. **Kept in sync** when the kernel evolves

## Using the Bootstrap Tool

### Quick Start

```bash
# From project root, ensure AGENTS.md exists
# Then run:
python3 docs/system-prompts/bootstrap.py

# By default, this is a DRY RUN - no changes made
# To actually apply changes:
python3 docs/system-prompts/bootstrap.py --commit
```

### Available Commands

```bash
# Dry-run mode (default) - shows what would happen
python3 bootstrap.py

# Apply changes to AGENTS.md
python3 bootstrap.py --commit

# Overwrite locally modified sections (use with caution)
python3 bootstrap.py --commit --force

# Analyze without changes
python3 bootstrap.py --analyze

# Specify a different project root
python3 bootstrap.py --root /path/to/project --commit
```

### How It Works

1. **Detection:** Identifies project language (Python, JavaScript, etc.)
2. **Comparison:** Reads current `AGENTS.md` and compares to ideal state
3. **Smart Updates:**
   - **Unmodified sections:** Overwrites with latest ideal state
   - **Modified sections:** Warns and skips (unless `--force` used)
   - **Missing sections:** Adds them
4. **Safe by Default:** Dry-run mode is the default; use `--commit` to write

## Section Markers

The bootstrap tool uses HTML comments to mark managed sections:

```markdown
<!-- SECTION: CORE-WORKFLOW -->
... section content ...
<!-- END-SECTION -->
```

Only content between these markers is managed. Project-specific rules can be added in a separate section:

```markdown
<!-- SECTION: PROJECT-SPECIFIC -->
This project uses:
- dev_notes/ for tracking
- config.example.json for config keys
... (your project rules) ...
<!-- END-SECTION -->
```

## Content Included

### 1. Workflow Core (`workflow/core.md`)
- **Steps A-E:** Analyze, Spec, Plan, Await Approval, Implement & Document
- **Unbreakable Rules:** Approval, Quality, Uncertainty, File Naming, Temp Files, Slack Notifications

### 2. Universal Definition of Done (`principles/definition-of-done.md`)
- Plan vs. Reality protocol
- Verification as data
- Codebase state integrity
- Agent handoff patterns

### 3. Python Definition of Done (`languages/python/definition-of-done.md`)
- Environment & dependencies (venv, requirements.txt, pyproject.toml)
- Testing with pytest
- Code quality standards
- File organization
- Fixtures and mocking
- Python version compatibility

### 4. Prompt Patterns (`patterns/prompt-patterns.md`)
- Request Analysis Pattern
- Planning & Design Pattern
- Implementation Pattern
- Verification Pattern
- Debugging Pattern
- Documentation Pattern
- Code Review Pattern
- Testing Pattern
- Integration/System Pattern
- And more...

## Project-Specific Extensions

Your project can extend the kernel with project-specific rules. Example:

```markdown
# MANDATORY AI Agent Instructions (Condensed)

<!-- SECTION: CORE-WORKFLOW -->
... (injected by bootstrap.py) ...
<!-- END-SECTION -->

<!-- SECTION: PROJECT-SPECIFIC -->

## Project-Specific Rules

1. **Development Notes:**
   - Use `dev_notes/specs/` for specification files
   - Use `dev_notes/project_plans/` for formal plans
   - Use `dev_notes/changes/` for implementation tracking

2. **Configuration:**
   - All config keys MUST be defined in `config.example.json`
   - Never hardcode secrets or API keys
   - Environment variables take precedence

3. **Documentation:**
   - API docs in `docs/api/`
   - Architecture decisions in `docs/adr/`
   - Implementation guides in `docs/implementation-reference.md`

<!-- END-SECTION -->
```

## Keeping Synchronized

To update your project when the kernel evolves:

```bash
# Check what would change
python3 docs/system-prompts/bootstrap.py --analyze

# Apply updates
python3 docs/system-prompts/bootstrap.py --commit

# Verify no critical info was lost
git diff AGENTS.md
```

## Safety Considerations

- **Dry Run First:** Always review with `--analyze` or dry-run
- **Backup:** Keep git history for easy rollback
- **Project-Specific:** Use `<!-- SECTION: PROJECT-SPECIFIC -->` for rules you want to keep
- **Modified Sections:** Bootstrap warns before overwriting custom content
- **Use `--force` Carefully:** This skips modification warnings

## Supported Languages

Currently supported language-specific content:
- **Python:** Definition of Done with pytest, venv, requirements management
- **JavaScript:** (Coming soon)
- **Go:** (Coming soon)

## Extending the Kernel

To add new patterns or guidelines to the kernel:

1. Create/modify files in `docs/system-prompts/`
2. Update `bootstrap.py` if needed to reference new sections
3. Commit and push the changes
4. Projects using the kernel can pull the latest version

## Troubleshooting

**Problem:** Bootstrap can't find project root
```bash
# Explicitly specify root
python3 bootstrap.py --root /path/to/project --analyze
```

**Problem:** AGENTS.md doesn't exist
```bash
# Create a basic one first
echo "# MANDATORY AI Agent Instructions" > AGENTS.md

# Then run bootstrap
python3 bootstrap.py --commit
```

**Problem:** Sections aren't being updated
```bash
# Check project language detection
python3 bootstrap.py --analyze

# Use --force to overwrite any modified sections
python3 bootstrap.py --commit --force
```

**Problem:** Want to keep custom section
```markdown
<!-- SECTION: MY-CUSTOM-SECTION -->
This won't be touched by bootstrap
<!-- END-SECTION -->
```

## Integration with Claude Code

The Agent Kernel is designed to work with [Claude Code](https://github.com/anthropics/claude-code) and other AI development tools.

To use in a new project:

1. Add `docs/system-prompts/` to your repo (or use as git submodule)
2. Create/initialize `AGENTS.md`
3. Run `python3 docs/system-prompts/bootstrap.py --commit`
4. Customize with project-specific rules
5. Commit the updated `AGENTS.md`

## Related Resources

- `docs/definition-of-done.md` - Detailed DoD documentation
- `AGENTS.md` - Your project's current agent instructions
- `/docs/templates.md` - Templates for specs and plans
- `/docs/prompt-patterns.md` - (Older location) Use `patterns/prompt-patterns.md` instead

## Version

Agent Kernel v1.0 - January 2026

For updates, issues, or contributions, refer to your project's development guidelines.
