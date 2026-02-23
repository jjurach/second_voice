# Project Context

This document captures the design rationale and external interface for second_voice. It exists so that an agent working in isolation within this module has the background needed to make consistent decisions without access to broader planning context.

---

## Design Rationale

**Why delegate to mellona instead of calling providers directly.** second_voice originally called OpenRouter and Groq APIs directly with hardcoded credentials and a large fallback model list in source. This was replaced with mellona integration so that: (1) credential management is consistent across tools, (2) the fallback chain is configurable per-user, and (3) provider implementations don't need to be duplicated in every tool.

**Config chain layering.** second_voice adds its own config file (`~/.config/second_voice/settings.json`) at the top of mellona's priority chain. This allows second_voice-specific defaults (e.g., preferred model for audio transcription) without forking mellona's config system.

**Phase ordering: LLM before STT.** Ph2 (LLM integration) was done before Ph3 (STT integration) because the LLM path had no external blockers — it only required mellona's sync wrappers and config chaining (both already complete). The STT path required mellona to implement its STT provider ABC first, so Ph3 had to wait. This ordering avoided an idle gap.

**Credential cutover (Ph4).** The decision to remove raw API keys from second_voice's config entirely (rather than keeping them as a fallback) was made deliberately. A dual-path approach would require maintaining two credential systems indefinitely. A hard cutover with a clear migration error message is cleaner and forces users to consolidate credentials in one place.

**CLI flag surface (`--mellona-*`).** The mellona arg parser is added as a parent parser, not reimplemented. This means second_voice automatically picks up new mellona flags without code changes, and the help output clearly groups them under "mellona options".

---

## Phase Roadmap

| Phase | Description | Status |
|---|---|---|
| Ph1 | Link mellona + Baseline Verification | complete |
| Ph2 | LLM Integration (replace raw API calls) | open |
| Ph3 | STT Integration (replace direct Groq/Whisper calls) | open — soft-blocked externally (see External Dependencies) |
| Ph4 | Hard Cutover — Credentials | open (blocked by Ph2 + Ph3) |
| Ph5 | CLI Integration (`--mellona-*` flags) | open |
| Ph6 | Test Updates + Config Documentation | open (blocked by Ph2, Ph3, Ph4, Ph5) |
| Ph7 | Self-Healing System Prompts | open (blocked by Ph6) |
| Ph8 | Workflow Improvement Analysis | open (blocked by Ph7 + external) |

---

## External Dependencies

**mellona STT provider ABC** (required for Ph3 and downstream)

Ph3 (STT Integration) cannot begin until mellona has a complete STT provider ABC with at least one working implementation. This is mellona's work, not second_voice's. When it is ready, second_voice Ph3 will replace the direct `_transcribe_local_whisper()` and `_transcribe_groq()` calls with `SyncMellonaClient.transcribe(provider=...)`.

To check status: look at mellona's `.beads/` for issues related to STT Provider ABC and LocalWhisper Provider, or check `modules/mellona/src/mellona/providers/` for `stt_base.py`.

When the block clears: remove the SOFT BLOCK note from second_voice-9jy (Ph4) and second_voice-nfa (Ph6).

---

## What This Module Exports

**CLI: `second-voice`**
- `second-voice <audio_file>` — transcribe and process audio
- `--mellona-profile`, `--mellona-provider`, `--mellona-model` — mellona passthrough flags
- `--output-format` — transcript output format
- Exit codes: 0 = success, non-zero = error with message on stderr

**Config: `~/.config/second_voice/settings.json`**
- `openrouter_fallback_models` — ordered list of fallback model IDs
- mellona config chain is layered underneath; see mellona's config schema for full options

**No importable Python API.** second_voice is a CLI application, not a library. Other modules invoke it via subprocess or shell, not via Python import.
