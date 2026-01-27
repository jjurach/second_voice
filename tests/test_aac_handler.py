"""Tests for AAC audio handling."""

import pytest
import os
import tempfile
from pathlib import Path
from src.second_voice.audio.aac_handler import AACHandler


class TestAACHandler:

    def test_is_aac_file(self):
        """Test AAC file detection."""
        assert AACHandler.is_aac_file("recording.aac")
        assert AACHandler.is_aac_file("song.m4a")
        assert AACHandler.is_aac_file("RECORDING.AAC")  # Case insensitive
        assert not AACHandler.is_aac_file("audio.wav")
        assert not AACHandler.is_aac_file("audio.mp3")
        assert not AACHandler.is_aac_file("audio.flac")

    def test_validate_nonexistent_file(self):
        """Test validation of missing file."""
        valid, msg = AACHandler.validate_aac_file("/nonexistent/file.aac")
        assert not valid
        assert "not found" in msg.lower()

    def test_validate_unreadable_file(self):
        """Test validation of unreadable file."""
        with tempfile.NamedTemporaryFile(suffix='.aac', delete=False) as tmp:
            tmp_path = tmp.name

        try:
            # Make file unreadable
            os.chmod(tmp_path, 0o000)
            valid, msg = AACHandler.validate_aac_file(tmp_path)
            assert not valid
            assert "not readable" in msg.lower()
        finally:
            # Clean up
            os.chmod(tmp_path, 0o644)
            os.unlink(tmp_path)

    def test_validate_invalid_aac(self):
        """Test validation of invalid AAC file."""
        with tempfile.NamedTemporaryFile(suffix='.aac', delete=False) as tmp:
            # Write garbage data
            tmp.write(b"This is not an AAC file")
            tmp_path = tmp.name

        try:
            valid, msg = AACHandler.validate_aac_file(tmp_path)
            assert not valid
            assert "invalid" in msg.lower() or "error" in msg.lower()
        finally:
            os.unlink(tmp_path)

    def test_supported_extensions(self):
        """Test that supported extensions list is correct."""
        assert '.aac' in AACHandler.SUPPORTED_EXTENSIONS
        assert '.m4a' in AACHandler.SUPPORTED_EXTENSIONS
        assert '.acc' in AACHandler.SUPPORTED_EXTENSIONS  # ADTS AAC format
        assert len(AACHandler.SUPPORTED_EXTENSIONS) == 3
