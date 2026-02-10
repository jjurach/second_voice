# Specification: Dual-Text Looping Editor Architecture

**Source:** dev_notes/inbox/second-voice-enhancements.md
**Status:** 🔵 Ready for Review
**Priority:** MEDIUM
**Timestamp:** 2026-02-09_17-00-00

---

## Overview

Preserve and pass both the original raw transcription AND the processed/cooked text through the iterative refinement loop. This enables users to see the evolution of their speech from raw → processed across multiple iterations, and allows the LLM to use both texts for better contextual understanding.

**Use Case:** User records five voice memos over the course of an hour, refining an idea. They want to see how their raw speech has evolved from stuttering and repetitive to clear and concise. They also want the LLM to understand both "what I actually said" (raw) and "what it means after cleanup" (processed) to provide better refinement suggestions.

---

## Problem Statement

Current implementation has a critical limitation:

1. **Original Raw Text Lost:** First iteration creates raw → processed text, but raw text is discarded
2. **Only Processed Passed Forward:** Second iteration receives ONLY the processed text from iteration 1
3. **Lost Context:** LLM cannot compare raw text from iteration 1 to new recording in iteration 2
4. **No Evolution Visibility:** User cannot see how raw speech has improved across iterations
5. **Implicit Refinement:** User doesn't see what the LLM changed; only sees final cleaned output

**Impact:** The system loses valuable context about the user's actual speech patterns and makes it harder for the LLM to provide intelligent refinements.

---

## Core Requirements

### FR-1: Preserve Original Raw Text
- Store original raw transcription (before any LLM processing) for all iterations
- Never discard the original speech-to-text output
- Maintain in context alongside processed text through all iterations

### FR-2: Dual-Text Context Structure
Change context storage from plain text to structured format:
```json
{
  "iteration": 1,
  "timestamp": "2026-02-09T12:00:00Z",
  "raw_text": "um so like we need to um make the performance better because the um users are complaining about speed",
  "processed_text": "We need to improve performance because users are complaining about speed.",
  "raw_length": 92,
  "processed_length": 62,
  "reduction_ratio": 0.33
}
```

### FR-3: LLM Receives Both Texts
When processing next iteration, system prompt includes:
```
Previous Context:
[RAW TEXT]
"um so like we need to um make the performance better..."

[PROCESSED TEXT]
"We need to improve performance because users are..."

Current Recording (Raw):
"and also the ui feels sluggish when you scroll"

[Process and refine based on both previous contexts]
```

### FR-4: Iteration Metadata
Track for each iteration:
- Iteration number (1, 2, 3, ...)
- Timestamp of recording
- Length of raw vs. processed (shows condensation ratio)
- User's optional notes (if captured)

### FR-5: Context Evolution Visibility
New CLI option: `--show-evolution`
- Displays context with raw vs. processed side-by-side
- Shows iteration count and timestamps
- Shows condensation ratios
- Helps user understand how their speech is being transformed

### FR-6: Context File Format Change
Move from plain text (`tmp-context.txt`) to structured JSON (`tmp-context.json`):
```json
{
  "current_iteration": 2,
  "sessions": [
    {
      "iteration": 1,
      "timestamp": "2026-02-09T12:00:00Z",
      "raw_text": "...",
      "processed_text": "...",
      "user_notes": null
    },
    {
      "iteration": 2,
      "timestamp": "2026-02-09T12:05:00Z",
      "raw_text": "...",
      "processed_text": "...",
      "user_notes": null
    }
  ]
}
```

### FR-7: Backward Compatibility
- Old plain-text `tmp-context.txt` format is still loadable
- System auto-converts to new format on load
- Can still save in both formats (with flag)
- Existing scripts/tools not broken

### FR-8: Context Size Management
- Even with dual text, manage total context size
- New config: `max_iteration_count` (default: 5 iterations)
- Older iterations are archived, newer iterations kept
- Or: `max_context_size_kb` (default: 50KB)
- Prevents context from growing too large

---

## Architecture

### Data Structure: Iteration Context

```python
class IterationContext:
    """Single iteration of raw + processed text."""
    iteration: int
    timestamp: datetime
    raw_text: str
    processed_text: str
    user_notes: Optional[str] = None

    def to_dict(self) -> dict:
        return {
            'iteration': self.iteration,
            'timestamp': self.timestamp.isoformat(),
            'raw_text': self.raw_text,
            'processed_text': self.processed_text,
            'user_notes': self.user_notes
        }
```

