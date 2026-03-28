# Spec: Mandatory Context Assembly for Agent-Specific System Prompts

**Created:** 2026-01-28
**Status:** Draft
**Workflow:** @logs-first

---

## Overview

Enhance `bootstrap.py` to automatically assemble comprehensive agent-specific instruction files (aider.md, claude.md, etc.) by compiling mandatory context from modular system prompt chapters. This eliminates the need for agents to chase down references via tool calls, ensuring all critical instructions are present on first LLM invocation.

---

## Problem Statement

### Current State
- Agent-specific files at project root contain minimal instructions ("see agents.md")
- Agents must use tools to follow references and gather mandatory context
- This creates unnecessary API round-trips and risks agents skipping important instructions
- No clear distinction between mandatory vs. optional/contextual documentation

### Desired State
- Agent-specific files (5-10k) contain all mandatory instructions inline
- Agents receive complete context on first invocation without tool calls
- Clear system for marking content as mandatory vs. optional
- Projects can inject their own mandatory content via `docs/mandatory.md`
- Agent-specific content is filtered appropriately (Claude-specific chapters excluded from aider.md, etc.)

---

## Background Context

### The System-Prompts Vision

The `docs/system-prompts/` directory is being developed as a standalone tool that will eventually be extracted from Second Voice to enhance all projects. It provides:

- **Agent Kernel:** Foundation for agentic workflows across different AI coding assistants
- **Workflows:** Specialized processes like logs-first, QA roles, merge roles, orchestrator roles
- **Portable System:** Can be forked/extracted to work across ~12 hobby projects and potentially ~80 work source trees

### Current Vendor-Specific Files

Different AI vendors require their own instruction files because they don't all honor a generic `agents.md`:
- `aider.md` - For Aider
- `claude.md` - For Claude Code
- `gemini.md` - For Gemini
- `cursor.md` - For Cursor (potentially)
- `.github/copilot-instructions` - For GitHub Copilot

Currently these files are small (~20 lines) and simply say "look at agents.md and do whatever it says."

### The Mandatory vs. Optional Distinction

**Mandatory content** should include:
- Definition of done
- Prohibited actions (don't edit files outside workspace, don't refactor base systems when extending)
- Project boundaries and scope
- Core workflows and conventions
- Error handling expectations
- Security guidelines

**Optional/contextual content** includes:
- Specific library usage patterns
- Subsystem-specific documentation
- Advanced techniques for specialized scenarios
- Architecture deep-dives (can be referenced when needed)

---

## Proposed Solution

### High-Level Approach

Instead of small agent files that reference other documents, **assemble** comprehensive agent-specific files by:

1. **Creating modular chapters:** Break down system-prompts content into focused, single-topic files
2. **Defining mandatory list:** Create a master list of which chapters are mandatory
3. **Automatic assembly:** `bootstrap.py` compiles these chapters into agent-specific files
4. **Intelligent filtering:** Agent-specific chapters are automatically included/excluded based on naming conventions
5. **Project extensibility:** Projects can add `docs/mandatory.md` for project-specific mandatory content

### Key Architecture Decisions

**1. Single mandatory list, not per-agent lists**
- One `docs/system-prompts/mandatory-contents.txt` file
- Lists all mandatory chapters in order
- Bootstrap.py filters automatically based on filename patterns

**2. Chapters directory for organization**
- Mandatory chapters live in `docs/system-prompts/chapters/`
- Reduces noise in system-prompts/ directory
- Files in other subdirectories can stay where they are

**3. Automatic agent-name filtering**
- Chapters named `tool-aider-*` only included in aider.md
- Chapters named `tool-claude-*` only included in claude.md
- Common chapters included in all agent files
- `agents.md` gets everything (no filtering)

**4. Graceful handling of missing files**
- Missing chapters are skipped with warnings (not errors)
- Allows incremental implementation
- `--strict` flag available for CI validation

**5. Change detection via checksums**
- Generated files include checksum metadata
- Bootstrap.py can detect manual edits
- Warns users to use `docs/mandatory.md` instead of editing generated files

---

## Example Structure

### Mandatory Contents File

```
# docs/system-prompts/mandatory-contents.txt
# Format: one file path per line, relative to project root
# Lines starting with # are comments

# Core principles (all agents)
docs/system-prompts/chapters/definition-of-done.md
docs/system-prompts/chapters/prohibited-actions.md
docs/system-prompts/chapters/boundaries-and-scope.md

# Development practices (all agents)
docs/system-prompts/chapters/git-workflow.md
docs/system-prompts/chapters/code-style.md
docs/system-prompts/chapters/testing-requirements.md

# Project-specific content
docs/mandatory.md

# Agent-specific chapters
docs/system-prompts/chapters/tool-aider-shortcuts.md
docs/system-prompts/chapters/tool-claude-features.md
docs/system-prompts/chapters/tool-gemini-setup.md
```

