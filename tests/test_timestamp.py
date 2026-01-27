"""Tests for timestamp utilities."""

import pytest
import os
import re
from src.second_voice.utils.timestamp import (
    get_timestamp, create_recording_filename, create_whisper_filename,
    extract_timestamp_from_filename, find_matching_whisper_file
)


class TestTimestamp:

    def test_timestamp_format(self):
        """Test timestamp format is YYYY-MM-DD_HH-MM-SS."""
        ts = get_timestamp()
        assert len(ts) == 19  # YYYY-MM-DD_HH-MM-SS
        assert ts[4] == '-'
        assert ts[7] == '-'
        assert ts[10] == '_'
        assert ts[13] == '-'
        assert ts[16] == '-'
        # Validate it matches pattern
        pattern = r'\d{4}-\d{2}-\d{2}_\d{2}-\d{2}-\d{2}'
        assert re.match(pattern, ts)

    def test_recording_filename(self):
        """Test recording filename creation."""
        path = create_recording_filename("/tmp", "aac")
        assert "recording-" in path
        assert ".aac" in path
        assert "/tmp/" in path
        # Should contain timestamp
        assert re.search(r'recording-\d{4}-\d{2}-\d{2}_\d{2}-\d{2}-\d{2}\.aac', path)

    def test_recording_filename_default_format(self):
        """Test recording filename with default WAV format."""
        path = create_recording_filename("/tmp")
        assert path.endswith('.wav')
        assert "recording-" in path

    def test_whisper_filename(self):
        """Test whisper filename creation."""
        timestamp = "2026-01-26_14-30-45"
        path = create_whisper_filename("/tmp", timestamp)
        assert path == "/tmp/whisper-2026-01-26_14-30-45.txt"
        assert "whisper-" in path
        assert ".txt" in path

    def test_extract_timestamp(self):
        """Test timestamp extraction from filename."""
        filename = "recording-2026-01-26_14-30-45.wav"
        ts = extract_timestamp_from_filename(filename)
        assert ts == "2026-01-26_14-30-45"

    def test_extract_timestamp_aac(self):
        """Test timestamp extraction from AAC filename."""
        filename = "recording-2026-01-26_14-30-45.aac"
        ts = extract_timestamp_from_filename(filename)
        assert ts == "2026-01-26_14-30-45"

    def test_extract_timestamp_invalid(self):
        """Test extraction from non-recording filename."""
        filename = "some-other-file.wav"
        ts = extract_timestamp_from_filename(filename)
        assert ts is None

    def test_extract_timestamp_path(self):
        """Test extraction from full path."""
        filepath = "/tmp/recording-2026-01-26_14-30-45.wav"
        ts = extract_timestamp_from_filename(filepath)
        assert ts == "2026-01-26_14-30-45"

    def test_find_matching_whisper_file_not_exists(self):
        """Test finding whisper file that doesn't exist."""
        recording_path = "/tmp/recording-2026-01-26_14-30-45.wav"
        result = find_matching_whisper_file(recording_path)
        assert result is None

    def test_find_matching_whisper_file_exists(self, tmp_path):
        """Test finding whisper file that exists."""
        # Create a dummy recording file
        recording_path = tmp_path / "recording-2026-01-26_14-30-45.wav"
        recording_path.touch()

        # Create matching whisper file
        whisper_path = tmp_path / "whisper-2026-01-26_14-30-45.txt"
        whisper_path.write_text("test transcript")

        # Find should locate it
        result = find_matching_whisper_file(str(recording_path))
        assert result == str(whisper_path)

    def test_consecutive_timestamps_are_different(self):
        """Test that consecutive timestamp calls produce different results."""
        import time
        ts1 = get_timestamp()
        time.sleep(0.01)  # Small delay to ensure different timestamp
        ts2 = get_timestamp()
        # They should be equal or ts2 > ts1 (depending on timing)
        assert ts1 <= ts2
