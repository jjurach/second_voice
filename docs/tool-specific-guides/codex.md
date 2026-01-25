# OpenAI Codex / GPT-4 - Guide (Experimental)

**Status:** ❓ Experimental - Not yet fully tested with this project

This guide is a template for using OpenAI Codex/GPT-4 with AGENTS.md. It will be completed and verified as Codex support is tested.

## Current Status

- ✅ Codex/GPT-4 can access function calling
- ✅ Codex has excellent code understanding
- ⚠️ CLI integration unknown
- ⚠️ Approval gate support unknown
- ⚠️ Task tracking unknown
- ⚠️ Git integration unknown

## Quick Start (Once Tested)

```bash
# Install OpenAI CLI (if available)
pip install openai-codex  # Or equivalent

# Initialize
cd /path/to/second_voice
openai-codex  # Or similar command

# Example (TBD)
> fix the tests
```

## Known Capabilities

| Feature | Codex | Status |
|---------|-------|--------|
| Function calling | ✅ Yes | ✅ |
| Code understanding | ✅ Excellent | ✅ |
| Code generation | ✅ Excellent | ✅ |
| Git integration | ❓ Unknown | ❓ |
| Web search | ⚠️ Maybe (requires setup) | ⚠️ |
| Approval gates | ❓ Unknown | ❓ |
| Task tracking | ❓ Unknown | ❓ |
| Context window | ~8k tokens | ⚠️ Lower |
| CLI tool | ❌ No official CLI | ⚠️ |

## Key Differences from Claude Code

```
Claude Code:
- Official Anthropic tool
- CLAUDE.md auto-discovery
- Approval gates built-in
- MCP server support

Codex/GPT-4:
- OpenAI tool (no official CLI)
- Approval gates unknown
- May need custom integration
- Different function syntax
```

## AGENTS.md Compatibility (TBD)

Assuming similar function calling support:

```
Step A: Analyze → Likely works
Step B: Create spec file → Via function call
Step C: Create plan → Via function call
Step D: Approval → Unknown - may need custom handling
Step E: Implement → Likely works
```

## Expected Workflow (Hypothetical)

```
1. Initialize Codex/GPT-4 integration
2. Request feature with context
3. Codex analyzes and creates spec
4. Codex creates plan
5. Request approval (mechanism TBD)
6. Implement step-by-step
7. Create change documentation
8. Make git commits
9. Verify completion
```

## Configuration (Template)

Once Codex is supported, might look like:

```yaml
# .openai-cli.yaml (if it exists)
project:
  api-key: ${OPENAI_API_KEY}

  instructions: |
    This project follows AGENTS.md workflow.
    See docs/ for details.

  model: gpt-4  # or gpt-4-turbo

  context:
    - AGENTS.md
    - docs/workflow-mapping.md
    - docs/tool-specific-guides/codex.md
```

## What Needs Testing

- [ ] Is there an official OpenAI CLI tool?
- [ ] How does it handle file operations?
- [ ] Does it support git commands?
- [ ] What's the approval mechanism?
- [ ] How are functions/tools named and called?
- [ ] Context window limitations (8k vs 16k vs 128k)?
- [ ] Web search integration?
- [ ] How to reference AGENTS.md?

## Challenges to Address

1. **No Official CLI:** OpenAI doesn't provide an official CLI like Claude Code
   - May need third-party wrapper
   - May need custom integration
   - API access via openai package

2. **Lower Context Window:** 8k tokens is limiting
   - May need to select relevant files
   - May need to use file references instead of inline content
   - Larger projects challenging

3. **Function Syntax:** OpenAI's function calling differs from Claude
   - Different parameter names
   - Different response format
   - May need translation layer

4. **Approval Mechanism:** Unknown if built-in support exists
   - May need to implement manually
   - Conversational approval may be only option

## Possible Integration Approaches

### Approach 1: API-Direct Integration
```python
import openai

openai.api_key = "sk-..."
response = openai.ChatCompletion.create(
    model="gpt-4",
    messages=[...],
    functions=[...]  # Function definitions
)
```

### Approach 2: Aider-Like Wrapper
Build a CLI wrapper similar to Aider that:
- Communicates with OpenAI API
- Manages files
- Handles git
- Implements approval gates

### Approach 3: Use Third-Party CLI
Find or build a third-party Codex CLI tool that:
- Wraps OpenAI API
- Provides user interface
- Manages project context

## Expected Advantages (If Implemented)

- ✅ Very fast code generation
- ✅ Excellent code understanding
- ✅ Lower cost than some alternatives
- ✅ Mature API and documentation
- ✅ Large community

## Expected Disadvantages

- ❌ No official CLI tool
- ❌ Smaller context window (8k tokens)
- ❌ Higher latency than some (API-based)
- ❌ Fewer built-in integrations
- ❌ Approval gates need custom implementation

## Contributing to This Guide

**To add Codex support:**

1. Research OpenAI CLI options
2. Choose integration approach
3. Build proof of concept
4. Test with simple tasks
5. Document findings
6. Update this guide
7. Create configuration file
8. Update tools-capabilities.md
9. Submit PR

## For Now

Use **Claude Code** or **Aider** until Codex support is verified:
- Claude Code: Best for formal workflows
- Aider: Best for collaborative approach
- Codex: Coming when integration is available

## Questions to Answer

1. **CLI Tool:** Is there an official OpenAI CLI? (As of 2026)
2. **Integration:** What's the best way to integrate with this project?
3. **Functions:** How to define file operations as functions?
4. **Approval:** How to implement approval gates?
5. **Context:** How to manage small context window?
6. **Git:** How to make commits via OpenAI API?
7. **Config:** What should `.openai-cli.yaml` look like?
8. **Testing:** Can it run pytest and understand output?

## Related Documents

- AGENTS.md - Core workflow (all tools)
- tools-capabilities.md - Capability matrix
- workflow-mapping.md - How AGENTS.md maps to each tool
- claude-code.md - Verified complete guide
- aider.md - Verified complete guide
- file-naming-conventions.md - Which file names matter

## Next Steps

1. Research current OpenAI CLI offerings (as of 2026)
2. Evaluate integration approaches
3. Build proof of concept
4. Test with this project
5. Update guide with findings
6. Create configuration file
7. Update capability matrix

---

**Status:** ⏳ Awaiting investigation and implementation
**Last Updated:** 2026-01-25
**Maintainer:** Team (to be assigned)
