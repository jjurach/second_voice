# Tool Capabilities Matrix

This document defines the capabilities and constraints of each supported CLI tool. Use this to understand what each tool can and cannot do, and how to adapt AGENTS.md workflows accordingly.

## Overview

| Capability | Claude Code | Aider | Gemini | Codex |
|-----------|------------|-------|--------|-------|
| **Git Integration** | ✅ Native | ✅ Native | ❓ Unknown | ❓ Unknown |
| **Approval Gates** | ✅ Built-in | ❌ Implicit | ❓ Unknown | ❓ Unknown |
| **Task Tracking** | ✅ TaskCreate | ❌ Manual | ❓ Unknown | ❓ Unknown |
| **Function Calling** | ✅ Full | ⚠️ Limited | ✅ Full | ❓ Unknown |
| **File Editing** | ✅ Edit tool | ✅ Direct | ✅ Via tool | ❓ Unknown |
| **Shell Commands** | ✅ Bash tool | ✅ Shell | ⚠️ Likely | ❓ Unknown |
| **MCP Servers** | ✅ Yes | ❌ No | ❓ Unknown | ❓ Unknown |
| **Web Search** | ✅ Yes | ⚠️ Maybe | ✅ Likely | ❓ Unknown |
| **Context Window** | ~200k tokens | Varies | ~32k tokens | ❓ Unknown |
| **Agent SDK** | ✅ Yes | ❌ No | ❓ Unknown | ❓ Unknown |

---

## Detailed Tool Profiles

### Claude Code (claude-cli)

**Status:** ✅ Fully Supported

**Overview:** Official Anthropic CLI tool for Claude with full integration to Claude's capabilities.

**Key Capabilities:**
- ✅ Full function calling (20+ tools)
- ✅ Native git integration (commit, push, etc.)
- ✅ Task tracking (TaskCreate, TaskUpdate, TaskList)
- ✅ MCP server support
- ✅ Web search and fetch
- ✅ Structured output (JSON, YAML)
- ✅ Agent SDK for custom agents
- ✅ Background task execution

**Approval Workflow:**
- Mandatory approval for plans via AGENTS.md Step D
- User must explicitly say "yes", "approved", "proceed", etc.
- Ambiguous responses require clarification
- No auto-execution of plans

**File Operations:**
- Read, Write, Edit, Glob, Grep tools with full semantics
- Proper error handling and validation
- Supports temporary files in current directory

**Git Operations:**
- Full Bash integration for git commands
- Proper commit message handling with heredoc
- Can create branches, tags, push, pull
- Pre-commit hooks supported

**Constraints:**
- Token limit: ~200k (Haiku 4.5)
- No destructive operations without explicit user request
- Cannot skip git hooks without user approval
- Proper quoting required for file paths with spaces

**Entry Point:** `CLAUDE.md` → `AGENTS.md`

**Approval Model:** Explicit (required)

---

### Aider

**Status:** ⚠️ Partially Supported

**Overview:** Collaborative AI coding tool with excellent code awareness and git integration.

**Key Capabilities:**
- ✅ Git integration (auto-commits changes)
- ✅ Code-aware editing (understands diffs)
- ✅ Excellent context preservation
- ✅ Shell commands
- ⚠️ Limited function calling (mostly manual)
- ⚠️ Web search (depends on model)

**Approval Workflow:**
- ❌ **No approval gates** - Aider edits files immediately
- Implicit approval through conversation
- Cannot pause for user confirmation mid-task
- Each response should be reversible (via git)

**File Operations:**
- Direct file editing (no separate Edit tool)
- Diffs shown before changes
- Full git awareness (shows uncommitted changes)
- Can list files and show code context

**Git Operations:**
- ✅ Auto-commits after changes
- Commit messages generated or from prompts
- Full git access via shell
- Excellent for showing diffs

