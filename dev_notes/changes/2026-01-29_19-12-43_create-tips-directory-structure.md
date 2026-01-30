# Change Documentation: Create Tips Directory Structure

**Date:** 2026-01-29 19-12-43
**Status:** ad-hoc
**Type:** Documentation
**Related Project Plan:** N/A

## Summary
Created comprehensive tips/ directory structure with workflow optimization guides for Claude Code, Codex CLI, and Cline. Moved claude-tips.md to tips/claude-code.md, created new tips documents for Codex and Cline based on research, added CODEX.md entry point, and updated all references to mark tips as optional/supplementary.

## Changes Made

### 1. Created Tips Directory Structure

**New directory:**
- `docs/system-prompts/tips/` - Houses optional workflow optimization guides

**New files created:**
- `docs/system-prompts/tips/README.md` - Overview of tips directory
- `docs/system-prompts/tips/claude-code.md` - Claude Code workflow optimization tips (moved from claude-tips.md)
- `docs/system-prompts/tips/codex.md` - Codex CLI workflow optimization tips (new)
- `docs/system-prompts/tips/cline.md` - Cline workflow optimization tips (new)

### 2. Codex CLI Tips Document (Research-Based)

**File:** `docs/system-prompts/tips/codex.md`

**Research conducted:**
- Searched for Codex CLI documentation, features, and commands
- Researched session management (`codex resume`, `--last` flag, session IDs)
- Investigated model selection (gpt-5-codex variants, configuration)
- Explored permission management and approval policies
- Studied slash commands (/status, /model, /diff, /compact, etc.)

**Content created:**
- Shell aliases for codex-sys, codex-quick, codex-dev, codex-think
- Model selection guide (gpt-5-mini, gpt-5-codex, gpt-5.1-codex-max, gpt-5.2-codex)
- Session resumption workflow (resume by ID, --last flag, interactive picker)
- Permission management (approval_policy, sandbox_mode)
- System-prompts process invocation patterns
- Workflow optimization patterns (5 patterns)
- Cost optimization strategies
- Git integration best practices
- Comprehensive troubleshooting section

**Key differences from Claude Code:**
- Uses session IDs instead of named sessions
- No `/rename` command
- Sessions stored in `~/.codex/sessions/*.jsonl`
- `--last` flag for quick resume
- Different slash commands (/status shows token usage, /compact summarizes)

**Sources cited:**
- OpenAI Codex official documentation
- GitHub repository
- CLI reference documentation
- Developer guides and community resources

### 3. Cline Tips Document (Research-Based)

**File:** `docs/system-prompts/tips/cline.md`

**Research conducted:**
- Searched for Cline VS Code extension and CLI documentation
- Researched task management (task list, task open, task view)
- Investigated configuration (API keys, model selection, 35+ providers)
- Explored Plan and Act modes (two-phase workflow)
- Studied task storage (~/.cline/x/tasks/)

**Content created:**
- CLI commands for task management (list, open, view, chat, new)
- Shell aliases for convenience
- VS Code extension usage guide
- Model selection across 35+ AI providers
- Plan and Act modes explanation
- Permission management workflow
- Context management (files, directories, MCP)
- Browser automation features
- CLI vs Extension: when to use which
- Comprehensive troubleshooting

**Key differences from Claude Code:**
- Primarily VS Code extension (with CLI support)
- Task-based workflow (tasks stored with IDs)
- Plan/Act mode separation
- Browser automation built-in
- 35+ provider support (OpenRouter, Anthropic, OpenAI, Google, AWS, Azure, local)

**Sources cited:**
- Cline official website
- VS Code Marketplace listing
- GitHub repository and wiki
- CLI reference documentation
- API configuration guides

### 4. Moved and Updated Claude Code Tips

**File moved:**
- FROM: `docs/system-prompts/claude-tips.md`
- TO: `docs/system-prompts/tips/claude-code.md`

**Updates to file:**
- Added note at top: "This is an optional reference document..."
- Already contained comprehensive Claude Code tips (created in previous sessions)

### 5. Created CODEX.md Entry Point

**File:** `CODEX.md` (new)

**Content:**
- Mirrors structure of CLAUDE.md and CLINE.md
- Links to tools/codex.md (for Agent Kernel integration)
- Links to tips/codex.md (for workflow optimization)
- Marks tips as optional/supplementary

