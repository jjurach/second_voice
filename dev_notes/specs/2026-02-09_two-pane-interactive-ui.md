# Specification: Two-Pane Interactive Interface

**Source:** dev_notes/inbox/second-voice-enhancements.md
**Status:** 🔵 Ready for Review
**Priority:** MEDIUM
**Timestamp:** 2026-02-09_17-00-00

---

## Overview

Implement a split-pane interface where the top pane displays target text (the refined/cooked output) and the bottom pane provides real-time chat interaction with the LLM. Users can edit the top pane while simultaneously asking the LLM for guidance or refinements in the bottom pane, enabling true collaborative authoring.

**Use Case:** User speaks, text appears in top pane. User sees an error or wants to improve something. Instead of closing the editor, they type in the bottom pane: "make this section more concise" or "add bullet points". The LLM responds in the chat area with suggestions or directly updates the top pane. Iterative refinement happens in real-time, without context switching.

---

## Problem Statement

Current workflow has friction points:

1. **Sequential Process:** Record → Transcribe → Process → Edit → Loop
   - Each step is blocking; must complete before next starts
   - Editor blocks LLM communication (single-threaded flow)

2. **No Real-Time Collaboration:** Editor and LLM don't talk
   - User edits top pane, but cannot ask LLM questions
   - User wants to ask "Is this grammar correct?" without exiting editor
   - Requires full exit-edit-reopen cycle for each LLM query

3. **Context Loss:** Switching between editor and CLI loses focus
   - User edits in one tool, must return to CLI for LLM interaction
   - Decisions made in editor aren't reflected back to LLM

4. **Not True "Two-Text-Area":** Current system has:
   - One editor window (inline or external via $EDITOR)
   - One LLM processing step
   - Not simultaneous or side-by-side

**Impact:** Users cannot have a fluid, interactive conversation while editing. The workflow feels disjointed instead of collaborative.

---

## Core Requirements

### FR-1: Split-Pane Interface Layout
```
┌─────────────────────────────────────────────────────────┐
│                   SECOND VOICE                          │
├──────────────── TARGET TEXT (Top Pane) ───────────────┤
│                                                         │
│  # My Document                                          │
│  Here is the text I've refined so far.                 │
│  The user can edit this directly.                       │
│                                                         │
│  [editable area - cursor active]                        │
│                                                         │
├──────────────── CHAT AREA (Bottom Pane) ─────────────┤
│                                                         │
│  Asst: I can help refine this. What would you like?   │
│  User: Make the first section more concise             │
│  Asst: Here's a shorter version:                       │
│         "The text has been refined." [APPLY] [DISCARD] │
│                                                         │
│  User Input: [________________] [SEND]                 │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

### FR-2: Top Pane - Target Text Editor
- Displays current refined/cooked text
- Fully editable by user (manual text entry)
- Text can be modified while chat is happening
- Changes are NOT automatically sent to LLM
- User can explicitly request "refine this" via chat

### FR-3: Bottom Pane - LLM Chat Interface
- Shows conversation history (Asst: / User: format)
- User types queries without leaving UI
- Queries can request:
  - "Make this more concise"
  - "Fix grammar here"
  - "Add more details to X section"
  - "Transform into bullet points"
- LLM responds with suggestions or modified text
- Responses can include `[APPLY]` and `[DISCARD]` buttons for suggested changes

### FR-4: Bi-Directional Flow
- User edits top pane → can ask LLM about edits via chat
- User writes in chat → LLM suggestions update to top pane
- Both panes are active simultaneously (not blocking)

### FR-5: Chat Commands
Special commands for LLM interaction:
```
/refine [text]   - Ask LLM to refine selected text
/grammar         - Check grammar of current text
/expand          - Ask for more details on a section
/condense        - Make text shorter
/format [style]  - Change formatting (bullets, headers, etc.)
/help            - Show available commands
/done            - Finalize and exit interactive mode
```

### FR-6: Non-Blocking Architecture
- Recording can happen while chat is active (new feature)
- LLM processing happens in background while user types
- UI remains responsive during API calls
- No "waiting for LLM..." blocking

### FR-7: Context Management
- Top pane content is the current context
- User edits in top pane automatically update what LLM sees
- Chat history is preserved during session
- On exit, final top pane content is saved as context

### FR-8: Multiple UI Backends
Specify which UI technology to use:
- **TUI (ncurses-based):** Terminal, SSH-friendly, keyboard-native
- **GUI (Tkinter):** GUI windows, mouse-friendly
- **Web (Flask + WebUI):** Browser-based, cross-platform, future option

### FR-9: Graceful Degradation
If interactive mode not available (e.g., no ncurses):
- Fall back to existing menu mode
- Or: Offer to launch in external editor instead
- No crashes, clear error messages

---

## Architecture

### Component: InteractiveMode Class
New mode extending `BaseMode`:

```python
class InteractiveMode(BaseMode):
    """Two-pane interactive interface for collaborative refinement."""

    def __init__(self, config, recorder, processor, ui_type='tui'):
        super().__init__(config, recorder, processor)
        self.ui_type = ui_type  # 'tui', 'gui', or 'web'
        self.ui = self._create_ui()
        self.top_pane_text = ""
        self.chat_history = []

    def _create_ui(self):
        """Factory for UI backend (TUI, GUI, Web)."""
        if self.ui_type == 'tui':
            return TUIInteractiveUI(...)
        elif self.ui_type == 'gui':
            return GUIInteractiveUI(...)
        else:
            raise ValueError(f"Unknown UI type: {self.ui_type}")

    def record_and_transcribe(self) -> str:
        """Record audio in background, return transcription."""
        # Non-blocking recording via threading

    def handle_chat_input(self, user_input: str) -> str:
        """Process user chat input, get LLM response."""
        # Parse commands (/refine, /grammar, etc.)
        # Send to LLM via processor
        # Return response text

    def apply_suggestion(self, suggested_text: str):
        """Apply LLM suggestion to top pane."""
        self.top_pane_text = suggested_text
        self.ui.update_top_pane(suggested_text)

    def run(self):
        """Main interactive loop."""
        # Initialize UI with top/bottom panes
        # Show initial text (from previous context)
        # Main loop:
        #   - Wait for user input (top pane edit or bottom pane chat)
        #   - Process accordingly
        #   - Update UI
        # On exit: save top pane text to context
