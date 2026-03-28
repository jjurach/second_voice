# Specification: Collaborative Refinement Session Mode

**Source:** dev_notes/inbox/second-voice-enhancements.md
**Status:** 🔵 Ready for Review
**Priority:** MEDIUM
**Timestamp:** 2026-02-09_17-00-00

---

## Overview

Formalize and enhance the iterative refinement loop into a dedicated "Collaborative Refinement Session" mode. This mode explicitly tracks iterations, shows text evolution, and facilitates multi-round conversations between user and LLM where user speaks → LLM structures → user reviews → user provides feedback → repeat.

**Use Case:** User initiates a brainstorming/authoring session. They speak their initial idea. The LLM structures it. They review, notice gaps, and speak again. The LLM refines further. After 3-4 rounds, they have a well-polished document. The session explicitly shows "Round 1", "Round 2", etc., making the collaborative nature visible.

---

## Problem Statement

Current menu loop implements collaboration implicitly:

1. **No Session Awareness:** Users don't know if they're in round 1 or round 5
2. **No Explicit Naming:** Menu mode is called "Menu", not "Collaborative Session"
3. **No Evolution Tracking:** Limited visibility into how text changed across rounds
4. **No Natural Break Points:** User must decide when session is "done"
5. **Limited Guidance:** No suggestions for "What should I refine?" or "Are you done?"

**Current Loop:**
```
Record → Transcribe → Process → Review → Loop
```

**Desired Loop:**
```
Start Session
  ↓
Round 1:
  Record → Transcribe → Structure → Review (user sees text)
  ↓
Round 2:
  Record feedback → Refine previous → Review (user sees evolution)
  ↓
[Continue until user says "Done"]
  ↓
Save Final Document
```

**Impact:** Users don't fully understand they're in a collaborative interaction. Session feels disjointed rather than intentional.

---

## Core Requirements

### FR-1: Session Initialization
User launches collaborative mode:
```bash
second_voice --collaborative
# or
second_voice --session-mode refine
```

System responds:
```
Starting Collaborative Refinement Session
Session ID: 2026-02-09_14-32-15_session-abc123

Round 1: Initial Capture
Speak your initial idea or content...
(when done, press Ctrl+C to process)
```

### FR-2: Round Tracking
Each iteration is explicitly numbered and tracked:
- Round 1: Initial idea/content capture
- Round 2+: Refinement/feedback rounds
- Display: `[Round 3/5]` or similar in UI
- Context shows: "You're in round N of session ABC123"

### FR-3: Explicit Processing vs. Review Phase
Two distinct phases per round:

**Phase A: Capture**
- User speaks their input
- System transcribes (shows raw text)

**Phase B: Structure & Review**
- System processes (shows processed text)
- Shows previous context if round > 1
- User reviews: "Yes, continue" or "I need to refine"

### FR-4: Round Progression Options
After each round, user sees:
```
─────────────────────────────────
ROUND 2 SUMMARY
─────────────────────────────────

Previous (Round 1):
"We need to improve performance..."

Current (Round 2):
"We need to improve performance and add caching..."

Consolidation: 20% reduction in repetition

Options:
[1] Continue refinement (Round 3)
[2] Accept and finalize
[3] Discard Round 2, go back to Round 1
[4] Start over with new session
[5] Save intermediate state and exit
```

### FR-5: Session Persistence
Sessions are saved with metadata:
```json
{
  "session_id": "2026-02-09_14-32-15_session-abc123",
  "created_at": "2026-02-09T14:32:15Z",
  "final_round": 4,
  "status": "completed",
  "rounds": [
    {
      "round_number": 1,
      "timestamp": "2026-02-09T14:32:15Z",
      "raw_text": "...",
      "processed_text": "...",
      "user_decision": "continue"
    },
    ...
  ],
  "final_output": "...",
  "tags": ["brainstorm", "feature-ideas"]
}
```

### FR-6: Session Resumption
User can resume incomplete sessions:
```bash
second_voice --resume-session 2026-02-09_14-32-15_session-abc123
```
System shows:
```
Resuming Session ABC123
Current status: Round 3 complete, ready for Round 4

Previous context:
[Shows text from previous rounds]

Continue refining? [Y/n]
```

### FR-7: Evolution Visualization
Display how text evolved across rounds:
```
Round 1: "um like we need to uh make it fast..."
Round 2: "We need to improve performance and add caching."
Round 3: "We need to improve performance. Solutions: 1) Caching 2) Optimization"
Round 4: "We need to improve performance. Key solutions: Implement caching, optimize queries"
```

User can see the refinement journey visually.

### FR-8: Session-Level Metadata
Track across entire session:
- Session ID (unique, timestamped)
- Created/modified timestamps
- Total rounds
- Tags/categories (optional, user-provided)
- Final status (completed, abandoned, paused)
- Associated output files

### FR-9: Smart Exit Handling
When user decides to exit:
```
Session ABC123 - Round 3 Complete

Options:
[1] Continue with Round 4
[2] Finalize (save as complete)
[3] Pause (resume later)
[4] Abandon (discard this session)

Your choice: [1-4]
```

