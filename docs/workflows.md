# Workflows in Agent Kernel

**What are workflows?** Workflows are optional sets of instructions that govern how AI agents approach development tasks. They let you adapt the Agent Kernel to your project's needs without losing consistency or accountability.

---

## Quick Start

### Check Your Project's Workflow

```bash
python3 docs/system-prompts/bootstrap.py --analyze-workflow
```

You'll see:
- What workflow is recommended for your project
- Current workflow state (enabled/disabled)
- Commands to enable/disable workflows

### Enable Logs-First Workflow

```bash
python3 docs/system-prompts/bootstrap.py --enable-logs-first --commit
```

This injects comprehensive development instructions into AGENTS.md.

### Disable Workflow

```bash
python3 docs/system-prompts/bootstrap.py --disable-logs-first --commit
```

Removes workflow instructions from AGENTS.md.

---

## Available Workflows

### Logs-First Workflow

**What it is:** A comprehensive workflow that emphasizes documentation and accountability through three connected documents: Spec → Project Plan → Change Documentation.

**When to use it:**
- Small teams (1-10 developers)
- Active projects with frequent changes
- Projects where you value decision history
- Internal or experimental tools

**Key features:**
- Complete audit trail (intentions → design → implementation)
- Multi-step approval process
- Comprehensive verification requirements
- Documentation as you go

**Example usage:**
```bash
python3 docs/system-prompts/bootstrap.py --enable-logs-first --commit
```

**Learn more:** See `docs/system-prompts/workflows/logs-first.md` for complete details.

---

## Creating Custom Workflows

Want a different workflow? Create your own!

1. **Start with the template:** Read `docs/system-prompts/workflows/custom-template.md`
2. **Create your workflow:** Save to `docs/system-prompts/workflows/my-workflow.md`
3. **Register with bootstrap.py:** Add to `section_map` and command-line args
4. **Enable it:** `python3 bootstrap.py --enable-my-workflow --commit`

**Example custom workflows:**
- **Rapid-iteration:** Minimal documentation, maximum speed
- **Enterprise:** Heavy approval gates and compliance checks
- **Research:** Flexible exploration with different success criteria
- **Lightweight:** Document only when necessary

See `docs/system-prompts/workflows/custom-template.md` for full template and examples.

---

## How Workflows Work

### Workflow State Management

Your project's workflow preference is stored in AGENTS.md as a simple HTML comment:

```html
<!-- BOOTSTRAP-STATE: logs_first=enabled -->
```

This allows bootstrap.py to:
- Remember your choice across runs
- Enable/disable without special files
- Support future workflows

### Workflow Injection

When you enable a workflow, bootstrap.py:
1. Reads the workflow file (e.g., `docs/system-prompts/workflows/logs-first.md`)
2. Injects it into AGENTS.md as a new section
3. Saves the state marker

When you disable a workflow, bootstrap.py:
1. Removes the workflow section from AGENTS.md
2. Updates the state marker

---

## Choosing a Workflow

### Decision Tree

**Is your project small (< 200 files) and actively developed?**
→ logs-first workflow recommended

**Is your team > 10 people or project > 50K lines?**
→ Consider a lightweight or custom workflow

**Do you need heavy compliance/approval processes?**
→ Create custom enterprise workflow

**Is this a one-off script or experiment?**
→ No workflow needed (or very lightweight)

---

## Workflow Philosophy

### Why Workflows Matter

Different projects have different needs:
- **Small startups** need speed and flexibility
- **Enterprise teams** need process and accountability
- **Research projects** need exploration room
- **Open-source** needs community engagement

One-size-fits-all doesn't work. Workflows let you choose.

### The Logs-First Philosophy

The logs-first workflow emphasizes:
- **Clarity:** Document what you're building and why
- **Accountability:** Prove the work was done correctly
- **Continuity:** New team members understand the history
- **Quality:** Multi-step approval before execution

This works well for small teams where every decision matters.

---

## Managing Workflow State

### Viewing Current State

```bash
python3 docs/system-prompts/bootstrap.py --analyze-workflow
```

Shows:
- Recommended workflow for your project
- Current workflow state
- Available commands

### Changing Workflow

```bash
# Enable
python3 docs/system-prompts/bootstrap.py --enable-logs-first --commit

# Disable
python3 docs/system-prompts/bootstrap.py --disable-logs-first --commit

# Check (no changes)
python3 docs/system-prompts/bootstrap.py --analyze-workflow
```

### How State Persists

Once you enable a workflow:
- It stays enabled across subsequent runs
- Explicit commands override prior state
- State is stored in AGENTS.md (no separate config files)

**Example:**
```bash
# First run: enable logs-first
python3 bootstrap.py --enable-logs-first --commit

# Days later: state is preserved
python3 bootstrap.py --analyze-workflow
# Output: "Current state: logs_first=enabled"

# Can disable if needed
python3 bootstrap.py --disable-logs-first --commit
```

---

## Troubleshooting

### Workflow not appearing in AGENTS.md?

**Symptom:** You ran `--enable-logs-first --commit` but don't see it in AGENTS.md

**Solution:**
1. Check workflow file exists: `ls docs/system-prompts/workflows/logs-first.md`
2. Verify bootstrap.py can read it: `python3 bootstrap.py --analyze-workflow`
3. Try again with `--force` flag: `python3 bootstrap.py --enable-logs-first --commit --force`

### State shows disabled but want enabled?

**Symptom:** `--analyze-workflow` shows "logs_first=disabled"

**Solution:** Run enable command
```bash
python3 bootstrap.py --enable-logs-first --commit
```

### Custom workflow not recognized?

**Symptom:** `--enable-my-workflow` doesn't work

**Solution:**
1. Verify file exists: `ls docs/system-prompts/workflows/my-workflow.md`
2. Check bootstrap.py has your workflow in `section_map`
3. Check bootstrap.py has your command-line arguments
4. Run `python3 bootstrap.py --help` to see if your args appear

---

## For Project Maintainers

### Setting Up This Project

This project (second_voice) uses the logs-first workflow:

```bash
python3 docs/system-prompts/bootstrap.py --analyze-workflow
# Output: Recommended: logs-first, Current state: logs_first=enabled
```

### If Adding New Workflows

1. Create `docs/system-prompts/workflows/new-workflow.md`
2. Add to bootstrap.py `section_map`
3. Add command-line args to bootstrap.py
4. Document in this file (docs/workflows.md)
5. Update `docs/system-prompts/workflows/README.md`

### For Other Projects

Copy relevant workflow files and register them in your project's bootstrap.py:

```bash
cp docs/system-prompts/workflows/logs-first.md /path/to/other-project/docs/system-prompts/workflows/
# Then register in their bootstrap.py...
```

---

## Learn More

- **Full logs-first workflow guide:** `docs/system-prompts/workflows/logs-first.md`
- **Custom workflow template:** `docs/system-prompts/workflows/custom-template.md`
- **Workflow directory:** `docs/system-prompts/workflows/README.md`
- **Project templates:** `docs/templates.md`
- **Definition of Done:** `docs/definition-of-done.md`

---

## Questions?

- **How do I know if logs-first is right for me?** → See "Decision Tree" section above
- **Can I switch workflows later?** → Yes, just run the disable/enable commands
- **What if I don't like my workflow?** → Create a custom one that works better
- **How do I share a workflow with other projects?** → Copy the .md file and register in their bootstrap.py
