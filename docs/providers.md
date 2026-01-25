# LLM Provider Architecture

## Overview

Second Voice uses a provider-based architecture to support multiple LLM backends. This allows users to choose between local GPU compute (Ollama) or cloud-based services (OpenRouter) based on their needs and available resources.

## Supported Providers

### Ollama (Local/Remote GPU)

**Use Case:** Local or SSH-tunneled GPU compute

**Pros:**
- Complete privacy (data never leaves your network)
- No per-request costs
- Full control over model selection
- Can run large models if you have VRAM

**Cons:**
- Requires GPU hardware or SSH tunnel to remote GPU
- Setup complexity (Docker, port forwarding)
- Limited to models you can fit in VRAM

**Configuration:**
```json
{
  "ollama": {
    "url": "http://localhost:11434/api/generate",
    "model": "llama-pro"
  }
}
```

**Models:** Any Ollama-compatible model you have pulled locally

### OpenRouter (Cloud API)

**Use Case:** Cloud-based inference with access to many models

**Pros:**
- No local infrastructure required
- Access to cutting-edge models (Claude, GPT-4, etc.)
- Works anywhere with internet
- Pay only for what you use

**Cons:**
- Data sent to third-party (OpenRouter + model provider)
- Per-request costs
- Requires internet connection
- Rate limits based on account tier

**Configuration:**
```json
{
  "openrouter": {
    "api_key": "${OPENROUTER_API_KEY}",
    "model": "anthropic/claude-3.5-sonnet",
    "base_url": "https://openrouter.ai/api/v1"
  }
}
```

