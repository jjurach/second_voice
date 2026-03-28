# Specification: Redundancy Removal & Brainstorm Consolidation

**Source:** dev_notes/inbox/second-voice-enhancements.md
**Status:** 🔵 Ready for Review
**Priority:** HIGH
**Timestamp:** 2026-02-09_17-00-00

---

## Overview

Enhance speech-to-structured-text processing to explicitly detect and remove redundant phrases, consolidate similar ideas across multiple voice segments, and produce coherent, deduplicated output. This is especially valuable for brainstorming sessions where users naturally repeat and refine ideas across multiple iterations.

**Use Case:** User brainstorms for 30 minutes with multiple recording segments. They repeat similar ideas, mention "that thing I said earlier," combine related concepts. Second Voice detects these patterns, consolidates duplicate concepts, and produces clean output without the repetition.

---

## Problem Statement

Currently, redundancy handling is implicit in the LLM system prompt:

```
"Consolidating similar ideas into coherent statements"
```

However:

1. **Implicit Only:** No explicit detection or measurement of redundancy
2. **LLM-Dependent:** Quality depends entirely on model capability and prompt clarity
3. **No User Feedback:** User doesn't see what was deduplicated or how ideas were consolidated
4. **No Configurable Thresholds:** All redundancy removal is automatic with no control
5. **Cross-Iteration Blindness:** Cannot compare ideas across multiple iterations (would need dual-text feature)

**Impact:** Brainstorm documents may still contain subtle repetitions, and users have no visibility into consolidation logic.

---

## Core Requirements

### FR-1: Enhanced System Prompt for Redundancy Detection
New system prompt that explicitly calls out redundancy removal:

```
You are a brainstorm consolidation assistant.
The user has spoken multiple times about related topics.

Your primary job is to:
1. IDENTIFY repeated phrases, concepts, or ideas
2. CONSOLIDATE related ideas into single, comprehensive statements
3. REMOVE exact duplicates and near-duplicates
4. PRESERVE each unique concept exactly once
5. Clean up speech artifacts (ums, ahs, stutters)

REDUNDANCY DETECTION:
- Look for exact phrase repetitions ("let's make it fast", "fast is important")
- Look for semantic similarity ("quick response", "rapid execution")
- Look for paraphrases of the same idea with different wording
- Group related concepts and represent once with combined details

CONSOLIDATION STRATEGY:
When two statements express similar ideas:
- Keep the clearest version
- Add details from both versions if they add new information
- Discard versions that are subsumed by others
- Note cross-connections if relevant

OUTPUT FORMAT:
- Use markdown with headers and bullets
- Each unique idea appears exactly once
- Consolidated statements combine best phrasing from all versions
- No preamble, just the clean consolidated content

IMPORTANT: This is NOT summarization. Include all unique ideas.
It IS deduplication. Each concept represented once, not multiple times."""
```

### FR-2: Explicit Redundancy Metrics
- **Repetition Count:** Track how many times each concept appears
- **Similarity Scores:** Identify near-duplicates (not exact matches)
- **Consolidation Ratio:** Percentage reduction from input to output
- Optional: Display metrics to user (informational only)

### FR-3: Multi-Pass Processing (Optional Enhancement)
**Basic Implementation (Single Pass):**
- Apply enhanced system prompt in one LLM call
- LLM handles consolidation via language understanding
- Simpler, faster, fewer API calls

**Advanced Implementation (Two-Pass) - Future consideration:**
- Pass 1: Extract unique concepts and tag duplicates
- Pass 2: Consolidate and format for clarity
- Better transparency but higher cost

**Recommendation for this spec:** Use single-pass approach. Two-pass can be future enhancement.

### FR-4: Configurable Redundancy Threshold
New CLI flag: `--consolidate-level`
- `minimal` (default): Remove only exact duplicates, rely on LLM
- `moderate`: LLM+ basic similarity detection for near-duplicates
- `aggressive`: Multiple passes, semantic similarity analysis
- `off`: Use generic system prompt, no special consolidation

### FR-5: Consolidation Reporting (Optional)
If `--report-consolidation` flag is set:
- Output includes a summary section showing:
  - Input concept count (estimated)
  - Output concept count
  - Redundancy ratio (% reduction)
  - Which ideas were consolidated
- Example report:
  ```
  ## Consolidation Summary
  - Input concepts: ~23 (from brainstorm)
  - Output concepts: 18 (after consolidation)
  - Redundancy: 21% reduction
  - Consolidated: "Performance" mentions (5→1), "UI clarity" (3→1)
  ```

### FR-6: Preservation of Intent
- All unique meanings preserved, nothing lost
- Consolidation combines details, doesn't discard nuance
- Cross-references preserved if relevant ("building on the point from earlier")

### FR-7: Integration with Existing Modes
- Works with menu mode (iterative refinement with dedupe each iteration)
- Works with document mode (consolidate brainstorm into structured doc)
- Optional parameter to existing `process_text()` method
- Backward compatible - default behavior unchanged

