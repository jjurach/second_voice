# Project Plan: Mandatory Context Assembly for Agent-Specific System Prompts

**Created:** 2026-01-28
**Status:** WONT-DO - Over-engineered solution, simpler alternative preferred
**Related Spec:** `dev_notes/specs/2026-01-28_10-36-41_mandatory-context-assembly.md`
**Alternative Plan:** `dev_notes/project_plans/2026-01-28_10-36-41_simple-mandatory-reading-lists.md`

---

## Why This Plan is WONT-DO

After thorough analysis across two independent conversations, this approach was determined to be **over-engineered for the actual problem it aims to solve**.

### Decision Rationale

**The core assumption is flawed:** The plan assumes that assembling mandatory context into a single file is significantly better than having agents read 3-5 separate files at the start of a session. This assumption doesn't hold up:

1. **Tool calls are cheap:** Reading 3-5 files takes ~5 tool calls, which is only 10% of one turn in a typical 50-turn agent session. Modern Claude models handle this effortlessly with negligible latency (1-2 seconds total).

2. **No evidence of the problem:** We have not observed agents actually skipping mandatory content when instructed to read specific files. This is premature optimization for a problem that may not exist.

3. **Complexity cost is too high:** The solution introduces:
   - Build steps (must run bootstrap.py after every edit)
   - Generated files (5-7 agent files regenerated for every chapter edit)
   - Version control noise (timestamps/checksums change in every generated file)
   - Abstraction layers (mandatory-contents.txt → chapters → assembly → generated files)
   - Learning curve (contributors must understand the templating system)
   - Maintenance burden (ongoing testing, validation, debugging)

4. **Loss of transparency:** The simple approach (direct references to files) is clearer, easier to debug, and more maintainable than an assembly system with filtering logic and checksums.

### What We're Doing Instead

**Simpler alternative (see alternative plan):** Update agent instruction files with clear, explicit mandatory reading lists:

```markdown
# MANDATORY READING - READ FIRST, EVERY SESSION

Before starting ANY task, you MUST read these files in order:
1. docs/system-prompts/workflows/logs-first.md
2. docs/system-prompts/principles/definition-of-done.md
3. docs/mandatory.md
```

This approach:
- ✓ Crystal clear what's mandatory vs. optional
- ✓ No build step required
- ✓ No generated files to maintain
- ✓ Easy to update and debug
- ✓ Clean git history
- ✗ Requires 3-5 tool calls (but this is negligible)

### When We Might Revisit

We would reconsider this approach if:
1. We observe **strong evidence** that agents frequently skip mandatory content, AND
2. This causes **real, measurable problems**, AND
3. The simpler alternative (explicit reading lists) fails to solve it, AND
4. We're deploying to 20+ projects where consistency tooling would be valuable

Until then, we're focusing on writing clearer, more focused instruction files rather than building complex assembly machinery.

### Key Lesson Learned

**"The best code is the code you don't have to write or maintain."**

Just because we *can* build a sophisticated system doesn't mean we *should*. Sometimes the simple solution is the right solution, especially when the problem itself is unproven.

---

## CRITICAL CONTEXT FROM PREVIOUS ANALYSIS

A previous conversation (see `dev_notes/inbox-archive/2026-01-28_10-36-41-mandatory-context-project-plan.md`) reached the conclusion that this full assembly system is **likely over-engineered**. Key findings:

1. **Tool calls are cheap:** 3-5 file reads = ~5 tool calls = 10% of one turn in a 50-turn session
2. **No evidence of problem:** Agents haven't been observed skipping mandatory content
3. **Complexity cost too high:** Build steps, version control noise, learning curve
4. **Simpler alternative better:** Clear reading lists in agent files

**Previous recommendation:** Use explicit reading lists instead of assembly system.

**This plan includes Phase 0 validation to confirm whether the problem even exists before building the complex solution.**

---

## Executive Summary

This plan implements an assembly system in `bootstrap.py` to compile comprehensive agent-specific instruction files from modular system-prompt chapters. The goal is to eliminate tool-call overhead and guarantee agents see mandatory context on first invocation.

