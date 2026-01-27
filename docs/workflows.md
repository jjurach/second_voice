# Workflows in Agent Kernel

**What are workflows?** Workflows are optional sets of instructions that govern how AI agents approach development tasks. They let you adapt the Agent Kernel to your project's needs without losing consistency or accountability.

---

## Quick Start: Opt-In Per Task

### For Simple Tasks

Just create a spec file without any special marker:

```markdown
# Spec: Fix button color

Fix the primary button to match brand colors.
```

Standard workflow applies - faster, less documentation.

### For Complex Tasks

Add `@logs-first` marker to trigger structured planning:

```markdown
# Spec: Implement Authentication System

**Workflow:** @logs-first

This system will handle user login, session management, and API key validation...
```

Agent will now:
1. Create a Project Plan
2. Wait for approval before implementing
3. Track all changes in dev_notes/
4. Verify completion rigorously

### Project-Level Configuration (Optional)

For teams that want logs-first by default:

```bash
python3 docs/system-prompts/bootstrap.py --enable-logs-first --commit
```

For teams that want to disable it entirely:

```bash
python3 docs/system-prompts/bootstrap.py --disable-logs-first --commit
```

---

## Available Workflows

### Logs-First Workflow

**What it is:** A comprehensive workflow that emphasizes documentation and accountability through three connected documents: Spec (often from Inbox) → Project Plan → Change Documentation.

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

## When to Use the Logs-First Marker

### Use `@logs-first` for:

✅ **Architectural decisions** - Changes that affect multiple systems
✅ **New major features** - Authentication, payment systems, etc.
✅ **Security/compliance work** - API design, encryption, permissions
✅ **Refactoring** - Large-scale restructuring that affects many files
✅ **Infrastructure changes** - Database schema, deployment pipeline
✅ **When you want structured review** - Get explicit approval before coding

### Skip the marker for:

⏩ **Bug fixes** - Simple patches and corrections
⏩ **UI polish** - Minor style/UX improvements
⏩ **Documentation updates** - README, docstrings, comments
⏩ **Dependency updates** - Routine library upgrades
⏩ **When you know the approach** - Straightforward implementations

### Decision Tree

**Is this a significant architectural change?**
→ Use `@logs-first` marker

**Will this change affect multiple systems?**
→ Use `@logs-first` marker

**Do you want structured approval before coding?**
→ Use `@logs-first` marker

**Is this a simple, focused task?**
→ Skip the marker (use standard workflow)

---

## Workflow Philosophy

### Why Per-Task Opt-In?

**Gradual adoption:** Introduce the workflow naturally, one feature at a time.

**No surprises:** Developers see the `@logs-first` marker and know what's expected.

**Flexible rigor:** Different tasks get different levels of structure based on complexity.

**Team learning:** New team members encounter the workflow when it matters most.

**Low barrier:** Simple tasks stay fast; complex ones get the rigor they need.

### The Logs-First Approach

When you include `@logs-first`:
- **Clarity:** Explicit planning before building
- **Accountability:** Documented decisions and proof of work
- **Continuity:** Future maintainers understand the reasoning
- **Quality:** Structured review gate before implementation
- **Flexibility:** Only triggered when needed

This opt-in model works well for teams gradually adopting structured practices.

---

## Project-Level Configuration (Optional)

### Default Behavior

By default, logs-first is **not** enabled project-wide. Individual tasks opt-in via the `@logs-first` marker in their spec file.

This is intentional: it lets teams experience the workflow per-task without forcing it on everyone.

### Enabling Project-Wide

If your entire team wants logs-first by default:

```bash
python3 docs/system-prompts/bootstrap.py --enable-logs-first --commit
```

This injects the full workflow into AGENTS.md, so all tasks follow it unless explicitly exempted.

### Disabling Project-Wide

To remove logs-first even from opt-in specs:

```bash
python3 docs/system-prompts/bootstrap.py --disable-logs-first --commit
```

### Viewing Current State

```bash
python3 docs/system-prompts/bootstrap.py --analyze-workflow
```

Shows:
- Recommended workflow for your project
- Current project-level state
- Available commands

### How State Persists

Project-level workflow state is stored in AGENTS.md and persists across runs, so your choice is remembered.

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