```python
class SessionContext:
    """Full session with multiple iterations."""
    iterations: List[IterationContext]
    current_iteration: int

    def get_context_for_prompt(self) -> str:
        """Returns formatted context string for LLM prompt."""
        # Builds display with raw + processed for all iterations

    def add_iteration(self, raw: str, processed: str):
        """Add new iteration and manage size."""
        # Auto-prune if exceeds size limits

    def to_json(self) -> str:
        """Serialize to JSON."""

    @staticmethod
    def from_json(json_str: str) -> SessionContext:
        """Deserialize from JSON."""
```

### Files to Modify

**1. `src/second_voice/core/processor.py`** - Context management
- Add `IterationContext` class (or use dict)
- Rename `save_context()` → `save_dual_context()` (keep old name for compatibility)
- Change from plain text to JSON
- New method: `format_context_for_prompt()` - builds string with raw + processed
- New method: `add_iteration()` - adds new iteration and manages size
- Update `process_with_headers_and_fallback()` to save both texts

**2. `src/second_voice/modes/menu_mode.py`** - Context handling
- Get both raw (from transcription) and processed (from LLM)
- Save both to context via new `add_iteration()` method
- When displaying context (option 2), show dual-text format
- Support `--show-evolution` flag

**3. `src/cli/run.py`** - CLI arguments
- Add `--show-evolution` flag
- Add `--max-iterations` config option
- Store in config

**4. `src/second_voice/utils/headers.py`** (possibly) - Evolution display
- New utility: `format_context_evolution()` - pretty-print dual-text context

### System Prompt for Dual-Text Context

Update prompt in `processor.py` to acknowledge both texts:

```
Previous Iterations:

ITERATION 1:
Raw: "um so we need to like make the thing faster because um users are saying it's slow"
Processed: "We need to improve speed because users report slow performance."

ITERATION 2:
Raw: "and also the interface feels laggy when scrolling"
Processed: "The interface also feels laggy when scrolling."

Current Recording (Raw):
"yeah and maybe we should like cache the results so it doesn't have to recalculate each time"

Your job:
1. Clean up the current recording
2. Consider how it relates to the previous raw and processed texts
3. Integrate the new idea with previous points
4. Output refined, consolidated text that includes all three pieces
```

---

## Implementation Approach

### Phase 1: JSON Context Structure
File: `src/second_voice/core/processor.py`

1. Create `IterationContext` dataclass
2. Create `SessionContext` class with methods:
   - `add_iteration(raw_text, processed_text)`
   - `format_for_prompt()` - returns string for LLM
   - `save_to_json()` / `load_from_json()`
   - `prune_old_iterations()` - keeps only N most recent
3. Update `save_context()` to call `SessionContext.save_to_json()`
4. Update `load_context()` to call `SessionContext.load_from_json()`
5. Add backward compatibility: detect old text format, auto-convert

### Phase 2: Dual-Text Saving
File: `src/second_voice/modes/menu_mode.py`

1. Capture transcription (raw_text)
2. Process with LLM (processed_text)
3. Call `processor.add_iteration(raw_text, processed_text)`
4. This automatically updates session context and saves JSON

### Phase 3: Updated System Prompt
File: `src/second_voice/core/processor.py`

1. Update `_build_system_prompt()` or `process_text()` to include both raw + processed from context
2. Show evolution in prompt when multiple iterations exist
3. Guide LLM to use both texts for better understanding

### Phase 4: Evolution Display
File: `src/second_voice/modes/menu_mode.py`

1. Menu option 2 ("Show context") checks for `--show-evolution` flag
2. If set, use `SessionContext.format_evolution_display()` → pretty table with raw | processed
3. Shows iteration count, timestamps, condensation ratio

### Phase 5: Size Management
File: `src/second_voice/core/processor.py`

1. Add config: `max_iterations` (default: 5)
2. Add config: `max_context_size_kb` (default: 50)
3. `SessionContext.prune_old_iterations()` removes oldest when limits exceeded
4. Keep track of what was pruned for user awareness

---

## Success Criteria