### FR-8: Works with Iterative Loop
- Each iteration applies consolidation to its input
- Over multiple iterations, redundancy is continuously removed
- Context between iterations benefits from cleaner, deduplicated text

---

## Architecture

### Data Flow

```
Brainstorm Input (possibly with repetitions)
    ↓
[If consolidate_level != 'off']
    ↓
Apply CONSOLIDATION system prompt (instead of generic cleanup)
    ↓
LLM processes → consolidated, deduplicated text
    ↓
[If report_consolidation flag]
    ↓
Generate metrics and append report section
    ↓
Output: Clean consolidated markdown
```

### Key Insight: Single-Pass vs Two-Pass

**Single-Pass (Recommended for this spec):**
- Replace generic system prompt with consolidation-aware prompt
- LLM handles redundancy detection and consolidation via language understanding
- Faster, fewer API calls, simpler implementation
- Quality depends on model capability and prompt clarity

**Two-Pass (Future enhancement):**
- Pass 1: LLM extracts concepts, tags duplicates
- Pass 2: LLM consolidates and formats
- More transparent but doubles API calls
- Out of scope for this spec

**This spec uses single-pass approach.**

### Files to Modify

**1. `src/cli/run.py`** - CLI argument parsing
- Add `--consolidate-level` flag (minimal/moderate/aggressive/off)
- Add `--report-consolidation` flag (boolean)
- Store in config

**2. `src/second_voice/core/processor.py`** - System prompt selection
- New attribute: `consolidation_level` from config
- Method `get_system_prompt()` that returns appropriate prompt:
  - If `consolidate_level == 'off'`: generic cleanup prompt
  - If `consolidate_level == 'minimal'`: consolidation prompt (FR-1)
  - If `consolidate_level == 'moderate'`: consolidation prompt + similarity hints
  - If `consolidate_level == 'aggressive'`: consolidation prompt + explicit semantic analysis request
- Update `process_text()` to use `get_system_prompt(consolidation_level)`

**3. `src/second_voice/core/processor.py`** - Consolidation reporting (optional)
- New method: `generate_consolidation_report(input_text, output_text)`
- Estimates concept counts (rough heuristic: sentence count)
- Calculates reduction ratio
- Appends report to output if flag is set

**4. `src/second_voice/modes/menu_mode.py`** - Integration
- No changes needed if consolidate_level is passed via config
- Existing flow automatically uses new system prompt

---

## System Prompts by Level

### Level: `off` (Default Cleanup)
```
You are a speech cleanup assistant. Your job is to clean up transcribed speech by:
1. Removing stutters and repeated phrases
2. Consolidating similar ideas into coherent statements
3. Fixing grammar and improving sentence structure
4. Maintaining the original meaning and intent

IMPORTANT: Do NOT answer questions or provide new information.
Only clean up the language.

OUTPUT FORMAT: Output ONLY the cleaned text.
```

### Level: `minimal` (Standard Consolidation)
```
You are a brainstorm consolidation assistant.
The user has spoken about related topics, possibly repeating ideas.

Your job is to:
1. REMOVE exact phrase repetitions
2. CONSOLIDATE closely related ideas
3. Clean up grammar and speech artifacts
4. Maintain the original meaning

When two statements express the same idea:
- Keep the clearest version
- Add unique details from other versions
- Discard redundant versions

OUTPUT FORMAT: Output ONLY the consolidated text. No preamble."""
```

### Level: `moderate` (Explicit Similarity Detection)
```
You are a brainstorm consolidation assistant.

Your job is to:
1. DETECT exact duplicates (same phrase repeated)
2. DETECT semantic duplicates (same idea, different wording)
3. CONSOLIDATE all similar ideas into single statements
4. PRESERVE all unique content
5. Clean grammar and remove speech artifacts

SIMILARITY DETECTION:
Pay special attention to:
- Phrases that mean the same thing in different words
- Related concepts that should be combined
- "That thing I mentioned before" type references
- Subtle variations of the same idea

For each consolidated statement, include the best phrasing
and most important details from all versions.

OUTPUT FORMAT: Output ONLY the consolidated text."""
```

### Level: `aggressive` (Explicit Semantic Analysis)
```
You are a brainstorm consolidation assistant specializing in semantic deduplication.

Your job is to:
1. ANALYZE each statement for core semantic content
2. CLUSTER statements by semantic similarity
3. CONSOLIDATE each cluster into single statement
4. PRESERVE nuance and unique details
5. Clean grammar and remove speech artifacts

SEMANTIC ANALYSIS:
- Group statements by topic/theme
- Within each group, identify core concept vs. elaborations
- Consolidate: Keep concept + combine elaborations
- Result: Each semantic idea appears exactly once

EXAMPLE:
Input:
  - "We need better performance"
  - "Speed is important for users"
  - "Making it fast will help"
  - "Performance matters"

Output:
  - "We need better performance and speed to help users"

OUTPUT FORMAT: Output ONLY the consolidated text."""
```

