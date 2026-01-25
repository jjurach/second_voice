# Project Plan: Agent Kernel Refactoring & Bootstrap Tool

**Status:** ⏳ Awaiting Approval

## Goal
Establish a reusable "Agent Kernel" structure in `docs/system-prompts/` to standardize agentic workflows across projects. Implement a `bootstrap.py` tool to manage the injection and maintenance of these standard files using a template-based approach with conflict detection.

## 1. Directory Structure (`docs/system-prompts/`)

We will create a new directory structure to house the "Kernel":

```
docs/system-prompts/
├── bootstrap.py                 # The manager script
├── principles/
│   └── definition-of-done.md    # Generic DoD (Verification, Plan vs Reality)
├── workflow/
│   └── core.md                  # The A-E Step Workflow (Analyze, Plan, etc.)
├── patterns/
│   └── prompt-patterns.md       # Generic prompt templates
└── languages/
    └── python/
        └── definition-of-done.md # Python-specific DoD (pytest, venv)
```

## 2. Refactoring Map

We will split existing monolithic documentation into composable generic and specific parts.

| Source File | Content | Destination File | Action |
|---|---|---|---|
| `AGENTS.md` | Steps A-E (The Workflow) | `docs/system-prompts/workflow/core.md` | Extract & Generalize |
| `docs/definition-of-done.md` | Universal Rules (Proof of Work) | `docs/system-prompts/principles/definition-of-done.md` | Extract |
| `docs/definition-of-done.md` | Python specifics (pytest, requirements.txt) | `docs/system-prompts/languages/python/definition-of-done.md` | Extract |
| `docs/prompt-patterns.md` | The whole file | `docs/system-prompts/patterns/prompt-patterns.md` | Move & Generalize |
| `AGENTS.md` | The "Unbreakable Rules" | `docs/system-prompts/workflow/core.md` | Move (as they are part of workflow) |

## 3. The Bootstrap Tool (`bootstrap.py`)

A standalone Python script (no external deps) to manage `AGENTS.md`.

### Requirements
- **No Dependencies:** Uses only `sys`, `os`, `argparse`, `re`.
- **Root Detection:** Checks for `README.md`, `.git`, or language markers (`pyproject.toml`, `package.json`) to confirm execution root.
- **Safety:** Default run is **Dry Run**. Requires `--commit` to write files.
- **Section Management:** Parses `AGENTS.md` for marker tags:
  ```markdown
  <!-- SECTION: CORE-WORKFLOW -->
  ... content ...
  <!-- END-SECTION -->
  ```
- **Logic:**
  1. Detect project language (e.g., Python).
  2. Read `AGENTS.md` (or create if missing).
  3. Identify sections.
  4. Compare existing section content with the "Ideal State" from `system-prompts/`.
  5. **Unmodified:** Overwrite with new ideal state.
  6. **Modified:** Warn user, show diff, do not overwrite (unless `--force` is used).
  7. **Missing:** Inject section.

### Code Snippet (Bootstrap Logic)

```python
def update_section(content, section_name, new_content):
    pattern = f"<!-- SECTION: {section_name} -->(.*?)<!-- END-SECTION -->"
    match = re.search(pattern, content, re.DOTALL)
    
    if not match:
        # Append if missing
        return content + f"\n\n<!-- SECTION: {section_name} -->\n{new_content}\n<!-- END-SECTION -->"
    
    current_content = match.group(1).strip()
    if current_content == new_content.strip():
        return content # No change
        
    # TODO: Implement hash check against "previous ideal state" here?
    # For V1, we might just warn if different from *current* ideal.
    print(f"WARNING: Section {section_name} is locally modified.")
    return content 
```

## 4. Execution Steps

1.  **Create Directories:** Set up the `system-prompts` hierarchy.
2.  **Migrate Content:**
    *   Read `AGENTS.md` -> Write `workflow/core.md`.
        *   **Refinement:** Explicitly define "Project Plan" as a formal file in `dev_notes/project_plans/`. Add note: "When asked to 'create a plan', you MUST create this file, not just summarize in chat."
    *   Read `docs/definition-of-done.md` -> Write `principles/DoD` and `languages/python/DoD`.
    *   Read `docs/prompt-patterns.md` -> Write `patterns/prompt-patterns.md`.
3.  **Implement `bootstrap.py`:** Write the script in `docs/system-prompts/`.
4.  **Create Documentation (`docs/system-prompts/README.md`):**
    *   Explain the "Agent Kernel" concept and `git remote add` pattern.
    *   Document `bootstrap.py` usage and arguments.
    *   List supported languages and extent of support.
    *   Explain how to wire the kernel into a target project.
5.  **Run Bootstrap:** Run `python3 docs/system-prompts/bootstrap.py --commit` to generate the new, sectioned `AGENTS.md`.
6.  **Verify:** Check that `AGENTS.md` properly references the new files and retains project-specific context (manually added back if needed).

## 5. Deliverables

- `docs/system-prompts/` directory populated.
- `docs/system-prompts/bootstrap.py` tool.
- `docs/system-prompts/README.md` (Human Guide).
- Refactored `AGENTS.md` using section markers.
- `docs/definition-of-done.md` replaced/symlinked (or managed by `AGENTS.md` reference).

## 6. Risks & Mitigations

- **Risk:** `AGENTS.md` becomes broken/unreadable.
  - **Mitigation:** The `bootstrap.py` defaults to dry-run/stdout. We verify the output before committing.
- **Risk:** Loss of project-specific rules in `AGENTS.md`.
  - **Mitigation:** We will manually populate the `<!-- SECTION: PROJECT-SPECIFIC -->` in the first run to ensure `dev_notes/` and `config.json` rules are preserved.
