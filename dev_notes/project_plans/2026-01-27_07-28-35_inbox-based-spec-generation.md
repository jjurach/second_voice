# Project Plan: Inbox-Based Automated Specification Generation System

**Source:** dev_notes/specs/2026-01-27_07-28-35_inbox-based-spec-generation.md
**Original File:** recording-01-answers.md
**Status:** 🔵 Ready for Implementation
**Timestamp:** 2026-01-27_07-28-35
**Last Updated:** 2026-01-27
**Estimated Phases:** 6
**Priority:** High - Foundational Infrastructure

---

## 📋 Executive Summary

Implement an automated workflow system that:
1. Processes user input files from an inbox directory
2. Generates professionally structured specification documents
3. Creates implementation-ready project plans
4. Maintains complete traceability throughout the development lifecycle
5. Enables efficient status tracking and queue management

**Key Changes:**
- Establish standardized document header system for all generated files
- Create lightweight Python status query tool (no external dependencies)
- Update .gitignore for proper directory exclusions
- Add agent instructions for inbox processing workflow
- Update documentation to reference inbox/specs/project_plans directories
- Ensure all pytests pass after implementation

---

## 🎯 Goals & Success Criteria

### Primary Goals
✅ Automated inbox → specs → project_plans workflow
✅ Standardized headers across all generated documents
✅ Status query tool for tracking incomplete work
✅ Git integration properly configured
✅ Documentation updated to reference new workflow
✅ All pytests passing

### Success Metrics
- [ ] Files dropped in `dev_notes/inbox/` are automatically processed
- [ ] Generated specs have standardized headers with metadata
- [ ] Original files moved to `dev_notes/inbox-archive/` after processing
- [ ] Status query tool identifies next unimplemented project plan
- [ ] `dev_notes/.gitignore` excludes logs/, inbox/, inbox-archive/
- [ ] All documentation mentioning "specs" or "project plans" also mentions "inbox"
- [ ] System prompts recognize "process the first inbox item" command
- [ ] 100% pytest pass rate (no regressions)

---

## 📊 Current State Analysis

### ✅ Already Working
1. Directory structure exists:
   - ✅ `dev_notes/inbox/`
   - ✅ `dev_notes/inbox-archive/`
   - ✅ `dev_notes/specs/`
   - ✅ `dev_notes/project_plans/`
   - ✅ `dev_notes/changes/`
   - ✅ `dev_notes/logs/`
2. Existing specs and project plans show varied header formats
3. Manual workflow for creating specs and project plans established

### ❌ Gaps to Address
1. **No standardized header system** - Headers vary across documents
2. **No automation for inbox processing** - Manual spec generation
3. **No status query tool** - Cannot determine next unimplemented plan
4. **Incomplete .gitignore** - May not exclude all necessary directories
5. **Documentation gaps** - Missing inbox references in system prompts
6. **No traceability** - Cannot track spec → plan → changes lineage
7. **No agent instructions** - System prompts don't recognize inbox commands

### 🔧 Status Format Variations (Research Summary)

Based on `grep -m1 '\*\*Status' dev_notes/*/*.md`:
- `Completed` / `COMPLETED`
- `✅ Complete` / `✅ COMPLETE`
- `✓ Completed`
- `Completed ✅`
- `🔵 Ready for Implementation`
- `Under Review` / `Pending Review`
- `Awaiting transformation`
- `In Progress` (proposed for active work)

**Recommended Standard:**
- `🔵 Ready for Implementation` - Not started
- `🟡 In Progress` - Currently being implemented
- `🟢 Awaiting Approval` - Completed, awaiting human review
- `✅ Complete` - Fully implemented and approved

---

## 🏗️ Implementation Plan

### Phase 1: Document Header Standardization

**Timeline:** Tasks 1-2 (foundation)

#### Task 1.1: Define Standard Header Format
**Files:** `docs/workflows.md` (or create new `docs/header-standard.md`)

Create documentation specifying:
```markdown
---
**Source:** <source-document-path>
**Original File:** <inbox-filename-if-applicable>
**Status:** <status-value>
**Timestamp:** <ISO-8601-timestamp>
---
```

**Acceptance Criteria:**
- [ ] Header format documented with examples
- [ ] Status value definitions documented
- [ ] Explains grep-friendly format for automation

#### Task 1.2: Create Header Template Snippets
**Files:** `dev_notes/templates/` (new directory)

Create template files:
- `spec-template.md` - Template for new specifications
- `project-plan-template.md` - Template for new project plans
- `change-log-template.md` - Template for implementation changes

**Acceptance Criteria:**
- [ ] Templates directory created
- [ ] All three templates include standardized headers
- [ ] Templates include example content structure

---

### Phase 2: Status Query Tool

**Timeline:** Tasks 3-5 (core automation)

#### Task 2.1: Create Status Scanner Script
**Files:** `tools/query_status.py` (new)

Implement Python script (stdlib only) that:
- Scans all `.md` files in `dev_notes/specs/`, `project_plans/`, `changes/`
- Extracts headers using regex: `\*\*(\w+):\*\*\s*(.+)`
- Builds relationship map: spec → plan → changes
- Recognizes all status format variations

