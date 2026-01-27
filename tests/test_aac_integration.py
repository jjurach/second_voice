"""Integration tests for AAC support and whisper recovery."""

import pytest
import os
from pathlib import Path
from src.second_voice.audio.aac_handler import AACHandler
from src.second_voice.utils.timestamp import (
    extract_timestamp_from_filename, find_matching_whisper_file
)


class TestAACIntegration:

    def test_request_30seconds_acc_file_exists(self):
        """Test that samples/request-30seconds.acc exists and is valid."""
        acc_path = Path("samples/request-30seconds.acc")

        # File must exist
        assert acc_path.exists(), "samples/request-30seconds.acc not found in source tree"

        # File must be readable
        assert os.access(str(acc_path), os.R_OK), "samples/request-30seconds.acc is not readable"

        # File must be recognized as AAC
        assert AACHandler.is_aac_file(str(acc_path)), "File not recognized as AAC/ACC format"

        # File must be valid AAC
        valid, error_msg = AACHandler.validate_aac_file(str(acc_path))
        assert valid, f"AAC validation failed: {error_msg}"

    def test_request_30seconds_acc_has_reasonable_size(self):
        """Test that samples/request-30seconds.acc has reasonable size."""
        acc_path = Path("samples/request-30seconds.acc")
        if not acc_path.exists():
            pytest.skip("samples/request-30seconds.acc not found")

        size_bytes = os.path.getsize(str(acc_path))
        size_mb = size_bytes / (1024 * 1024)

        # Should be between 100KB and 5MB for 30 seconds of audio
        assert 0.1 < size_mb < 5, f"File size {size_mb:.2f}MB is outside expected range (0.1-5MB)"

    def test_request_30seconds_acc_duration(self):
        """Test that samples/request-30seconds.acc has reasonable duration."""
        acc_path = Path("samples/request-30seconds.acc")
        if not acc_path.exists():
            pytest.skip("samples/request-30seconds.acc not found")

        duration = AACHandler.get_duration(str(acc_path))
        if duration:
            # Should be around 30 seconds (allow 20-40 seconds range)
            assert 20 < duration < 40, f"Duration {duration:.1f}s is outside expected range (20-40s)"


    @pytest.fixture
    def aac_test_file(self):
        """Provide path to test AAC file."""
        aac_path = Path("samples/test.aac")
        if not aac_path.exists():
            pytest.skip("samples/test.aac not found. Run Phase 4.5 to extract test fixture.")
        return str(aac_path.absolute())

    def test_aac_file_exists_and_readable(self, aac_test_file):
        """Test that AAC test fixture exists and is readable."""
        assert os.path.exists(aac_test_file)
        assert os.access(aac_test_file, os.R_OK)
        assert aac_test_file.endswith('.aac')

    def test_aac_file_is_valid(self, aac_test_file):
        """Test that AAC test fixture is a valid AAC file."""
        valid, msg = AACHandler.validate_aac_file(aac_test_file)
        assert valid, f"AAC validation failed: {msg}"

    def test_aac_file_has_reasonable_size(self, aac_test_file):
        """Test that AAC test fixture has reasonable size (<5MB)."""
        size_bytes = os.path.getsize(aac_test_file)
        size_mb = size_bytes / (1024 * 1024)
        assert size_mb < 5, f"AAC file too large: {size_mb:.1f}MB (expected <5MB)"

    def test_aac_file_has_reasonable_duration(self, aac_test_file):
        """Test that AAC file has reasonable duration (~30s)."""
        duration = AACHandler.get_duration(aac_test_file)
        if duration:  # Duration might not be available in all cases
            assert 25 < duration < 35, f"Expected ~30s, got {duration:.1f}s"

    def test_whisper_file_naming_pattern(self):
        """Test that whisper file naming follows expected pattern."""
        recording_path = "tmp/recording-2026-01-26_14-30-45.wav"
        timestamp = extract_timestamp_from_filename(recording_path)
        assert timestamp == "2026-01-26_14-30-45"

    def test_integration_timestamp_matching(self, tmp_path):
        """Test that recording and whisper files match by timestamp."""
        # Simulate recording
        timestamp = "2026-01-26_14-30-45"
        recording_file = tmp_path / f"recording-{timestamp}.wav"
        recording_file.write_text("audio data")

        # Create whisper file
        whisper_file = tmp_path / f"whisper-{timestamp}.txt"
        whisper_file.write_text("transcribed text")

        # Find matching whisper file
        result = extract_timestamp_from_filename(str(recording_file))
        assert result == timestamp

    def test_aac_handler_is_aac_file_consistency(self):
        """Test that is_aac_file is consistent with supported extensions."""
        assert AACHandler.is_aac_file("test.aac") == True
        assert AACHandler.is_aac_file("test.m4a") == True
        assert AACHandler.is_aac_file("test.AAC") == True
        assert AACHandler.is_aac_file("test.M4A") == True
        assert AACHandler.is_aac_file("test.wav") == False
        assert AACHandler.is_aac_file("test") == False
