# Project Plan: Make Logs-First Workflow Optional

**Created:** 2026-01-26 08:54:55
**Status:** Completed
**Implementation Reference:** `dev_notes/changes/2026-01-26_09-11-17_implement-optional-workflows.md`

## Overview

Make the "logs-first" workflow (Spec → Project Plan → Changes documentation pattern) optional for projects. Enable projects to explicitly opt-in or be automatically opt-in based on project characteristics. This allows the Agent Kernel to serve both small, iterative projects and large, multi-team projects with different needs.

## Phase 1: Design & Architecture

**Goal:** Establish the design pattern for workflow configuration using bootstrap.py state tracking.

### 1.1 Workflow State Tracking in bootstrap.py

Define the mechanism projects use to enable/disable the logs-first workflow:

- **Command-line arguments:** `bootstrap.py --enable-logs-first` and `bootstrap.py --disable-logs-first`
- **State persistence:** bootstrap.py tracks enabled workflows in a marker section in AGENTS.md (e.g., `<!-- BOOTSTRAP-STATE: logs-first=enabled -->`)
- **Auto-detection:** On subsequent runs, bootstrap.py detects prior state and maintains it unless explicit arguments override
- **Behavioral clarity:** If `--enable-logs-first` was used before and no explicit arg is passed now, logs-first remains enabled

**Success indicator:** bootstrap.py command structure defined and documented

### 1.2 Define Auto-Detection Behavior

Establish how projects inherit workflow defaults on first run:

- **Auto-detect on first run:** bootstrap.py examines project characteristics (size, structure, git history) to recommend logs-first
- **Developer can override:** `--enable-logs-first` or `--disable-logs-first` explicitly sets preference
- **State retention:** Once set, behavior persists across subsequent runs unless explicitly changed
- **Detection criteria:** Project size, commit history length, presence of dev_notes/, test coverage expectations

**Success indicator:** Clear auto-detection logic documented and implemented

## Phase 2: Create Workflow Documentation

**Goal:** Extract the logs-first workflow into standalone, reusable documentation.

### 2.1 Create docs/system-prompts/workflows/logs-first.md

Create a comprehensive document that contains:

- Complete Agent Kernel Core Workflow (Steps A-E from AGENTS.md)
- Definition of Done principles (universal and language-specific)
- File naming conventions for spec, plan, change documentation
- State transition rules
- Checklist for marking tasks complete

**Details:**
- Mirror the content currently in AGENTS.md Section "CORE-WORKFLOW" and "PRINCIPLES"
- Add instructions for project setup (creating dev_notes/ structure)
- Include examples from the templates.md document
- Add a preamble explaining when/why projects use this workflow

**Success indicator:** Standalone docs/system-prompts/workflows/logs-first.md that fully explains the workflow without referencing AGENTS.md

### 2.2 Create docs/system-prompts/workflows/custom-template.md

For projects that want to create their own custom workflows:

- Template showing structure of workflow documentation
- Example sections that workflows should include
- Guidelines for naming and formatting workflow docs
- Example of how to reference workflow from AGENTS.md

**Details:**
- Provide a markdown template with placeholders
- Document what sections are required vs. optional
- Show integration points with bootstrap.py
- Include examples from logs-first workflow

**Success indicator:** docs/system-prompts/workflows/custom-template.md with clear guidance for creating custom workflows

## Phase 3: Update Bootstrap Tool

**Goal:** Extend bootstrap.py to support workflow selection with state tracking.

### 3.1 Add Auto-Detection Logic

Modify `docs/system-prompts/bootstrap.py`:

- Add `detect_recommended_workflow()` method that examines:
  - Project file count and total size
  - Git history length and commit patterns
  - Presence of dev_notes/ structure
  - Test coverage and documentation
- Return recommendation (e.g., "logs-first" for small active projects)
- Document detection criteria in docstring

**Details:**
- Heuristics for small projects: < 100 files, < 1 year git history, active commits
- Heuristics for large projects: > 1000 files, > 5 years history, multiple contributors
- Medium projects get recommendation but with explanation

**Success indicator:** Auto-detection works and logs recommended workflow

### 3.2 Add Command-Line Arguments for Workflow Control

Add arguments to bootstrap.py:

```bash
bootstrap.py --enable-logs-first     # Turn on logs-first workflow
bootstrap.py --disable-logs-first    # Turn off logs-first workflow
bootstrap.py --analyze-workflow      # Show current state and recommendation
```

