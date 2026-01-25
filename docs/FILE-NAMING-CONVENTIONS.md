# File Naming Conventions: Which Names Matter?

This document clarifies which file names are **tool-specific standards**, which are **just for linking/reference**, and which names can be changed.

## TL;DR

| File/Pattern | Auto-Discovered? | Required? | Can Rename? | Purpose |
|---|---|---|---|---|
| `CLAUDE.md` | ✅ Claude Code | Yes for claude-cli | No | Claude entry point |
| `.aider.conf` | ✅ Aider | Yes for aider | No | Aider config |
| `pytest.ini` | ✅ pytest | Recommended | No | Test configuration |
| `AGENTS.md` | ❌ No | Core principle | Yes, but update links | Workflow definition |
| `docs/TOOLS-CAPABILITIES.md` | ❌ No | No (reference only) | ✅ YES - just update links | Capability matrix |
| `docs/WORKFLOW-MAPPING.md` | ❌ No | No (reference only) | ✅ YES - just update links | Workflow guide |
| `docs/PROMPT-PATTERNS.md` | ❌ No | No (reference only) | ✅ YES - just update links | Prompt examples |
| `docs/TOOL-SPECIFIC-GUIDES/` | ❌ No | No (reference only) | ✅ YES - just update links | Per-tool guides |
| `dev_notes/specs/` | ❌ No | Core principle | No (timestamp format) | Spec files |
| `dev_notes/project_plans/` | ❌ No | Core principle | No (timestamp format) | Plan files |
| `dev_notes/changes/` | ❌ No | Core principle | No (timestamp format) | Change docs |

---

## Auto-Discovered Files (Tool-Specific)

These files are **automatically discovered and read** by the tools. Their names are **non-negotiable**.

### CLAUDE.md
- **Discovered by:** Claude Code CLI
- **Auto-loaded:** Yes, automatically read when using `claude-code` or `claude` CLI
- **Cannot rename:** ❌ No - tool looks for this specific name
- **Purpose:** Entry point containing project instructions
- **Current status:** ✅ Already created in your project
- **Content:** Should reference AGENTS.md

**Example:**
```markdown
# Claude Code Instructions

See AGENTS.md for the complete workflow.
```

### .aider.conf
- **Discovered by:** Aider CLI
- **Auto-loaded:** Yes, automatically read when using `aider`
- **Cannot rename:** ❌ No - tool looks for this specific name
- **Purpose:** Aider-specific configuration
- **Current status:** ⚠️ Not yet created (optional for your project)
- **Content:** Aider configuration + reference to AGENTS.md

**Example:**
```yaml
[aider]
# Aider config options
auto-commits = true

# Reference to AGENTS.md workflow
# See AGENTS.md for approval and documentation practices
```

### .gemini-cli.yaml or similar
- **Discovered by:** Gemini CLI (if it exists)
- **Auto-loaded:** Probably (TBD)
- **Cannot rename:** ❌ Probably not - tool will look for specific name
- **Purpose:** Gemini-specific configuration
- **Current status:** ❓ Unknown (tool not fully supported yet)

### pytest.ini
- **Discovered by:** pytest
- **Auto-loaded:** Yes, automatically read when running `pytest`
- **Cannot rename:** ❌ No - pytest looks for this specific name
- **Purpose:** pytest configuration
- **Current status:** ✅ Already created
- **Content:** Test configuration (tool-agnostic testing setup)

---

## Reference Files (Just Documentation)

These files are **NOT automatically discovered**. They exist only because other documents **link to them**. **You can rename them as long as you update the links.**

### docs/TOOLS-CAPABILITIES.md
- **Auto-discovered:** ❌ No
- **Referenced by:** README.md, AGENTS.md, WORKFLOW-MAPPING.md
- **Can rename:** ✅ YES - if you update links everywhere
- **Suggested names if renaming:**
  - `docs/tool-capabilities-matrix.md`
  - `docs/CAPABILITY-MATRIX.md`
  - `docs/supported-tools.md`

### docs/WORKFLOW-MAPPING.md
- **Auto-discovered:** ❌ No
- **Referenced by:** AGENTS.md, README.md, TOOLS-CAPABILITIES.md
- **Can rename:** ✅ YES - if you update links everywhere
- **Suggested names if renaming:**
  - `docs/tool-workflow-mapping.md`
  - `docs/TOOL-WORKFLOWS.md`
  - `docs/IMPLEMENTATION-BY-TOOL.md`