---

## Implementation Approach

### Step 1: Add CLI Flags
File: `src/cli/run.py`
- Parse `--consolidate-level {off,minimal,moderate,aggressive}` (default: off)
- Parse `--report-consolidation` (boolean flag)
- Store in config dict passed to processor

### Step 2: Enhance System Prompt Logic
File: `src/second_voice/core/processor.py`
- Create constant dict: `CONSOLIDATION_PROMPTS` with all 4 levels
- Add method: `get_system_prompt(consolidation_level, meta_operation=None)`
  - Returns appropriate prompt based on consolidation level
  - Handles meta-operations (outline, summarize, etc.)
- Modify `_process_ollama()`, `_process_openrouter()`, `_process_cline()` to use `get_system_prompt()`
- Pass consolidation_level via instance variable set in `__init__`

### Step 3: Optional Consolidation Reporting
File: `src/second_voice/core/processor.py` (optional for this spec)
- Method: `generate_consolidation_report(input_text, output_text)` → string
  - Count sentences in input and output
  - Calculate reduction ratio: `(input_count - output_count) / input_count * 100`
  - Return formatted report string
- If `--report-consolidation` flag set, append report to final output

### Step 4: Integration
File: `src/second_voice/modes/menu_mode.py`
- Set consolidation level in processor during initialization (or per-call)
- Everything else works automatically

### Step 5: Testing (for future agents)
- Test each consolidation level with repetitive brainstorm input
- Verify exact duplicates are removed
- Verify semantic consolidation works
- Verify output is still valid markdown
- Test `--report-consolidation` output format
- Test backward compatibility (default behavior unchanged)

---

## Success Criteria

### User Perspective
- [ ] User can run: `second_voice --consolidate-level moderate`
- [ ] Repeated ideas in brainstorm are automatically deduplicated
- [ ] Similar ideas are consolidated into single clear statements
- [ ] All unique concepts are preserved
- [ ] Output is shorter but complete (no information lost)
- [ ] With `--report-consolidation`, see metrics showing deduplication work

### Developer Perspective
- [ ] CLI flags parsed correctly
- [ ] `get_system_prompt()` returns appropriate prompt for each level
- [ ] System prompts emphasize redundancy detection and consolidation
- [ ] Processor uses selected system prompt automatically
- [ ] Consolidation reporting (if implemented) generates accurate metrics
- [ ] Default behavior (consolidate-level=off) unchanged

### Quality Gates
- [ ] No breaking changes to existing functionality
- [ ] All existing tests pass
- [ ] New consolidation mode outputs valid markdown
- [ ] Brainstorm documents show clear reduction of repetition
- [ ] Unique concepts are preserved (nothing lost, just deduplicated)

---

## Design Decisions

### Why Single-Pass?
- Simpler to implement
- Fewer API calls, lower cost
- LLMs are good at this task with clear prompts
- Two-pass can be future enhancement after evaluation

### Why Configurable Levels?
- Users may want different behavior for different inputs
- `off`: Run existing cleanup without consolidation
- `minimal`: Basic deduplication via LLM
- `moderate`: Explicit emphasis on similarity detection
- `aggressive`: Deep semantic analysis for brainstorms

### Why Optional Reporting?
- Core functionality works without it
- Reporting adds observability for users interested in metrics
- Can be implemented as post-processing, not core requirement

---

## Integration with Other Specifications

### Works With: Structured Document Creation (Spec 2026-02-09_structured-document-creation.md)
```
second_voice --document-mode --output notes.md --consolidate-level moderate
```
User brainstorms, system structures AND deduplicates in one step.

### Works With: Dual-Text Looping (Future Spec)
Would preserve original text while consolidating processed text.

### Works With: Existing Menu Mode
No changes needed. Use `--consolidate-level` with menu loop for iterative refinement.

---

## Future Enhancements (Out of Scope)

1. **Semantic Clustering API** - Use embedding-based similarity for better detection
2. **Consolidation History** - Show user what was consolidated and why
3. **Custom Dictionaries** - User-defined synonyms for domain-specific terms
4. **Multi-Recording Consolidation** - Deduplicate across multiple voice segments
5. **Preserve Alternative Phrasings** - Optional: keep 2nd-best version as footnote

---

## References

### Related Documents
- `docs/current-capabilities.md` - Current feature inventory
- `docs/architecture.md` - System architecture
- `2026-02-09_structured-document-creation.md` - Document mode spec (pairs well with this)

### System Prompt Examples
- See: All FR-1 and "System Prompts by Level" section above

### Code References
- `src/second_voice/core/processor.py:_process_ollama()` (L364-433)
- `src/second_voice/core/processor.py:_process_openrouter()` (L435-613)
- `src/second_voice/modes/menu_mode.py:run()` (L174-387)
