# Specification: Cloud Code Integration (Ctrl+G Trigger)

**Source:** dev_notes/inbox/second-voice-enhancements.md
**Status:** 🔵 Ready for Review (Research Required)
**Priority:** LOW
**Timestamp:** 2026-02-09_17-00-00

---

## Overview

Enable users to trigger second-voice from within Claude Code (Cloud IDE) using a keyboard shortcut (Ctrl+G). User presses Ctrl+G in Claude Code, speaks, second-voice processes the input, and the result appears in the Claude Code buffer for review and integration. This bridges voice-based note-taking with cloud-based IDE development.

**Use Case:** Developer is coding in Claude Code. They want to add a comment or docstring by voice. Press Ctrl+G, speak the comment, second-voice structures it, and it appears ready-to-insert in the editor. No context switching, no external tools.

---

## Problem Statement

Currently, second-voice is standalone CLI:

1. **Manual Invocation:** User must leave IDE, open terminal, run `second_voice`
2. **Result Handling:** Output is in temp file or external editor, requires manual copy-paste
3. **No IDE Awareness:** System doesn't know what file/language context user is in
4. **Context Loss:** IDE context is lost during voice interaction
5. **Workflow Friction:** Speech → IDE requires multiple steps

**Impact:** Voice-based enhancement feels disconnected from coding workflow. Would require significant workflow change to be practical.

---

## Core Requirements

### FR-1: Ctrl+G Keyboard Shortcut
- User presses Ctrl+G in Claude Code editor
- Triggers second-voice in accessible way (modal, popup, or inline)
- No IDE restart or complex setup required

### FR-2: Voice Capture in IDE Context
- Recording happens without leaving IDE
- Optional: Show "recording..." indicator in IDE
- Optional: Show VU meter or audio level
- Ctrl+C or ESC to cancel recording

### FR-3: LLM Processing
- Transcription → LLM processing happens
- Optional: Can customize system prompt (e.g., "generate comment" vs. "generate docstring")
- Uses existing second-voice provider logic (Ollama, OpenRouter, etc.)

### FR-4: Result Return to Buffer
- Processed text appears in IDE buffer/selection
- At cursor position or replacing selection
- Ready for user to accept/edit/insert
- No manual copy-paste required

### FR-5: Mode Selection (Optional)
User can specify intent before speaking:
- `/comment` - Generate code comment
- `/docstring` - Generate docstring/documentation
- `/message` - Generate commit message
- `/note` - Generate note/todo
- Default: generic text processing

### FR-6: Integration Points (Research-Dependent)
Multiple possible approaches (see Architecture section):
- Option A: Cloud Code extension/plugin
- Option B: Shell script integration via keyboard macro
- Option C: External daemon listening for IDE signals
- Option D: HTTP webhook from IDE to second-voice

### FR-7: IDE Environment Detection
System should be aware of:
- Current file language (Python, JavaScript, etc.)
- Current file path
- Cursor position
- Selected text (if any)
- Can customize system prompt based on language

### FR-8: Configuration
New settings in `~/.config/second_voice/settings.json`:
```json
{
  "cloud_code": {
    "enabled": true,
    "shortcut": "ctrl+g",
    "mode": "auto",
    "auto_insert": true,
    "show_preview": true
  }
}
```

### FR-9: Graceful Fallback
If Cloud Code integration unavailable:
- Ctrl+G doesn't trigger anything (or shows helpful message)
- Standalone `second_voice` still works
- No errors or confusion

### FR-10: Platform Support
Specify which platforms are supported:
- macOS: probably via keyboard shortcut automation
- Linux: could use X11 window events or shell integration
- Windows: via keyboard hook or shell integration
- Status: Requires research to determine feasibility

---

## Problem: Research Required ⚠️

**This spec has a critical dependency: Cloud Code extension API availability.**

