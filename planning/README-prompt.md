# Second Voice Enhancement Specifications

**Last Updated:** 2026-02-09
**Status:** Ready for Implementation

This directory contains detailed specifications for second-voice architectural enhancements. All specifications are implementation-ready with clear requirements, architecture guidance, and success criteria.

---

## Quick Reference

### By Priority

#### HIGH Priority (Immediate Value)

| Spec | Focus | Value | Complexity |
|------|-------|-------|-----------|
| **Structured Document Creation** | Document mode from voice | Create brainstorms/notes as markdown | Moderate |
| **Redundancy Removal & Consolidation** | Deduplication via enhanced prompts | Clean up repetitive speech | Low |

#### MEDIUM Priority (Foundation & Enhancement)

| Spec | Focus | Value | Complexity |
|------|-------|-------|-----------|
| **Dual-Text Looping** | Preserve raw+cooked context | Better LLM understanding & UX | Moderate |
| **Two-Pane Interactive UI** | Chat-based refinement | Real-time collaboration | High |
| **Collaborative Refinement Session** | Formalize iterative loop | Explicit session management | Moderate |

#### LOW Priority (Research-Dependent)

| Spec | Focus | Value | Complexity |
|------|-------|-------|-----------|
| **Cloud Code Integration** | IDE keyboard shortcut | Voice in IDE workflow | High (research-blocked) |

---

## File Listing

```
2026-02-09_structured-document-creation.md
  └─ User specifies output file, speaks content, system structures into markdown

2026-02-09_redundancy-removal-consolidation.md
  └─ CLI flag --consolidate-level enables explicit deduplication by LLM

2026-02-09_dual-text-looping-editor.md
  └─ Both original raw and processed text persist through iterations

2026-02-09_two-pane-interactive-ui.md
  └─ Split-pane: target text (top, editable) + chat with LLM (bottom)

2026-02-09_collaborative-refinement-session.md
  └─ Formalize loop as session with round tracking, pause/resume, evolution view

2026-02-09_cloud-code-ctrl-g-integration.md
  └─ Ctrl+G shortcut in IDE triggers second-voice (research-dependent)
```

---

## Implementation Roadmap

### Recommended Sequence

```
START
  ↓
Spec 2: Redundancy Removal (Quick win, low risk)
  ↓
Spec 1: Structured Document Creation (High value, moderate effort)
  ↓
Spec 3: Dual-Text Looping (Foundation for collaborative features)
  ↓
Spec 4 & 5 (Parallel): Two-Pane UI + Refinement Sessions
  ↓
Spec 6: Cloud Code Integration (After research spike)
  ↓
COMPLETE
```

### Why This Order?

1. **Redundancy Removal First**
   - Low implementation cost (system prompt changes)
   - Low risk (non-breaking)
   - Demonstrates quick iteration and value delivery

2. **Document Creation Second**
   - High user value (new workflow)
   - Moderate complexity (new CLI mode)
   - Builds on existing pipeline

3. **Dual-Text Foundation Third**
   - Prerequisites for collaborative features
   - Moderate effort
   - Improves LLM context understanding

4. **UI & Sessions Parallel**
   - Both depend on dual-text looping
   - Can be developed in parallel
   - Higher complexity but worthwhile

5. **Cloud Code Last**
   - Blocked on external research
   - Lower priority (standalone CLI works fine)
   - Can proceed after internal features solid

---

## Specification Format

Each specification includes:

### Structure
- **Overview** - What is this feature?
- **Problem Statement** - Why is it needed?
- **Core Requirements** - FR-1, FR-2, FR-3... (functional requirements)
- **Architecture** - Data flow, components, design
- **Implementation Approach** - Step-by-step phases
- **Success Criteria** - How to know it's done
- **Integration Notes** - Works with what?
- **References** - Related code and docs

### Quality Standards
- Clear, numbered requirements (FR-*)
- Specific file paths to modify
- Example CLI commands and output
- Data structure examples (JSON, etc.)
- Code snippets where helpful
- Multiple design approaches explained

---

## Key Features Across Specs

### CLI Flags Introduced

| Flag | Spec | Purpose |
|------|------|---------|
| `--document-mode` | Spec 1 | Enable document creation mode |
| `--output <path>` | Specs 1, 3 | Specify output file location |
| `--consolidate-level` | Spec 2 | Set redundancy removal level |
| `--report-consolidation` | Spec 2 | Show consolidation metrics |
| `--interactive` | Spec 4 | Enable two-pane interactive mode |
| `--ui {tui,gui,web}` | Spec 4 | Select UI backend |
| `--collaborative` | Spec 5 | Start collaborative session mode |
| `--resume-session <id>` | Spec 5 | Resume previous session |
| `--show-evolution` | Spec 3 | Display context evolution |
| (Ctrl+G) | Spec 6 | Keyboard trigger (research-dependent) |

### Data Structures Introduced

| Structure | Spec | Purpose |
|-----------|------|---------|
| JSON Context | Spec 3 | Store both raw+cooked text per iteration |
| IterationContext | Spec 3 | Single iteration with metadata |
| SessionContext | Spec 5 | Multiple iterations in a session |
| ChatMessage | Spec 4 | Message in interactive mode |
| UIEvent | Spec 4 | UI event from TUI/GUI |

### System Prompts Enhanced

