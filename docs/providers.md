# Provider Architecture Guide

## Overview

Second Voice uses a dual provider architecture supporting both Speech-to-Text (STT) and Language Model (LLM) processing. You can choose providers based on your privacy requirements, infrastructure availability, and use case.

**Key Principle:** Local providers offer complete data sovereignty - your audio and text never leave your control. Cloud providers offer convenience and zero-infrastructure setup.

---

## Provider Philosophy: Privacy First

### Privacy-First (Recommended for Sensitive Work)

**Local Whisper + Ollama**
- ✅ Complete data sovereignty
- ✅ No external dependencies after setup
- ✅ Ideal for medical, legal, proprietary work
- ✅ One-time setup cost, no ongoing fees

### Convenience Option (Quick Start)

**Groq + OpenRouter**
- ✅ Zero infrastructure - works in 2 minutes
- ✅ Groq offers generous free tier
- ✅ OpenRouter pay-as-you-go (no minimum)
- ✅ Access to latest models

### Hybrid Approaches

Mix and match based on needs:
- **Local STT + Cloud LLM:** Keep audio private, use cloud for text processing
- **Cloud STT + Local LLM:** Quick transcription, private LLM processing

---

## STT (Speech-to-Text) Providers

### Local Whisper (Privacy-First)

**When to use:**
- Working with sensitive/confidential audio
- Medical, legal, or proprietary conversations
- Already have GPU infrastructure
- Want complete control over data

**Benefits:**
- ✅ Audio never leaves your network
- ✅ No per-request costs
- ✅ No internet required (after setup)
- ✅ Full control over model and performance

    "url": "http://localhost:9090/v1/audio/transcriptions",
    "model": "small.en"
  }
}
```

**Docker Setup:**
```yaml
services:
  whisper:
    image: fedirz/faster-whisper-server:latest-cuda
          ports: ["9090:9090"]    environment:
      - WHISPER_MODEL=small.en
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              capabilities: [gpu]
```

**SSH Tunnel (for remote GPU):**
```bash
    ssh -N -L 9090:localhost:9090 your-server```

**Models:** small.en, medium.en, large-v3 (based on VRAM)

---

### Groq (Free Tier, Fast Cloud)

**When to use:**
- Quick start without infrastructure
- Testing Second Voice
- Don't work with sensitive data
- Want extremely fast transcription

**Benefits:**
- ✅ Generous free tier
- ✅ Sub-second transcription (very fast)
- ✅ Zero setup required
- ✅ OpenAI-compatible API

**Setup:**
```json
{
  "groq": {
    "api_key": "${GROQ_API_KEY}",
    "model": "whisper-large-v3"
  }
}
```

**Get API Key:** https://console.groq.com/keys

**Environment Variable:**
```bash
export GROQ_API_KEY="gsk_..."
```

**Cost:** Free tier available, then pay-as-you-go

---

### OpenAI (Official, Paid)

**When to use:**
- Need highest reliability
- Enterprise use with budget
- Already using OpenAI services

**Benefits:**
- ✅ Most reliable commercial option
- ✅ Official Whisper implementation
- ✅ Good uptime SLA

**Setup:**
```json
{
  "openai": {
    "api_key": "${OPENAI_API_KEY}",
    "model": "whisper-1"
  }
}
```

**Get API Key:** https://platform.openai.com/api-keys

**Cost:** ~$0.006 per minute of audio

---

## LLM (Language Model) Providers

### Ollama (Privacy-First)

**When to use:**
- Working with proprietary/confidential text
- Medical, legal, or sensitive content
- Already have GPU infrastructure
- Want full control over model behavior

**Benefits:**
- ✅ Text never leaves your network
- ✅ No per-request costs
- ✅ Full model control and customization
- ✅ No rate limits

**Setup:**
```json
{
  "ollama": {
    "url": "http://localhost:11434/api/generate",
    "model": "llama-pro"
  }
}
```

**Docker Setup:**
```yaml
services:
  ollama:
    image: ollama/ollama:latest
    ports: ["11434:11434"]
    volumes:
      - ./ollama:/root/.ollama
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              capabilities: [gpu]
```

**Pull Models:**
```bash
docker exec -it ollama ollama pull llama-pro
docker exec -it ollama ollama pull mistral
```

**SSH Tunnel (for remote GPU):**
```bash
ssh -N -L 11434:localhost:11434 your-server
```

---

### OpenRouter (Cloud, Many Models)

**When to use:**
- Quick start without infrastructure
- Want access to Claude, GPT-4, etc.
- Occasional use
- Testing different models

**Benefits:**
- ✅ Access to 100+ models
- ✅ No infrastructure needed
- ✅ Pay only for what you use
- ✅ Latest models available

**Setup:**
```json
{
  "openrouter": {
    "api_key": "${OPENROUTER_API_KEY}",
    "model": "anthropic/claude-3.5-sonnet",
    "base_url": "https://openrouter.ai/api/v1"
  }
}
```

**Get API Key:** https://openrouter.ai/keys

**Popular Models:**
- `anthropic/claude-3.5-sonnet` (best quality)
- `meta-llama/llama-3.1-70b-instruct` (good balance)
- `google/gemini-pro` (fast, affordable)

**Cost:** Varies by model, see https://openrouter.ai/models

---

## Provider Auto-Detection

Second Voice automatically selects appropriate providers based on available API keys:

### STT Auto-Detection Priority

1. **Check for `GROQ_API_KEY`** → Use Groq
2. **Check for `OPENAI_API_KEY`** → Use OpenAI
3. **Default** → Use Local Whisper

### LLM Auto-Detection Priority

1. **Check for `OPENROUTER_API_KEY`** → Use OpenRouter
2. **Default** → Use Ollama

### Override Auto-Detection

Use CLI flags to explicitly choose providers:

```bash
# Force specific providers
second_voice --stt-provider local --llm-provider ollama

