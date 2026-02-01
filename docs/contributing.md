# Contributing to Second Voice

Thank you for your interest in contributing to Second Voice!

## Code Quality Standards

This project follows the **Agent Kernel** code quality standards. See:

- **[Python Definition of Done](system-prompts/languages/python/definition-of-done.md)** - Code quality standards
- **[Definition of Done](definition-of-done.md)** - Project-specific requirements

## Development Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/jamesjurach/second_voice.git
   cd second_voice
   ```

2. **Create and activate a virtual environment:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   pip install -e .
   ```

## Workflow

AI agents MUST follow the **[AGENTS.md](../AGENTS.md)** workflow.

## Running Tests

We use `pytest` for testing.

```bash
# Run all tests
pytest

# Run tests with coverage
pytest --cov=second_voice
```

## Pull Request Process

1. Ensure all tests pass.
2. Follow the commit message format: `type: description` (e.g., `feat: add whisper recovery`).
3. Include the `Co-Authored-By` trailer if assisted by an AI agent.

---
Last Updated: 2026-02-01