### FR-10: Collaborative Cues
UI provides guidance at key points:
- "What aspects would you like to refine?" (after each round)
- "This looks complete. Ready to finalize?" (when text stabilizes)
- "You've been refining this idea for 4 rounds. Would you like one more pass?"
- "No changes detected in this round. Session seems complete."

---

## Architecture

### Component: CollaborativeRefinementMode Class
Extends `BaseMode`:

```python
class CollaborativeRefinementMode(BaseMode):
    """Collaborative refinement session with round tracking."""

    def __init__(self, config, recorder, processor):
        super().__init__(config, recorder, processor)
        self.session_id = self._generate_session_id()
        self.current_round = 0
        self.max_rounds = config.get('max_rounds', 10)
        self.rounds = []  # List of round data

    def _generate_session_id(self) -> str:
        """Generate unique session ID with timestamp."""
        timestamp = get_timestamp()
        random_suffix = generate_random_id(6)
        return f"{timestamp}_session-{random_suffix}"

    def start_session(self):
        """Initialize new session."""
        print(f"Starting Collaborative Refinement Session: {self.session_id}")
        self._show_round_banner(1)

    def capture_round(self) -> dict:
        """Run one round: capture, transcribe, process, review."""
        self.current_round += 1

        # Phase A: Capture
        audio_path = self.start_recording()
        raw_text = self.processor.transcribe(audio_path)

        # Phase B: Process
        previous_context = self._get_context_from_previous_rounds()
        processed_text = self.processor.process_with_headers_and_fallback(
            raw_text,
            context=previous_context
        )

        # Phase C: Review
        user_decision = self._show_round_summary(
            round_num=self.current_round,
            previous=previous_context,
            current=processed_text,
            raw=raw_text
        )

        # Store round data
        round_data = {
            'round_number': self.current_round,
            'timestamp': get_timestamp(),
            'raw_text': raw_text,
            'processed_text': processed_text,
            'user_decision': user_decision,
            'reduction_ratio': self._calculate_reduction(raw_text, processed_text)
        }
        self.rounds.append(round_data)

        return round_data

    def _show_round_summary(self, round_num, previous, current, raw) -> str:
        """Display round summary and get user decision."""
        print(f"\n─ ROUND {round_num} SUMMARY ─")
        if previous:
            print(f"\nPrevious:\n{previous[:200]}...")
        print(f"\nCurrent:\n{current}")
        print(f"\nOptions:")
        print("[1] Continue refinement")
        print("[2] Accept and finalize")
        print("[3] Discard this round")
        print("[4] Start over")
        print("[5] Exit and save")

        choice = input("Your choice [1-5]: ").strip()
        return {'choice': choice, 'raw_text': raw}

    def finalize_session(self) -> str:
        """Prepare final output and save session."""
        final_text = self.rounds[-1]['processed_text']

        # Save session to JSON
        session_data = {
            'session_id': self.session_id,
            'created_at': self.rounds[0]['timestamp'],
            'final_round': self.current_round,
            'status': 'completed',
            'rounds': self.rounds,
            'final_output': final_text
        }
        self._save_session(session_data)

        return final_text

    def run(self):
        """Main collaborative refinement loop."""
        self.start_session()

        while self.current_round < self.max_rounds:
            round_data = self.capture_round()

            # Process user decision
            choice = round_data['user_decision']['choice']
            if choice == '1':  # Continue
                continue
            elif choice == '2':  # Finalize
                final_output = self.finalize_session()
                self._save_output(final_output)
                print(f"Session {self.session_id} finalized.")
                break
            elif choice == '3':  # Discard
                self.rounds.pop()  # Remove last round
                self.current_round -= 1
                continue
            elif choice == '4':  # Start over
                self.rounds = []
                self.current_round = 0
                continue
            elif choice == '5':  # Exit
                self._save_session_state()  # For resumption
                print("Session paused. Resume later with --resume-session")
                break
```

### Files to Modify/Create

**New Files:**
1. `src/second_voice/modes/collaborative_refinement_mode.py` - Main mode class
2. `src/second_voice/session/session_manager.py` - Session persistence

**Modified Files:**
1. `src/cli/run.py` - Add `--collaborative`, `--resume-session` flags
2. `src/second_voice/modes/__init__.py` - Register new mode
3. `src/second_voice/utils/timestamp.py` - Add session ID generation

### Data Storage

Sessions stored as JSON in:
```
~/.config/second_voice/sessions/
  ├── 2026-02-09_14-32-15_session-abc123.json
  ├── 2026-02-09_13-00-00_session-def456.json
  └── ...
```

Example structure:
```json
{
  "session_id": "2026-02-09_14-32-15_session-abc123",
  "created_at": "2026-02-09T14:32:15Z",
  "final_round": 4,
  "status": "completed",
  "rounds": [
    {
      "round_number": 1,
      "timestamp": "2026-02-09T14:32:15Z",
      "raw_text": "um...",
      "processed_text": "We need...",
      "user_decision": "continue",
      "reduction_ratio": 0.35
    }
  ],
  "final_output": "complete text",
  "tags": []
}
```