# Mix providers
second_voice --stt-provider groq --llm-provider ollama
```

---

## Complete Configuration Examples

### Privacy-First Setup

**~/.config/second_voice/settings.json:**
```json
{
  "local_whisper": {
    "url": "http://localhost:9090/v1/audio/transcriptions",
    "model": "medium.en"
  },
  "ollama": {
    "url": "http://localhost:11434/api/generate",
    "model": "llama-pro"
  }
}
```

**Usage:**
```bash
# Auto-detects local providers
second_voice
```

**Benefits:**
- Complete data sovereignty
- No external dependencies
- Zero ongoing costs
- Ideal for sensitive work

---

### Zero-Infrastructure Quick Start

**Environment Variables:**
```bash
export GROQ_API_KEY="gsk_..."
export OPENROUTER_API_KEY="sk-or-..."
```

**Usage:**
```bash
# Auto-detects cloud providers
second_voice
```

**Benefits:**
- Works in 2 minutes
- No Docker/GPU required
- Groq free tier available
- Great for trying Second Voice

---

### Hybrid: Private Audio, Cloud LLM

**Config + Environment:**
```json
{
  "local_whisper": {
    "url": "http://localhost:9090/v1/audio/transcriptions",
    "model": "small.en"
  }
}
```
```bash
export OPENROUTER_API_KEY="sk-or-..."
```

**Usage:**
```bash
second_voice --stt-provider local --llm-provider openrouter
```

**Benefits:**
- Audio stays private (local transcription)
- Text processing uses powerful cloud models
- Good middle ground

---

## Provider Comparison Tables

### STT Provider Comparison

| Feature | Local Whisper | Groq | OpenAI |
|---------|---------------|------|--------|
| **Privacy** | ✅ Complete | ❌ Cloud | ❌ Cloud |
| **Setup** | Medium (Docker + GPU) | Easy (API key) | Easy (API key) |
| **Cost** | Hardware only | Free tier | ~$0.006/min |
| **Speed** | GPU-dependent | Very Fast | Fast |
| **Internet** | Not required | Required | Required |
| **Best For** | Sensitive audio | Quick start | Enterprise |

### LLM Provider Comparison

| Feature | Ollama | OpenRouter |
|---------|--------|------------|
| **Privacy** | ✅ Complete | ❌ Cloud |
| **Setup** | Medium (Docker + GPU) | Easy (API key) |
| **Cost** | Hardware only | Pay-per-use |
| **Models** | Local models | 100+ models |
| **Latency** | Low (local) | Network-dependent |
| **Best For** | Proprietary work | Model variety |

---

## CLI Reference

### Bifurcated Command-Line Options

**STT (Speech-to-Text) Options:**
```bash
--stt-provider {local,groq,openai}  # Override auto-detection
--stt-model MODEL                    # Model name (whisper-large-v3, whisper-1, etc.)
--stt-api-key KEY                    # API key for cloud providers
--stt-url URL                        # Local Whisper URL
```

**LLM (Language Model) Options:**
```bash
--llm-provider {ollama,openrouter}   # Override auto-detection
--llm-model MODEL                    # Model name (llama-pro, claude-3.5-sonnet, etc.)
--llm-api-key KEY                    # API key for OpenRouter
--llm-url URL                        # Ollama URL
```

**General Options:**
```bash
--verbose                            # Show provider info and timings
--debug                              # Show full request/response details
--config PATH                        # Custom config file
```

### Usage Examples

**Privacy-first (all local):**
```bash
second_voice --stt-provider local --llm-provider ollama
```

**Quick start (all cloud):**
```bash
second_voice --stt-provider groq --llm-provider openrouter
```

**Specific models:**
```bash
second_voice \
  --stt-provider groq --stt-model whisper-large-v3 \
  --llm-provider openrouter --llm-model anthropic/claude-3.5-sonnet