### Generated File Structure

```markdown
<!-- GENERATED FILE - DO NOT EDIT -->
<!-- Generated by bootstrap.py from docs/system-prompts/mandatory-contents.txt -->
<!-- Target agent: aider -->
<!-- Last generated: 2026-01-28T10:30:00Z -->
<!-- Checksum: sha256:abc123... -->

<!-- BEGIN CHAPTER: docs/system-prompts/chapters/definition-of-done.md -->
[content here]
<!-- END CHAPTER: docs/system-prompts/chapters/definition-of-done.md -->

<!-- BEGIN CHAPTER: docs/system-prompts/chapters/tool-aider-shortcuts.md -->
[content here]
<!-- END CHAPTER: docs/system-prompts/chapters/tool-aider-shortcuts.md -->
```

---

## Implementation Requirements

### Phase 1: Analysis & Inventory
1. Inventory all files in `docs/system-prompts/`
2. Categorize each as mandatory, agent-specific mandatory, or contextual/optional
3. Identify files covering multiple topics (candidates for splitting)
4. Determine logical ordering
5. Document rationale for classifications

### Phase 2: Content Refactoring (If Needed)
1. Split multi-topic files into focused single-topic chapters
2. Ensure each chapter is self-contained
3. Create `docs/system-prompts/chapters/` directory
4. Rename agent-specific chapters to include agent name

