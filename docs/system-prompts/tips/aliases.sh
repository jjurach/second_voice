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
alias gemini-sys='export GEMINI_MODEL=gemini-3-flash && gemini'

# Quick exploration (use Flash for low latency)
alias gemini-quick='export GEMINI_MODEL=gemini-3-flash && gemini'

# Full dev work (use Pro for better reasoning)
alias gemini-dev='export GEMINI_MODEL=gemini-3-pro && gemini'

# Deep reasoning/Architecture (use Pro for max capability)
alias gemini-think='export GEMINI_MODEL=gemini-3-pro && gemini'

# Debug mode
alias gemini-debug='export GEMINI_DEBUG=true && gemini'

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
# Gemini CLI:
#   gemini-sys (then ask: 'apply document-integrity-scan process')
#   gemini-dev (then ask: 'implement OAuth authentication')
#   gemini-quick (then ask: 'find all error handling code')
#   gemini-think (then ask: 'design the caching architecture')
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
