# Plan-and-Dispatch Workflow

**Purpose:** Enable parallel agent execution with dependency-aware task graphs using beads for state tracking.

**Best for:**
- Projects with parallel work streams
- Complex multi-phase implementations
- Teams using external orchestration
- Projects requiring formal approval gates

**Prerequisites:**
- Beads CLI installed (`npm install -g @steveyegge/beads`)
- Beads initialized in project (run `python3 docs/system-prompts/planning-init.py`)

**Not recommended for:** Simple single-agent workflows or projects without beads support

---

## What is the Plan-and-Dispatch Workflow?

The plan-and-dispatch workflow extends the [logs-first workflow](logs-first.md) with **beads** - a git-backed graph issue tracker that manages task state and dependencies. This enables:

- **Planner agents** to break work into dependency-aware task graphs
- **Human approval gates** before implementation begins
- **External orchestrators** to dispatch ready tasks to worker pools
- **Parallel execution** of independent tasks with automatic dependency resolution

This workflow maintains the logs-first audit trail (Spec → Plan → Changes) while adding **execution state tracking** via beads.

---

## Architecture Overview

```
┌──────────────┐
│ PLANNER      │  Creates beads, manages dependencies
│ AGENT        │  Marks beads ready after approval
└──────┬───────┘
       │
       ▼
┌──────────────┐
│ BEADS        │  Task graph with dependencies
│ DATABASE     │  States: ready, in-progress, closed
└──────┬───────┘
       │
       ▼
┌──────────────┐
│ EXTERNAL     │  Watches for ready beads
│ ORCHESTRATOR │  Dispatches to worker pool
└──────┬───────┘
       │
       ▼
┌──────────────┐
│ WORKER       │  Claims bead, implements, closes
│ AGENTS       │  Creates failure beads on errors
└──────────────┘
```

**Key concept:** Beads **augments** project plans, not replaces them. Project plans document implementation details, beads track execution state.

---

## Bead Patterns

All beads use labels (`--label <type>`) to encode their purpose.

### 1. Approval Beads (`--label approval`)

**Purpose:** Block implementation work until human reviews and approves plan

**Creation:**
```bash
bd create "Approve: Backend Restructure Plan" --label approval \
  --body "Plan: dev_notes/project_plans/2026-02-15_10-30-00_backend-restructure.md

Review Checklist:
- [ ] Plan phases are clear and sequenced
- [ ] Dependencies identified
- [ ] Risk mitigation adequate
- [ ] Effort estimates reasonable

Approve by closing this bead with: bd update <id> --close"
```

**Lifecycle:**
1. Planner creates approval bead referencing project plan
2. Planner creates implementation beads `blocked_by` approval bead
3. Human reviews project plan file
4. Human closes approval bead: `bd update <id> --close`
5. Implementation beads automatically become "ready"

### 2. Milestone Beads (`--label milestone`)

**Purpose:** Group related work, track epic-level progress

**Pattern:** Use hierarchical IDs
```bash
bd create "Backend API Migration" --label milestone    # bd-a1b2
bd create "Copy Lambda functions" --label implementation  # bd-a1b2.1
```

### 3. Planning Beads (`--label planning`)

**Purpose:** Convert inbox items into executable plans

**Work:** Read inbox → Create spec → Create plan → Create beads → Close planning bead

### 4. Research Beads (`--label research`)

**Purpose:** Investigation before implementation (no code changes)

**Closure:** When findings documented

### 5. Verification Beads (`--label verification`)

**Purpose:** Quality gates (e.g., "All tests pass") that block deployment

### 6. Documentation Beads (`--label documentation`)

**Purpose:** Track documentation work, often `blocked_by` implementation beads

### 7. Worker Session Beads (`--label worker-session`)

**Purpose:** Audit trail of worker agent sessions (created by orchestrator)

**Note:** Worker capacity managed externally, not in beads

### 8. Failure Beads (`--label failure`)

**Purpose:** Track worker failures requiring human intervention

**Creation:**
```bash
bd create "FAILURE: Test errors in bd-a1b2.1" --label failure \
  --body "Original Task: bd-a1b2.1

Error Details:
[Full error message, stack trace, test output]

Recommendation:
[Suggested next steps for human]"

# Block original work bead
bd dep add bd-a1b2.1 bd-failure-123
```

