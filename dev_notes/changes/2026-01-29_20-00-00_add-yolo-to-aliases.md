# Change Log: Add --yolo equivalent to Agent Aliases

## 2026-01-29 20:00:00 - Add --yolo equivalent to Agent Aliases

### Context
User requested to add the equivalent of `--dangerously-skip-permissions` (referred to as `--yolo`) to all agent tips aliases and `aliases.sh` to enable autonomous, pre-approved execution in quick scripts.

Additionally, user requested improvements to environment variable handling in aliases and optimizations to the `close-task` process for documentation updates.

### Changes
1.  **Modified `docs/system-prompts/tips/aliases.sh`:**
    *   Updated `gemini-*` aliases to include `--dangerously-skip-permissions` and use inline environment variable assignment (preventing shell pollution).
    *   Updated `codex-*` aliases to include `--approval-mode full-auto`.
    *   Updated `cline-*` aliases to include `CLINE_APPROVAL_MODE=auto`.

2.  **Modified Documentation Tips:**
    *   Updated `docs/system-prompts/tips/gemini.md`: Reflected alias changes.
    *   Updated `docs/system-prompts/tips/codex.md`: Reflected alias changes.
    *   Updated `docs/system-prompts/tips/cline.md`: Reflected alias changes.

3.  **Modified `docs/system-prompts/processes/close-task.md`:**
    *   Updated Phase 2 to include an optimization rule: For documentation-only changes, regression tests and non-doc-specific DoD measures are skipped.

### Impact
*   **Autonomous Workflows:** Users sourcing `docs/system-prompts/tips/aliases.sh` will now have "YOLO" behavior enabled by default for `*-sys`, `*-quick`, `*-dev`, and `*-think` aliases.
*   **Cleaner Environment:** Gemini aliases no longer leave `GEMINI_MODEL` or `GEMINI_DEBUG` vars set in the user's shell.
*   **Efficient Documentation Updates:** The `close-task` process is now faster for documentation/config-only tasks by skipping unnecessary regression testing.