### Phase 3: Create Mandatory Contents File
1. Create `docs/system-prompts/mandatory-contents.txt`
2. List all mandatory chapters in logical order
3. Add comments explaining sections
4. Include `docs/mandatory.md` reference (will be skipped if doesn't exist)

### Phase 4: Implement Bootstrap.py Assembly Logic
1. Add CLI command: `python bootstrap.py assemble`
2. Parse mandatory-contents.txt (skip comments and blank lines)
3. Filter chapters based on target agent and known agent names
4. Load chapter content (handle missing files gracefully)
5. Assemble with metadata markers
6. Generate checksums for change detection
7. Write to project root (aider.md, claude.md, etc.)

### Phase 5: Project Integration
1. Document `docs/mandatory.md` convention
2. Create Second Voice `docs/mandatory.md` with descriptions/keywords for other docs
3. Handle case where `docs/mandatory.md` doesn't exist

### Phase 6: Testing & Validation
1. Create test suite (non-pytest, self-contained)
2. Test parsing, filtering, assembly, checksums
3. Integration tests with fixtures
4. Validation that generated files match expected structure

---

## Bootstrap.py CLI Interface

```bash
# Generate all agent files
python bootstrap.py assemble

# Generate specific agents only
python bootstrap.py assemble --agents aider,claude

# Dry run (preview without writing)
python bootstrap.py assemble --dry-run --verbose

# Force regeneration (ignore manual edit warnings)
python bootstrap.py assemble --force

# Check if generated files are up-to-date (for CI)
python bootstrap.py assemble --check

# Strict mode (fail on missing chapters)
python bootstrap.py assemble --strict
```

---

## Key Decisions & Trade-offs

### Decision 1: Generate vs. Reference

**Chosen:** Generate comprehensive files
**Alternative:** Keep small files that reference others

**Rationale:**
- Guarantees agents see mandatory content on first invocation
- No reliance on tool calls (some agents/modes may have restricted tooling)
- Clear audit trail of what instructions agent had

**Trade-off:** Build step required, version control noise

### Decision 2: Filtering Method

**Chosen:** Automatic filtering based on filename patterns
**Alternative:** Explicit configuration per agent

**Rationale:**
- Self-documenting (filename tells you which agent it's for)
- No need to maintain separate config for each agent
- Easy to add new agents (just add to KNOWN_AGENTS list)

**Trade-off:** Filename conventions must be followed carefully

### Decision 3: Missing File Handling

**Chosen:** Warn and skip by default, `--strict` flag for CI
**Alternative:** Always fail on missing files

**Rationale:**
- Allows incremental implementation
- Projects can reference chapters they haven't created yet
- CI can enforce completeness with --strict flag

**Trade-off:** Might hide typos in chapter paths

---

## Success Criteria

1. Agent-specific files contain 5-10k of mandatory content
2. Agents no longer need Read/Grep tools for mandatory instructions
3. Zero dangling references ("see X for mandatory info")
4. Clear audit trail (metadata shows included chapters)
5. Projects can easily add content via `docs/mandatory.md`
6. System works across multiple projects
7. Adding new agent only requires adding to KNOWN_AGENTS list

---

## Open Questions

### Architecture
1. Should generated files be committed to git or generated on-the-fly and gitignored?
2. Should `agents.md` include ALL chapters (including agent-specific), or filter to common only?
3. Should generated files go in project root, or subdirectory like `.agents/` or `docs/generated/`?

### Content Organization
4. What makes content "mandatory" vs. "optional"? Need clear criteria.
5. Can we share current `docs/system-prompts/` structure for analysis?
6. Should we aim for many small chapters (50-100 lines) or fewer medium ones (200-300 lines)?
7. Preferred naming convention: `tool-{agent}-{topic}.md`, `{agent}-{topic}.md`, or `agent-{agent}-{topic}.md`?

### Project Integration
8. Should `docs/mandatory.md` contain inline content, serve as a menu/index, or both?
9. Will this be shared across projects as git submodule?
10. Any enterprise considerations (security, compliance) for work projects?

### Filtering
11. Should agent names be hard-coded, CLI flag, or config file?
12. Use simple substring matching or word-boundary regex for filtering?
13. How to handle false positives (e.g., `claudette.md` matching "claude")?
14. How to handle chapters relevant to multiple agents?

### Change Detection
15. If someone edits generated aider.md, should bootstrap.py refuse to overwrite, warn, backup, or fail?
16. Should bootstrap.py auto-detect chapter changes and offer to regenerate?
17. Show diff of manual edits before overwriting?

### Advanced Features
18. Should Phase 1 design for role-specific assemblies (QA, DevOps, etc.)?
19. Need conditional content (only include if certain files/dirs exist)?
20. Need deployment optimization (strip all chapters, keep only assembled file)?

### Technical
21. What does bootstrap.py currently do? (to avoid conflicts)
22. Should docscan.py validate mandatory-contents references, no circular deps, naming conventions, etc.?
23. Preferred metadata format (HTML comments, YAML front-matter, custom)?
24. Should mandatory-contents.txt support inline comments, section headers?

---

## Critical Evaluation

### Is This Over-Engineered?

**Core assumption:** Assembling mandatory context into one file is better than having agents read 3-5 files at session start.

**Arguments against implementing:**
1. **Tool calls are cheap:** Reading 3-5 files = ~5 tool calls = 10% of one turn in 50-turn session
2. **No evidence of problem:** Have agents actually been skipping mandatory content?
3. **Significant complexity:** Build steps, filtering logic, change detection, testing, maintenance
4. **Loss of transparency:** "Read these 3 files" is clearer than assembly system with templates
5. **Version control noise:** Every chapter edit regenerates 5-7 agent files
6. **Build step brittleness:** Contributors must remember to run bootstrap.py

**Arguments for implementing:**
1. **Guaranteed context:** Agents cannot skip mandatory content
2. **Agent-specific filtering:** Cleaner context, less confusion
3. **Scalability:** Valuable if deploying to 20+ projects
4. **Audit trail:** Generated files show exactly what agent saw

### Simpler Alternative

Just use explicit reading lists in agent files:

```markdown
# Mandatory Reading - READ THESE FIRST, EVERY SESSION

Before starting ANY task, you MUST read these files in order:
1. docs/system-prompts/definition-of-done.md
2. docs/system-prompts/prohibited-actions.md
3. docs/mandatory.md
```

This approach:
- ✓ Crystal clear what's mandatory
- ✓ No build step
- ✓ No generated files
- ✓ Easy to update and debug
- ✗ Requires 3-5 tool calls (but is this actually a problem?)

### Recommendation

**Consider starting with the simpler alternative** unless:
1. Evidence that agents skip mandatory content exists, AND
2. This causes real, measurable problems, AND
3. The simpler approach fails to solve it, AND
4. Deploying to 20+ projects where consistency tooling adds value

Otherwise, invest time in writing clearer instruction files rather than building assembly machinery.

---

## Next Steps

1. **User decision:** Is the full assembly system needed, or should we try the simpler alternative first?
2. **If proceeding:** Answer open questions above to refine design
3. **Create project plan** with detailed implementation strategy
4. **Get approval** before implementation

---

## References

- `docs/system-prompts/workflows/logs-first.md` - Current workflow structure
- `docs/system-prompts/bootstrap.py` - Existing bootstrap functionality
- `docs/system-prompts/docscan.py` - Validation/linting tool
- `AGENTS.md` - Current agent instructions
- `CLAUDE.md` - Claude-specific instructions
