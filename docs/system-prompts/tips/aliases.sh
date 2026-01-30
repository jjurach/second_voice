#!/usr/bin/env bash
# AI Coding Tool Aliases for Agent Kernel Workflows
#
# Source this file in your ~/.bashrc or ~/.zshrc:
#   source /path/to/docs/system-prompts/tips/aliases.sh
#
# Or add to your shell config:
#   echo "source $(pwd)/docs/system-prompts/tips/aliases.sh" >> ~/.bashrc
#   echo "source $(pwd)/docs/system-prompts/tips/aliases.sh" >> ~/.zshrc

# ============================================================================
# Claude Code Aliases
# ============================================================================
# See: docs/system-prompts/tips/claude-code.md

# System-prompts processes (skip permissions, use sonnet)
alias claude-sys='claude --model sonnet --dangerously-skip-permissions'

# Quick exploration (skip permissions, use haiku for speed)
alias claude-quick='claude --model haiku --dangerously-skip-permissions'

# Full dev work (skip permissions, use sonnet)
alias claude-dev='claude --model sonnet --dangerously-skip-permissions'

# Deep reasoning (skip permissions, use opus)
alias claude-think='claude --model opus --dangerously-skip-permissions'

# ============================================================================
# Codex CLI Aliases
# ============================================================================
# See: docs/system-prompts/tips/codex.md

# System-prompts processes (use default model)
alias codex-sys='codex'

# Quick exploration (use mini model for speed/cost)
alias codex-quick='codex --model gpt-5-mini'

# Full dev work (use codex-max model)
alias codex-dev='codex --model gpt-5.1-codex-max'

# Deep reasoning (use latest frontier model)
alias codex-think='codex --model gpt-5.2-codex'

# ============================================================================
# Cline Aliases
# ============================================================================
# See: docs/system-prompts/tips/cline.md

# Quick task management
alias cline-list='cline task list'
alias cline-resume='cline task open'
alias cline-view='cline task view'
alias cline-new='cline task new'
alias cline-chat='cline task chat'

# System-prompts processes
alias cline-sys='cline task new "apply system-prompts process"'
alias cline-dev='cline task new "development task"'

# ============================================================================
# Usage Examples
# ============================================================================
#
# Claude Code:
#   claude-sys 'apply document-integrity-scan process'
#   claude-dev 'implement OAuth authentication'
#   claude-quick 'find all error handling code'
#   claude-think 'design the caching architecture'
#
# Codex CLI:
#   codex-sys 'apply close-task process'
#   codex-dev 'refactor authentication module'
#   codex-quick 'list all TODOs'
#   codex-think 'review system architecture'
#
# Cline:
#   cline-list
#   cline-resume 1760501486669
#   cline-new 'implement feature X'
#   cline-sys
#
# Session Resumption:
#   claude --continue                    # Resume most recent
#   claude -r session-name               # Resume named session
#   codex resume --last                  # Resume most recent
#   codex resume <SESSION_ID>            # Resume by ID
#   cline-resume <TASK_ID>               # Resume by task ID
#
# ============================================================================

# Optional: Print loaded message
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    echo "AI Coding Tool Aliases loaded"
    echo "Available: claude-{sys,quick,dev,think}, codex-{sys,quick,dev,think}, cline-{list,resume,view,new,chat,sys,dev}"
fi
