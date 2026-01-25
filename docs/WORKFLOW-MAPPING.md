# Workflow Mapping: AGENTS.md for All Tools

This document maps the core AGENTS.md workflow to each supported tool, showing how the mandatory steps translate to tool-specific actions.

## Core Workflow (AGENTS.md)

```
Step A: Analyze & Declare Intent
  ↓
Step B: Create Spec File (if needed)
  ↓
Step C: Create Project Plan (if non-trivial)
  ↓
Step D: AWAIT EXPLICIT APPROVAL
  ↓
Step E: Implement & Document Concurrently
  ↓
DONE: All verification requirements met
```

This workflow is **tool-agnostic**. The steps below show how each tool implements it.

---

## Step-by-Step Mapping

### Step A: Analyze the Request & Declare Intent

**Universal:**
Read the user request and categorize:
1. Simple question? → Answer directly
2. Trivial change? → Make it directly
3. Just fix tests? → Fix directly
4. Research/docs? → Change directly
5. Anything else? → Create plan

**Claude Code:**
```
Use judgment to categorize.
If plan needed, announce: "I will create a Project Plan"
Proceed to Step B.
```

**Aider:**
```
Respond conversationally about what you understand.
Clarify scope with user if needed.
Same categorization applies.
```

**Gemini/Codex:**
```
Same as Claude Code (until tool-specific guidance available)
```

---

### Step B: Create Spec File

**Universal Requirement:**
- File: `dev_notes/specs/YYYY-MM-DD_HH-MM-SS_spec-description.md`
- Contains: User intentions, goals, acceptance criteria
- Updates: If processing existing spec, update with new context

**Claude Code:**
```python
# In code (via Write tool):
ts = datetime.now().isoformat()
path = f"dev_notes/specs/{ts[:19].replace(':', '-')}_spec-description.md"
Write(file_path=path, content=spec_content)
```

**Aider:**
```bash
# Type directly or ask Aider to create:
"Create dev_notes/specs/YYYY-MM-DD_HH-MM-SS_spec-description.md
with the following content..."
```

**Gemini/Codex:**
```
Same as Claude Code (use function calling to create file)
```

---

### Step C: Create Project Plan

**Universal Requirement:**
- File: `dev_notes/project_plans/YYYY-MM-DD_HH-MM-SS_description.md`
- Contains: Step-by-step implementation plan
- Detail: Enough for another agent to execute

**Claude Code:**
```
Use Write tool to create plan file.
Use ExitPlanMode tool to signal ready for approval.
```

**Aider:**
```
Create plan file directly in conversation.
Summarize plan and ask user: "Should I proceed with this approach?"
Wait for user confirmation before executing.
```

**Gemini/Codex:**
```
Same as Claude Code (create file via function call)
```

---

### Step D: AWAIT EXPLICIT APPROVAL ⚠️ CRITICAL DIFFERENCE

This is where tools diverge most.

**Claude Code:**
```
Use ExitPlanMode() to formally request approval.
BLOCK all execution until user responds with "yes", "approved",
"proceed", "ok", or "go ahead".

If response is ambiguous ("maybe", "probably"):
  Ask clarification: "Confirm: should I proceed? Yes/No"

NEVER execute without explicit approval.
```

**Aider:**
```
❌ Aider has NO approval gates.
   Changes apply immediately.

⚠️ ADAPTATION:
   Aider users should:
   1. Frame work as collaborative guidance
   2. Use smaller tasks (reversible via git)
   3. Ask for confirmation conversationally
   4. Trust that git allows undo
   5. Update dev_notes manually if needed

Example:
  "I'll make these three changes:
   1. Create test_feature.py
   2. Update config.py
   3. Run tests

   Should I proceed?"

  User says "yes" → changes apply immediately
  User says "no" → don't make changes
```

**Gemini/Codex:**
```
❓ UNKNOWN approval model
   Assume similar to Claude Code until testing shows otherwise.
   May differ - see TOOL-SPECIFIC-GUIDES/gemini.md when available.
```

---

### Step E: Implement & Document Concurrently

**Universal Requirement:**
- Execute plan step-by-step
- After each logical change, create/update change documentation
- File: `dev_notes/changes/YYYY-MM-DD_HH-MM-SS_description.md`
- Contents: What changed, why, how to verify

**Claude Code:**
```
1. Execute step from plan
2. Create or update change doc
3. Verify step works
4. Repeat for next step

All while communicating progress to user.
```

**Aider:**
```
1. Execute step (changes apply immediately)
2. Create/update change doc
3. Verify step works
4. Repeat for next step

Same pattern, just faster iteration.
```

**Gemini/Codex:**
```
Same as Claude Code
```

---

### Final: Verification & Completion

**Universal Requirements:**
All must satisfy DEFINITION-OF-DONE.md:
- [ ] Tests pass
- [ ] Code follows patterns
- [ ] No secrets in commits
- [ ] Documentation updated
- [ ] Changes committed
- [ ] Plan status updated

**Claude Code:**
```
Verify all criteria met.
TaskUpdate each task to "completed".
Commit changes.
```

**Aider:**
```
Verify all criteria met.
Update dev_notes/changes/ and dev_notes/project_plans/
Commit changes (auto via Aider).
```

**Gemini/Codex:**
```
Verify all criteria met.
Commit changes.
```

---

## Detailed Tool-Specific Workflows

### Claude Code Complete Workflow