**STRONGLY RECOMMENDED:** Start with Phase 0 validation and the simpler alternative. Only proceed with full assembly system if Phase 0 reveals actual problems that the simple approach cannot solve.

---

## Phase 0: Validate the Problem (MUST COMPLETE FIRST)

**Goal:** Determine if we need the full assembly system or should use a simpler approach.

### Tasks

1. **Test current agent behavior** with existing instruction files:
   - Start fresh Claude Code session
   - Observe: Does it read the referenced files without prompting?
   - Measure: How many tool calls does it take?
   - Record: Any instances where mandatory content was skipped?

2. **Create simple alternative** in one agent file (e.g., claude.md):
   ```markdown
   # MANDATORY READING - READ FIRST, EVERY SESSION

   Before ANY task, you MUST read these files in order:
   1. docs/system-prompts/workflows/logs-first.md
   2. docs/system-prompts/principles/definition-of-done.md
   3. docs/mandatory.md (if exists)
   ```

3. **Test simple alternative**:
   - Start fresh session with updated claude.md
   - Observe agent behavior
   - Measure tool calls required
   - Assess: Does this solve the problem adequately?

4. **Decision gate:**
   - **If simple approach works:** STOP. Update all agent files with clear reading lists. Done.
   - **If agents skip content:** Continue to Phase 1.
   - **If tool calls are excessive (>10):** Continue to Phase 1.

**Deliverable:** Decision document in `dev_notes/decisions/2026-01-28_assembly-system-decision.md`

**Estimated effort:** 1-2 hours testing

---

## Phase 1: Content Inventory & Analysis

**Goal:** Understand current system-prompts structure and identify mandatory content.

### Current Structure Analysis

Based on `docs/system-prompts/` directory listing:

```
docs/system-prompts/
├── workflows/          # Contains logs-first.md, core.md, custom-template.md
├── tools/              # Tool-specific guides (aider.md, claude-code.md, gemini.md, etc.)
├── principles/         # definition-of-done.md
├── languages/python/   # Language-specific guides
├── templates/          # Document templates
├── patterns/           # Implementation patterns
├── processes/          # Bootstrap, docscan, tool-entry-points
├── README.md
└── reference-architecture.md
```

### Categorization Tasks

1. **Inventory all .md files** in system-prompts:
   ```bash
   find docs/system-prompts -name "*.md" -type f > /tmp/inventory.txt
   ```

2. **Categorize each file**:
   - **Mandatory (all agents):** Core principles, definition of done, prohibited actions
   - **Mandatory (agent-specific):** Tool-specific best practices
   - **Contextual/Optional:** Architecture deep-dives, advanced patterns
   - **Meta/Process:** README files, bootstrap documentation

3. **Identify multi-topic files** that should be split:
   - Check each file's length and topic coverage
   - Flag files >500 lines or covering >2 distinct topics

4. **Determine logical ordering**:
   - Principles first
   - Core workflow
   - Development practices
   - Project-specific
   - Agent-specific

### Deliverable

Create `dev_notes/analysis/2026-01-28_system-prompts-inventory.md` with:
- Complete file listing with categorizations
- Rationale for mandatory vs. optional
- Recommended chapter organization
- List of files to split (if any)
- Proposed ordering for mandatory-contents.txt

**Estimated effort:** 2-3 hours

---

## Phase 2: Design Assembly Architecture

**Goal:** Design the technical approach before implementation.

### Key Design Decisions

1. **Where chapters live:**
   - **Option A:** Create new `docs/system-prompts/chapters/` directory
   - **Option B:** Use existing subdirectory structure (tools/, principles/, etc.)
   - **Recommendation:** Option B (less file movement, preserves existing organization)

2. **Mandatory contents format:**
   - Use `docs/system-prompts/mandatory-contents.txt`
   - Plain text, one file path per line
   - Comments with `#`
   - Paths relative to project root

