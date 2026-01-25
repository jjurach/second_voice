# Google Gemini - Guide (Experimental)

**Status:** ❓ Experimental - Not yet fully tested with this project

This guide is a template for using Google Gemini with AGENTS.md. It will be completed and verified as Gemini support is tested.

## Current Status

- ✅ Gemini can access function calling
- ✅ Gemini supports code understanding
- ⚠️ Git integration unknown
- ⚠️ Approval gate support unknown
- ⚠️ Task tracking unknown
- ❓ File I/O capabilities unknown

## Quick Start (Once Tested)

```bash
# Install Gemini CLI (when available)
pip install gemini-cli  # Or equivalent

# Initialize
cd /path/to/second_voice
gemini-cli

# Example (TBD)
> fix the tests
```

## Known Differences from Claude Code

| Feature | Claude Code | Gemini | Status |
|---------|---|---|---|
| Function calling | ✅ Yes | ✅ Likely | ✅ |
| Code understanding | Good | Good | ? |
| Git integration | Manual | TBD | ❓ |
| Web search | ✅ Yes | ✅ Likely | ✅ |
| MCP servers | ✅ Yes | ❌ Unlikely | ❌ |
| Context window | 200k tokens | 32k typical | ⚠️ |
| Tool syntax | Claude-specific | Different | ⚠️ |

## AGENTS.md Compatibility (TBD)

Assuming Gemini supports similar patterns:

```
Step A: Analyze → Likely works
Step B: Create spec file → Needs function call
Step C: Create plan → Needs function call
Step D: Approval → UNKNOWN - may not have approval gates
Step E: Implement → Likely works
```

## Expected Workflow (Once Verified)

```
1. Start Gemini
2. Request feature with context
3. Gemini analyzes scope
4. Create spec file (via function call)
5. Create plan (via function call)
6. Request approval (mechanism TBD)
7. Implement step-by-step
8. Create change docs
9. Commit changes
```

## What Needs Testing

- [ ] Does Gemini detect project instructions automatically?
- [ ] What's the equivalent of CLAUDE.md for Gemini?
- [ ] How does Gemini handle file operations?
- [ ] Can Gemini make git commits?
- [ ] Does Gemini support approval gates?
- [ ] What's the context window limit?
- [ ] How are tool names/syntax different?
- [ ] Can we use environment detection?

## Configuration (Template)

Once Gemini is tested, create `.gemini-cli.yaml`:

```yaml
project:
  # Reference the workflow
  instructions: |
    This project follows AGENTS.md workflow.
    See docs/ for details.

  # Tool integration
  tools:
    files: true
    git: true
    shell: true

  # Context files
  context-files:
    - AGENTS.md
    - docs/WORKFLOW-MAPPING.md
    - docs/TOOL-SPECIFIC-GUIDES/gemini.md
```

## Contributing to This Guide

**To add Gemini support:**

1. Test Gemini with simple tasks
2. Document what works/doesn't work
3. Update this guide with findings
4. Create `.gemini-cli.yaml` configuration
5. Update TOOLS-CAPABILITIES.md with actual capabilities
6. Submit PR with changes

## For Now

Use **Claude Code** or **Aider** until Gemini support is verified:
- Claude Code: Best for formal approval gates
- Aider: Best for collaborative approach
- Gemini: Coming soon!

## Expected Benefits of Gemini Support

Once tested, Gemini would offer:
- Multimodal input (images, video, audio)
- Fast inference for simpler tasks
- Low-cost alternative to Claude/GPT models
- Good code understanding (expected)

## Questions to Answer

1. **Approval mechanism:** Does Gemini have built-in approval gates like Claude Code?
2. **File operations:** How does Gemini interact with files? Function calls? Tools?
3. **Git workflow:** Can Gemini make commits? How?
4. **Configuration:** What does a `.gemini-cli.yaml` look like?
5. **Tool syntax:** Are function calling conventions different?
6. **Context:** Can Gemini handle ~1300 lines of code per module?
7. **Testing:** Can Gemini run pytest and interpret results?
8. **Documentation:** How to reference AGENTS.md from Gemini?

## Related Documents

- AGENTS.md - Core workflow (all tools)
- TOOLS-CAPABILITIES.md - Capability matrix
- WORKFLOW-MAPPING.md - How AGENTS.md maps to each tool
- claude-code.md - Verified complete guide
- aider.md - Verified complete guide
- FILE-NAMING-CONVENTIONS.md - Which file names matter

## Next Steps

1. Install Gemini CLI when available
2. Test with simple task
3. Document findings
4. Update this guide with actual information
5. Update TOOLS-CAPABILITIES.md
6. Create .gemini-cli.yaml
7. Add more examples

---

**Status:** ⏳ Awaiting testing and implementation
**Last Updated:** 2026-01-25
**Maintainer:** Team (to be assigned)