**Acceptance Criteria:**
- [ ] Script runs with `python tools/query_status.py`
- [ ] No external dependencies (uses only stdlib)
- [ ] Parses all existing status formats correctly
- [ ] Returns structured data (JSON or human-readable)

#### Task 2.2: Add Query Commands
**Files:** `tools/query_status.py`

Add command-line interface:
```bash
python tools/query_status.py --next          # Next unimplemented plan
python tools/query_status.py --oldest        # Oldest pending plan
python tools/query_status.py --incomplete    # All incomplete plans
python tools/query_status.py --orphans       # Plans without source specs
python tools/query_status.py --summary       # Overall status summary
```

**Acceptance Criteria:**
- [ ] All commands work as described
- [ ] Output is clear and actionable
- [ ] Handles edge cases (no files, missing headers)

#### Task 2.3: Add Documentation for Query Tool
**Files:** `tools/README.md` (new)

Document:
- Purpose and use cases
- Command examples
- Integration with agent workflows
- Header format requirements

**Acceptance Criteria:**
- [ ] README explains all commands
- [ ] Examples show typical usage
- [ ] Links to header standard documentation

---

### Phase 3: Git Integration

**Timeline:** Task 6

#### Task 3.1: Update .gitignore
**Files:** `dev_notes/.gitignore`

Add exclusions:
```gitignore
# Temporary and log files
logs/
*.log

# Inbox processing (work-in-progress)
inbox/
inbox-archive/
```

**Note:** Verify if `dev_notes/.gitignore` exists or if root `.gitignore` should be updated.

**Acceptance Criteria:**
- [ ] .gitignore updated (or created if needed)
- [ ] `git status` doesn't show inbox/inbox-archive/logs files
- [ ] Existing tracked files remain tracked
- [ ] Document rationale in comments

---

### Phase 4: Agent Automation Instructions

**Timeline:** Tasks 7-9 (agent integration)

#### Task 4.1: Update System Prompts with Inbox Workflow
**Files:**
- `docs/system-prompts/tools/claude-code.md`
- `docs/system-prompts/tools/aider.md`
- `docs/system-prompts/tools/cline.md`
- (any other tool-specific prompts)

Add section explaining inbox workflow:
```markdown
## Inbox Processing Workflow

When user says "process the first inbox item" or "process inbox":
1. List files in `dev_notes/inbox/` (lexicographically sorted)
2. Read the first file
3. Generate a professional specification in `dev_notes/specs/`
   - Use timestamp-based naming: `YYYY-MM-DD_HH-MM-SS_description.md`
   - Include standardized header with Source and Timestamp
4. Move original file to `dev_notes/inbox-archive/`
5. Ask: "Should I create a project plan for this spec?" or proceed if instructed
```

**Acceptance Criteria:**
- [ ] All tool system prompts include inbox workflow
- [ ] Instructions are clear and actionable
- [ ] Naming conventions specified
- [ ] Header requirements referenced

#### Task 4.2: Add Project Plan Generation Instructions
**Files:** Same as 4.1

Add instructions for plan creation:
```markdown
## Generating Project Plans

When creating a project plan from a spec:
1. Research the codebase to understand current implementation
2. Create detailed, phased implementation plan
3. Include clarifying questions if requirements are ambiguous
4. Save to `dev_notes/project_plans/` with matching timestamp
5. Set **Status: 🔵 Ready for Implementation**
6. Set **Source:** to the spec file path
7. Stop and await human review (unless instructed to proceed)
```

**Acceptance Criteria:**
- [ ] Plan generation workflow documented
- [ ] Human intervention points clearly marked
- [ ] Status transition rules specified

#### Task 4.3: Add Implementation Workflow Instructions
**Files:** Same as 4.1

Add implementation phase instructions:
```markdown
## Implementing Project Plans

When user approves a plan ("implement the plan", "I approve"):
1. Update plan **Status: 🟡 In Progress**
2. Execute tasks according to plan phases
3. Create `dev_notes/changes/` log with matching timestamp
4. Update change log as tasks complete
5. When all tasks complete, update plan **Status: 🟢 Awaiting Approval**
6. Update change log **Status: 🟢 Awaiting Approval**
7. Stop and await human review
```

**Acceptance Criteria:**
- [ ] Implementation workflow documented
- [ ] Status transitions clearly defined
- [ ] Change log requirements specified
- [ ] Human approval gates identified

---

### Phase 5: Documentation Updates

**Timeline:** Tasks 10-11

#### Task 5.1: Update All References to Specs/Plans to Include Inbox
**Files:**
- `README.md`
- `docs/workflows.md`
- `AGENTS.md`
- `CLAUDE.md`
- `AIDER.md`
- Any other documentation mentioning specs or project_plans

Find and update all references:
- "specs directory" → "inbox/specs directories"
- "project plans" → "project plans (generated from inbox items or specs)"
- Add inbox workflow overview to main README

**Acceptance Criteria:**
- [ ] All documentation files updated
- [ ] Inbox workflow mentioned consistently
- [ ] No stale references to manual spec creation
- [ ] grep confirms all instances updated

