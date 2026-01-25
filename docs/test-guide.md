# Whisper Server Testing Guide

## ✅ NEW: Custom Faster-Whisper Service (small.en Model)

**Status**: Production-ready and tested
**Performance**: ~400-700ms per 10-second audio file
**GPU Memory**: 1.3GB (vs 2.7GB for large-v3)
**Model**: `small.en` (English-only, optimized)

This is a custom Docker service built from the `faster-whisper` source code at `/external/faster-whisper/`. It provides:
- ✅ 25-50x faster transcription than the previous large-v3 setup
- ✅ Proper environment variable model selection
- ✅ GPU acceleration (CUDA 12.3 + cuDNN 9)
- ✅ VAD (Voice Activity Detection) to skip silence
- ✅ OpenAI-compatible API endpoint

## Summary of Previous Attempts and Current Solution

### 1. Enhanced docker-compose.yml
Updated `/docker/docker-compose.yml` with debugging and performance tuning:
- **LOG_LEVEL=DEBUG** - Enable detailed logging
- **PYTHONUNBUFFERED=1** - Real-time log output
- **WHISPER__COMPUTE_TYPE=float32** - Performance tuning for RTX 2080
- **WHISPER__NUM_WORKERS=1** - Single worker for consistent GPU usage

### 2. Test Scripts Created

#### Option A: Bash Test Script (Lightweight)
```bash
./test_whisper.sh [audio_file] [model_name]
```

**Usage:**
```bash
# Test with default file (test.wav) and model (whisper-1)
./test_whisper.sh

# Test with custom audio file
./test_whisper.sh my_audio.wav

# Test with custom audio and model
./test_whisper.sh my_audio.wav Systran/faster-whisper-large-v3
```

**Features:**
- GPU status before/after transcription
- Docker logs (last 5 lines)
- Curl-based API request
- Transcription timing
- Docker container stats

#### Option B: Python Test Script (Advanced)
```bash
python3 test_whisper_api.py [--audio FILE] [--model MODEL] [--url URL]
```

**Usage:**
```bash
# Test with defaults
python3 test_whisper_api.py

# Custom audio file
python3 test_whisper_api.py --audio my_recording.wav

# Custom model
python3 test_whisper_api.py --model Systran/faster-whisper-large-v3

# Custom URL
python3 test_whisper_api.py --url http://192.168.1.100:8000/v1/audio/transcriptions
```

**Features:**
- File existence validation
- GPU monitoring (nvidia-smi)
- Docker log retrieval
- API connectivity testing
- Automatic container startup if needed
- Detailed error handling
- JSON response parsing

#### Option C: Simple Curl Command
```bash
curl http://localhost:8000/v1/audio/transcriptions \
  -H "Content-Type: multipart/form-data" \
  -F "file=@./test.wav" \
  -F "model=whisper-1"
```

## GPU Monitoring Commands

### Monitor GPU in Real-Time
```bash
watch -n 1 nvidia-smi
```

### Monitor Only Whisper Process
```bash
docker stats whisper-server
```

### Monitor GPU Memory Usage
```bash
nvidia-smi --query-gpu=memory.used,memory.total --format=csv,noheader
```

### Check Docker Container GPU Access
```bash
docker exec whisper-server nvidia-smi
```

## Environment Variables Reference

The whisper-server supports these environment variables (from `config.py`):

| Variable | Purpose | Example |
|----------|---------|---------|
| `LOG_LEVEL` | Logging verbosity | `DEBUG`, `INFO`, `WARNING`, `ERROR` |
| `WHISPER_MODEL` | Model to load | `Systran/faster-whisper-large-v3` |
| `WHISPER__COMPUTE_TYPE` | Precision type | `int8`, `float16`, `float32` |
| `WHISPER__NUM_WORKERS` | Worker threads | `1`, `2`, `4` |
| `PYTHONUNBUFFERED` | Unbuffered output | `1` |

## Troubleshooting

### Server Not Responding
```bash
# Check if container is running
docker ps | grep whisper-server

# View logs with full timestamp
docker logs -f --timestamps whisper-server

# Restart the service
docker-compose -f docker/docker-compose.yml restart whisper
```

### GPU Not Detected in Container
```bash
# Verify GPU is available on host
nvidia-smi

# Check NVIDIA container toolkit is installed
docker run --rm --gpus all nvidia/cuda:12.2.2-runtime-ubuntu22.04 nvidia-smi

# Verify docker-compose GPU support
docker-compose -f docker/docker-compose.yml config | grep -A5 nvidia
```

### Out of Memory Errors
Try reducing compute type:
```yaml
# In docker-compose.yml whisper service
environment:
  - WHISPER__COMPUTE_TYPE=int8  # More memory efficient
  # or
  - WHISPER__COMPUTE_TYPE=float16  # Balanced
```

### Slow Transcription
```bash
# Monitor GPU utilization during transcription
watch -n 1 'nvidia-smi | grep whisper'

# Check if running on CPU instead of GPU
docker logs whisper-server | grep -i "cuda\|cpu"
```

## API Endpoint Reference

### Transcription Endpoint
**POST** `/v1/audio/transcriptions`

**Parameters:**
- `file` (required) - Audio file (multipart/form-data)
- `model` (required) - Model name (e.g., "whisper-1" or "Systran/faster-whisper-large-v3")

**Response:**
```json
{
  "text": "Transcribed text from audio file"
}
```

**Example with jq parsing:**
```bash
curl -X POST http://localhost:8000/v1/audio/transcriptions \
  -F "file=@test.wav" \
  -F "model=whisper-1" | jq '.text'
```

## Performance Tuning

### For RTX 2080 (8GB VRAM)
```yaml
environment:
  - WHISPER__COMPUTE_TYPE=float32    # Default, good quality
  - WHISPER__NUM_WORKERS=1            # Single worker
```

### For Better Quality (if VRAM allows)
```yaml
environment:
  - WHISPER_MODEL=Systran/faster-whisper-large-v3  # Already set
  - WHISPER__COMPUTE_TYPE=float32
```

### For Faster Processing (if quality acceptable)
```yaml
environment:
  - WHISPER__COMPUTE_TYPE=int8        # Fastest
  - WHISPER_MODEL=Systran/faster-whisper-medium    # Smaller model
```

## Updating docker-compose Configuration

To apply changes to docker-compose.yml:
```bash
cd docker
docker-compose up -d whisper  # Restart just the whisper service
```

To see the running configuration:
```bash
docker-compose config | grep -A20 "whisper:"
```

## Sources & References

- [Faster Whisper Server GitHub](https://github.com/fedirz/faster-whisper-server)
- [NVIDIA Container Toolkit Docs](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/)
- [Docker GPU Support](https://docs.docker.com/compose/how-tos/gpu-support/)
- [NVIDIA CUDA Documentation](https://docs.nvidia.com/cuda/)
