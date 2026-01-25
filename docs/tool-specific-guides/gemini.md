# Google Gemini - Guide (Supported)

**Status:** ✅ Supported

This guide describes how to use **Google Gemini CLI** with the AGENTS.md workflow.

## Quick Start

1.  **Install/Setup:** Ensure you have the Gemini CLI installed and configured.
2.  **Configuration:** Create a `GEMINI.md` file in the root of your project (see below).
3.  **Run:**
    ```bash
    gemini
    ```

## How Gemini Discovers Project Instructions

Gemini looks for a `GEMINI.md` file in the project root. This file serves the same purpose as `CLAUDE.md`.

## Workflow Mapping (AGENTS.md)

| AGENTS.md Step | Gemini Action | Tool Used |
|---|---|---|
| **A. Analyze** | Analyze request & context | Internal reasoning |
| **B. Spec** | Write spec file | `write_file` |
| **C. Plan** | Write plan file | `write_file` |
| **D. Approval** | Ask user for confirmation | **Conversation** (No explicit tool) |
| **E. Implement** | Edit files, run commands | `read_file`, `replace`, `run_shell_command` |
| **F. Verify** | Run tests | `run_shell_command` ("pytest") |

## Key Differences from Claude Code

| Feature | Claude Code | Gemini CLI |
|---|---|---|
| **Entry Point** | `CLAUDE.md` | `GEMINI.md` |
| **Approval** | `ExitPlanMode()` (Explicit) | **Conversational** ("Do you approve?") |
| **Git** | `Bash(git ...)` | `run_shell_command(git ...)` |
| **Task Tracking** | Built-in (`TaskCreate`) | **Manual** (via `dev_notes/`) |
| **Context** | ~200k tokens | ~1M+ tokens (1.5 Pro) |

## Configuration: GEMINI.md

Create a `GEMINI.md` file in your project root with the following content:

```markdown
# Second Voice - Gemini Instructions

## Core Workflow
This project follows the **AGENTS.md** workflow.
- **MANDATORY:** Read `AGENTS.md` before starting any task.
- **MANDATORY:** Read `docs/definition-of-done.md` before marking tasks complete.

## Development Environment
- **Language:** Python 3.12+
- **Testing:** `pytest`
- **Linting:** Standard Python conventions
- **Project Structure:**
  - `src/`: Source code
  - `tests/`: Unit tests
  - `dev_notes/`: Documentation & Plans

## Key Commands
- Run App: `python3 src/cli/run.py`
- Run Tests: `pytest`
- Check Types: `mypy .`
```

## Common Patterns

### 1. Creating a Plan
```
User: "Refactor the config loader"
Gemini: "I will analyze the request."
[Gemini reads files]
Gemini: "I have created a plan in dev_notes/project_plans/..."
Gemini: "Do you approve this plan?"
User: "Yes"
Gemini: [Proceeds to implementation]
```

### 2. Running Tests
```
Gemini: "I will verify the changes."
Tool: run_shell_command(command="pytest tests/test_config.py")
```

### 3. Git Operations
Gemini uses `run_shell_command` for git operations.
```
Tool: run_shell_command(command="git status")
Tool: run_shell_command(command="git add . && git commit -m '...'")
```

## FAQ / Known Issues

1.  **Approval Gates:** Gemini does not have a hard "ExitPlanMode" state. You must explicitly ask the user "Do you approve?" and wait for their text response.
2.  **Task Tracking:** Gemini does not have a `Task` tool. Use the `dev_notes/` directory to track progress.
3.  **File Editing:** Gemini uses `replace` which requires unique context. Ensure you provide enough context lines.

## Contributing

To update this guide:
1.  Verify new Gemini features.
2.  Update `GEMINI.md` template if needed.
3.  Update this file.