```

### UI Backends

**TUI Backend (ncurses):**
- Top pane: editable text area (vim-like or nano-like)
- Bottom pane: chat history + input line
- Tab key to switch focus between panes
- Keyboard-native (no mouse required)
- SSH-friendly, no X11 needed

**GUI Backend (Tkinter):**
- Top pane: tk.Text widget with syntax highlighting
- Bottom pane: tk.Text (read-only) + tk.Entry for input
- Mouse support for clicking buttons
- Better for desktop use
- DISPLAY required

**Web Backend (Future):**
- Flask server with WebUI
- Browser-based interface
- No local dependencies beyond Python
- Future enhancement, out of scope for this spec

### Files to Create/Modify

**New Files:**
1. `src/second_voice/modes/interactive_mode.py` - InteractiveMode class
2. `src/second_voice/ui/base_ui.py` - BaseUI abstract class
3. `src/second_voice/ui/tui_interactive_ui.py` - TUI implementation
4. `src/second_voice/ui/gui_interactive_ui.py` - GUI implementation (optional for MVP)

**Modified Files:**
1. `src/cli/run.py` - Add `--interactive` flag, UI type selection
2. `src/second_voice/modes/__init__.py` - Register InteractiveMode
3. `src/second_voice/core/processor.py` - Add chat-specific methods

### Data Flow

```
User launches: second_voice --interactive --ui tui

1. Initialize InteractiveMode with TUI backend
2. Load previous context (top pane)
3. Show two-pane interface

Main Loop:
  ┌─ User Types in Top Pane
  │  └─ Text updates in real-time
  │
  ├─ User Presses Tab → Focus shifts to Bottom Pane
  │
  └─ User Types in Chat, Presses Enter
     ├─ Parse: is it a command (/refine) or chat?
     ├─ Send to LLM via processor
     ├─ LLM responds with suggestion or modification
     ├─ Show response in bottom pane
     ├─ If suggestion includes [APPLY]:
     │  └─ User presses/types APPLY
     │     └─ Top pane updates with suggestion
     └─ Back to input for next chat message

On Exit (/done or Ctrl+C):
  └─ Save top pane text as new context