### docs/PROMPT-PATTERNS.md
- **Auto-discovered:** ❌ No
- **Referenced by:** README.md, AGENTS.md, TOOL-SPECIFIC-GUIDES/
- **Can rename:** ✅ YES - if you update links everywhere
- **Suggested names if renaming:**
  - `docs/PROMPT-TEMPLATES.md`
  - `docs/prompt-best-practices.md`
  - `docs/REQUEST-PATTERNS.md`

### docs/TOOL-SPECIFIC-GUIDES/ (directory + files)
- **Auto-discovered:** ❌ No
- **Referenced by:** README.md, TOOLS-CAPABILITIES.md
- **Can rename:** ✅ YES (directory and files) - if you update links everywhere
- **Suggested alternatives:**
  - `docs/tools/` (shorter)
  - `docs/per-tool-guides/` (more explicit)
  - `docs/guides/` (simpler)

**Files in this directory:**
- `claude-code.md` - Can rename to `claude-code-guide.md`
- `aider.md` - Can rename to `aider-guide.md`
- `gemini.md` - Can rename to `gemini-guide.md`
- `codex.md` - Can rename to `codex-guide.md`

---

## Core Required Files (AGENTS.md Standard)

These files are **defined by AGENTS.md** and have **non-negotiable structure**, but the directory names can be customized if you update AGENTS.md.

### dev_notes/specs/YYYY-MM-DD_HH-MM-SS_*.md
- **Purpose:** User intention capture
- **Location:** `dev_notes/specs/` (defined in AGENTS.md)
- **Naming:** `YYYY-MM-DD_HH-MM-SS_description.md` (required format)
- **Can rename directory:** ✅ YES if you update AGENTS.md
- **Can rename format:** ❌ NO - timestamp format is standardized
- **Alternative directory names:**
  - `planning/specs/` (less clear)
  - `project-docs/requirements/` (more corporate)
  - Stick with `dev_notes/specs/` (clearest)

### dev_notes/project_plans/YYYY-MM-DD_HH-MM-SS_*.md
- **Purpose:** Implementation plan
- **Location:** `dev_notes/project_plans/` (defined in AGENTS.md)
- **Naming:** `YYYY-MM-DD_HH-MM-SS_description.md` (required format)
- **Can rename directory:** ✅ YES if you update AGENTS.md
- **Can rename format:** ❌ NO - timestamp format is standardized
- **Alternative directory names:**
  - `planning/plans/` (less clear)
  - `architecture/` (too broad)
  - Stick with `dev_notes/project_plans/` (clearest)

### dev_notes/changes/YYYY-MM-DD_HH-MM-SS_*.md
- **Purpose:** Change documentation
- **Location:** `dev_notes/changes/` (defined in AGENTS.md)
- **Naming:** `YYYY-MM-DD_HH-MM-SS_description.md` (required format)
- **Can rename directory:** ✅ YES if you update AGENTS.md
- **Can rename format:** ❌ NO - timestamp format is standardized
- **Alternative directory names:**
  - `dev_notes/modifications/` (less clear)
  - `dev_notes/updates/` (vague)
  - Stick with `dev_notes/changes/` (clearest)

---

## How Tool Auto-Discovery Works

### Claude Code
```
User runs: claude-code
Tool looks for: CLAUDE.md in current directory
If found: Reads it and extracts project instructions
Falls back to: System prompt if not found
```

### Aider
```
User runs: aider
Tool looks for: .aider.conf in current directory
If found: Reads configuration
Falls back to: Default config if not found
```

### pytest
```
User runs: pytest
Tool looks for: pytest.ini (or setup.cfg, pyproject.toml)
If found: Reads configuration
Falls back to: Default test discovery if not found
```

### Gemini, Codex
```
Unknown - will update when tools are tested
Likely: Similar to Claude Code or Aider patterns
Probably: .gemini-cli.yaml or similar
```

---

## Naming Strategy

### For Auto-Discovered Files
**Use the standard names only:**
- `CLAUDE.md` (not `claude-instructions.md`)
- `.aider.conf` (not `aider.config`)
- `pytest.ini` (not `pytest.config`)

These are **non-negotiable**. Tools don't look for alternatives.

### For Reference Documentation
**Use clear, descriptive names:**
- `docs/TOOLS-CAPABILITIES.md` - What each tool can do
- `docs/WORKFLOW-MAPPING.md` - How AGENTS.md works per tool
- `docs/PROMPT-PATTERNS.md` - Universal prompt structures
- `docs/TOOL-SPECIFIC-GUIDES/` - Per-tool detailed guides

