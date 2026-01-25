# OpenAI Codex CLI - Guide (Supported)

**Status:** ✅ Supported

This guide describes how to use the **OpenAI Codex CLI** (`@openai/codex`) with this project.

## Quick Start

```bash
# Install (requires Node.js 16+)
npm install -g @openai/codex

# Set API Key
export OPENAI_API_KEY="sk-..."

# Run in project root
cd /path/to/second_voice
codex
```

## Native AGENTS.md Support

**Codex CLI natively supports `AGENTS.md`!**

It automatically discovers and reads `AGENTS.md` from the repository root. No special configuration is required to make it follow our workflow.

## Configuration

Codex uses a global configuration file at `~/.codex/config.json` or `.yaml`.

### Recommended Config (`~/.codex/config.yaml`)

```yaml
model: gpt-4o
approvalMode: suggest  # or auto-edit / full-auto
notify: true
```

### Project-Specific Instructions

Codex looks for `AGENTS.md` in the following order (merging them):
1. `~/.codex/AGENTS.md` (Global)
2. `./AGENTS.md` (Project Root - **This exists!**)
3. `./subdir/AGENTS.md` (Directory specific)

## Workflow Mapping

| Feature | Codex Capability | AGENTS.md Integration |
|---|---|---|
| **Approval Gates** | `--approval-mode` | Use `suggest` mode for manual approval. |
| **Context** | Auto-reads files | Reads `AGENTS.md` natively. |
| **Git** | Auto-commits | Can be configured/requested. |
| **Sandboxing** | macOS/Linux sandbox | Runs commands safely. |

## Usage Patterns

### Interactive Mode
```bash
codex
> "Refactor src/cli/run.py to use Click instead of argparse"
```

### Non-Interactive (CI/Scripting)
```bash
codex --quiet --approval-mode auto-edit "Fix linting errors in src/"
```

### Asking for Plans
```bash
codex "Create a project plan for adding a new STT provider in dev_notes/project_plans/"
```

## Key Differences from Claude Code

- **Language:** Node.js/Rust based.
- **Sandboxing:** Has built-in OS-level sandboxing (Seatbelt/Docker).
- **Approval:** granular modes (`suggest`, `auto-edit`, `full-auto`).
- **Context:** Natively designed around `AGENTS.md`.

## FAQ

**Q: Does it support other providers?**
A: Yes, via `--provider` (e.g., `--provider ollama`, `--provider anthropic`).

**Q: How do I stop it from editing files?**
A: Run in `suggest` mode (default). It will ask before writing.

**Q: Can it run tests?**
A: Yes, it can execute shell commands like `pytest`.

## Verification Status

- ✅ CLI Tool exists and is active.
- ✅ Native `AGENTS.md` support confirmed.
- ✅ Workflow compatible with `second_voice`.