# Open Questions & Strategic Goals

This document tracks unresolved technical questions and strategic initiatives to improve the quality of agentic development within the Second Voice project.

---

## 1. Unresolved Technical Questions

### OpenAI Codex / GPT-4 Integration
- **Official CLI:** As of 2026, is there an official OpenAI CLI tool that supports function calling and file operations natively?
- **Deprecation:** Should `docs/tool-specific-guides/codex.md` be deprecated in favor of `Aider` (which already supports GPT-4) to reduce maintenance overhead?
- **Approval gates:** If using the raw API, how do we implement and enforce `ExitPlanMode`-style approval gates?

### Tool Capabilities Matrix
- **Gemini Status:** Complete the "TBD" fields in `docs/tools-capabilities.md` based on recent verification (Git auto-commit, Task tracking, etc.).
- **Context Windows:** Update the token limits for 2026 models (Gemini 1.5 Pro, GPT-4o, etc.) to ensure agents make informed decisions about context management.

### Prompt Patterns
- **Completeness Review:** Finalize the draft patterns in `docs/prompt-patterns.md` and remove "Is this complete?" placeholders.

---

## 2. Strategic Initiatives (Agentic Quality)

### "CI for Agents" (Automated Validation)
- **Goal:** Programmatically enforce the "State Machine" rules defined in `AGENTS.md` and `docs/definition-of-done.md`.
- **Question:** How can we automatically validate the presence and format of `dev_notes/changes/` entries on every commit?
- **Proposal:** Implement a pre-commit hook or GitHub Action that checks for mandatory headers (Verification Results, exact command, terminal output).

### Context Pruning & Hygiene
- **Goal:** Prevent "Context Bloat" where agents are overwhelmed by old logs.
- **Question:** What is our archiving strategy for the `dev_notes/` directory?
- **Proposal:** Move change logs and project plans older than 30 days or 10 major iterations to a `dev_notes/archive/` folder.

### Architectural Decision Records (ADRs)
- **Goal:** Lock in architectural choices to prevent agents from suggesting "improvements" that reverse previous decisions.
- **Question:** Where do we store permanent, immutable decisions (e.g., "Why we switched from PyAudio to sounddevice")?
- **Proposal:** Create a `docs/decisions/` directory for formal ADRs.

### Agent Integration Benchmarking
- **Goal:** Objectively verify new tools before declaring them "Supported".
- **Question:** How do we prove a tool can handle the full `AGENTS.md` cycle?
- **Proposal:** Define a standard "Benchmark Task" (e.g., "Implement a --version flag with full spec/plan/doc cycle") that any new tool must pass.

---

## 3. Immediate Action Items
- [ ] **Codex Resolution:** Decide whether to keep or remove the Codex guide.
- [ ] **Gemini Update:** Sync `docs/tools-capabilities.md` with findings from the Gemini testing session.
- [ ] **ADR Initialization:** Draft `docs/decisions/0001-use-sounddevice.md`.

---
*Last Updated: 2026-01-25*