**Details:**
- Parse arguments before processing
- If explicit arg provided, use it; otherwise use detected recommendation
- Store state in AGENTS.md via marker section: `<!-- BOOTSTRAP-STATE: logs-first=enabled -->`

**Success indicator:** bootstrap.py supports --enable/--disable arguments

### 3.3 Add State Persistence and Detection

Modify bootstrap.py to track state across runs:

- Add `_read_bootstrap_state()` method to extract marker from AGENTS.md
- Add `_write_bootstrap_state()` method to write marker back
- On run: check for existing state marker
- If no explicit arg and state exists: preserve prior state
- If no explicit arg and no state: use auto-detected recommendation

**Details:**
- State format: `<!-- BOOTSTRAP-STATE: logs-first=enabled -->`
- Store before and after existing sections
- Validate state values (enabled/disabled)

**Success indicator:** State persists across multiple bootstrap.py runs

### 3.4 Add Workflow Injection to AGENTS.md

Modify bootstrap.py to inject workflow content when enabled:

- If logs-first is enabled: inject `docs/system-prompts/workflows/logs-first.md` content
- Add new section: `<!-- SECTION: LOGS-FIRST-WORKFLOW -->`
- Section is optional and only present if enabled
- Remove section if workflow is disabled

**Details:**
- Follows existing bootstrap.py pattern for section updates
- Uses `load_system_prompt()` method to read workflow file
- Updates section via `_update_section()` method

**Success indicator:** When logs-first is enabled, AGENTS.md contains complete workflow instructions

## Phase 5: Update AGENTS.md

**Goal:** Restructure AGENTS.md to support optional workflows while maintaining backward compatibility.

### 5.1 Add Workflow State Section

Add new section to AGENTS.md that documents current workflow state:

- Show which workflows are enabled/disabled
- Document how to change with bootstrap.py
- Explain auto-detection behavior
- Link to workflow documentation

**Details:**
- Place near top of file for visibility
- Use clear language for non-technical developers
- Include quick-start command examples

**Success indicator:** AGENTS.md clearly shows current workflow configuration

### 5.2 Keep Existing Content as Fallback

Ensure AGENTS.md always contains a baseline set of instructions:

- Core workflow steps (always present)
- Universal Definition of Done (always present)
- Language-specific DoD (always present)
- Optional: Full logs-first workflow content (conditionally included via bootstrap.py)

**Success indicator:** AGENTS.md remains functional even if bootstrap.py isn't run or logs-first is disabled

### 5.3 Add Bootstrap.py Usage Documentation

Document how to use bootstrap.py for workflow management:

```bash
# See what workflow is recommended
python3 docs/system-prompts/bootstrap.py --analyze-workflow

# Enable logs-first workflow (inject into AGENTS.md)
python3 docs/system-prompts/bootstrap.py --enable-logs-first --commit

# Disable logs-first workflow (remove from AGENTS.md)
python3 docs/system-prompts/bootstrap.py --disable-logs-first --commit

# Check current state without changes (dry-run)
python3 docs/system-prompts/bootstrap.py --analyze-workflow
```

**Success indicator:** AGENTS.md includes clear bootstrap.py usage instructions

## Phase 6: Documentation & Guidance

**Goal:** Help developers understand workflows and bootstrap.py capabilities.

### 6.1 Create docs/workflows.md

User-facing guide explaining:

- What workflows are and why they exist
- Logs-first workflow explanation (what it is, when to use)
- How to enable/disable workflows
- Running bootstrap.py commands
- Creating custom workflows

**Details:**
- Explain that workflows are optional system prompts
- Show example output from --analyze-workflow
- Provide decision tree: "Should I use logs-first?"
- Link to custom-template.md for advanced users

**Success indicator:** docs/workflows.md with clear guidance on workflow selection and management

### 6.2 Update docs/architecture.md

Add section explaining:

- Workflow layer in Agent Kernel architecture
- How bootstrap.py injects workflow content into AGENTS.md
- State persistence via HTML comments
- Why projects choose different workflows (small vs. large teams)

**Success indicator:** docs/architecture.md includes workflow architecture explanation

### 6.3 Add README to docs/system-prompts/workflows/

Create directory README explaining:

- Purpose of workflows directory
- Available workflows (logs-first, custom-template)
- How to create and integrate custom workflows
- Link to custom-template.md

**Success indicator:** docs/system-prompts/workflows/README.md with clear directory structure

## Implementation Order