---

## The Plan-and-Dispatch Workflow

### Prerequisites

Before using this workflow, ensure beads is initialized:

```bash
# Check if beads is initialized
ls .beads/ 2>/dev/null && echo "✓ Beads initialized" || echo "✗ Beads not initialized"

# Initialize if needed
python3 docs/system-prompts/planning-init.py
```

### Step 1: Process Inbox (Planner Agent)

**Trigger:** Human requests "process dev_notes/inbox/next.md"

**Actions:**

1. **Follow logs-first workflow** through Step C (Create Project Plan)
   - Read inbox item
   - Create spec file: `dev_notes/specs/YYYY-MM-DD_HH-MM-SS_name.md`
   - Create project plan: `dev_notes/project_plans/YYYY-MM-DD_HH-MM-SS_name.md`
   - Archive inbox item to `dev_notes/inbox-archive/`

2. **Create approval bead**
   ```bash
   timestamp=$(date +%Y-%m-%d_%H-%M-%S)
   plan_file="dev_notes/project_plans/${timestamp}_name.md"

   bd create "Approve: [Plan Name]" --label approval \
     --body "Plan: ${plan_file}

Review Checklist:
- [ ] Plan phases are clear and sequenced
- [ ] Dependencies identified
- [ ] Risk mitigation adequate

Approve by closing this bead."
   ```

3. **Create implementation beads for each phase/task**
   ```bash
   # For each phase in project plan
   bd create "[Task description from plan]" --label implementation
   ```

4. **Append the Standard Epic Suffix Sequence**
   Every epic MUST conclude with these two beads to ensure continuous improvement and proper project closure:

   - **Bead A: Self-Healing & System Prompt Updates**
     ```bash
     bd create "Phase N: Self-Healing System Prompts & Documentation" --label implementation \
       --body "Update docs/system-prompts/ based on lessons learned. See Phase N of [Plan File]"
     ```
   - **Bead B: Workflow Improvement Analysis**
     ```bash
     bd create "Phase N+1: Workflow Improvement Analysis" --label implementation \
       --body "Apply docs/system-prompts/processes/workflow-improvement-analysis.md to evaluate change logs and plan future fixes."
     ```

   **Planner Instruction:** Always insert your specific implementation beads *before* this suffix sequence. The final dependency chain should always end with: `... → [Last Implementation Task] → [Self-Healing Task] → [Workflow Analysis Task]`.

5. **Add dependencies**
   ```bash
   # Block all implementation beads by approval bead
   bd dep add ${task1_id} ${approval_id}
   ...
   # Ensure sequential suffix
   bd dep add ${analysis_id} ${self_healing_id}
   ```

5. **Update project plan status**
   - Edit plan file
   - Change status from "Draft" to "Awaiting Approval"
   - Add bead references to plan

6. **Report to human**
   ```
   ✅ Project plan created and beads initialized

   Plan: dev_notes/project_plans/2026-02-15_10-30-00_backend-restructure.md
   Approval Bead: bd-a1b2
   Implementation Beads: 3 (all blocked until approval)

   Review the plan and close the approval bead to begin work:
   bd update bd-a1b2 --close

   View beads status:
   python3 docs/system-prompts/planning-summary.py
   ```

### Step 2: Human Approval

**Actions:**

1. **Review project plan**
   ```bash
   cat dev_notes/project_plans/2026-02-15_10-30-00_backend-restructure.md
   ```

2. **Check bead graph**
   ```bash
   # View approval bead details
   bd show bd-a1b2

   # View all beads
   python3 docs/system-prompts/planning-summary.py
   ```

3. **If approved, close approval bead**
   ```bash
   bd update bd-a1b2 --close
   ```

   Implementation beads automatically become "ready"

4. **If changes needed**
   - Provide feedback to planner
   - Planner updates plan and beads
   - Return to step 1

### Step 3: Orchestrator Dispatches Work

**Note:** This step is performed by an **external orchestrator**, not part of this codebase.

**Orchestrator logic:**

