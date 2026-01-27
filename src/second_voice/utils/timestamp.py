"""Timestamp utilities for file naming and logging."""

from datetime import datetime
from pathlib import Path
import os


def get_timestamp() -> str:
    """Get current timestamp in format YYYY-MM-DD_HH-MM-SS."""
    return datetime.now().strftime("%Y-%m-%d_%H-%M-%S")


def create_recording_filename(tmp_dir: str, format: str = "wav") -> str:
    """Create timestamped recording filename.

    Args:
        tmp_dir: Temporary directory path
        format: Audio format (default: 'wav')

    Returns:
        str: Full path to recording file
        Example: /tmp/recording-2026-01-26_14-30-45.wav
    """
    timestamp = get_timestamp()
    filename = f"recording-{timestamp}.{format}"
    return os.path.join(tmp_dir, filename)


def create_whisper_filename(tmp_dir: str, timestamp: str) -> str:
    """Create timestamped whisper output filename.

    Args:
        tmp_dir: Temporary directory path
        timestamp: Recording timestamp (for matching)

    Returns:
        str: Full path to whisper output file
        Example: /tmp/whisper-2026-01-26_14-30-45.txt
    """
    filename = f"whisper-{timestamp}.txt"
    return os.path.join(tmp_dir, filename)


def extract_timestamp_from_filename(filename: str) -> str:
    """Extract timestamp from recording filename.

    Args:
        filename: Recording filename

    Returns:
        str: Timestamp in YYYY-MM-DD_HH-MM-SS format
        Example: "2026-01-26_14-30-45" from "recording-2026-01-26_14-30-45.wav"
    """
    # Extract pattern: recording-<TIMESTAMP>.ext
    name_only = Path(filename).stem  # Remove extension
    if name_only.startswith('recording-'):
        return name_only[10:]  # Remove 'recording-' prefix
    return None


def find_matching_whisper_file(recording_path: str) -> str:
    """Find whisper output file matching a recording.

    Args:
        recording_path: Path to recording file

    Returns:
        str: Path to matching whisper file, or None if not found
    """
    timestamp = extract_timestamp_from_filename(recording_path)
    if not timestamp:
        return None

    tmp_dir = os.path.dirname(recording_path)
    whisper_path = create_whisper_filename(tmp_dir, timestamp)

    return whisper_path if os.path.exists(whisper_path) else None