```

**Override API keys:**
```bash
second_voice \
  --stt-api-key gsk_... \
  --llm-api-key sk-or-...
```

---

## Troubleshooting

### STT Provider Issues

**Local Whisper: Connection Refused**
```
   STTProviderConnectionError: Cannot connect to http://localhost:9090```
**Solutions:**
   1. Check SSH tunnel: `lsof -i :9090`2. Verify Docker: `docker ps | grep whisper`
   3. Test endpoint: `curl http://localhost:9090/health`
**Groq: Authentication Failed**
```
STTProviderAuthError: Invalid API key
```
**Solutions:**
1. Check key format: starts with `gsk_`
2. Verify env var: `echo $GROQ_API_KEY`
3. Get new key: https://console.groq.com/keys

**OpenAI: Rate Limited**
```
STTProviderError: Rate limit exceeded (HTTP 429)
```
**Solutions:**
1. Wait for rate limit reset
2. Upgrade OpenAI account tier
3. Use Groq instead (higher limits)

### LLM Provider Issues

**Ollama: Model Not Found**
```
ProviderError: Model 'llama-pro' not found
```
**Solutions:**
1. Pull model: `docker exec -it ollama ollama pull llama-pro`
2. List models: `docker exec -it ollama ollama list`

**OpenRouter: Invalid API Key**
```
ProviderAuthError: Invalid API key
```
**Solutions:**
1. Check key format: starts with `sk-or-v1-`
2. Verify env var: `echo $OPENROUTER_API_KEY`
3. Get new key: https://openrouter.ai/keys

---

## API Key Security

### Best Practices

1. **Use environment variables** for API keys
2. **Never commit** keys to version control
3. **Rotate keys** periodically
4. **Monitor usage** for unexpected activity

### API Key Masking

Second Voice automatically masks API keys in output:

**Verbose Mode:**
```
STT Provider: groq
API Key: gsk_***********xyz (masked)
```

**Debug Mode:**
```
Authorization: Bearer gsk_***********xyz (masked)
```

---

## Adding New Providers

For developers who want to add additional providers, see the implementation guide in `docs/implementation-reference.md`.

**Provider Pattern:**
1. Create provider class inheriting from `BaseSTTProvider` or `BaseLLMProvider`
2. Implement required methods: `process()`, `validate_config()`, `is_available()`
3. Register in provider factory
4. Add tests
5. Update documentation

---

## Further Reading

- **Architecture:** See `docs/architecture.md` for data flow diagrams
- **Implementation:** See `docs/implementation-reference.md` for code templates
- **Quick Start:** See `README.md` for step-by-step setup
