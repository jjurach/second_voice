#!/usr/bin/env python3
"""
Faster Whisper API Service
OpenAI-compatible transcription endpoint
"""

import logging
import os
from io import BytesIO

from flask import Flask, request, jsonify
from faster_whisper import WhisperModel

# Configuration from environment
MODEL_NAME = os.getenv("WHISPER_MODEL", "small.en")
COMPUTE_TYPE = os.getenv("WHISPER__COMPUTE_TYPE", "float32")
NUM_WORKERS = int(os.getenv("WHISPER__NUM_WORKERS", "1"))
DEVICE = os.getenv("WHISPER_DEVICE", "cuda")
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

# Setup logging
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Global model instance (loaded once at startup)
model = None


def load_model():
    """Load the Whisper model on startup"""
    global model
    if model is None:
        logger.info(f"Loading {MODEL_NAME} model on device '{DEVICE}'...")
        model = WhisperModel(
            MODEL_NAME,
            device=DEVICE,
            compute_type=COMPUTE_TYPE,
            num_workers=NUM_WORKERS,
        )
        logger.info(f"Model loaded successfully")
    return model


@app.route("/health", methods=["GET"])
def health():
    """Health check endpoint"""
    return jsonify({"status": "ok", "model": MODEL_NAME}), 200


@app.route("/v1/audio/transcriptions", methods=["POST"])
def transcribe():
    """OpenAI-compatible transcription endpoint"""
    try:
        # Check if file is present
        if "file" not in request.files:
            return jsonify({"error": "No file provided"}), 400

        audio_file = request.files["file"]
        if audio_file.filename == "":
            return jsonify({"error": "No file selected"}), 400

        # Get model from request (optional, use default if not specified)
        requested_model = request.form.get("model", MODEL_NAME)
        logger.info(f"Transcription request: file={audio_file.filename}, model={requested_model}")

        # Load model
        whisper_model = load_model()

        # Read audio file into memory
        audio_data = audio_file.read()

        # Transcribe
        logger.debug(f"Starting transcription of {len(audio_data)} bytes")
        segments, info = whisper_model.transcribe(
            BytesIO(audio_data),
            language="en",  # small.en is English-only
            vad_filter=True,
        )

        # Combine segments into single text
        text = " ".join([segment.text.strip() for segment in segments])

        logger.info(f"Transcription completed: {len(text)} characters")

        return jsonify({"text": text}), 200

    except Exception as e:
        logger.error(f"Transcription error: {str(e)}", exc_info=True)
        return jsonify({"error": str(e)}), 500


@app.route("/docs", methods=["GET"])
def docs():
    """Minimal API documentation"""
    return (
        """
        <html>
            <head><title>Whisper Transcription API</title></head>
            <body>
                <h1>Faster Whisper Transcription Service</h1>
                <h2>Endpoint</h2>
                <p><code>POST /v1/audio/transcriptions</code></p>
                <h2>Parameters</h2>
                <ul>
                    <li><code>file</code> (required) - Audio file (multipart/form-data)</li>
                    <li><code>model</code> (optional) - Model name (default: """ + MODEL_NAME + """)</li>
                </ul>
                <h2>Response</h2>
                <pre>{"text": "transcribed text"}</pre>
                <h2>Example</h2>
                <pre>curl -X POST http://localhost:8000/v1/audio/transcriptions \\
  -F "file=@audio.wav" \\
  -F "model=small.en"</pre>
                <h2>Health Check</h2>
                <p><code>GET /health</code></p>
            </body>
        </html>
        """,
        200,
        {"Content-Type": "text/html"},
    )


if __name__ == "__main__":
    # Pre-load model before starting server
    load_model()
    logger.info(f"Starting Whisper API server on 0.0.0.0:8000")
    app.run(host="0.0.0.0", port=8000, threaded=True)