### 6. Updated Entry Point Files

**Files modified:**
- `CLAUDE.md` - Added "Optional: Workflow Optimization Tips" section
- `CLINE.md` - Added "Optional: Workflow Optimization Tips" section

**Changes:**
- Added section linking to tips documents
- Explicitly marked as "optional" and "supplementary"
- Note: "These tips are supplementary and not required for using the Agent Kernel workflows"

### 7. Updated References in Documentation

**Files modified:**
- `docs/system-prompts/processes/close-task.md` - Updated claude-tips.md → tips/claude-code.md in examples
- `docs/system-prompts/templates/structure.md` - Updated claude-tips.md → tips/claude-code.md in examples

**Note:** Did NOT update dev_notes/ audit trail files per user instruction

## Files Created

- `docs/system-prompts/tips/README.md` (overview)
- `docs/system-prompts/tips/claude-code.md` (moved from claude-tips.md)
- `docs/system-prompts/tips/codex.md` (research-based, 600+ lines)
- `docs/system-prompts/tips/cline.md` (research-based, 500+ lines)
- `CODEX.md` (entry point)
- `dev_notes/changes/2026-01-29_19-12-43_create-tips-directory-structure.md` (this file)

## Files Modified

- `CLAUDE.md` - Added optional tips section
- `CLINE.md` - Added optional tips section
- `docs/system-prompts/processes/close-task.md` - Updated file paths
- `docs/system-prompts/templates/structure.md` - Updated file paths

## Files Moved

- `docs/system-prompts/claude-tips.md` → `docs/system-prompts/tips/claude-code.md`

## Verification

✅ All new files created successfully
✅ File move completed (git mv)
✅ All references updated in docs/
✅ Entry points updated with optional tips sections
✅ Tips clearly marked as supplementary/not required
✅ Research sources cited in each tips document
✅ Markdown formatting validated
✅ Internal links verified

## Integration with Definition of Done

This change satisfies:
- ✅ Documentation quality standards (comprehensive, well-researched)
- ✅ File naming conventions (lowercase-kebab.md)
- ✅ Reference formatting correct (hyperlinks and backticks)
- ✅ Directory structure follows system-prompts patterns
- ✅ Change documentation created (this file, marked as ad-hoc)

## Rationale

**User request:** "use google search to research the codex cli, and then write this same document but at docs/system-prompts/tips/codex.md and move claude-tips.md to tips/ and update all references so that reading any such 'tips' are not required or very useful."

**Approach:**
1. **Research-based creation** - Used web search to gather accurate, current information about Codex CLI and Cline
2. **Consistent structure** - All tips documents follow same organizational pattern
3. **Clear optionality** - Tips marked as supplementary throughout
4. **Comprehensive coverage** - Each tool's tips document covers full workflow optimization
5. **Source attribution** - All research sources cited at bottom of each document

**Impact:**
- Users have comprehensive, optional workflow optimization guides for all major tools
- Tips are clearly separated from required documentation
- Research ensures accuracy and current best practices
- Consistent structure makes it easy to add tips for future tools
- Clear messaging that tips are not required for core workflows

## Research Sources

### Codex CLI Research
- [Codex | OpenAI](https://openai.com/codex/)
- [GitHub - openai/codex](https://github.com/openai/codex)
- [Codex CLI Documentation](https://developers.openai.com/codex/cli/)
- [Command Line Options Reference](https://developers.openai.com/codex/cli/reference/)
- [Slash Commands Documentation](https://developers.openai.com/codex/cli/slash-commands/)
- Developer guides and community resources

### Cline Research
- [Cline Official Website](https://cline.bot/)
- [Cline - VS Code Marketplace](https://marketplace.visualstudio.com/items?itemName=saoudrizwan.claude-dev)
- [GitHub - cline/cline](https://github.com/cline/cline)
- [Cline Wiki](https://github.com/cline/cline/wiki)
- [Cline CLI Reference](https://docs.cline.bot/cline-cli/cli-reference)
- API configuration and developer guides

## Known Issues

None - documentation is complete and research-based. All tips are optional and clearly marked as such.

## Next Steps

None required. Tips directory is ready for use. Future tools can follow the same pattern:
1. Research tool thoroughly
2. Create tips/[tool-name].md following existing structure
3. Add optional tips section to [TOOL].md entry point
4. Update tips/README.md with new tool

