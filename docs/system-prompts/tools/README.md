# Tool-Specific Workflow Guides

This directory contains generic, reusable workflow guides for integrating different AI development tools with the AGENTS.md workflow.

## Available Guides

- **[claude-code.md](./claude-code.md)** - Claude Code (Python CLI, Anthropic)
  - Interactive development IDE with explicit approval gates (ExitPlanMode)
  - Comprehensive toolset (Read, Write, Edit, Bash, Task)
  - Best for structured workflows with detailed planning

- **[aider.md](./aider.md)** - Aider (Terminal-based code editor)
  - Trust-based collaboration with cascade agents
  - Multi-file refactoring with automatic testing
  - Git-first workflow with readable commits

- **[cline.md](./cline.md)** - Cline (Code editor CLI)
  - Open-source interactive development tool
  - Multi-file editing with auto-commit to git
  - Flexible approval modes (suggest, auto, conversational)

- **[codex.md](./codex.md)** - OpenAI Codex (Code editor CLI)
  - Native AGENTS.md discovery
  - Granular approval modes (suggest, auto-edit, full-auto)
  - GPT-5.2 optimization for long-horizon tasks

- **[gemini.md](./gemini.md)** - Google Gemini (Open-source AI agent CLI)
  - ReAct loop architecture with reasoning transparency
  - MCP (Model Context Protocol) for custom integrations
  - Web search grounding and SWE-bench verified models

## Purpose & Reusability

These guides are **generic documentation** explaining how each tool integrates with AGENTS.md workflow patterns. They are **not project-specific** and can be:

- Copied to other projects
- Referenced by bootstrap.py
- Integrated into system-prompts infrastructure
- Used as reference material for developers

## Project-Specific Tool Guides

For guides specific to individual projects (e.g., how Cline integrates with second_voice), see the project's `docs/tool-specific-guides/` directory.

## How Agents Use These Guides

These guides are **reference material**, not mandatory loading for agents. Agents should:

- Consult these when they need to understand a tool's capabilities
- Use them for troubleshooting tool-specific issues
- Reference patterns and examples as needed
- NOT treat them as imperative instructions to follow

Mandatory tool instructions (how to use ExitPlanMode, basic workflow mapping) are located in AGENTS.md or tool-specific configuration files (CLAUDE.md, GEMINI.md, AIDER.md).

## Conditional References

These guides contain **optional technique documentation**:

- Timestamped file naming patterns (used if logs-first is enabled)
- Approval gate mechanisms (used if tool supports them)
- Dev_notes workflow examples (used if logs-first is enabled)

**All techniques are described as conditional:** "If you need to...", "When using...", "Optional pattern...". They do NOT mandate specific behavior.

## Updates & Maintenance

When updating these guides:

1. Maintain **tool-agnostic language** where possible
2. Use **conditional phrasing** for project-specific patterns
3. Keep **technique-focused** rather than prescriptive
4. Document **as reference material**, not mandatory instructions
5. Test **referential integrity** across projects