| Prompt | Spec | Change |
|--------|------|--------|
| Document System Prompt | Spec 1 | New: optimize for markdown structure |
| Consolidation Prompts (4 variants) | Spec 2 | New: explicit redundancy guidance |
| Dual-Text Context Prompt | Spec 3 | Enhanced: include both raw+cooked |
| Chat Command Prompts | Spec 4 | New: handle /commands and intent |

---

## Integration Points

### Works With Existing Features
- All specs maintain backward compatibility
- Existing menu mode unchanged by default
- CLI flags are optional; system works without them
- Default behavior is unchanged

### Works With Each Other
```
Spec 3 (Dual-Text)
  ↓ Foundation for ↓
Spec 4 (Two-Pane UI) ←→ Spec 5 (Collaborative Session)
  ↓
Spec 2 (Redundancy Removal) [works with any of the above]
  ↓
Spec 1 (Document Mode) [orthogonal, works standalone]
  ↓
Spec 6 (Cloud Code) [can use any of the above + IDE integration]
```

### Architecture Assumptions
- Existing processor.py handles LLM calls
- Existing modes extend BaseMode
- Existing CLI parsing via run.py
- Existing provider system (Ollama, OpenRouter, Groq)
- Existing recorder and config systems

---

## For Implementation Agents

### Getting Started
1. **Choose a spec** (see recommended order above)
2. **Read the spec completely** (don't skip sections)
3. **Identify files to modify** (each spec lists them)
4. **Follow implementation phases** (step-by-step guidance provided)
5. **Verify success criteria** (testable outcomes)

### Questions to Ask Per Spec
- What CLI flags or config keys are new?
- What new classes or modules are created?
- What existing files are modified (and how)?
- What's the data flow through the system?
- How does it integrate with existing code?
- What are the edge cases and error scenarios?

### Testing Strategy
- Each spec includes "Success Criteria" section
- Success criteria are testable and measurable
- Test both happy path and error cases
- Verify backward compatibility
- Update docs after implementation

### Documentation After Implementation
- Update `docs/architecture.md` to mark feature as "Implemented"
- Update `docs/current-capabilities.md` to move feature from "NOT Implemented" to "Implemented"
- Add any learnings or changes to spec as "Implementation Notes"
- Document any deviations from spec

---

## References

### Documentation
- **Architecture Overview:** `docs/architecture.md`
- **Current Capabilities Inventory:** `docs/current-capabilities.md`
- **Implementation Reference:** `docs/implementation-reference.md`
- **Workflows & Processes:** `docs/workflows.md`

### Related Code
- **CLI Entry:** `src/cli/run.py`
- **Mode System:** `src/second_voice/modes/`
- **Processor (LLM):** `src/second_voice/core/processor.py`
- **Configuration:** `src/second_voice/core/config.py`
- **Headers:** `src/second_voice/utils/headers.py`

### Previous Specs (for reference)
- Older specs in this directory from 2026-01-* dates
- Show patterns for how specs have evolved

---

## Notes for Future Work

### After All Specs Implemented
1. **Performance Review:** Measure LLM cost per feature
2. **User Testing:** Get feedback on new features
3. **Refinement:** Address any gaps discovered in implementation
4. **Next Wave:** Plan further enhancements based on usage

### Potential Future Specs (Out of Scope)
- Multi-recording document accumulation
- Semantic analysis and topic extraction
- Audio waveform visualization
- Export to multiple formats (Markdown, HTML, PDF)
- Collaborative multi-user editing
- Cloud-based session storage
- Analytics on content evolution

### Known Limitations to Address Later
- Context size management (currently simple truncation)
- No full session history (only last few rounds)
- No branching/version control for ideas
- Redundancy detection is LLM-based only (no algorithmic similarity)

---

## Questions & Clarifications

### For User (if spec needs refinement)
- What output format should `--report-consolidation` use?
- Should Cloud Code integration support voice-while-editing or just button-triggered?
- Should sessions be cloud-backed or local-only?
- What's the maximum number of rounds in a collaborative session?

### For Implementation Team
- Which spec should we start with? (See recommended order above)
- How much testing is expected per feature?
- Should new modes have their own test files?
- What's the policy on backward compatibility during implementation?

---

## Version History

| Date | Change | Author |
|------|--------|--------|
| 2026-02-09 | Created 6 specs from user voice input | Mayor |
| TBD | Spec 1 Implementation | TBD |
| TBD | Spec 2 Implementation | TBD |
| TBD | Spec 3 Implementation | TBD |
| TBD | Spec 4 Implementation | TBD |
| TBD | Spec 5 Implementation | TBD |
| TBD | Spec 6 Research & Implementation | TBD |

---

## How to Use This Directory

### For Developers
```bash
# Find a spec to work on
ls 2026-02-09_*.md

# Read the full spec
cat 2026-02-09_structured-document-creation.md

# Identify modified files
grep "File:" 2026-02-09_structured-document-creation.md

# Start implementation following "Implementation Approach" section
```

### For Project Managers
```bash
# Check implementation status
grep "STATUS:" 2026-02-09_*.md

# See dependencies between specs
grep "Depends on\|Prerequisite for\|Works with" 2026-02-09_*.md

# Review success criteria
grep "Success Criteria" 2026-02-09_*.md
```

### For Code Reviewers
```bash
# Verify spec was followed
cat 2026-02-09_structured-document-creation.md
# Compare against PR changes

# Check success criteria were met
# (listed in each spec)

# Verify no breaking changes
# (each spec addresses backward compatibility)
```

---

**Status:** All specifications ready for implementation. Start with Spec 2 (Redundancy Removal) for quick win, then Spec 1 (Document Creation) for high value.