---

## Implementation Approach

### Phase 1: CollaborativeRefinementMode Class
1. Create `src/second_voice/modes/collaborative_refinement_mode.py`
2. Implement core methods: `capture_round()`, `_show_round_summary()`, `finalize_session()`, `run()`
3. Extend `BaseMode` for compatibility

### Phase 2: Session Persistence
1. Create `src/second_voice/session/session_manager.py`
2. Implement: `save_session()`, `load_session()`, `list_sessions()`, `resume_session()`
3. Use JSON for storage

### Phase 3: CLI Integration
1. Update `src/cli/run.py`:
   - Add `--collaborative` flag
   - Add `--resume-session <id>` flag
   - Route to `CollaborativeRefinementMode`

2. Update `src/second_voice/modes/__init__.py`:
   - Import and register new mode

### Phase 4: Session Listing & Management
1. Add command: `second_voice --list-sessions` → show all past sessions
2. Add command: `second_voice --session-info <id>` → show session details
3. Add command: `second_voice --delete-session <id>` → remove session

### Phase 5: Testing (for future agents)
- Test session initialization with unique ID
- Test round capture and storage
- Test round navigation (continue, restart, discard)
- Test session finalization and JSON storage
- Test session resumption
- Test session listing
- Test evolution visualization

---

## Success Criteria

### User Perspective
- [ ] User can run: `second_voice --collaborative`
- [ ] System shows: "Round 1: Initial Capture"
- [ ] After speaking, system shows processed text
- [ ] User sees menu: "Continue / Accept / Discard / Start Over / Exit"
- [ ] After multiple rounds, user can finalize session
- [ ] Session appears in `--list-sessions` with summary
- [ ] User can resume incomplete session: `second_voice --resume-session abc123`

### Developer Perspective
- [ ] `CollaborativeRefinementMode` class implemented
- [ ] Round tracking and storage working
- [ ] Session persistence (JSON save/load) implemented
- [ ] CLI flags `--collaborative` and `--resume-session` parsed
- [ ] Session manager can list and resume sessions
- [ ] Round metadata includes all required fields

### Quality Gates
- [ ] No breaking changes to existing modes
- [ ] Existing tests pass
- [ ] Session JSON is well-formed
- [ ] Evolution visualization shows changes correctly
- [ ] Session resumption loads correct state

---

## Design Decisions

### Why Explicit Round Numbering?
- Users understand they're in a collaborative process
- Makes it clear when to stop (after round 4-5, many users feel satisfied)
- Helps debug if things go wrong ("what happened in round 2?")

### Why Session Persistence?
- Allows users to pause and resume later
- Creates audit trail of how ideas evolved
- Enables batch processing of multiple sessions
- Future: could analyze how ideas mature across rounds

### Why Optional Resumption vs. Automatic?
- Users may want to start fresh even if old session exists
- Resumption is opt-in via `--resume-session`, not automatic
- Prevents accidental mixing of old and new sessions

### Why JSON for Storage (not database)?
- Simple, human-readable
- No external dependencies
- Easy to backup, share, analyze
- Sufficient for expected volume (~10-100 sessions per user)

---

## Integration with Other Specifications

### Works With: Dual-Text Looping (Spec 2026-02-09_dual-text-looping-editor.md)
- Each round stores both raw and processed text
- Session shows evolution from raw → processed across rounds

### Works With: Redundancy Removal (Spec 2026-02-09_redundancy-removal-consolidation.md)
- Each round applies consolidation
- Session shows deduplication across rounds

### Similar To: Two-Pane Interactive UI (Spec 2026-02-09_two-pane-interactive-ui.md)
- Could integrate: two-pane UI launches within collaborative session
- Or: collaborative session uses two-pane for refinement interaction

---

## Limitations & Future Work

### MVP Scope (This Spec)
- ✅ Round-by-round iteration with tracking
- ✅ Session initialization and finalization
- ✅ Session persistence to JSON
- ✅ Session resumption
- ✅ Evolution visualization (text display)
- ✅ Round metadata and statistics

### Out of Scope (Future Enhancements)
- ❌ Session tagging and categorization
- ❌ Batch processing multiple sessions
- ❌ Analysis/insights on session evolution
- ❌ Sharing sessions with collaborators
- ❌ Session merging (combine ideas from multiple sessions)
- ❌ Visual timeline of rounds (web UI)

---

## References

### Related Documents
- `docs/current-capabilities.md` - Current feature inventory
- `docs/architecture.md` - System architecture
- `2026-02-09_dual-text-looping-editor.md` - Dual-text foundation
- `2026-02-09_two-pane-interactive-ui.md` - Interactive UI foundation

### Code References
- `src/second_voice/modes/base.py` - BaseMode abstract class
- `src/second_voice/modes/menu_mode.py` - Similar iterative loop (L174-387)
- `src/second_voice/utils/timestamp.py` - Timestamp utilities

### Dependencies
- `json` (stdlib) - Session storage
- `pathlib` (stdlib) - File management
- No new external dependencies