1. Watch beads JSONL file for changes
2. When change detected, run `bd ready --json`
3. If ready beads exist and worker slots available:
   - Select next ready bead
   - Spawn worker: `claude implement bd-a1b2.1`
   - Create worker session bead for audit trail

See [External Orchestrator](external-orchestrator.md) for details.

### Step 4: Worker Implementation

**Trigger:** Orchestrator spawns worker with bead ID in prompt

**Prompt received:**
```
Implement bead bd-a1b2.1

Use `bd show bd-a1b2.1` to see task details.
Follow close-project.md process when complete.
```

**Actions:**

1. **Claim bead**
   ```bash
   bd update bd-a1b2.1 --claim
   ```

2. **Read task details**
   ```bash
   bd show bd-a1b2.1
   ```

3. **Implement the task**
   - Write code
   - Write tests
   - Update documentation
   - Follow standard development workflow

4. **Create change documentation**
   ```bash
   timestamp=$(date +%Y-%m-%d_%H-%M-%S)
   # Create: dev_notes/changes/${timestamp}_description.md
   # Include: Bead: bd-a1b2.1
   # IMPORTANT: Add "Workflow & Tooling Feedback" section if you encountered
   # any friction with beads, system prompts, or the process itself.
   ```

5. **Follow close-project.md process**
   - Verify Definition of Done
   - Run tests
   - Commit changes
   - **Close bead** (new Phase 4.5 in close-project.md)

6. **Close bead**
   ```bash
   bd update bd-a1b2.1 --close
   ```

### Step 5: Worker Failure Handling

**Trigger:** Worker encounters non-trivial error that cannot be fixed

**Actions:**

1. **Create failure bead**
   ```bash
   bd create "FAILURE: Test errors in bd-a1b2.1" --label failure \
     --body "Original Task: bd-a1b2.1

Error Details:
========================= FAILURES =========================
test_migration.py::test_schema_migration - AssertionError: expected table 'users_v2', got 'users'

Context:
Attempted to migrate DynamoDB schema but table creation failed.
Migration script at src/migrate_schema.py line 45.

Recommendation:
- Review DynamoDB permissions in IAM policy
- Check if table name conflicts with existing table
- Verify migration script logic for table creation"
   ```

2. **Block original bead**
   ```bash
   failure_id="bd-failure-123"
   bd dep add bd-a1b2.1 ${failure_id}
   ```

3. **Unclaim original bead (so it shows as blocked, not in-progress)**
   ```bash
   bd update bd-a1b2.1 --unclaim
   ```

4. **Report to human**
   ```
   ❌ Worker failed on bd-a1b2.1

   Created failure bead: bd-failure-123
   Original bead is now blocked until failure is resolved.

   See failure details:
   bd show bd-failure-123

   Human intervention required.
   ```

---

## Monitoring Work Progress

### View Current Status

```bash
# Quick summary
python3 docs/system-prompts/planning-summary.py

# Show only ready beads
python3 docs/system-prompts/planning-summary.py --status ready

# Show failures
python3 docs/system-prompts/planning-summary.py --label failure

# Verbose mode with full descriptions
python3 docs/system-prompts/planning-summary.py --verbose
```

### Check for Problems

```bash
# Detect and fix issues
python3 docs/system-prompts/planning-doctor.py
```

Common issues detected:
- Orphaned beads (blocked by non-existent beads)
- Circular dependencies
- Stale in-progress beads (abandoned by workers)
- Missing labels

## Self-Healing & Continuous Improvement

The plan-and-dispatch workflow incorporates a **self-healing** mechanism to ensure the system improves with every execution:

1. **Lessons Learned:** Every project plan includes a "Lessons Learned" section. Workers must update this section with technical insights or process improvements discovered during implementation.
2. **System Prompt Updates:** If an insight is generally applicable to all projects, agents should immediately update the relevant documentation in `docs/system-prompts/` (e.g., principles, processes, or templates).
3. **Closing the Loop:** Planners should review "Lessons Learned" from previous phases or similar plans when creating or updating project plans to ensure knowledge persists across agent sessions.

See **[Self-Healing Principle](../principles/self-healing.md)** for more details.

---

## Integration with Logs-First Workflow

The plan-and-dispatch workflow **extends** logs-first, not replaces it:

| Aspect | Logs-First | Plan-and-Dispatch |
|--------|------------|-------------------|
| **Inbox processing** | Create spec → plan | Same + create beads |
| **Project plan** | Required | Required + referenced by approval bead |
| **Approval** | Human reviews plan file | Human reviews plan file + closes approval bead |
| **Implementation** | Agent implements directly | Orchestrator dispatches to worker pool |
| **Change docs** | Required | Required + includes bead ID |
| **Completion** | close-project.md | close-project.md + close bead |
| **Audit trail** | Spec → Plan → Changes | Spec → Plan → Changes + Beads |

**Key difference:** Beads adds **execution state tracking** and **parallel dispatch capability**.

---

## When to Use Plan-and-Dispatch

**Use plan-and-dispatch when:**
- ✅ Work can be parallelized across independent tasks
- ✅ Using external orchestration for worker management
- ✅ Need formal approval gates with automatic unblocking
- ✅ Want audit trail of which worker did which work
- ✅ Managing complex dependency graphs

**Stick with logs-first when:**
- ❌ Simple single-agent workflow
- ❌ Sequential work with no parallelization
- ❌ No external orchestration
- ❌ Overhead of beads not justified

---

## Common Patterns

### Pattern: Sequential Phases

```bash
# Create phase beads
bd create "Phase 1: Database migration" --label implementation
bd create "Phase 2: API updates" --label implementation
bd create "Phase 3: Frontend changes" --label implementation

# Chain dependencies
bd dep add bd-phase2 bd-phase1  # Phase 2 blocked by Phase 1
bd dep add bd-phase3 bd-phase2  # Phase 3 blocked by Phase 2
```

### Pattern: Parallel Work Streams

```bash
# Create parallel tasks
bd create "Backend: Add authentication" --label implementation
bd create "Frontend: Add login UI" --label implementation
bd create "Docs: Update API docs" --label implementation

# No dependencies between them - all become ready simultaneously
```

### Pattern: Research Before Implementation

```bash
# Create research bead
bd create "Research OAuth2 providers" --label research

# Create implementation bead blocked by research
bd create "Implement OAuth2 authentication" --label implementation
bd dep add bd-impl bd-research
```

### Pattern: Verification Gates

```bash
# Create implementation beads
bd create "Implement feature X" --label implementation
bd create "Write tests for X" --label implementation

# Create verification bead blocked by implementation
bd create "All X tests pass" --label verification
bd dep add bd-verify bd-impl
bd dep add bd-verify bd-tests

# Create deployment bead blocked by verification
bd create "Deploy X to production" --label implementation
bd dep add bd-deploy bd-verify
```

---

## Troubleshooting

### Beads aren't becoming ready after approval

**Check:**
```bash
# Show approval bead status
bd show bd-approval-id

# Should show: status: closed
```

**Fix:**
```bash
# Close approval bead if not closed
bd update bd-approval-id --close
```

### Worker can't claim bead

**Check:**
```bash
# Show bead status
bd show bd-task-id

# Should show: status: ready
# If blocked_by: [...], dependencies not yet closed
```

**Fix:** Close blocking beads first

### Circular dependency detected

**Check:**
```bash
python3 docs/system-prompts/planning-doctor.py
```

**Fix:** Manually remove circular dependency
```bash
bd dep remove bd-child-id bd-parent-id
```

### Stale in-progress beads

**Cause:** Worker crashed or abandoned work

**Check:**
```bash
python3 docs/system-prompts/planning-doctor.py
```

**Fix:**
```bash
# Unclaim abandoned bead
bd update bd-stale-id --unclaim

# Or close if work was actually done
bd update bd-stale-id --close
```

---

## See Also

- **[External Orchestrator](external-orchestrator.md)** - Orchestrator architecture and operation
- **[Logs-First Workflow](logs-first.md)** - Foundation workflow for documentation
- **[Close Project Process](../processes/close-project.md)** - Includes bead closure step
- **[Planning Init](../processes/planning-init.md)** - Initialize beads in project
- **[Planning Doctor](../processes/planning-doctor.md)** - Detect and fix bead issues
- **[Planning Summary](../processes/planning-summary.md)** - View execution status

---

**Last Updated:** 2026-02-15
