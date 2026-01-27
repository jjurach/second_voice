# Specification: Inbox-Based Automated Specification Generation System

**Original File:** recording-01-answers.md
**Status:** ✅ Complete
**Timestamp:** 2026-01-27_07-28-35

---

## Overview

This specification defines an automated workflow system that processes user input files from an inbox directory, reformats them into professionally structured specification documents, and maintains traceability throughout the development lifecycle from initial request through implementation completion.

---

## Core Requirements

### 1. File Processing Pipeline

**FR-1.1: Inbox File Detection**
- System SHALL monitor `dev_notes/inbox/` directory for input files
- Files SHALL be processed in lexicographic order (first alphabetically)
- Any file naming convention is acceptable

**FR-1.2: Specification Generation**
- System SHALL generate professional specification documents in `dev_notes/specs/`
- Generated files SHALL follow naming convention: `YYYY-MM-DD_HH-MM-SS_description.md`
- Specifications SHALL include standardized metadata headers

**FR-1.3: File Archival**
- Original files SHALL be moved to `dev_notes/inbox-archive/` after processing
- Original filename SHALL be preserved during archival
- Archive operation SHALL occur only after successful spec generation

**FR-1.4: Project Plan Generation**
- System SHALL optionally generate project plans in `dev_notes/project_plans/`
- Plans SHALL reference their source specification
- Plans SHALL await human review before implementation

---

## Directory Structure

### 2. Required Directories

**FR-2.1: Directory Hierarchy**
```
dev_notes/
├── inbox/              # User input drop location
├── inbox-archive/      # Original files (siblings, not nested)
├── specs/              # Formatted specifications
├── project_plans/      # Implementation plans
├── changes/            # Implementation tracking logs
└── logs/               # Codec and agent logs
```

**FR-2.2: Directory Purpose**
- `inbox/`: Accepts any file format; no constraints on naming
- `inbox-archive/`: Preserves original user input for audit trail
- `specs/`: Contains professionally formatted specifications
- `project_plans/`: Contains phased implementation plans
- `changes/`: Contains implementation completion records
- `logs/`: Contains diagnostic and processing logs

---

## Version Control Integration

### 3. Git Configuration

**FR-3.1: Excluded Directories**
The following directories SHALL be excluded from version control via `.gitignore`:
- `dev_notes/logs/`
- `dev_notes/inbox/`
- `dev_notes/inbox-archive/`

**FR-3.2: Tracked Directories**
The following directories SHALL be tracked in version control:
- `dev_notes/specs/`
- `dev_notes/project_plans/`
- `dev_notes/changes/`

**Rationale:** Specifications and plans are permanent artifacts; inbox and logs are transient.

---

## Document Header System

### 4. Standardized Metadata

**FR-4.1: Required Header Attributes**

All generated documents SHALL include the following header:
```markdown
**Source:** <source-document-path>
**Original File:** <inbox-filename-if-applicable>
**Status:** <status-value>
**Timestamp:** <YYYY-MM-DD_HH-MM-SS>
```

**FR-4.2: Attribute Definitions**
- **Source:** References the originating document
  - Specs: Original inbox filename (before archival)
  - Project Plans: Path to source spec
  - Change Logs: Path to source project plan
- **Original File:** Only for specs; inbox filename that was archived
- **Status:** Current completion state (see FR-4.3)
- **Timestamp:** Matches filename format (`YYYY-MM-DD_HH-MM-SS`)

**FR-4.3: Status Values**

Standard status progression:
- `🔵 Ready for Implementation` - Not started
- `🟡 In Progress` - Currently being worked on
- `🟢 Awaiting Approval` - Completed, pending human review
- `✅ Complete` - Approved and finalized

**FR-4.4: Backward Compatibility**

Status query tool SHALL recognize legacy formats:
- `Completed`, `COMPLETED`, `✓ Completed`, `Completed ✅`
- `Under Review`, `Pending Review`
- `Awaiting transformation`

**FR-4.5: Grep-Friendly Format**
- Headers SHALL use `**Key:** Value` format for regex extraction
- No nested formatting within header values
- One attribute per line

---

## Automation and Tooling

### 5. Status Query Tool

**FR-5.1: Core Functionality**

Status query tool SHALL:
- Scan all `.md` files in `specs/`, `project_plans/`, `changes/`
- Extract headers using regex pattern matching
- Build relationship maps: spec → plan → changes
- Recognize all status format variations (FR-4.4)

**FR-5.2: Query Commands**

Tool SHALL support:
```bash
--next         # Next unimplemented project plan
--oldest       # Oldest pending project plan
--incomplete   # All incomplete project plans
--orphans      # Plans without source specs
--summary      # Overall status summary
```