```

---

## Implementation Approach

### Phase 1: Abstract UI Base & Data Structures
1. Create `src/second_voice/ui/base_ui.py`:
   - `BaseUI` abstract class
   - `ChatMessage` dataclass (role, content, timestamp)
   - `UIEvent` dataclass (type, payload)

2. Create `src/second_voice/modes/interactive_mode.py`:
   - `InteractiveMode` class extending `BaseMode`
   - Core logic for chat handling, context management
   - Abstract UI creation

### Phase 2: TUI Implementation (MVP)
1. Create `src/second_voice/ui/tui_interactive_ui.py`:
   - Use `rich` library (already in dependencies)
   - Two panels using `rich.layout.Layout`
   - Top panel: editable text (or manual input area)
   - Bottom panel: chat history + input

2. Implement:
   - `show()` - render UI
   - `get_top_pane_text()` - get edited content
   - `set_top_pane_text()` - update top pane
   - `add_chat_message()` - append to chat
   - `get_user_input()` - blocking read of chat input

### Phase 3: CLI Integration
1. Update `src/cli/run.py`:
   - Add `--interactive` flag
   - Add `--ui {tui,gui,web}` option
   - Route to `InteractiveMode` if flag set

2. Update `src/second_voice/modes/__init__.py`:
   - Import `InteractiveMode`
   - Add to mode factory

### Phase 4: Chat Command Processing
1. Implement in `InteractiveMode`:
   - `parse_command(user_input)` - detect /command or natural language
   - `handle_command(command, args)` - execute /refine, /grammar, etc.
   - `handle_chat(message)` - send natural language to LLM

2. Update `processor.py` if needed for new processing modes

### Phase 5: Testing (for future agents)
- Test TUI rendering with various window sizes
- Test chat input parsing and command execution
- Test top pane editing and updates
- Test LLM response suggestions and apply/discard buttons
- Test context saving on exit
- Test graceful degradation if ncurses unavailable

---

## Success Criteria

### User Perspective
- [ ] User can launch: `second_voice --interactive --ui tui`
- [ ] Interface shows two panes: text editor (top) and chat (bottom)
- [ ] User can type in top pane and see live updates
- [ ] User can press Tab to move to bottom pane
- [ ] User can type `/refine Make this more concise` and LLM responds
- [ ] LLM suggestions appear as `[APPLY] [DISCARD]` buttons/options
- [ ] User can press `/done` or Ctrl+C to exit and save content

### Developer Perspective
- [ ] `InteractiveMode` class implemented extending `BaseMode`
- [ ] `BaseUI` abstract class defined
- [ ] `TUIInteractiveUI` implemented using `rich`
- [ ] Chat message parsing and command detection works
- [ ] LLM integration for chat queries functional
- [ ] Context saving on exit works correctly
- [ ] CLI flags `--interactive` and `--ui` parsed correctly

### Quality Gates
- [ ] No breaking changes to existing modes
- [ ] Existing tests pass
- [ ] TUI renders correctly in standard terminal sizes
- [ ] Chat commands execute without errors
- [ ] LLM responses appear in chat without blocking UI

---

## Design Decisions

### Why TUI First (not GUI)?
- SSH-friendly (works over remote connections)
- Lighter dependencies (rich already used)
- Faster iteration
- GUI (Tkinter) can be added later

### Why Rich Library for TUI?
- Already in codebase (used in tui_mode.py)
- Excellent for layouts and styling
- Good documentation
- Simpler than raw ncurses

### Why Non-Blocking Architecture?
- Recording while chatting is a future enhancement
- Responsive UI while LLM processes is critical
- Threading needed for background LLM calls

### Why Chat Commands (/refine, /grammar)?
- Structured way for users to request specific transformations
- LLM can specialize responses based on command
- Natural language fallback still supported
- Easier to parse and handle programmatically

---

## Integration with Other Specifications

### Builds On: Dual-Text Looping (Spec 2026-02-09_dual-text-looping-editor.md)
- Dual-text feature provides richer context for chat-based refinements
- Top pane shows processed text, chat can reference raw text from context

### Works With: Collaborative Refinement Session (Future Spec)
- Interactive mode IS collaborative refinement session
- Could be same thing with different naming

### Future Enhancement: Redundancy Removal
- Chat command: `/consolidate` - asks LLM to remove repetitions from top pane
- Works seamlessly with redundancy removal spec

---

## Limitations & Future Work

### MVP Scope (This Spec)
- ✅ Top/bottom panes side-by-side
- ✅ Text editing in top pane
- ✅ Chat interface in bottom pane
- ✅ Basic commands (/refine, /grammar, etc.)
- ✅ TUI implementation using rich
- ✅ Chat history display

### Out of Scope (Future Specs)
- ❌ GUI implementation (Tkinter) - future phase
- ❌ Web implementation (Flask) - future phase
- ❌ Recording while chatting - needs architecture redesign
- ❌ Syntax highlighting in top pane - future enhancement
- ❌ Voice commands in chat - needs audio+text mixing
- ❌ Collaborative multi-user (shared editing) - far future

---

## References

### Related Documents
- `docs/current-capabilities.md` - Current feature inventory
- `docs/architecture.md` - System architecture
- `2026-02-09_dual-text-looping-editor.md` - Dual-text foundation
- `2026-02-09_collaborative-refinement-session.md` - Refinement context

### Dependencies
- `rich` (already required for TUI mode)
- `threading` (stdlib) - for non-blocking architecture
- No new external dependencies for MVP

### Code References
- `src/second_voice/modes/base.py` - BaseMode abstract class
- `src/second_voice/modes/tui_mode.py` - Example TUI implementation
- `src/second_voice/core/processor.py` - LLM processing integration
