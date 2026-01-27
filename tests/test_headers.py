"""Tests for metadata headers."""

import pytest
from src.second_voice.utils.headers import Header, generate_title, infer_project_name


class TestHeader:

    def test_header_creation(self):
        """Test header object creation."""
        header = Header("recording-01.aac", status="Awaiting transformation")
        assert "recording-01.aac" in header.to_string()
        assert "Awaiting transformation" in header.to_string()

    def test_header_with_all_fields(self):
        """Test header with all fields populated."""
        header = Header(
            source="recording-01.aac",
            date="2026-01-26 10:30:00",
            status="Awaiting ingest",
            title="Example Recording",
            project="second-voice"
        )
        header_str = header.to_string(include_title=True, include_project=True)
        assert "recording-01.aac" in header_str
        assert "2026-01-26 10:30:00" in header_str
        assert "Example Recording" in header_str
        assert "second-voice" in header_str

    def test_header_to_string_without_optional_fields(self):
        """Test that optional fields are not included by default."""
        header = Header(
            source="recording.aac",
            title="My Title",
            project="my-project"
        )
        header_str = header.to_string()  # Don't include title/project
        assert "recording.aac" in header_str
        assert "My Title" not in header_str
        assert "my-project" not in header_str

    def test_header_from_string(self):
        """Test parsing header from markdown text."""
        text = """**Source**: recording-01.aac
**Date:** 2026-01-26 10:30:00
**Status:** Awaiting transformation

Some content here"""
        header = Header.from_string(text)
        assert header is not None
        assert header.source == "recording-01.aac"
        assert header.date == "2026-01-26 10:30:00"
        assert header.status == "Awaiting transformation"

    def test_header_from_string_with_all_fields(self):
        """Test parsing header with all fields."""
        text = """**Source**: recording-01.aac
**Date:** 2026-01-26 10:30:00
**Status:** Awaiting ingest
**Title:** Example Title
**Project:** second-voice"""
        header = Header.from_string(text)
        assert header.source == "recording-01.aac"
        assert header.title == "Example Title"
        assert header.project == "second-voice"

    def test_header_from_string_no_header(self):
        """Test that no header is found if source is missing."""
        text = "Just some random text without headers"
        header = Header.from_string(text)
        assert header is None

    def test_generate_title(self):
        """Test title generation."""
        text = "Please implement a new API endpoint for user authentication in the system"
        title = generate_title(text)
        assert len(title) <= 60
        assert title.startswith("Please")
        assert title  # Not empty

    def test_generate_title_max_length(self):
        """Test that title respects max length."""
        text = "This is a very long title that goes on and on and should be truncated at sixty characters or less"
        title = generate_title(text, max_length=60)
        assert len(title) <= 60

    def test_generate_title_with_headers_in_text(self):
        """Test that title skips header lines."""
        text = """**Source**: recording.aac
**Date:** 2026-01-26

This is the actual content to use for title generation"""
        title = generate_title(text)
        assert "**Source**" not in title
        assert "actual content" in title

    def test_infer_project_voice(self):
        """Test project inference for voice-related content."""
        assert infer_project_name("fix the voice transcription system") == "second-voice"
        assert infer_project_name("whisper transcription issues") == "second-voice"

    def test_infer_project_api(self):
        """Test project inference for API-related content."""
        assert infer_project_name("I need a REST API endpoint") == "api"
        assert infer_project_name("implement HTTP request handling") == "api"

    def test_infer_project_ui(self):
        """Test project inference for UI-related content."""
        assert infer_project_name("add a button to the interface") == "ui"
        assert infer_project_name("design the react component") == "ui"

    def test_infer_project_unknown(self):
        """Test that unknown content defaults to 'unknown'."""
        assert infer_project_name("completely unrelated topic xyz") == "unknown"
        assert infer_project_name("") == "unknown"
        assert infer_project_name("abc def ghi") == "unknown"
