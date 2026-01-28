# Definition of Done - Second Voice

**Referenced from:** [AGENTS.md](../AGENTS.md)

This document defines the "Done" criteria for Second Voice. It extends the universal Agent Kernel Definition of Done with project-specific requirements.

## Agent Kernel Definition of Done

This project follows the Agent Kernel Definition of Done. **You MUST review these documents first:**

### Universal Requirements

See **[Universal Definition of Done](system-prompts/principles/definition-of-done.md)** for:
- Plan vs Reality Protocol
- Verification as Data
- Codebase State Integrity
- Agent Handoff
- Status tracking in project plans
- dev_notes/ change documentation requirements

### Python Requirements

See **[Python Definition of Done](system-prompts/languages/python/definition-of-done.md)** for:
- Python environment & dependencies
- Testing requirements (pytest)
- Code quality standards
- File organization
- Coverage requirements

## Project-Specific Extensions

The following requirements are specific to Second Voice and extend the Agent Kernel DoD:

### 1. Configuration & Dependencies

**Configuration Drift:**
- If you modify configuration, update **`config.example.json`** (not just generic config files).
- Update `docs/implementation-reference.md` or `docs/config.md`.

**Dependencies:**
- If any new library is imported, you must update BOTH:
  - `requirements.txt`
  - `pyproject.toml`

### 2. Documentation Reference Formatting

**Hyperlinks for Navigation:**
- When creating a reference that users should navigate to, use markdown hyperlinks: `[text](path)`
- Examples: `[AGENTS.md](AGENTS.md)`, `[docs/test-guide.md](docs/test-guide.md)`

**Backticks for File References in Prose:**
- When mentioning a file inline in text, use backticks: `` `filename.md` ``
- Examples: "The `AGENTS.md` file defines the workflow"

**What NOT to Do:**
- Do NOT use plain text file references: ❌ "See AGENTS.md" (no formatting)

### 3. Pre-Commit Checklist

**Code Quality:**
- [ ] Python formatting applied
- [ ] Linting passes
- [ ] Type hints present

**Testing:**
- [ ] All unit tests pass: `pytest`
- [ ] Integration tests pass (if applicable)

**Project-Specific Checks:**
- [ ] `config.example.json` updated for any new config keys
- [ ] `requirements.txt` AND `pyproject.toml` synced

## See Also

- [AGENTS.md](../AGENTS.md) - Core A-E workflow
- [Universal DoD](system-prompts/principles/definition-of-done.md) - Agent Kernel universal requirements
- [Python DoD](system-prompts/languages/python/definition-of-done.md) - Agent Kernel language requirements
- [Architecture](architecture.md) - System design
- [Implementation Reference](implementation-reference.md) - Code patterns
- [Workflows](workflows.md) - Development workflows

---
Last Updated: 2026-01-28