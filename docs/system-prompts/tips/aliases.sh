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
# Gemini CLI Aliases
# ============================================================================
# See: docs/system-prompts/tips/gemini.md

# System-prompts processes (use Flash for speed)
alias gemini-sys='GEMINI_MODEL=gemini-3-flash-preview gemini --yolo --prompt'

# Quick exploration (use Flash for low latency)
alias gemini-quick='GEMINI_MODEL=gemini-3-flash-preview gemini --yolo --prompt'

# Full dev work (use Pro for better reasoning)
alias gemini-dev='GEMINI_MODEL=gemini-3-pro-preview gemini --yolo --prompt'

# Deep reasoning/Architecture (use Pro for max capability)
alias gemini-think='GEMINI_MODEL=gemini-3-pro-preview gemini --yolo --prompt'

# Debug mode
alias gemini-debug='GEMINI_DEBUG=true gemini --yolo --prompt'

# ============================================================================
# Codex CLI Aliases
# ============================================================================
# See: docs/system-prompts/tips/codex.md

# System-prompts processes (use default model)
alias codex-sys='codex --approval-mode full-auto'

# Quick exploration (use mini model for speed/cost)
alias codex-quick='codex --model gpt-5-mini --approval-mode full-auto'

# Full dev work (use codex-max model)
alias codex-dev='codex --model gpt-5.1-codex-max --approval-mode full-auto'

# Deep reasoning (use latest frontier model)
alias codex-think='codex --model gpt-5.2-codex --approval-mode full-auto'

# ============================================================================
# Cline Aliases
# ============================================================================
# See: docs/system-prompts/tips/cline.md

# Quick task management
alias cline-list='cline task list'
alias cline-resume='CLINE_APPROVAL_MODE=auto cline task open'
alias cline-view='cline task view'
alias cline-new='CLINE_APPROVAL_MODE=auto cline task new'
alias cline-chat='CLINE_APPROVAL_MODE=auto cline task chat'

# System-prompts processes
alias cline-sys='CLINE_APPROVAL_MODE=auto cline task new "apply system-prompts process"'
alias cline-dev='CLINE_APPROVAL_MODE=auto cline task new "development task"'

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
# Gemini CLI:
#   gemini-sys 'apply document-integrity-scan process'
#   gemini-dev 'implement OAuth authentication'
#   gemini-quick 'find all error handling code'
#   gemini-think 'design the caching architecture'
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
    echo "Available: claude-*, gemini-*, codex-*, cline-*"
fi