Key unknowns:
1. **Does Cloud Code have extension/plugin API?**
   - If yes: Can we hook into keyboard events?
   - If no: Must use indirect methods (shell scripts, daemons)

2. **IDE Integration Mechanism:**
   - Direct extension: Simplest if supported
   - Shell script: More fragile, platform-dependent
   - Daemon: Complex but flexible
   - HTTP webhook: Could work if IDE supports it

3. **Data Exchange:**
   - How to pass cursor position from IDE to second-voice?
   - How to return text to IDE buffer?
   - How to show preview or confirmation dialog?

4. **Platform-Specific Challenges:**
   - macOS: Keyboard shortcut automation vs. extension API
   - Linux: X11 window events vs. shell integration
   - Windows: Keyboard hooks vs. shell integration

**Recommendation:** This spec should be preceded by a **research spike** to determine feasibility.

---

## Architecture (Conditional on Research)

### Approach A: Cloud Code Extension (If Supported)

**Assumptions:**
- Cloud Code has extension API similar to VS Code
- Extensions can register keyboard shortcuts
- Extensions can communicate with external processes

**Architecture:**
```
Cloud Code Extension (JavaScript/TypeScript)
  ↓
  On Ctrl+G:
    - Send signal to second-voice CLI daemon
    - Pass IDE context (file, position, selection)
    ↓
  second-voice daemon (Python)
    - Record audio
    - Transcribe + process
    - Return result
    ↓
  Cloud Code Extension
    - Receive result
    - Insert into buffer at cursor
    - Show accept/reject options
```

**Advantages:**
- Native IDE integration
- Can pass rich context (language, file, position)
- Responsive and reliable

**Disadvantages:**
- Requires extension development (new language/toolchain)
- Requires Cloud Code to support extensions
- Maintenance burden if Cloud Code changes APIs

### Approach B: Shell Script + Keyboard Macro (If No Extension API)

**Assumptions:**
- Can invoke shell script via keyboard shortcut
- Script can communicate with second-voice
- Script can use xdotool or similar to manipulate IDE

**Architecture:**
```
Keyboard shortcut (e.g., Ctrl+G)
  ↓
  Shell script: `~/.config/second_voice/ide-bridge.sh`
    - Show GUI modal or TUI for recording
    - Call second-voice CLI
    - Get result
    ↓
  xdotool or similar
    - Type result into IDE buffer at cursor
    ↓
  Result appears in IDE
```

**Advantages:**
- No Cloud Code extension needed
- Can use existing second-voice CLI
- Simpler to implement