**FR-5.3: Implementation Constraints**
- Python standard library ONLY (no external dependencies)
- Executable via `python tools/query_status.py`
- Output SHALL be human-readable and/or JSON

**FR-5.4: Use Cases**
- "What is the next unimplemented project plan?"
- "What is the oldest project plan awaiting implementation?"
- "Which project plans are incomplete?"
- "Show me all specs without project plans"

---

## Agent Workflow Integration

### 6. System Prompt Instructions

**FR-6.1: Inbox Processing Command**

Agents SHALL recognize command: **"process the first inbox item"**

Workflow:
1. List files in `dev_notes/inbox/` (lexicographically sorted)
2. Read the first file
3. Generate specification in `dev_notes/specs/` with:
   - Timestamp-based naming
   - Standardized header
   - Professional formatting
4. Move original file to `dev_notes/inbox-archive/`
5. Ask user: "Should I create a project plan?"

**FR-6.2: Project Plan Generation**

When generating project plans:
1. Research codebase to understand current state
2. Create detailed, phased implementation plan
3. Include clarifying questions if requirements unclear
4. Save to `dev_notes/project_plans/` with matching timestamp
5. Set **Status: 🔵 Ready for Implementation**
6. Set **Source:** to spec file path
7. Stop and await human review

**FR-6.3: Implementation Execution**

When user approves plan ("implement the plan", "I approve"):
1. Update plan **Status: 🟡 In Progress**
2. Execute tasks according to phases
3. Create change log in `dev_notes/changes/`
4. Update change log as tasks complete
5. When done, update both to **Status: 🟢 Awaiting Approval**
6. Stop and await human review

---

## Documentation Requirements

### 7. Documentation Updates

**FR-7.1: Cross-References**

All documentation mentioning "specs" or "project plans" SHALL also mention "inbox":
- `README.md`
- `docs/workflows.md`
- `AGENTS.md`
- `CLAUDE.md`, `AIDER.md`, and other tool guides
- `docs/system-prompts/tools/*.md`

**FR-7.2: Workflow Examples**

Documentation SHALL include end-to-end examples showing:
- User drops file in inbox
- Agent processes to spec
- Agent generates project plan
- Human reviews and approves
- Agent implements and marks complete

---

## Testing Requirements

### 8. Quality Assurance

**FR-8.1: Pytest Coverage**

Test suite SHALL include:
- Header parsing from markdown files
- Status format recognition (all variations)
- Relationship mapping (spec → plan → changes)
- Edge cases (missing headers, malformed files)

**FR-8.2: Integration Testing**

Manual or automated tests SHALL verify:
- Complete inbox → spec → archive workflow
- Correct header generation
- Naming convention compliance
- File movement operations

**FR-8.3: Regression Prevention**

All existing pytests SHALL continue to pass after implementation.

---

## Non-Functional Requirements

### 9. Performance & Usability

**NFR-9.1: Processing Speed**
- Inbox file processing SHALL complete within reasonable time (< 2 minutes)
- Status queries SHALL return results within 5 seconds

**NFR-9.2: Reliability**
- Failed spec generation SHALL NOT move inbox file to archive
- Partial failures SHALL be logged for debugging

**NFR-9.3: Maintainability**
- Status query tool SHALL use only Python standard library
- No heavy dependencies required (e.g., pandas, SQLAlchemy)

---

## Future Enhancements (Out of Scope)

The following are acknowledged but deferred to future specifications:

### 10. Voice-to-Specification Pipeline
- Audio capture via microphone
- Speech-to-text via Whisper
- LLM-based text refinement (grammar, punctuation, paragraphs)
- Global inbox with multi-project routing

### 11. Advanced Automation
- Automated status polling (watch for changes)
- Pull request creation after implementation
- Slack/communication tool integration

---

## Success Criteria

Implementation is considered successful when:
- [ ] Files in `dev_notes/inbox/` can be processed via agent command
- [ ] Generated specs have standardized headers
- [ ] Original files moved to `dev_notes/inbox-archive/`
- [ ] Status query tool identifies next unimplemented plan
- [ ] Git properly ignores inbox/archive/logs
- [ ] All documentation references inbox workflow
- [ ] All pytests pass (100% pass rate)
- [ ] Manual end-to-end workflow test succeeds

---

## References

- **Original Input:** dev_notes/inbox/recording-01-answers.md
- **Related Plans:** dev_notes/project_plans/2026-01-27_07-28-35_inbox-based-spec-generation.md
- **Workflows:** docs/workflows.md
- **Agent Instructions:** AGENTS.md, CLAUDE.md, AIDER.md