```
User provides request
↓
Tool: Analyze (read request, determine category)
Tool: Declare intent (announce if plan needed)
↓
IF non-trivial AND not tests/docs/fix:
  Tool: Write → Create spec file in dev_notes/specs/
  Tool: Write → Create plan file in dev_notes/project_plans/
  Tool: ExitPlanMode → Request explicit approval
  User: Responds with "yes" or asks questions
  IF questions: Answer them, return to "request approval"
  IF "yes": Proceed to implementation
↓
Step through plan:
  Tool: Bash/Read/Write/Edit as needed
  Tool: Write → Update change documentation
  Tool: Bash → Commit changes
  Tool: Bash → Run tests
↓
Verification:
  Tool: Bash → Run full test suite
  Tool: Read → Verify all DEFINITION_OF_DONE criteria
  Tool: TaskUpdate → Mark task complete
  Tool: Bash → Final git commit with summary
```

### Aider Complete Workflow

```
User provides request
↓
Conversational: Analyze and clarify scope
Conversational: Declare intent and approach
↓
IF non-trivial:
  Chat: Create spec file (type content)
  Chat: Create plan file (type content)
  Chat: Show plan and ask "Proceed?"
  User: Yes/No
  IF No: Stop or revise plan
  IF Yes: Proceed to implementation
↓
Step through plan:
  Code: Make changes (apply immediately)
  Chat: Update change documentation
  Shell: Run tests
  Conversational: Show progress
↓
Verification:
  Shell: Run full test suite
  Chat: Summarize what was done
  Chat: Show what to commit (if not auto)
  Shell: git commit (automatic or manual)
```

### Gemini Complete Workflow

```
❓ TBD - Update when tool support is added
```

---

## Key Differences by Tool

### Approval Gates

| Tool | Approval Model | Implementation |
|------|---|---|
| **Claude** | Explicit mandatory | ExitPlanMode blocks execution |
| **Aider** | Implicit/conversational | Ask before proceeding, trust user response |
| **Gemini** | Unknown | TBD |

### File Creation

| Tool | Method | Implementation |
|------|---|---|
| **Claude** | Write tool | `Write(file_path=..., content=...)` |
| **Aider** | Direct editing | Type or ask to create file |
| **Gemini** | Function call | Via file creation function |

### Git Commits

| Tool | Method | When |
|------|---|---|
| **Claude** | Bash (manual) | User decides when to commit |
| **Aider** | Automatic | After each significant change |
| **Gemini** | TBD | TBD |

### Change Documentation

| Tool | Responsibility | Timing |
|------|---|---|
| **Claude** | Agent creates files | After each step |
| **Aider** | Agent creates or updates | After each step |
| **Gemini** | Agent creates files | After each step |

### Task Tracking

| Tool | Capability | Implementation |
|------|---|---|
| **Claude** | TaskCreate/TaskUpdate | `TaskCreate()` and `TaskUpdate()` |
| **Aider** | Manual in dev_notes | Update files directly |
| **Gemini** | Unknown | TBD |

---

## Conditional Logic for Multi-Tool Support

If building a system that detects which tool is running:

```python
def get_approval_workflow():
    if tool == "claude-code":
        return "explicit_with_exitplanmode"
    elif tool == "aider":
        return "implicit_conversational"
    elif tool == "gemini":
        return "unknown_assume_explicit"
    else:
        return "unknown_ask_user"

def should_create_plan(request):
    # Same for all tools
    return not (is_simple_question(request) or
                is_trivial_change(request) or
                is_test_fix(request) or
                is_docs_change(request))

def get_approval_prompt():
    if tool == "claude-code":
        return "Use ExitPlanMode(). Wait for explicit approval."
    elif tool == "aider":
        return "Ask user: 'Should I proceed?' and wait for response."
    else:
        return "Ask user: 'Shall I implement this plan?'"
```

---

## File Naming Convention

**Universal (all tools):**
```
YYYY-MM-DD_HH-MM-SS_description.md

Examples:
  2026-01-25_18-46-25_add-tests-fix-pytest.md
  2026-01-25_13-30-00_implement-auth-system.md
```

How to generate:
```bash
# Claude Code
date -u +%Y-%m-%d_%H-%M-%S

# Aider
date "+%Y-%m-%d_%H-%M-%S"

# Shell (universal)
python3 -c "from datetime import datetime; print(datetime.now().strftime('%Y-%m-%d_%H-%M-%S'))"
```

---

## Summary: Key Takeaways

| Aspect | Claude | Aider | Gemini | Note |
|--------|--------|-------|--------|------|
| **Read AGENTS.md** | ✅ Fully | ⚠️ With adaption | ⚠️ With adaption | Core is universal |
| **Step A-C** | ✅ Same | ✅ Same | ✅ Same | Categorize, spec, plan |
| **Step D** | ✅ ExitPlanMode | ⚠️ Conversational | ⚠️ TBD | Different approval |
| **Step E** | ✅ Same | ✅ Same | ✅ Same | Implement and document |
| **File naming** | ✅ Same | ✅ Same | ✅ Same | Timestamp format |
| **Commit pattern** | Manual | Auto | TBD | Different but compatible |

The **core workflow is the same for all tools**. The differences are in HOW each tool implements the steps, not WHAT the steps are.

---

## Using This Document

1. **For Claude Code users:** Read AGENTS.md directly, use CLAUDE.md entry point
2. **For Aider users:** Read AGENTS.md + this document's "Aider" sections
3. **For Gemini/Codex users:** Reference this document once tool-specific guides are ready
4. **For tool developers:** Use this as template for adding new tool support

Each tool section shows the minimum changes needed to adapt AGENTS.md to that tool's constraints.
