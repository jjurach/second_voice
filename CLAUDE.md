# Claude Code Instructions

This project follows the **AGENTS.md** workflow for all development.

## Using Claude Code with This Project

1. **Read AGENTS.md first** - Understand the core development workflow (mandatory)
2. **Understand logs-first (optional)** - See `docs/workflows.md` if you want to use structured planning
3. **See Claude Code specifics below** - How to use Claude Code with this project's patterns

## Key Concepts

**When the user refers to "the plan" or "a plan" or "project plans" etc.:** They are referring to what is in AGENTS.md regarding that topic.

## Available Tools

Claude Code provides these tools for development:
- **Read** - Read files from the project
- **Write** - Create new files
- **Edit** - Modify existing files
- **Bash** - Execute shell commands
- **Task** - Create and manage development tasks
- **ExitPlanMode** - Request explicit approval for project plans
- **WebFetch** - Retrieve web content
- **WebSearch** - Search the internet

## For Claude Code Users

See **[docs/system-prompts/tools/claude-code.md](docs/system-prompts/tools/claude-code.md)** for:
- Complete workflow integration guide
- How to use each tool
- Approval gate patterns (ExitPlanMode)
- Common patterns and examples
- Troubleshooting

## Development Environment

- **Language:** Python 3.12+
- **Testing:** `pytest`
- **Linting:** PEP 8 style guide
- **Project Structure:**
  - `src/` - Source code
  - `tests/` - Unit tests
  - `docs/` - Documentation
  - `dev_notes/` - Planning and documentation

## Key Resources

- **AGENTS.md** - Core workflow (mandatory, read first)
- **CLAUDE.md** - This file (entry point)
- **docs/definition-of-done.md** - Completion criteria
- **docs/system-prompts/tools/claude-code.md** - Claude-specific guide
- **docs/workflows.md** - Optional logs-first workflow
- **docs/file-naming-conventions.md** - Naming standards

## Quick Start

1. Read AGENTS.md to understand the workflow
2. For any request, follow Steps A-E
3. Use ExitPlanMode() before implementing non-trivial plans
4. Consult definition-of-done.md before marking work complete
5. See tool-specific guide for detailed usage patterns