**Models:** See [OpenRouter Models](https://openrouter.ai/models) for full list

## Provider Auto-Detection

Second Voice automatically selects the appropriate provider based on configuration:

### Detection Logic
1. **Check for OpenRouter API key:**
   - Environment variable: `OPENROUTER_API_KEY`
   - Config file: `openrouter.api_key`
2. **If API key exists:** Use OpenRouterProvider
3. **If no API key:** Use OllamaProvider (default)

### Override Auto-Detection

Use the `--provider` flag to explicitly choose:

```bash
# Force Ollama even if OpenRouter is configured
second_voice --provider ollama

# Force OpenRouter
second_voice --provider openrouter --api-key sk-or-...
```

## Configuration Guide

### Full Configuration Example

`~/.config/second_voice/settings.json`:

```json
{
  "ollama": {
    "url": "http://localhost:11434/api/generate",
    "model": "llama-pro"
  },

  "openrouter": {
    "api_key": "${OPENROUTER_API_KEY}",
    "model": "anthropic/claude-3.5-sonnet",
    "base_url": "https://openrouter.ai/api/v1"
  },

  "whisper_url": "http://localhost:8000/v1/audio/transcriptions",
  "whisper_model": "small.en"
}
```

### Environment Variables

Set environment variables for sensitive data:

```bash
export OPENROUTER_API_KEY="sk-or-v1-..."
```

The config file can reference environment variables using `${VAR_NAME}` syntax.

### API Key Security

**Best Practices:**
- Use environment variables for API keys
- Never commit API keys to git
- Rotate keys periodically
- API keys are automatically masked in verbose output

## Provider API Differences

### Request Format

**Ollama:**
```python
POST /api/generate
{
  "model": "llama-pro",
  "prompt": "...",
  "system": "...",
  "stream": false
}
```

**OpenRouter (OpenAI-compatible):**
```python
POST /v1/chat/completions
Headers: {"Authorization": "Bearer sk-or-..."}
{
  "model": "anthropic/claude-3.5-sonnet",
  "messages": [
    {"role": "system", "content": "..."},
    {"role": "user", "content": "..."}
  ]
}
```

### Response Format

**Ollama:**
```json
{
  "response": "Generated text here",
  "model": "llama-pro",
  "done": true
}
```

**OpenRouter:**
```json
{
  "choices": [
    {
      "message": {
        "content": "Generated text here"
      }
    }
  ]
}
```

Both are normalized by the provider classes to return plain text.

## Provider Comparison

| Feature | Ollama | OpenRouter |
|---------|--------|------------|
| **Setup Complexity** | High (Docker + GPU) | Low (API key only) |
| **Privacy** | Complete | Data sent to cloud |
| **Cost** | Hardware only | Per-request |
| **Internet Required** | No (or just SSH) | Yes |
| **Model Selection** | Limited by VRAM | 100+ models |
| **Latency** | Low (local GPU) | Network dependent |
| **Reliability** | Self-managed | SLA-backed |

## Crash Log Behavior

When an LLM provider fails, Second Voice saves a crash log to preserve your work:

**Location:** `tmp-crash-{timestamp}.txt`

**Contents:**
```
=== Second Voice Crash Log ===
Timestamp: 2026-01-24 23:45:12
Provider: openrouter
Model: anthropic/claude-3.5-sonnet

=== Original STT Transcription ===
[Your voice-to-text content here]

=== Error Details ===
ProviderAuthError: Invalid API key

=== Stack Trace ===
[Full Python stack trace]
```

**Recovery:**
1. Check the crash log for your transcribed text
2. Fix the issue (reconnect, API key, etc.)
3. Copy text from crash log and process manually or re-record

## Usage Examples

### Basic Usage (Auto-Detect)

```bash
# Uses OpenRouter if OPENROUTER_API_KEY is set, else Ollama
second_voice
```

### Explicit Provider Selection

```bash
# Use Ollama
second_voice --provider ollama --model llama-pro

# Use OpenRouter
second_voice --provider openrouter --model anthropic/claude-3.5-sonnet
```

### Temporary API Key

```bash
# Override config with CLI flag
second_voice --provider openrouter --api-key sk-or-v1-abc123
```

### Verbose Mode (See Provider Info)

```bash
second_voice --verbose
# Output includes:
# Provider: openrouter
# Model: anthropic/claude-3.5-sonnet
# API endpoint: https://openrouter.ai/api/v1/chat/completions
```

## Troubleshooting

### Ollama Issues

**Problem:** Connection refused
```
ProviderConnectionError: Cannot connect to http://localhost:11434
```

**Solutions:**
1. Check SSH tunnel is active: `lsof -i :11434`
2. Verify Docker container running: `docker ps | grep ollama`
3. Test endpoint: `curl http://localhost:11434/api/generate`

**Problem:** Model not found
```
ProviderError: Model 'llama-pro' not found
```

**Solutions:**
1. Pull model: `docker exec -it ollama ollama pull llama-pro`
2. List available models: `docker exec -it ollama ollama list`

### OpenRouter Issues

**Problem:** Authentication failed
```
ProviderAuthError: Invalid API key
```

**Solutions:**
1. Check API key format starts with `sk-or-v1-`
2. Verify key in environment: `echo $OPENROUTER_API_KEY`
3. Get new key: https://openrouter.ai/keys
4. Check account status (suspended, credits)

**Problem:** Rate limited
```
ProviderError: Rate limit exceeded (HTTP 429)
```

**Solutions:**
1. Wait for rate limit reset
2. Upgrade OpenRouter account tier
3. Implement retry logic (future enhancement)

**Problem:** Model not available
```
ProviderError: Model 'anthropic/claude-3.5-sonnet' not available
```

**Solutions:**
1. Check model list: https://openrouter.ai/models
2. Verify model ID spelling
3. Check account permissions for model access

## Adding New Providers

For developers who want to add additional providers:

### 1. Create Provider Class

Create `src/second_voice/engine/providers/yourprovider.py`:

```python
from .base import BaseLLMProvider, ProviderError

class YourProvider(BaseLLMProvider):
    def __init__(self, config):
        self.config = config.get('yourprovider', {})
        self.url = self.config.get('url')
        self.model = self.config.get('model')

    def process(self, prompt, system_prompt="", context=""):
        # Your implementation here
        pass

    def validate_config(self):
        # Check required config fields
        pass

    def is_available(self):
        # Test connectivity
        pass

    def get_provider_name(self):
        return "yourprovider"
```

### 2. Register in Factory

Update `get_provider()` in `providers/__init__.py`:

```python
def get_provider(config, provider_name=None):
    if provider_name == 'yourprovider':
        from .yourprovider import YourProvider
        return YourProvider(config)
    # ... existing providers
```

### 3. Add Tests

Create tests in `tests/test_providers.py` following existing patterns.

### 4. Update Documentation

Add provider documentation to this file and update README.md.

## API Reference

See implementation reference in `docs/implementation-reference.md` for complete code examples.
