# Tool-Specific Guides: Consistency Analysis

**Date:** 2026-01-26
**Analysis Type:** Documentation standardization audit
**Files Analyzed:** docs/tool-specific-guides/*.md

---

## Executive Summary

The project has 5 tool-specific guides covering different types of AI development tools. There are **significant inconsistencies** in structure, detail level, and coverage that impact user experience and maintainability.

**Key Finding:** Tools fall into **three distinct categories** that require different documentation approaches:
1. **Interactive Development IDEs** (Claude Code, Aider) - Need detailed workflow mapping
2. **Code Editing CLIs** (Codex, Gemini) - Need brief, comparison-focused guides
3. **Programmatic LLM Providers** (Cline) - Need architecture and integration focus

---

## 1. Structural Inconsistencies

### Status Field Presence

| File | Has Status | Format |
|------|-----------|--------|
| claude-code.md | ❌ NO | — |
| aider.md | ❌ NO | — |
| cline.md | ✅ YES | `**Status:** ✅ Supported` |
| codex.md | ✅ YES | `**Status:** ✅ Supported` |
| gemini.md | ✅ YES | `**Status:** ✅ Supported` |

**Recommendation:** All guides should have explicit Status field at top (like cline, codex, gemini)

### Title Format Inconsistency

```
✅ Consistent (3 files):
   - "Cline CLI - Integration Guide (Supported)"
   - "OpenAI Codex CLI - Guide (Supported)"
   - "Google Gemini - Guide (Supported)"

❌ Inconsistent (2 files):
   - "Claude Code (claude-cli) - Complete Guide"
   - "Aider - Complete Guide"
```

**Recommendation:** Use pattern: `**Tool Name** - **Type** Guide (Status)`

### Quick Start Section

| File | Present | Detail Level |
|------|---------|--------------|
| claude-code.md | ✅ | ~6 lines |
| aider.md | ✅ | ~10 lines |
| cline.md | ✅ | ~11 lines |
| codex.md | ✅ | ~8 lines |
| gemini.md | ✅ | ~5 lines |

**Status:** ✅ Consistent (all present, reasonable variation)

---

## 2. Content Coverage Matrix

| Topic | Claude Code | Aider | Cline | Codex | Gemini |
|-------|-------------|-------|-------|-------|--------|
| **Overview/Intro** | ✅ | ✅ | ✅ | ✅ | ✅ |
| **Quick Start** | ✅ | ✅ | ✅ | ✅ | ✅ |
| **Configuration** | CLAUDE.md | .aider.yml | Env vars | ~/.codex/ | GEMINI.md |
| **How to Discover Instructions** | ✅ | ❌ | ❌ | ✅ | ✅ |
| **AGENTS.md Workflow Mapping** | ✅✅✅ (Detailed) | ✅✅ (Adapted) | ✅ (Brief) | ✅ (Table) | ✅ (Table) |
| **Tool-Specific Capabilities** | ✅✅✅ (Detailed) | ✅✅ (Brief) | ✅ (Moderate) | ❌ | ❌ |
| **Common Patterns/Examples** | ✅✅✅ (4 patterns) | ✅✅ (Partial) | ❌ | ❌ | ✅ (3 patterns) |
| **Error Handling** | ✅ | ❌ | ✅ | ❌ | ✅ |
| **Troubleshooting** | ✅ | ❌ | ✅ | ❌ | ❌ |
| **Limitations/Constraints** | ✅✅✅ (Detailed) | ✅ (Mentioned) | ✅ | ❌ | ✅ |
| **Best Practices/Tips** | ✅ (7 tips) | ❌ | ❌ | ❌ | ❌ |
| **Comparison Table** | ✅ (implicit) | ✅ | ✅ | ✅ | ✅ |
| **FAQ** | ❌ | ❌ | ❌ | ✅ | ✅ |
| **Verification Status** | ❌ | ❌ | ✅ | ✅ | ❌ |

**Key Findings:**
- Claude Code guide is **most comprehensive** (577 lines)
- Cline guide is **well-structured for LLM provider** (356 lines)
- Codex & Gemini are **too brief** (94, 104 lines)
- Aider has **good philosophy section** but missing execution details
- Missing: Consistent error handling, troubleshooting, verification status

---

## 3. Tool Category Analysis

### Category A: Interactive Development IDEs
**Files:** claude-code.md, aider.md
**Characteristics:** User types commands in interactive session, tool modifies code and files

**Current State:**
- ✅ claude-code.md: Excellent (577 lines) - has examples, error handling, patterns
- ⚠️ aider.md: Good philosophy (622 lines) - but missing execution examples

**Needs:**
- Step-by-step AGENTS.md workflow mapping
- Tool-specific capabilities/commands reference
- Common usage patterns with examples
- Error handling and recovery strategies
- Limitations and constraints

### Category B: Code Editing CLIs
**Files:** codex.md, gemini.md
**Characteristics:** Lightweight CLI tools, used for quick edits and queries

**Current State:**
- ⚠️ codex.md: Very brief (94 lines) - only basic info
- ⚠️ gemini.md: Very brief (104 lines) - workflow table present but sparse

**Needs:**
- More detail on how tool discovers AGENTS.md
- Common patterns and usage scenarios (3-5 patterns)
- Comparison with Claude Code (context, approval, git)
- Troubleshooting section
- More complete workflow mapping examples

### Category C: Programmatic LLM Providers
**Files:** cline.md
**Characteristics:** Used programmatically by application, not interactive

**Current State:**
- ✅ cline.md: Well-structured (356 lines) - architecture focused, provider comparison

**Model for Success:**
- Clear Architecture section explaining provider pattern
- Provider comparison table
- Use case documentation
- Troubleshooting for integration issues

---

## 4. Specific Gaps

### Missing: Tool-Specific Command Reference

**Present in:** claude-code.md (Quick Reference Card table)
**Missing from:** aider.md, cline.md, codex.md, gemini.md

**Recommendation:** Add quick reference table showing most common commands/patterns

### Missing: Consistent Verification Status Section

**Present in:** cline.md, codex.md
**Missing from:** claude-code.md, aider.md, gemini.md

**Recommendation:** Add to all guides:
```markdown
## Verification Status

- ✅ Tool CLI exists and is maintained
- ✅ AGENTS.md support confirmed
- ✅ Workflow compatible with second_voice
- ✅ Configuration working
```

### Missing: How Tool Discovers Instructions

**Present in:** claude-code.md (CLAUDE.md), codex.md (AGENTS.md), gemini.md (GEMINI.md)
**Missing from:** aider.md, cline.md

**aider.md needs:**
```markdown
## How Aider Discovers Project Instructions

Aider reads `AGENTS.md` from the project root and uses it to guide development work.
```

**cline.md needs:** Nothing (programmatic, no discovery needed)

---

## 5. Depth & Completeness Scoring

| File | Lines | Sections | Examples | Patterns | Overall |
|------|-------|----------|----------|----------|---------|
| claude-code.md | 577 | 15 | ✅ (6) | ✅ (4) | ⭐⭐⭐⭐⭐ |
| aider.md | 622* | 10 | ⚠️ (2) | ⚠️ (2) | ⭐⭐⭐ |
| cline.md | 356 | 11 | ✅ (3) | ❌ | ⭐⭐⭐⭐ |
| codex.md | 94 | 8 | ❌ | ❌ | ⭐⭐ |
| gemini.md | 104 | 8 | ⚠️ (3) | ⚠️ (2) | ⭐⭐⭐ |

*Partial read, likely longer

---

## 6. Recommended Standardization Template

All tool-specific guides should follow this structure:

```markdown
# [Tool Name] - [Type] Guide

**Status:** ✅ Supported (or ⚠️ Experimental, ❌ Deprecated)

## Overview
- What the tool is
- How it fits in the second_voice ecosystem
- Key strength/differentiator

## Quick Start
- Installation
- Basic setup
- Example invocation

## How [Tool] Discovers Project Instructions
- Looks for CLAUDE.md / GEMINI.md / AGENTS.md / config
- What files it reads

## Configuration
- Config file location(s)
- Environment variables
- Example configuration

## AGENTS.md Workflow Mapping
[Type A (IDEs): Detailed step-by-step]
[Type B (CLIs): Comparison table + notes]
[Type C (Providers): Architecture section]

## Key Capabilities
- What makes this tool unique
- Notable features
- Comparison with alternatives

## Common Patterns & Examples
- Pattern 1: [Use case]
- Pattern 2: [Use case]
- Pattern 3: [Use case]

## Tool-Specific Commands Reference
| Task | Command | Notes |
|------|---------|-------|
| ... | ... | ... |

## Error Handling & Troubleshooting
- Common issues
- Solutions
- Recovery strategies

## Limitations & Constraints
- What it can't do
- Known issues
- Workarounds

## Verification Status
- ✅ [Specific capability verified]
- ✅ [Specific capability verified]

## Quick Reference Card
[Cheat sheet or reference table]
```

---

## 7. Specific Recommendations by File

### claude-code.md
**Status:** ⭐⭐⭐⭐⭐ Excellent - Use as model

**Minor improvements:**
- [ ] Add explicit Status field at top
- [ ] Update title format for consistency
- No other changes needed

### aider.md
**Status:** ⭐⭐⭐ Good - Needs expansion

**Changes needed:**
- [ ] Add explicit Status field at top (✅ Supported)
- [ ] Update title format: "Aider - Interactive Development Guide (Supported)"
- [ ] Add "How Aider Discovers Project Instructions" section
- [ ] Expand "AGENTS.md Workflow - Aider Adaptation" with more examples
- [ ] Add "Tool-Specific Commands Reference" table
- [ ] Add "Error Handling & Troubleshooting" section (currently only in Step D)
- [ ] Add "Verification Status" section
- [ ] Add more complete workflow examples (currently only Step D shown)

**Estimated additions:** ~150-200 lines

### cline.md
**Status:** ⭐⭐⭐⭐ Good - Programmatic focus appropriate

**Minor improvements:**
- [ ] Add "Common Patterns & Examples" section (currently no usage examples)
- [ ] Add "Tool-Specific Commands Reference" table for CLI invocation
- [ ] Expand troubleshooting section
- Keep current structure; it's appropriate for LLM provider

**Estimated additions:** ~50 lines

### codex.md
**Status:** ⭐⭐ Too brief - Needs substantial expansion

**Changes needed:**
- [ ] Double content depth
- [ ] Add "Tool-Specific Commands Reference" table
- [ ] Add "Common Patterns & Examples" section (at least 3 patterns)
- [ ] Expand "Error Handling & Troubleshooting" section
- [ ] Add more details on approval modes
- [ ] Add "Limitations & Constraints" section
- [ ] Restructure following standard template

**Estimated additions:** ~150-200 lines → Target: 250+ lines total

### gemini.md
**Status:** ⭐⭐⭐ Brief but functional - Needs some expansion

**Changes needed:**
- [ ] Add explicit Status field (✅ Supported)
- [ ] Update title format: "Google Gemini - Code Editor Guide (Supported)"
- [ ] Expand "Workflow Mapping" section with examples
- [ ] Add "Common Patterns & Examples" section (currently has 3, expand with detail)
- [ ] Add "Tool-Specific Commands Reference" table
- [ ] Expand "FAQ / Known Issues" to "Error Handling & Troubleshooting"
- [ ] Add context limits and token information

**Estimated additions:** ~80-100 lines → Target: 200+ lines total

---

## 8. Action Items

### Priority 1 (Quick, high-impact)
- [ ] **claude-code.md:** Add Status field + update title (5 min)
- [ ] **aider.md:** Add Status field + update title (5 min)
- [ ] **cline.md:** Add examples section (30 min)
- [ ] **codex.md:** Add missing sections (60 min)
- [ ] **gemini.md:** Add Status field + expand (45 min)

### Priority 2 (Thorough standardization)
- [ ] Create shared template in `docs/tool-specific-guides/README.md`
- [ ] Audit all files against template
- [ ] Create standardized "Quick Reference Card" format

### Priority 3 (Long-term)
- [ ] Add integration tests to verify each tool works
- [ ] Create comparison matrix showing feature support
- [ ] Document tool selection criteria

---

## 9. Summary Table: What Gets Added

| File | Status Field | Title Update | Examples | Ref Table | Troubleshooting | Expansion |
|------|--------------|--------------|----------|-----------|-----------------|-----------|
| claude-code.md | ✅ Add | ✅ Rename | ✅ Keep | ✅ Keep | ✅ Keep | None |
| aider.md | ✅ Add | ✅ Rename | ✅ Expand | ✅ Add | ✅ Add | ~150 lines |
| cline.md | ✅ OK | ✅ OK | ✅ Add | ✅ Add | ✅ Expand | ~50 lines |
| codex.md | ✅ Add | ✅ Rename | ✅ Add | ✅ Add | ✅ Add | ~150 lines |
| gemini.md | ✅ Add | ✅ Rename | ✅ Expand | ✅ Add | ✅ Expand | ~100 lines |

**Total additions:** ~450 lines across 5 files
**Estimated effort:** 4-5 hours for comprehensive standardization
**Risk level:** Low (additive only, no removal)

---

## 10. Template for Tool-Specific Guide Structure (Proposed)

```markdown
# [Tool Name] - [Type] Guide

**Status:** ✅ Supported

> **Type categories:**
> - Interactive Development IDE (Claude Code, Aider)
> - Code Editor CLI (Codex, Gemini)
> - Programmatic LLM Provider (Cline)

## Overview

What the tool is and why it matters for this project.

## Quick Start

Installation, setup, basic usage. 4-10 lines of bash/config.

## How [Tool Name] Discovers Project Instructions

How it finds CLAUDE.md, GEMINI.md, AGENTS.md, etc.

## Configuration

Where config lives, what settings exist, example config.

## [Type-Specific Section]

- **For IDEs:** "AGENTS.md Workflow Mapping" (detailed, step-by-step)
- **For CLIs:** "Workflow Integration" (comparison table, notes)
- **For Providers:** "Architecture & Integration" (how it fits in pipeline)

## Key Capabilities

What makes this tool unique/useful.

## Common Patterns & Examples

3-5 realistic examples showing how to use it.

## Tool-Specific Commands Reference

Quick reference table (like Claude Code has).

## Error Handling & Troubleshooting

What to do when things go wrong.

## Limitations & Constraints

What it can't do, known issues.

## Verification Status

What was tested and confirmed working.

---

[Specific notes, tips, or additional sections as needed]
```

---

## Conclusion

The tool-specific guides are **functional but inconsistent**. They fall into three categories that would benefit from category-specific templates. The main gaps are:

1. **Standardization:** Missing Status field, inconsistent titles
2. **Depth:** Codex and Gemini guides are too brief
3. **Coverage:** Missing examples, command references, troubleshooting in some guides
4. **Structure:** No consistent template to guide future additions

**Recommendation:** Implement Priority 1 items immediately (1-2 hours), then plan Priority 2 standardization in next sprint.