### User Perspective
- [ ] User records iteration 1: raw speech is captured and processed
- [ ] User records iteration 2: LLM has access to both raw and processed from iteration 1
- [ ] User records iteration 3: LLM has access to all previous raw and processed texts
- [ ] Running with `--show-evolution` shows a table of iterations with raw vs. processed
- [ ] Over multiple iterations, LLM provides increasingly intelligent refinements
- [ ] User can see how their raw speech improves over iterations

### Developer Perspective
- [ ] `IterationContext` class exists with proper fields
- [ ] `SessionContext` class manages multiple iterations
- [ ] JSON context file format is used (with backward compatibility)
- [ ] `format_for_prompt()` builds proper context string for LLM
- [ ] System prompt updated to reference both raw and processed texts
- [ ] Size limits (`max_iterations`, `max_context_size_kb`) are enforced
- [ ] Old plain-text format is detected and auto-converted

### Quality Gates
- [ ] No breaking changes to existing menu mode
- [ ] Existing tests pass
- [ ] JSON context file is properly formatted and loadable
- [ ] Auto-conversion from old text format works correctly
- [ ] Evolution display is readable and informative
- [ ] LLM receives correct dual-text context

---

## Design Decisions

### Why JSON Instead of Structured Text?
- **Queryable:** Can extract specific iterations, filter by timestamp
- **Extensible:** Easy to add new fields (user_notes, tags, metadata)
- **Parsing:** Libraries handle it; no custom parsing needed
- **Backward Compatibility:** Old text format still works via auto-conversion

### Why Keep Max Iterations vs. Max Size?
- **Max Iterations:** User-friendly ("keep last 5 recordings")
- **Max Size:** Safety limit ("don't exceed 50KB context")
- Both together: users control, system has safety valve

### Why Not Archive Pruned Iterations?
- Out of scope for this spec
- Could be future feature: save old iterations to `archive-context.json`
- Simpler implementation: just discard old iterations

---

## Integration with Other Specifications

### Prerequisite for: Collaborative Refinement Session (Future Spec)
Dual-text looping is a foundation for collaborative refinement. That spec would build on this one.

### Works With: Redundancy Removal (Spec 2026-02-09_redundancy-removal-consolidation.md)
```
The system can now see:
- Raw version of iteration 1: "we need fast we need speed we need to be quick"
- Processed version: "We need good performance"
- LLM can recognize "fast", "speed", "quick" were deduplicated in iteration 1
- Better informed deduplication in iteration 2
```

### Works With: Two-Pane Interactive UI (Future Spec)
Two-pane UI would display raw text in one pane, processed in other, and show evolution.

---

## Data Migration Notes

### Converting Old Context Format

Old format (plain text):
```
We need to improve performance because users report slow performance.
```

New format (JSON):
```json
{
  "current_iteration": 1,
  "sessions": [
    {
      "iteration": 1,
      "timestamp": "2026-02-09T12:00:00Z",
      "raw_text": "We need to improve performance because users report slow performance.",
      "processed_text": "We need to improve performance because users report slow performance.",
      "user_notes": null
    }
  ]
}
```

Note: When converting, raw_text = processed_text (we don't have the original raw), and we estimate timestamp.

---

## Future Enhancements (Out of Scope)

1. **Evolution Visualization** - Timeline view of how ideas changed across iterations
2. **Iteration Archiving** - Save pruned iterations to separate archive file
3. **User Notes** - Allow user to add notes to each iteration ("I refined this idea here")
4. **Diff Highlighting** - Show what changed between iterations in editor
5. **Branching Sessions** - Fork context at an iteration and explore different directions
6. **Full History Export** - Export complete session with all iterations as structured document

---

## References

### Related Documents
- `docs/current-capabilities.md` - Current feature inventory (section "Recursive Context Feature")
- `docs/architecture.md` - System architecture (section "Recursive Context Feature")
- `2026-02-09_collaborative-refinement-session.md` - Future spec that builds on this

### Code References
- `src/second_voice/core/processor.py:save_context()` (L615-629)
- `src/second_voice/core/processor.py:load_context()` (L631-644)
- `src/second_voice/modes/menu_mode.py:_display_menu()` (L110-119) - Would add evolution option
- `src/second_voice/modes/menu_mode.py` (L359-365) - Show context menu option

### Dependencies
- `json` (stdlib) - Context serialization
- `dataclasses` (stdlib) - IterationContext structure
- `datetime` (stdlib) - Timestamps