3. **Agent filtering strategy:**
   - Filename-based: `tool-aider-*`, `tool-claude-*`, etc.
   - Word boundary regex matching to avoid false positives
   - Hard-coded KNOWN_AGENTS list initially (can make configurable later)

4. **Generated file location:**
   - Project root (aider.md, claude.md, etc.)
   - Matches current convention
   - Agents expect to find them there

5. **Change detection:**
   - SHA256 checksum in generated file metadata
   - Warn on manual edits, suggest using docs/mandatory.md
   - `--force` flag to override

### Bootstrap.py Integration Points

Existing bootstrap.py has:
- Section injection mechanism (`_update_section`)
- Workflow management (`apply_workflow_state`)
- AGENTS.md synchronization

New functionality needed:
- `assemble` command
- Mandatory contents parsing
- Chapter filtering by agent name
- Content assembly with metadata
- Checksum generation/validation

### API Design

```python
# New methods to add to Bootstrap class

def parse_mandatory_contents(self, contents_path: str) -> list[str]:
    """Parse mandatory-contents.txt, return list of chapter paths."""

def filter_chapters_for_agent(self, paths: list[str], agent: str) -> list[str]:
    """Filter chapters based on agent name patterns."""

def load_chapter(self, path: str, strict: bool = False) -> str | None:
    """Load chapter content, handle missing files."""

def assemble_agent_file(self, agent: str, chapters: list[str]) -> tuple[str, str]:
    """Assemble content with metadata, return (content, checksum)."""

def write_agent_file(self, agent: str, content: str, force: bool = False) -> bool:
    """Write agent file with change detection."""
```

### CLI Design

```bash
python bootstrap.py assemble [--agents AGENT1,AGENT2] [--verbose] [--dry-run] [--force] [--strict] [--check]
```

### Deliverable

Create `dev_notes/designs/2026-01-28_assembly-architecture.md` with:
- Detailed technical design
- Data structures
- Algorithm pseudocode
- Edge case handling
- Integration points with existing bootstrap.py

**Estimated effort:** 2-3 hours

---

## Phase 3: Create Mandatory Contents List

**Goal:** Define which chapters are mandatory and in what order.

### Tasks

1. **Create initial mandatory-contents.txt** based on Phase 1 analysis:
   ```
   # Core principles
   docs/system-prompts/principles/definition-of-done.md

   # Workflows
   docs/system-prompts/workflows/logs-first.md

   # Tool-specific (filtered per agent)
   docs/system-prompts/tools/aider.md
   docs/system-prompts/tools/claude-code.md
   docs/system-prompts/tools/gemini.md

   # Project-specific (if exists)
   docs/mandatory.md
   ```

2. **Review with user** for approval

3. **Create docs/mandatory.md** for Second Voice project:
   - Describe project structure
   - List key documentation with keywords
   - Reference architecture.md, implementation-reference.md, etc.

