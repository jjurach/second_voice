# Documentation Index

Complete documentation for Second Voice.

## Quick Start

**For AI Agents:**
- Start with **[AGENTS.md](../AGENTS.md)** - Mandatory workflow and unbreakable rules
- Check **[Definition of Done](definition-of-done.md)** - Quality standards

**For Developers:**
- Read **[README.md](../README.md)** - Project overview
- See **[Contributing](../docs/contributing.md)** - How to contribute (if exists)
- Review **[Architecture](architecture.md)** - System design

## For AI Agents

### Core Workflow
- **[AGENTS.md](../AGENTS.md)** - Mandatory A-E workflow
- **[Definition of Done](definition-of-done.md)** - Complete quality checklist
- **[Workflows](workflows.md)** - Development workflows
- **[Templates](templates.md)** - Planning document templates

### Tool-Specific Guides
- **[Aider Guide](system-prompts/tools/aider.md)** - Aider documentation
- **[Claude Code Guide](system-prompts/tools/claude-code.md)** - Claude Code documentation
- **[Cline Guide](system-prompts/tools/cline.md)** - Cline documentation
- **[Gemini Guide](system-prompts/tools/gemini.md)** - Gemini documentation

## Architecture & Design

- **[Architecture](architecture.md)** - System architecture
- **[Implementation Reference](implementation-reference.md)** - Implementation patterns
- **[Mandatory Guidelines](mandatory.md)** - Project-specific rules

## Project-Specific Sections

### Audio Processing
- **[AAC Handler](../src/second_voice/audio/aac_handler.py)** - AAC file handling
- **[Recorder](../src/second_voice/core/recorder.py)** - Audio recording logic

### CLI
- **[Run Script](../src/cli/run.py)** - CLI entry point
- **[CLI Tests](../tests/test_cli.py)** - CLI testing

## System Prompts (Agent Kernel)

The Agent Kernel provides reusable workflows and standards:

- **[Agent Kernel README](system-prompts/README.md)** - Complete Agent Kernel documentation
- **[Universal DoD](system-prompts/principles/definition-of-done.md)** - Universal Definition of Done
- **[Python DoD](system-prompts/languages/python/definition-of-done.md)** - Python-specific standards
- **[Templates](system-prompts/templates/structure.md)** - Document structure templates
- **[Workflows](system-prompts/workflows/README.md)** - Workflow documentation

## Navigation Tips

### Finding Information

**"How do I mark a task done?"**
→ [Definition of Done](definition-of-done.md)

**"What is the system architecture?"**
→ [Architecture](architecture.md)

**"Where are the templates?"**
→ [Templates](templates.md)

### For AI Agents Starting Work

1. Read [AGENTS.md](../AGENTS.md) - Mandatory workflow
2. Check [Definition of Done](definition-of-done.md) - Quality standards
3. Review [Workflows](workflows.md) - Development processes
4. Use [Templates](templates.md) - For planning documents

## See Also

- **[Project README](../README.md)** - Main project documentation
- **[AGENTS.md](../AGENTS.md)** - Agent workflow and rules

---
Last Updated: 2026-01-29