**You can rename these if needed**, as long as you:
1. Update all links to the new name
2. Update any cross-references in AGENTS.md
3. Update README.md if it references them

### For AGENTS.md-Required Directories
**Keep the standard names:**
- `dev_notes/specs/` - Spec files
- `dev_notes/project_plans/` - Plans
- `dev_notes/changes/` - Changes

These are defined in AGENTS.md. Changing them means updating AGENTS.md too.

---

## Checking Which Files Are Which

**Quick test - Does a tool auto-discover it?**

1. Delete the file
2. Run the tool (`claude-code`, `aider`, `pytest`, etc.)
3. Does the tool look for it by default?
   - ✅ YES → It's auto-discovered (don't rename)
   - ❌ NO → It's just documentation (can rename)

---

## Creating Tool Config Files

### For Claude Code
Create `CLAUDE.md`:
```markdown
# Claude Code Instructions

This project uses the AGENTS.md workflow for all development.

See: [AGENTS.md](./AGENTS.md) - Core development workflow
See: [TOOLS-CAPABILITIES.md](./docs/TOOLS-CAPABILITIES.md) - Tool support matrix
See: [WORKFLOW-MAPPING.md](./docs/WORKFLOW-MAPPING.md) - How workflow maps to each tool
```

### For Aider
Create `.aider.conf`:
```yaml
[aider]
# Aider configuration
auto-commits = true
commit-prompt = "Use the change documentation format from dev_notes/changes/"

# Project instructions - also see CLAUDE.md equivalent content
# Reference: AGENTS.md for the core workflow
```

### For Gemini (when supported)
Create `.gemini-cli.yaml`:
```yaml
project:
  instructions: AGENTS.md
  tools: gemini
  context-files:
    - docs/TOOLS-CAPABILITIES.md
    - docs/WORKFLOW-MAPPING.md
    - docs/TOOL-SPECIFIC-GUIDES/gemini.md
```

---

## Recommendations for Your Project

### Keep (Don't Rename)
✅ `CLAUDE.md` - Tool auto-discovers this
✅ `pytest.ini` - pytest auto-discovers this
✅ `AGENTS.md` - Referenced everywhere
✅ `dev_notes/specs/` - AGENTS.md standard
✅ `dev_notes/project_plans/` - AGENTS.md standard
✅ `dev_notes/changes/` - AGENTS.md standard

### Reference Files (Can Rename, But Keep Current Names)
⚠️ `docs/TOOLS-CAPABILITIES.md` - Clear name, leave as is
⚠️ `docs/WORKFLOW-MAPPING.md` - Clear name, leave as is
⚠️ `docs/PROMPT-PATTERNS.md` - Clear name, leave as is
⚠️ `docs/TOOL-SPECIFIC-GUIDES/` - Clear name, leave as is

**Recommendation:** Use the current names. They're clear and unlikely to cause confusion.

---

## Summary Table (Which Files Matter?)

| File | Tool Auto-Discovers? | Rename Safe? | Status |
|------|---|---|---|
| CLAUDE.md | ✅ Claude Code | ❌ No | ✅ Created |
| .aider.conf | ✅ Aider | ❌ No | ⚠️ Optional |
| pytest.ini | ✅ pytest | ❌ No | ✅ Created |
| AGENTS.md | ❌ No | ✅ Yes (but don't) | ✅ Created |
| docs/TOOLS-CAPABILITIES.md | ❌ No | ✅ Yes (but don't) | ✅ Created |
| docs/WORKFLOW-MAPPING.md | ❌ No | ✅ Yes (but don't) | ✅ Created |
| docs/PROMPT-PATTERNS.md | ❌ No | ✅ Yes (but don't) | ✅ Created |
| docs/TOOL-SPECIFIC-GUIDES/ | ❌ No | ✅ Yes (but don't) | 🔄 Creating |
| dev_notes/specs/ | ❌ No | ✅ Yes (but don't) | ✅ Standard |
| dev_notes/project_plans/ | ❌ No | ✅ Yes (but don't) | ✅ Standard |
| dev_notes/changes/ | ❌ No | ✅ Yes (but don't) | ✅ Standard |

---

## Next Steps

1. **For Claude Code:** Already have CLAUDE.md ✅
2. **For Aider:** Create .aider.conf if you want Aider support (optional)
3. **For Gemini/Codex:** Create guides when testing those tools
4. **Link everything:** Update README.md to reference all documents
5. **Document this:** Share this FILE-NAMING-CONVENTIONS.md with team

The key principle: **Auto-discovered files have fixed names. Everything else is flexible as long as links are updated.**