4. **Validate all paths** actually exist (or document which don't yet)

### Deliverable

- `docs/system-prompts/mandatory-contents.txt`
- `docs/mandatory.md`

**Estimated effort:** 1 hour

---

## Phase 4: Implement Assembly in Bootstrap.py

**Goal:** Add assembly functionality to bootstrap.py.

### Implementation Steps

#### 4.1: Core Parsing & Filtering

```python
KNOWN_AGENTS = ['aider', 'claude', 'gemini', 'cursor', 'cody', 'copilot', 'agents']

def parse_mandatory_contents(self, contents_path: str) -> list[str]:
    """Parse mandatory-contents.txt."""
    chapters = []
    with open(contents_path, 'r') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            chapters.append(line)
    return chapters

def filter_chapters_for_agent(self, paths: list[str], agent: str) -> list[str]:
    """Filter chapters for specific agent."""
    filtered = []
    for path in paths:
        filename = os.path.basename(path).lower()

        # Check for other agent names
        exclude = False
        for other_agent in KNOWN_AGENTS:
            if other_agent == agent or other_agent == 'agents':
                continue
            # Word boundary matching
            if re.search(rf'\b{other_agent}\b', filename):
                exclude = True
                break

        if not exclude:
            filtered.append(path)

    return filtered
```

#### 4.2: Chapter Loading

```python
def load_chapter(self, path: str, strict: bool = False) -> str | None:
    """Load chapter content."""
    full_path = os.path.join(self.project_root, path)

    if not os.path.exists(full_path):
        if strict:
            raise FileNotFoundError(f"Chapter not found: {path}")
        return None

    with open(full_path, 'r') as f:
        return f.read()
```

#### 4.3: Assembly & Checksums

```python
import hashlib
from datetime import datetime, timezone

def assemble_agent_file(self, agent: str, chapter_paths: list[str]) -> tuple[str, str]:
    """Assemble agent file with metadata."""
    timestamp = datetime.now(timezone.utc).isoformat()

    lines = [
        "<!-- GENERATED FILE - DO NOT EDIT -->",
        f"<!-- Generated by bootstrap.py from docs/system-prompts/mandatory-contents.txt -->",
        f"<!-- Target agent: {agent} -->",
        f"<!-- Last generated: {timestamp} -->",
        "<!-- Checksum: PLACEHOLDER -->",
        "",
    ]

    # Add chapters
    for path in chapter_paths:
        content = self.load_chapter(path, strict=False)
        if content is None:
            continue

        lines.append(f"<!-- BEGIN CHAPTER: {path} -->")
        lines.append(content)
        lines.append(f"<!-- END CHAPTER: {path} -->")
        lines.append("")

    # Generate content and checksum
    content = "\n".join(lines)
    checksum = hashlib.sha256(content.encode()).hexdigest()

    # Replace placeholder
    content = content.replace("<!-- Checksum: PLACEHOLDER -->",
                            f"<!-- Checksum: sha256:{checksum} -->")

    return content, checksum
```

#### 4.4: Change Detection & Writing

```python
def detect_manual_edits(self, path: str) -> bool:
    """Check if generated file was manually edited."""
    if not os.path.exists(path):
        return False

    with open(path, 'r') as f:
        content = f.read()

    # Extract stored checksum
    match = re.search(r'<!-- Checksum: sha256:([a-f0-9]+) -->', content)
    if not match:
        return True  # No checksum = assume edited

    stored = match.group(1)

    # Compute actual checksum (remove checksum line first)
    content_for_hash = re.sub(
        r'<!-- Checksum: sha256:[a-f0-9]+ -->',
        '<!-- Checksum: PLACEHOLDER -->',
        content
    )
    actual = hashlib.sha256(content_for_hash.encode()).hexdigest()

    return stored != actual

def write_agent_file(self, agent: str, content: str, force: bool = False) -> bool:
    """Write agent file with change detection."""
    path = os.path.join(self.project_root, f"{agent}.md")

    if self.detect_manual_edits(path) and not force:
        print(f"WARNING: {path} has been manually edited!")
        print("  Manual edits will be lost. Add content to docs/mandatory.md instead.")
        print("  Use --force to regenerate anyway.")
        return False

    # Write file
    if self.dry_run:
        print(f"[DRY RUN] Would write: {path}")
        return True

    with open(path, 'w') as f:
        f.write(content)

    print(f"✓ Generated: {path}")
    return True
```

#### 4.5: Main Assemble Function

```python
def assemble(self, agents: list[str] = None, verbose: bool = False,
             strict: bool = False, force: bool = False) -> bool:
    """Main assembly function."""
    if agents is None:
        agents = KNOWN_AGENTS

    # Parse mandatory contents
    contents_path = os.path.join(
        self.system_prompts_dir, "mandatory-contents.txt"
    )

    if not os.path.exists(contents_path):
        print(f"ERROR: {contents_path} not found")
        return False

    chapter_paths = self.parse_mandatory_contents(contents_path)

    if verbose:
        print(f"Loaded {len(chapter_paths)} chapters from {contents_path}")

    # Generate for each agent
    success = True
    for agent in agents:
        if verbose:
            print(f"\nGenerating {agent}.md...")

        # Filter chapters
        filtered = self.filter_chapters_for_agent(chapter_paths, agent)

        if verbose:
            for path in filtered:
                exists = os.path.exists(os.path.join(self.project_root, path))
                status = "✓" if exists else "⚠"
                print(f"  {status} {path}")

        # Assemble
        content, checksum = self.assemble_agent_file(agent, filtered)

        # Write
        if not self.write_agent_file(agent, content, force):
            success = False

    return success
```

#### 4.6: CLI Integration

```python
def main():
    parser = argparse.ArgumentParser(description="Agent Kernel Bootstrap Tool")

    # ... existing arguments ...

    # New assemble command
    parser.add_argument(
        "--assemble",
        action="store_true",
        help="Assemble agent-specific files from mandatory contents"
    )
    parser.add_argument(
        "--agents",
        type=str,
        help="Comma-separated list of agents to generate (default: all)"
    )

    # ... existing force, verbose, dry-run arguments ...
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Fail on missing chapter files (default: warn and skip)"
    )

    args = parser.parse_args()
    bootstrap = Bootstrap(dry_run=args.dry_run)

    if args.assemble:
        agents = args.agents.split(',') if args.agents else None
        success = bootstrap.assemble(
            agents=agents,
            verbose=args.verbose,
            strict=args.strict,
            force=args.force
        )
        sys.exit(0 if success else 1)

    # ... existing functionality ...
```

### Testing During Implementation

After each subsection, test with:
```bash
python bootstrap.py --assemble --dry-run --verbose
```

### Deliverable

- Updated `docs/system-prompts/bootstrap.py` with assembly functionality
- Generated agent files (aider.md, claude.md, etc.)

**Estimated effort:** 4-6 hours

---

## Phase 5: Testing & Validation

**Goal:** Ensure assembly system works correctly.

### Manual Testing

1. **Test basic assembly:**
   ```bash
   python bootstrap.py --assemble --verbose
   ```

2. **Test filtering:**
   - Verify aider.md doesn't contain Claude-specific content
   - Verify claude.md doesn't contain Aider-specific content
   - Verify agents.md contains everything

3. **Test missing file handling:**
   - Add non-existent path to mandatory-contents.txt
   - Verify warning is shown
   - Verify `--strict` mode fails

4. **Test change detection:**
   - Manually edit generated aider.md
   - Run assembly without `--force`
   - Verify warning is shown

5. **Test dry-run mode:**
   - Verify no files are written
   - Verify output shows what would be done

### Automated Testing (Optional)

Create simple test script in `/tmp/`:
```python
#!/usr/bin/env python3
# Test script for assembly functionality

def test_parsing():
    # Test mandatory-contents.txt parsing
    pass

def test_filtering():
    # Test agent name filtering
    pass

def test_assembly():
    # Test content assembly
    pass

if __name__ == '__main__':
    test_parsing()
    test_filtering()
    test_assembly()
    print("All tests passed!")
```

### Deliverable

- Verified assembly system works correctly
- Test results documented in `dev_notes/changes/2026-01-28_*_assembly-implementation.md`

**Estimated effort:** 2-3 hours

---

## Phase 6: Documentation & Cleanup

**Goal:** Document the new system for users and future maintainers.

### Tasks

1. **Update bootstrap.py --help output:**
   - Document new `--assemble` flag
   - Document all related options

2. **Update docs/system-prompts/README.md:**
   - Add "Assembling Agent Files" section
   - Explain mandatory-contents.txt format
   - Show example usage

3. **Create usage guide** (if not in README):
   - When to regenerate
   - How to add new chapters
   - How to handle manual edits (use docs/mandatory.md)

4. **Update CLAUDE.md** (and other agent files at root):
   - Update with new "GENERATED FILE" header
   - Remove old manual content

### Deliverable

- Updated documentation
- All agent files regenerated with new system

**Estimated effort:** 1-2 hours

---

## Risk Assessment

### High Risks

1. **Complexity overkill:**
   - **Risk:** Building machinery for a non-existent problem
   - **Mitigation:** Phase 0 validation step
   - **Contingency:** Revert to simple reading lists if validation fails

2. **Version control noise:**
   - **Risk:** Every chapter edit regenerates 5-7 files
   - **Mitigation:** Clear commit messages, consider .gitignore
   - **Contingency:** Add `--check` mode for CI to detect drift

3. **User confusion:**
   - **Risk:** Contributors don't understand generated file workflow
   - **Mitigation:** Clear "DO NOT EDIT" warnings, good documentation
   - **Contingency:** Add validation in docscan.py to detect manual edits

### Medium Risks

1. **Bootstrap.py conflicts:**
   - **Risk:** New code conflicts with existing functionality
   - **Mitigation:** Careful integration, test existing features still work
   - **Contingency:** Rollback if issues found

2. **False positive filtering:**
   - **Risk:** File like "claudette.md" incorrectly filtered
   - **Mitigation:** Word boundary regex matching
   - **Contingency:** Add explicit exclusion list if needed

### Low Risks

1. **Performance:** File I/O is fast, not a concern
2. **Compatibility:** Pure Python, no new dependencies

---

## Success Criteria

1. **Phase 0 decision made:** Either simple approach adopted, or full system justified
2. **If full system:** Assembly generates 5+ agent files without errors
3. **Filtering works:** Agent-specific content correctly included/excluded
4. **Change detection works:** Manual edits are detected and warned
5. **Documentation complete:** Users understand how to use and maintain system
6. **No regressions:** Existing bootstrap.py features still work

---

## Estimated Timeline

- **Phase 0:** 1-2 hours (validation testing)
- **Phase 1:** 2-3 hours (inventory & analysis)
- **Phase 2:** 2-3 hours (architecture design)
- **Phase 3:** 1 hour (mandatory-contents.txt creation)
- **Phase 4:** 4-6 hours (implementation)
- **Phase 5:** 2-3 hours (testing)
- **Phase 6:** 1-2 hours (documentation)

**Total:** 13-20 hours

**Note:** If Phase 0 determines simple approach is sufficient, total drops to 1-2 hours.

---

## Open Questions for User

1. **Should we proceed with Phase 0 validation first?** (Recommended: Yes)

2. **If simple approach works, should we stop there?** (Recommended: Yes)

3. **Should generated files be committed to git?**
   - Yes: Agents always have context even without running bootstrap
   - No: Cleaner git history, but requires running bootstrap first

4. **Should we create docs/mandatory.md for Second Voice now?**
   - If yes, what should it contain?

5. **Which agents should we generate for?**
   - Current list: aider, claude, gemini, cursor, cody, copilot, agents
   - Should we add/remove any?

6. **Should we create automated tests?**
   - Simple script in tmp/
   - Full pytest suite
   - Just manual testing

---

## Next Steps

1. **User reviews this plan**
2. **User approves or requests changes**
3. **Begin Phase 0 validation**
4. **Make decision to continue or use simple approach**
5. **If continuing, proceed through phases sequentially**

---

## Appendix: Alternative Simpler Approach

If Phase 0 shows the full system isn't needed, here's the simple alternative:

### Update Agent Files with Explicit Reading Lists

**claude.md:**
```markdown
# Claude Code Instructions

## MANDATORY READING - READ FIRST, EVERY SESSION

Before starting ANY task, you MUST read these files in order:

1. **Logs-First Workflow:** docs/system-prompts/workflows/logs-first.md
2. **Definition of Done:** docs/system-prompts/principles/definition-of-done.md
3. **Claude-Specific Guide:** docs/system-prompts/tools/claude-code.md
4. **Project Specifics:** docs/mandatory.md (if exists)

## Other Available Resources

These are optional - read if relevant to your task:
- Architecture: docs/architecture.md
- Implementation Reference: docs/implementation-reference.md
- Workflows: docs/workflows.md
```

**aider.md:**
```markdown
# Aider Instructions

## MANDATORY READING - READ FIRST, EVERY SESSION

Before starting ANY task, you MUST read these files in order:

1. **Logs-First Workflow:** docs/system-prompts/workflows/logs-first.md
2. **Definition of Done:** docs/system-prompts/principles/definition-of-done.md
3. **Aider-Specific Guide:** docs/system-prompts/tools/aider.md
4. **Project Specifics:** docs/mandatory.md (if exists)

## Other Available Resources

These are optional - read if relevant to your task:
- Architecture: docs/architecture.md
- Implementation Reference: docs/implementation-reference.md
```

**Effort:** 30 minutes to update all agent files
**Maintenance:** Update lists when adding new mandatory content
**Pros:** Simple, transparent, easy to debug
**Cons:** Requires 3-5 tool calls per session start

---

## Comparison with Previous Project Plan

### Alignment with Previous Analysis

After reviewing `dev_notes/inbox-archive/2026-01-28_10-36-41-mandatory-context-project-plan.md`, I found:

**Key Agreements:**
1. Both plans include Phase 0 validation (I arrived at this independently)
2. Both recognize the simpler alternative may be sufficient
3. Both acknowledge complexity cost is significant
4. Both provide detailed implementation IF the full system is needed

**Key Differences:**
1. **Previous plan:** Marked STATUS: WONT-DO, recommending NOT to implement
2. **This plan:** More neutral, presents both options with Phase 0 decision gate
3. **Previous plan:** Had extensive critical evaluation section explaining why not to build it
4. **This plan:** Assumes user wants the option, provides full technical design

**New Insights from Old Plan:**
1. The previous agent had access to broader context and made stronger recommendation against implementation
2. Specific observation: "No evidence of the problem" - agents aren't actually skipping mandatory content
3. Version control noise was emphasized more heavily in previous analysis
4. "Best code is code you don't have to write" philosophy

### Updated Recommendation

Based on both analyses, my updated recommendation:

**TIER 1 - Do This First (1-2 hours):**
1. Implement the simple alternative (explicit reading lists in agent files)
2. Test with real usage for 1-2 weeks
3. Monitor whether agents actually skip content or if 3-5 tool calls causes problems

**TIER 2 - Only If Tier 1 Fails (13-20 hours):**
4. If evidence emerges that simple approach doesn't work, proceed with full assembly system
5. Start with minimal implementation (no filtering, just concatenation)
6. Iterate based on actual problems encountered

**TIER 3 - Probably Never Needed:**
7. Full assembly system with all features (filtering, change detection, etc.)
8. Only if deploying to 20+ projects where tooling adds significant value

### Clarifying Questions Based on Both Plans

1. **Have you observed agents skipping mandatory content in practice?**
   - If no: Strongly recommend simple alternative only
   - If yes: What specific content and how often?

2. **Are the 3-5 tool calls at session start actually a problem?**
   - If no: Simple alternative is clearly better
   - If yes: Why? (latency, cost, reliability?)

3. **Do you plan to deploy this to 20+ projects?**
   - If no: Complexity cost likely outweighs benefits
   - If yes: Assembly system might make sense at scale

4. **What's your appetite for maintaining build steps?**
   - Low: Use simple alternative
   - High: Full system is feasible

5. **Given the previous analysis concluded WONT-DO, why revisit?**
   - Has something changed?
   - New requirements emerged?
   - Just want the option documented?

---

## Final Recommendation Summary

**🟢 RECOMMENDED PATH:**
- Implement simple alternative (Phase 0 appendix)
- 30 minutes of work
- No complexity overhead
- Solves the stated problem (ensuring agents read mandatory content)

**🟡 CONTINGENCY PATH:**
- If simple approach fails after real-world testing
- Implement minimal assembly (just concatenation, no filtering)
- Iterate based on actual problems

**🔴 NOT RECOMMENDED:**
- Full assembly system as described in Phases 1-6
- Unless strong evidence emerges that it's needed
- Previous analysis was correct: likely over-engineered

**Decision Point:** User should decide based on answers to clarifying questions above.

---