**Constraints:**
- ❌ No task tracking (TaskCreate doesn't exist)
- ❌ No structured approval (must trust AI judgment)
- Token limits vary by model
- Cannot use MCP servers
- Limited to what the model supports

**Differences from Claude Code:**
- No "pause for approval" capability
- Must frame work as guidance, not orders
- Changes are immediate, not staged for review
- Git is primary undo mechanism

**Entry Point:** `.aider.conf` → Bridge docs

**Approval Model:** Implicit (trust-based)

---

### Google Gemini

**Status:** ❓ Experimental

**Overview:** Google's latest AI model with multimodal capabilities.

**Key Capabilities:**
- ✅ Function calling (though syntax differs from Claude)
- ✅ Multimodal input (images, audio, video)
- ✅ Very fast inference
- ✅ Web search integration
- ⚠️ Lower context window (~32k tokens typical)
- ❓ Git integration (unknown)
- ❓ Task tracking (unknown)

**Approval Workflow:**
- ❓ Unknown if approval gates possible
- ❓ May require per-tool approval
- Implementation TBD

**File Operations:**
- Function calling for file operations
- Tool names likely different from Claude
- May have different parameter semantics

**Git Operations:**
- Likely available via shell function call
- Syntax TBD

**Constraints:**
- Lower context window (32k typical)
- Function calling syntax differs from Claude
- Tool names and parameters may differ
- Model capabilities less tested for agentic work

**Entry Point:** `.gemini-cli.yaml` (to be created)

**Approval Model:** TBD

---

### OpenAI Codex / GPT-4

**Status:** ❌ Not Yet Supported

**Overview:** OpenAI's code generation and reasoning model.

**Key Capabilities:**
- ✅ Function calling (similar to Claude)
- ✅ Code understanding
- ⚠️ Web search (requires separate integration)
- ❓ Git integration (unknown)
- ❓ Task tracking (unknown)
- ❓ MCP server support (unknown)

**Approval Workflow:**
- ❓ Unknown

**File Operations:**
- Function calling for file operations
- Tool names likely different

**Git Operations:**
- Likely available via shell
- Syntax TBD

**Constraints:**
- Different function calling conventions
- Tool parameter semantics differ
- Less integration with code-specific workflows

**Entry Point:** `.codex-cli.yaml` (to be created)

**Approval Model:** TBD

---

## Capability Comparison Table (Detailed)

### Core Features
| Feature | Claude | Aider | Gemini | Codex |
|---------|--------|-------|--------|-------|
| Function calling | ✅ 20+ tools | ❌ No | ✅ Yes | ✅ Yes |
| Approval gates | ✅ Yes | ❌ No | ❓ TBD | ❓ TBD |
| Task tracking | ✅ Yes | ❌ No | ❓ TBD | ❓ TBD |
| Git auto-commit | ⚠️ Manual | ✅ Auto | ❓ TBD | ❓ TBD |
| Code awareness | ⚠️ Limited | ✅ Excellent | ❌ Lower | ✅ Excellent |
| Multimodal | ❌ No | ❌ No | ✅ Yes | ❌ No |

### File & Development
| Feature | Claude | Aider | Gemini | Codex |
|---------|--------|-------|--------|-------|
| Read files | ✅ Read tool | ✅ Shell | ✅ Function | ✅ Function |
| Edit files | ✅ Edit tool | ✅ Direct | ✅ Function | ✅ Function |
| Create files | ✅ Write tool | ✅ Direct | ✅ Function | ✅ Function |
| Search files | ✅ Grep/Glob | ✅ Shell | ✅ Function | ✅ Function |
| Diff viewing | ❌ Manual | ✅ Auto | ❓ TBD | ❓ TBD |

### Integration & Learning
| Feature | Claude | Aider | Gemini | Codex |
|---------|--------|-------|--------|-------|
| MCP servers | ✅ Yes | ❌ No | ❓ TBD | ❌ No |
| Agent SDK | ✅ Yes | ❌ No | ❓ TBD | ❌ No |
| Web search | ✅ Yes | ⚠️ Maybe | ✅ Yes | ⚠️ Maybe |
| Context retention | ✅ Good | ✅ Good | ⚠️ Limited | ⚠️ Limited |
| Token efficiency | ⚠️ 200k | ✅ Adaptive | ⚠️ 32k | ⚠️ Varies |

---

## Constraint Categories

### Approval Constraints
- **Hard Approval Required:** Claude Code (Step D of AGENTS.md)
- **Implicit Approval:** Aider (changes applied immediately)
- **Unknown:** Gemini, Codex

### File Operation Constraints
- **Dedicated Tools:** Claude (Read, Write, Edit, Glob, Grep)
- **Shell-Based:** Aider, likely Codex/Gemini
- **Function Calling:** Gemini, likely Codex

### Git Constraints
- **Manual:** Claude (user responsible for commits)
- **Automatic:** Aider (commits after changes)
- **Unknown:** Gemini, Codex

### Context Constraints
- **Large:** Claude (200k tokens) - Full repo context possible
- **Medium:** Aider (varies) - Good for focused work
- **Small:** Gemini (32k typical) - May need file selection

### Tool Integration
- **Rich:** Claude (MCP, Agent SDK, web search)
- **Basic:** Aider (shell only)
- **Unknown:** Gemini, Codex

---

## Decision Tree: Choosing a Tool

```
Do you need explicit approval gates for plans?
  YES → Use Claude Code (AGENTS.md required)
  NO  → Consider Aider (implicit approval)

Do you need task tracking?
  YES → Use Claude Code (TaskCreate/TaskUpdate)
  NO  → Any tool works

Is the project large (full repo context)?
  YES → Use Claude Code (200k tokens)
  NO  → Aider or Gemini acceptable

Do you need multimodal input (images, etc)?
  YES → Use Gemini
  NO  → Any tool works

Do you need MCP server integration?
  YES → Use Claude Code
  NO  → Any tool works

Is code awareness critical?
  YES → Use Aider or Claude Code
  NO  → Any tool works
```

---

## Implementing AGENTS.md for Each Tool

### For Claude Code:
- ✅ Follow AGENTS.md exactly as written
- ✅ All features supported
- ✅ Use entry point: CLAUDE.md

### For Aider:
- ⚠️ Skip Step D (approval gates) - use implicit approval
- ⚠️ Skip TaskCreate/TaskUpdate - use dev_notes directly
- ⚠️ Frame requests as collaborative guidance
- ✅ Use entry point: WORKFLOW-MAPPING.md → aider guide

### For Gemini/Codex:
- ⚠️ TBD based on testing
- ❓ Approval gates unknown
- ❓ Task tracking unknown
- 📝 See TOOL-SPECIFIC-GUIDES as they're created

---

## Universal Requirements

Regardless of tool, all AGENTS.md-compliant work must:

1. **Create a spec file** in `dev_notes/specs/` with timestamp
2. **Create a plan file** in `dev_notes/project_plans/` with timestamp (if non-trivial)
3. **Document changes** in `dev_notes/changes/` after each logical step
4. **Follow code patterns** - match existing style and conventions
5. **No secrets in commits** - .env, credentials, keys always .gitignore'd
6. **Quality first** - Code quality > Speed

These requirements are tool-agnostic and apply to all implementations.

---

## Future Tool Support

To add support for a new tool:

1. Create `docs/TOOL-SPECIFIC-GUIDES/{tool-name}.md`
2. Document capability profile here
3. Add tool-specific workflow to WORKFLOW-MAPPING.md
4. Create `.{tool}-config` file if needed
5. Update README with tool entry points
6. Test AGENTS.md compliance with tool

---

## Contributing to This Document

When adding support for a new tool, update:
- This capabilities matrix
- WORKFLOW-MAPPING.md
- TOOL-SPECIFIC-GUIDES/ directory
- README.md

Keep information current as tool capabilities evolve.
