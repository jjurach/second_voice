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
├── templates/
│   ├── README.md                # Templates directory guide
│   └── structure.md             # Documentation templates (specs, plans, changes)
├── workflows/                   # Optional workflow patterns
│   ├── README.md                # Workflows directory guide
│   ├── logs-first.md            # Documented development workflow
│   └── custom-template.md       # Template for creating custom workflows
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

# Workflow Commands (Optional Workflows)
python3 bootstrap.py --analyze-workflow        # Show workflow state and recommendation
python3 bootstrap.py --enable-logs-first --commit   # Enable logs-first workflow
python3 bootstrap.py --disable-logs-first --commit  # Disable logs-first workflow
```

### How It Works

1. **Detection:** Identifies project language (Python, JavaScript, etc.)
2. **Comparison:** Reads current `AGENTS.md` and compares to ideal state
3. **Smart Updates:**
   - **Unmodified sections:** Overwrites with latest ideal state
   - **Modified sections:** Warns and skips (unless `--force` used)
   - **Missing sections:** Adds them
4. **Safe by Default:** Dry-run mode is the default; use `--commit` to write

## Understanding Workflows

The Agent Kernel includes optional **Workflows**—sets of instructions that govern how AI agents approach development tasks. Projects can enable, disable, or create custom workflows.

### What is Logs-First Workflow?

The **logs-first workflow** emphasizes documentation and accountability through three connected documents:

1. **Spec File** (`dev_notes/specs/YYYY-MM-DD_HH-MM-SS_spec-*.md`)
   - Documents user intentions and requirements
   - Example: "Add user authentication to the app"
   - Simple outline with acceptance criteria

2. **Project Plan** (`dev_notes/project_plans/YYYY-MM-DD_HH-MM-SS_plan-*.md`)
   - Details the implementation strategy
   - Broken into phases with specific tasks
   - Requires explicit developer approval before work begins

3. **Change Documentation** (`dev_notes/changes/YYYY-MM-DD_HH-MM-SS_change-*.md`)
   - Proof that work was completed correctly
   - Includes actual test output, coverage metrics
   - References the approved plan

**When Logs-First is Enabled:**
- AGENTS.md includes the complete logs-first workflow (inserted between `<!-- SECTION: LOGS-FIRST-WORKFLOW -->` markers)
- AI agents automatically follow the three-document pattern for non-trivial tasks
- The workflow state is tracked in AGENTS.md via `<!-- BOOTSTRAP-STATE: logs_first=enabled -->`
- Developers expect agents to ask for approval before implementing plans
- Definition of Done checklist includes verification requirements

**When Logs-First is Disabled:**
- The LOGS-FIRST-WORKFLOW section is removed from AGENTS.md
- Agents fall back to basic guidelines (core workflow, universal DoD)
- Less structured development allowed
- Suitable for large projects or teams with different needs

### Using Logs-First Even When Not Enabled

You can follow the logs-first workflow **manually** at any time, regardless of whether it's enabled in AGENTS.md:

1. **Create a Spec File** (optional)
   - Location: `dev_notes/specs/YYYY-MM-DD_HH-MM-SS_what-you-want.md`
   - Format: Brief description of what you're asking for
   - Timing: Write before the Project Plan

   **Example:**
   ```markdown
   # Spec: Add Dark Mode Support

   **Date:** 2026-01-26

   ## User Request
   - Add dark mode toggle to GUI
   - Save preference to config
   - Auto-detect system theme on startup

   ## Goals
   - Improve UX for users in dark environments
   - Follow existing config patterns

   ## Acceptance Criteria
   - [ ] Dark mode toggle appears in settings
   - [ ] Preference persists between sessions
   - [ ] All UI elements are readable in dark mode
   - [ ] Tests verify toggle functionality
   ```

2. **Create a Project Plan** (recommended for non-trivial tasks)
   - Location: `dev_notes/project_plans/YYYY-MM-DD_HH-MM-SS_plan-name.md`
   - Format: See `docs/templates.md` for template
   - Timing: Submit for approval BEFORE implementing

   **What to include:**
   - Overview of what you're building
   - Detailed phases with specific tasks
   - Files that will be created/modified
   - Success criteria
   - Risk assessment

3. **Present to Developers**
   - Share the plan and ask for approval
   - Wait for explicit "yes" or "approved"
   - Document feedback and iterate if needed

4. **Implement with Tracking**
   - Execute the approved plan step-by-step
   - After each major milestone, create a Change Documentation entry

5. **Create Change Documentation**
   - Location: `dev_notes/changes/YYYY-MM-DD_HH-MM-SS_what-changed.md`
   - Format: See `docs/templates.md` for template
   - Include: What was changed, test results, metrics

   **What to include:**
   - Summary of work completed
   - Detailed changes per component
   - Test execution results (actual output)
   - Coverage metrics
   - Verification against Definition of Done
   - Known issues or limitations

### Decision Tree: To Enable or Not?

- **Is the project small (< 200 files)?** → Consider enabling logs-first
- **Are you value detailed decision history?** → Enable logs-first
- **Is the team > 10 people?** → Consider disabling or custom workflow
- **Do you just want the option to use logs-first sometimes?** → Leave disabled and use manually

### Logs-First Benefits

When used (enabled or manually):
- ✅ Complete audit trail of decisions
- ✅ Prevents miscommunication via formal plans
- ✅ Makes onboarding easier (new devs understand the "why")
- ✅ Reduces rework when plans are discussed upfront
- ✅ Proof of correctness via verification in change docs

### Logs-First Trade-offs

- ⚠️ More documentation overhead (3 documents per feature)
- ⚠️ Slower time-to-first-code (planning before implementation)
- ⚠️ Not ideal for rapid prototyping or one-off scripts
- ⚠️ Requires discipline from team to follow patterns

### Custom Workflows

You can create custom workflows (lighter, heavier, or specialized) using the template:
- See `docs/system-prompts/workflows/custom-template.md`
- Register in `bootstrap.py`
- Enable/disable like logs-first

---

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

### 4. Documentation Templates (`templates/structure.md`)
- Spec File Template (user intentions & requirements)
- Project Plan Template (implementation strategy)
- Change Documentation Template (proof of work)
- Best practices, naming conventions, and state transitions

### 5. Prompt Patterns (`patterns/prompt-patterns.md`)
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

## Customizing for Your Project

The Agent Kernel is **generic and reusable**. To adopt it in a new project:

### 1. Choose Your Planning Directory

The kernel references `[PLANNING_DIR]` as a placeholder. Choose your naming:
- **Option A:** `dev_notes/` (recommended, matches examples in this kernel)
- **Option B:** `docs/planning/`
- **Option C:** `.ai-plans/`
- **Option D:** Any other directory structure

Your AGENTS.md should document which convention you chose.

### 2. Create Project-Specific Documentation

After adopting the kernel, create these files:
- `docs/templates.md` - Copy from `docs/system-prompts/templates/structure.md` if customizing the structure
- `docs/implementation-reference.md` - Implementation patterns for your tech stack
- `docs/file-naming-conventions.md` - Your project's file naming rules (if different from the kernel)

### 3. Document Your Configuration Format

Update your `config.example.json` (or `.env.example`, `config.sample.yaml`, etc.) to document configuration keys. The kernel references this in the Definition of Done.

### 4. Language-Specific Setup

- **Python projects:** Use `docs/system-prompts/languages/python/definition-of-done.md` as-is (no changes needed)
- **JavaScript/Node projects:** Create similar guidance in `docs/system-prompts/languages/javascript/definition-of-done.md`
- **Other languages:** Create language-specific DoD following the Python structure

### 5. Project-Specific Rules

Add a `PROJECT-SPECIFIC` section to your AGENTS.md (see "Project-Specific Extensions" above) to document:
- Your planning directory choice
- Configuration management practices
- Code style/formatting requirements
- Custom patterns or tools

---

## Integration with Claude Code

The Agent Kernel is designed to work with [Claude Code](https://github.com/anthropics/claude-code) and other AI development tools.

To use in a new project:

1. Add `docs/system-prompts/` to your repo (or use as git submodule)
2. Create/initialize `AGENTS.md`
3. Run `python3 docs/system-prompts/bootstrap.py --commit`
4. Customize with project-specific rules
5. Commit the updated `AGENTS.md`

## Related Resources

- `docs/system-prompts/principles/definition-of-done.md` - Detailed universal DoD
- `docs/system-prompts/languages/python/definition-of-done.md` - Python-specific requirements
- `docs/system-prompts/templates/structure.md` - Templates for specs, plans, and changes
- `docs/system-prompts/patterns/prompt-patterns.md` - Universal prompt patterns
- `docs/system-prompts/workflows/logs-first.md` - Complete logs-first workflow documentation
- `docs/system-prompts/workflows/custom-template.md` - Template for creating custom workflows
- `docs/system-prompts/workflows/README.md` - Workflows directory guide
- `docs/workflows.md` - User guide for managing workflows
- `AGENTS.md` - Your project's customized agent instructions (generated by bootstrap.py)

## Version

Agent Kernel v1.0 - January 2026

For updates, issues, or contributions, refer to your project's development guidelines.