**Disadvantages:**
- Platform-specific (xdotool on Linux, different on macOS/Windows)
- Less reliable (keyboard events can be fragile)
- Limited context awareness (doesn't know IDE context)
- Typing result into IDE is hackish (no rich text, encoding issues)

### Approach C: External Daemon + Clipboard (Fallback)

**Assumptions:**
- Can't hook IDE keyboard directly
- But can use clipboard for data exchange

**Architecture:**
```
User: Copy text to clipboard, press Ctrl+G
  ↓
  Daemon watches clipboard
    - Detects new content
    - Triggers second-voice
    ↓
  second-voice processes
    - Result goes to clipboard
    ↓
  User: Paste (Ctrl+V) to insert in IDE
```

**Advantages:**
- Works on all platforms (clipboard is universal)
- No IDE integration needed

**Disadvantages:**
- Requires manual copy → Ctrl+G → paste cycle
- Not seamless like direct integration
- Could overwrite important clipboard data

### Approach D: HTTP Webhook (If IDE Supports)

**Assumptions:**
- Cloud Code has webhook support
- Can trigger webhook on keyboard shortcut

**Architecture:**
```
Cloud Code Webhook
  ↓
  HTTP POST to: http://localhost:9999/transcribe
    {
      "action": "record_and_transcribe",
      "context": {
        "file": "script.py",
        "language": "python",
        "position": 142
      }
    }
  ↓
  Local second-voice daemon (HTTP server)
    - Record and transcribe
    - Return result as JSON
  ↓
  Cloud Code receives response
    - Inserts result in buffer
```

**Advantages:**
- No IDE extension needed
- Rich context and data exchange
- Can use existing second-voice logic

**Disadvantages:**
- Cloud Code must support webhooks
- Requires local HTTP daemon (new code)
- Network/security considerations

---

## Recommended Implementation Path

### Step 1: Research Spike (Blocking)
**Deliverable:** Document answering these questions:
1. Does Cloud Code have extension/plugin API?
2. Can extensions register keyboard shortcuts?
3. Can extensions invoke external processes or HTTP calls?
4. What are Cloud Code's security restrictions?
5. What platforms does Cloud Code support?

**Estimated Outcome:** 1-2 weeks research
**Result:** Choose implementation approach (A, B, C, or D)

### Step 2: Proof of Concept
Based on research result:
- If Approach A (extension): POC extension + integration
- If Approach B (shell script): POC shell script + keyboard setup
- If Approach C (clipboard): POC clipboard monitor
- If Approach D (HTTP): POC daemon + webhook

### Step 3: Full Implementation
Once POC validates approach:
- Build full integration
- Test on target platforms
- Document setup process

### Step 4: Documentation & Setup
- Installation guide for Ctrl+G keyboard shortcut
- Configuration guide
- Troubleshooting guide

---

## Files (Contingent on Research)

**If Extension Approach:**
- `cloud-code-extension/` (new directory with JavaScript/TypeScript)
  - `extension.js` - Main extension entry point
  - `package.json` - Extension metadata
  - Integration with second-voice CLI via child_process

**If Shell Script Approach:**
- `scripts/cloud-code-bridge.sh` - Keyboard shortcut handler
- `src/second_voice/daemon.py` - Optional daemon for always-on listening
- Configuration in `~/.config/second_voice/cloud-code-config`

**If Daemon Approach:**
- `src/second_voice/http_daemon.py` - HTTP server for IDE communication
- Routes: `/transcribe`, `/transcribe-and-process`, etc.
- Integration with recorder and processor

**Configuration:**
- Update `src/cli/run.py` - Add `--daemon` mode for HTTP server
- Update `~/.config/second_voice/settings.json` - Cloud Code settings

---

## Success Criteria (Conditional)

### Research Phase
- [ ] Documented Cloud Code API capabilities
- [ ] Evaluated all 4 approaches (A, B, C, D)
- [ ] Recommended best approach with rationale
- [ ] Identified any blockers or limitations

### Implementation Phase (Approach TBD)
- [ ] Ctrl+G triggers second-voice within IDE context
- [ ] User records and speaks
- [ ] Result appears in IDE buffer
- [ ] Works on macOS, Linux, Windows (if applicable)
- [ ] Configuration is straightforward

### Quality Gates
- [ ] No crashes or hangs when Ctrl+G triggered
- [ ] IDE remains responsive during recording/processing
- [ ] Results are correctly inserted without encoding issues
- [ ] Falls back gracefully if second-voice unavailable

---

## Design Decisions

### Why Ctrl+G?
- Mnemonic: "G" = "Generate" or "Grab voice"
- Relatively uncommon shortcut in most IDEs
- Easy to type, not modal

### Why Research-Dependent?
- Cloud Code API is unknown (not documented in spec source)
- Different approaches have very different implementation costs
- Want to avoid 50+ hours on unfeasible approach

### Why Low Priority?
- Useful but not core second-voice functionality
- Standalone CLI works fine
- IDE integration is nice-to-have, not must-have

---

## Integration with Other Specs

### Could Use: Structured Document Creation (Spec 2026-02-09_structured-document-creation.md)
```
User: Ctrl+G in IDE
System: "Generating docstring"
User: Speaks detailed documentation
System: Structures it into proper docstring format
Result: Ready-to-insert docstring appears in IDE
```

### Could Use: Redundancy Removal (Spec 2026-02-09_redundancy-removal-consolidation.md)
```
User: Ctrl+G to generate commit message
User: Speaks rambling explanation of changes
System: Consolidates into clean commit message
Result: Well-structured message for git commit
```

### Alternative: Two-Pane Interactive UI (Spec 2026-02-09_two-pane-interactive-ui.md)
- Could launch two-pane UI when Ctrl+G triggered
- Top pane shows draft, bottom pane for refinement chat
- Result returned to IDE buffer

---

## Deferred / Out of Scope

1. **Collaborative Development:** Multiple users in IDE → Out of scope
2. **Real-Time Voice Transcription:** Showing transcript as user speaks → Out of scope
3. **Custom Shortcuts:** User-configurable keyboard binding → Future (can be in settings)
4. **Language-Specific Prompts:** Python docstring vs. JavaScript JSDoc → Future enhancement
5. **IDE Theme Matching:** Modal/popup matches IDE appearance → Nice-to-have
6. **Cross-IDE Support:** VS Code, JetBrains, etc. → Out of scope (focused on Cloud Code)

---

## References

### Related Documents
- `docs/current-capabilities.md` - Current feature inventory
- `docs/architecture.md` - System architecture
- `2026-02-09_structured-document-creation.md` - Document generation
- `2026-02-09_two-pane-interactive-ui.md` - Interactive UI

### Research Topics
- Cloud Code (Google Cloud IDE) API documentation
- VS Code extension API (for comparison)
- Desktop automation tools (xdotool, pyautogui)
- HTTP daemon frameworks for Python (Flask, FastAPI)
- Keyboard event handling in Python (pynput, keyboard)

### Decision Precedent
- Approach A (extension) is most desirable but requires Cloud Code API support
- Approach B (shell script) is most portable but less elegant
- Approach C (clipboard) is fallback but requires manual steps
- Approach D (HTTP) is good middle ground if Cloud Code supports webhooks

---

## Next Steps

**BEFORE implementation:**

1. **Research spike:** Investigate Cloud Code extension capabilities (2 weeks)
2. **Decision:** Choose implementation approach (A, B, C, or D) based on findings
3. **Spike-to-Spec:** Update this spec with approach-specific details after research
4. **POC:** Build proof of concept to validate approach
5. **Full Spec:** Update this spec with final implementation plan
6. **Implementation:** Build full integration based on chosen approach

**AFTER implementation:**

1. Testing on macOS, Linux, Windows
2. User documentation and setup guide
3. Troubleshooting guide
4. Integration tests with Cloud Code

---

## Appendix: Initial Research Questions

These should be answered during research spike:

### Cloud Code Capability Questions
- [ ] Does Cloud Code support extensions/plugins?
- [ ] If yes, what's the extension API? (Like VS Code, or custom?)
- [ ] Can extensions register keyboard shortcuts?
- [ ] Can extensions execute arbitrary commands or only IDE operations?
- [ ] Does Cloud Code support webhooks or HTTP callbacks?
- [ ] Can extensions access clipboard?
- [ ] Security model: What restrictions on extensions?

### IDE Context Questions
- [ ] Can extension know: Current file path?
- [ ] Can extension know: Current language/file type?
- [ ] Can extension know: Cursor position?
- [ ] Can extension know: Selected text?
- [ ] Can extension insert text at cursor?
- [ ] Can extension replace selection?

### Platform Questions
- [ ] Does Cloud Code run natively on macOS, Linux, Windows?
- [ ] Or is it browser-based?
- [ ] If browser-based, how are keyboard shortcuts configured?
- [ ] Can localhost services be accessed from Cloud Code?

### Security Questions
- [ ] Can extensions invoke shell commands?
- [ ] Can extensions make HTTP requests to localhost?
- [ ] Are there sandboxing restrictions?
- [ ] How are extension permissions managed?