1. **Phase 1** (Design & Architecture) - Decide on configuration mechanism before implementation
2. **Phase 2** (Workflow Documentation) - Create standalone workflow docs
3. **Phase 3** (Bootstrap Updates) - Extend bootstrap.py with workflow support
4. **Phase 4** (Configuration Schema) - Define and implement configuration
5. **Phase 5** (AGENTS.md Update) - Restructure AGENTS.md for flexibility
6. **Phase 6** (Documentation & Guidance) - Create user-facing documentation

## Files to Create/Modify

### New Files
- `docs/system-prompts/workflows/logs-first.md` - Complete logs-first workflow documentation
- `docs/system-prompts/workflows/custom-template.md` - Template for custom workflows
- `docs/system-prompts/workflows/README.md` - Directory guide
- `docs/workflows.md` - User guide for workflow selection and management

### Modified Files
- `docs/system-prompts/bootstrap.py` - Add auto-detection, state tracking, and workflow injection
- `AGENTS.md` - Add "Workflow Configuration" section explaining current state and bootstrap.py usage
- `docs/architecture.md` - Add "Workflow Layer" section explaining architecture

### Not Modified
- Core sections of AGENTS.md (Steps A-E, Definition of Done) remain unchanged
- Existing bootstrap.py functionality preserved (backward compatible)
- No new configuration files needed (state stored in AGENTS.md HTML comments)

## Success Criteria

✅ bootstrap.py auto-detects recommended workflow for project
✅ bootstrap.py supports --enable-logs-first and --disable-logs-first arguments
✅ Workflow state persists across bootstrap.py runs (stored in AGENTS.md marker)
✅ When logs-first enabled, AGENTS.md includes complete workflow instructions
✅ When logs-first disabled, AGENTS.md workflow section is removed
✅ Logs-first workflow fully documented in standalone docs/system-prompts/workflows/logs-first.md
✅ Custom workflow template available for projects creating custom workflows
✅ Backward compatibility maintained (existing projects unaffected)
✅ Clear user guidance in docs/workflows.md on when/how to use workflows
✅ Architecture documentation explains workflow layer design

## Risk Assessment

- **Low Risk:** Creating new workflow documentation files (no code changes, pure documentation)
- **Low Risk:** Adding configuration schema (new functionality, non-breaking)
- **Medium Risk:** Modifying bootstrap.py (affects system prompt injection, requires careful testing)
- **Medium Risk:** Restructuring AGENTS.md (must maintain backward compatibility)
- **Low Risk:** Creating user-facing documentation (pure documentation)

## Estimated Scope

- **New documentation:** ~1800-2200 lines
  - logs-first.md: ~800-1000 lines (extracted from AGENTS.md)
  - custom-template.md: ~200-300 lines
  - workflows.md (user guide): ~400-500 lines
  - workflows/README.md: ~100-150 lines
  - architecture.md updates: ~200-300 lines

- **bootstrap.py changes:** ~400-600 lines
  - Auto-detection logic: ~150-200 lines
  - State persistence methods: ~100-150 lines
  - Command-line argument parsing: ~50-100 lines
  - Workflow injection: ~100-150 lines

- **AGENTS.md updates:** ~150-200 lines
  - Workflow Configuration section: ~100-150 lines
  - Bootstrap.py usage instructions: ~50-100 lines

- **Total:** ~2,350-3,000 lines

## Clarified Design Decisions

Based on developer feedback:

1. ✅ **Configuration Mechanism:** bootstrap.py command-line arguments with state persistence
   - `--enable-logs-first` and `--disable-logs-first` set preference
   - State stored in AGENTS.md HTML marker for persistence across runs
   - No separate config files needed

2. ✅ **Auto-Detection:** Yes, with explicit override capability
   - bootstrap.py auto-detects recommended workflow on first run
   - Explicit args override auto-detection
   - State persists unless explicitly changed on subsequent runs

3. ✅ **Workflow Naming:** Keep "logs-first" (current name)
   - Consistent with existing documentation
   - Already familiar to project team

4. ✅ **Workflow Scope:** logs-first + custom-template for others to fork
   - Logs-first: Complete, fully-featured workflow for small/active projects
   - Custom-template: Template for projects creating their own workflows
   - Minimal/other workflows can be added in future iterations

## Miscellaneous Notes

- Research found that major AI projects (Google, OpenAI, Microsoft) use context-based routing and multi-prompt strategies for different agent types
- MCP (Model Context Protocol) supports prompt templates and conditional injection
- The existing bootstrap.py is well-designed and extensible; this plan builds on its architecture
- State persistence via HTML comments is elegant and requires no new file types
- This design is scalable for adding new workflows without major restructuring
