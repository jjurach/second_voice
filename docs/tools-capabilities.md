# Tool Capabilities Matrix

This document defines the capabilities and constraints of each supported CLI tool. Use this to understand what each tool can and cannot do, and how to adapt AGENTS.md workflows accordingly.

## Overview

| Capability | Claude Code | Aider | Gemini | Codex |
|-----------|------------|-------|--------|-------|
| **Git Integration** | ✅ Native | ✅ Auto-commit | ⚠️ Via Shell | ✅ Auto-commit |
| **Approval Gates** | ✅ Built-in | ❌ Conversational | ⚠️ Conversational | ✅ Granular |
| **Task Tracking** | ✅ TaskCreate | ❌ Manual | ❌ Manual | ❌ Manual |
| **Function Calling** | ✅ Full | ⚠️ Limited | ✅ Full | ✅ Full |
| **File Editing** | ✅ Edit tool | ✅ Direct | ✅ Replace tool | ✅ Auto-Edit |
| **Shell Commands** | ✅ Bash tool | ✅ Shell | ✅ Shell tool | ✅ Shell |
| **MCP Servers** | ✅ Yes | ❌ No | ✅ Yes | ❌ No |
| **Web Search** | ✅ Yes | ⚠️ Maybe | ✅ Yes | ⚠️ Maybe |
| **Context Window** | ~200k | Varies | ~1M+ | Varies |
| **Entry Point** | `CLAUDE.md` | `.aider.conf.yml` | `GEMINI.md` | `AGENTS.md` |

---

## Detailed Tool Profiles

### Claude Code (claude-cli)

**Status:** ✅ Fully Supported

**Overview:** Official Anthropic CLI tool for Claude with full integration to Claude's capabilities.

**Key Capabilities:**
- ✅ Full function calling (20+ tools)
- ✅ Native git integration
- ✅ Task tracking (TaskCreate, TaskUpdate)
- ✅ MCP server support
- ✅ Web search and fetch
- ✅ Agent SDK

**Approval Workflow:**
- **Explicit:** Mandatory `ExitPlanMode()` step blocks execution until user approves.

**File/Git Operations:**
- Dedicated tools for Read, Write, Edit, Bash.
- Manual commit workflow (user controls commits).

**Entry Point:** `CLAUDE.md`

---

### Aider

**Status:** ✅ Supported

**Overview:** Collaborative AI coding tool with excellent code awareness and auto-commits.

**Key Capabilities:**
- ✅ Auto-commits changes (Granular history)
- ✅ Code-aware editing (understands diffs)
- ✅ Excellent context preservation
- ⚠️ Conversational approval only

**Approval Workflow:**
- **Implicit/Conversational:** No hard gate. User must review diffs and say "ok" or "go ahead" in chat.

**File/Git Operations:**
- Direct file editing.
- Automatic commits after every logical change.

**Entry Point:** `.aider.conf.yml`

---

### Google Gemini CLI

**Status:** ✅ Supported

**Overview:** Google's multimodal AI agent for the terminal.

**Key Capabilities:**
- ✅ Multimodal input (images, audio)
- ✅ Fast inference (Flash models)
- ✅ Web search integration
- ✅ Large context window (1M+ tokens)

**Approval Workflow:**
- **Conversational:** Agent asks "Do you approve?" before taking critical actions.

**File/Git Operations:**
- Uses `read_file`, `write_file`, `replace`.
- Uses `run_shell_command` for git operations.

**Entry Point:** `GEMINI.md`

---

### OpenAI Codex CLI

**Status:** ✅ Supported

**Overview:** Official OpenAI CLI with native support for agentic workflows.

**Key Capabilities:**
- ✅ **Native AGENTS.md support** (Auto-discovery)
- ✅ Granular approval modes (`suggest`, `auto-edit`, `full-auto`)
- ✅ OS-level sandboxing (Seatbelt/Docker)
- ✅ Multi-provider support

**Approval Workflow:**
- **Configurable:** Can be strict (`suggest`) or autonomous (`full-auto`).

**File/Git Operations:**
- Intelligent file patching.
- Can automate git operations.

**Entry Point:** `AGENTS.md` (Native discovery)

---

## Decision Tree: Choosing a Tool

```
Do you need explicit approval gates?
  YES → Use Claude Code OR Codex (suggest mode)
  NO  → Consider Aider (implicit approval)

Do you need task tracking?
  YES → Use Claude Code
  NO  → Any tool (track manually in dev_notes/)

Is the project large (full repo context)?
  YES → Gemini (1M+) or Claude Code (200k)
  NO  → Aider or Codex acceptable

Do you need multimodal input?
  YES → Use Gemini
  NO  → Any tool works

Do you need MCP server integration?
  YES → Use Claude Code or Gemini
  NO  → Aider or Codex

Is code awareness/diff review critical?
  YES → Use Aider
  NO  → Any tool works
```

---

## Universal Requirements

Regardless of tool, all AGENTS.md-compliant work must:

1. **Create a spec file** in `dev_notes/specs/`
2. **Create a plan file** in `dev_notes/project_plans/`
3. **Document changes** in `dev_notes/changes/`
4. **Follow code patterns**
5. **No secrets in commits**

---

## Contributing to This Document

When adding support for a new tool:

**For generic, reusable tool guides:**
1. Create `docs/system-prompts/tools/{tool}.md`
2. Update this matrix
3. Document AGENTS.md workflow mapping
4. Verify reusability across projects

**For project-specific tool integrations:**
1. Create `docs/tool-specific-guides/{tool}.md`
2. Update this matrix
3. Create entry point config file (if needed)
4. Verify AGENTS.md workflow compliance
---
Last Updated: 2026-01-28