#### Task 5.2: Update AGENTS.md with Inbox Example
**Files:** `AGENTS.md`

Add practical example:
```markdown
## Example: Processing Inbox Item

User: "Process the first inbox item"

Agent:
1. Reads `dev_notes/inbox/feature-request.md`
2. Creates `dev_notes/specs/20260127-120000_feature-request.md`
3. Moves original to `dev_notes/inbox-archive/feature-request.md`
4. Asks: "I've created the spec. Should I generate a project plan?"
```

**Acceptance Criteria:**
- [ ] Example added to AGENTS.md
- [ ] Shows complete workflow
- [ ] Demonstrates agent/human interaction points

---

### Phase 6: Testing & Validation

**Timeline:** Tasks 12-14 (verification)

#### Task 6.1: Create Pytest for Header Parsing
**Files:** `tests/test_status_query.py` (new)

Test coverage:
- Header extraction from sample markdown files
- Status format recognition (all variations)
- Relationship mapping (spec → plan → changes)
- Edge cases (missing headers, malformed files)

**Acceptance Criteria:**
- [ ] Test file created
- [ ] All status variations tested
- [ ] Tests pass with 100% coverage of query_status.py
- [ ] Edge cases handled gracefully

#### Task 6.2: Create Integration Test for Inbox Workflow
**Files:** `tests/test_inbox_workflow.py` (new)

Test end-to-end:
1. Place test file in inbox
2. Verify spec generation with correct header
3. Verify file moved to inbox-archive
4. Verify naming conventions followed

**Note:** This may be a manual test case if full automation isn't feasible in pytest.

**Acceptance Criteria:**
- [ ] Test or test case documented
- [ ] Verifies complete workflow
- [ ] Can be run for regression testing

#### Task 6.3: Run Full Test Suite & Verify
**Files:** N/A (verification task)

Execute:
```bash
pytest
python tools/query_status.py --summary
git status  # verify .gitignore working
```

**Acceptance Criteria:**
- [ ] All pytests pass (no regressions)
- [ ] Query tool runs successfully
- [ ] Git ignores inbox/inbox-archive/logs
- [ ] No broken references in documentation

---

## 🚀 Implementation Sequence

### Recommended Order
1. **Phase 1** (Tasks 1-2): Establish header standard and templates
2. **Phase 2** (Tasks 3-5): Build status query tool
3. **Phase 3** (Task 6): Configure git integration
4. **Phase 4** (Tasks 7-9): Update agent system prompts
5. **Phase 5** (Tasks 10-11): Update documentation
6. **Phase 6** (Tasks 12-14): Test and validate

### Dependencies
- Phase 2 depends on Phase 1 (header format must be defined)
- Phase 4 depends on Phase 1 (agents need header standard)
- Phase 6 depends on all previous phases

### Human Intervention Points
- **After Phase 1:** Review header standard before proceeding
- **After Phase 2 Task 3:** Test query tool manually
- **After Phase 4:** Review system prompt updates
- **After Phase 6:** Final approval before marking complete

---

## 📝 Open Questions & Decisions

### Q1: Should Archive be a subdirectory of inbox or separate?
**Decision from spec:** `inbox-archive` is a sibling to `inbox` ✅

### Q2: What status format variations should the query tool recognize?
**Decision from spec:** All variations found via grep (see "Status Format Variations" above) ✅

### Q3: Should project plan execution be triggered automatically?
**Decision from spec:** No, human approval required. Agent updates status when human says "implement the plan" ✅

### Q4: What abstractions needed in later phases?
**Decision from spec:** None for now. Future PR creation will be in system prompts, not software ✅

### Q5: Voice-to-specification pipeline priority?
**Decision:** Deferred to future phases. Focus on core inbox → spec → plan workflow first.

---

## 🔍 Future Enhancements (Out of Scope)

The following are mentioned in the spec but deferred:
1. **Voice-to-Text Pipeline:** Audio capture → Whisper → LLM refinement → inbox
2. **Global Inbox Router:** Multi-project inbox with automatic routing
3. **Automated Plan Execution Polling:** Watch for status changes (current design uses human trigger)
4. **Pull Request Integration:** Automatic PR creation after implementation

These will be addressed in separate specifications and project plans.

---

## 📚 References

- **Source Specification:** dev_notes/inbox/recording-01-answers.md
- **Existing Plans (for format reference):** dev_notes/project_plans/2026-01-26_23-00-24_aac-support-and-whisper-recovery.md
- **Workflows Documentation:** docs/workflows.md
- **Agent Instructions:** AGENTS.md, CLAUDE.md, AIDER.md

---

## ✅ Definition of Done

- [ ] All 14 tasks completed
- [ ] All pytests passing
- [ ] Status query tool functional
- [ ] Documentation updated with inbox references
- [ ] System prompts include inbox workflow
- [ ] .gitignore properly configured
- [ ] Manual testing of inbox workflow successful
- [ ] Human review and approval complete

**Status will transition to:** 🟢 Awaiting Approval when all tasks complete.
