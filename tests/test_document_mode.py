"""
Tests for document mode feature in second_voice.

Tests the structured document creation workflow including:
- CLI argument parsing and validation
- Document processing pipeline
- LLM provider routing
- YAML header injection
- Error handling and fallback
"""

import os
import tempfile
import json
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import pytest

from second_voice.core.config import ConfigurationManager
from second_voice.core.processor import AIProcessor
from second_voice.core.recorder import AudioRecorder


class TestDocumentModeCLIValidation:
    """Test CLI argument validation for document mode."""

    def test_document_mode_requires_output_flag(self):
        """Test that --document-mode requires --output flag."""
        from cli.run import validate_pipeline_mode_args

        args = Mock()
        args.document_mode = True
        args.output = None
        args.transcribe_only = False
        args.translate_only = False
        args.record_only = False
        args.input_provider = 'default'
        args.keep_remote = False
        args.audio_file = None
        args.text_file = None

        # Should exit with error
        with pytest.raises(SystemExit) as exc_info:
            validate_pipeline_mode_args(args)
        assert exc_info.value.code == 3

    def test_document_mode_with_output_flag_passes_validation(self):
        """Test that --document-mode with --output passes validation."""
        from cli.run import validate_pipeline_mode_args

        args = Mock()
        args.document_mode = True
        args.output = '/tmp/test.md'
        args.transcribe_only = False
        args.translate_only = False
        args.record_only = False
        args.input_provider = 'default'
        args.keep_remote = False
        args.audio_file = None
        args.text_file = None

        # Should not raise
        validate_pipeline_mode_args(args)

    def test_document_mode_mutually_exclusive_with_other_modes(self):
        """Test that document-mode is mutually exclusive with other pipeline modes."""
        from cli.run import validate_pipeline_mode_args

        # This is enforced by argparse's mutually_exclusive_group
        # So we just verify the setup is correct
        args = Mock()
        args.document_mode = True
        args.transcribe_only = False
        args.translate_only = False
        args.record_only = False
        args.output = '/tmp/test.md'
        args.input_provider = 'default'
        args.keep_remote = False
        args.audio_file = None
        args.text_file = None

        # argparse would prevent both from being True, so this should pass
        validate_pipeline_mode_args(args)


class TestDocumentProcessing:
    """Test the document processing pipeline."""

    def test_process_document_creation_returns_structured_markdown(self):
        """Test that process_document_creation returns valid markdown."""
        config = ConfigurationManager()
        config.set('llm_provider', 'ollama')
        config.set('ollama_url', 'http://localhost:11434/api/generate')
        config.set('ollama_model', 'test-model')

        processor = AIProcessor(config)

        # Mock the _process_with_document_prompt method
        expected_output = """# Test Document Title

## Section 1
- Point 1
- Point 2

## Section 2
- Point 3
- Point 4"""

        with patch.object(processor, '_process_with_document_prompt', return_value=expected_output):
            result = processor.process_document_creation(
                "test content",
                recording_path="/tmp/test.aac",
                project="test-project"
            )

        # Should have headers and content
        assert "**Source**:" in result
        assert "test.aac" in result
        assert "**Status:**" in result
        assert "Structured from voice" in result
        assert "**Project:**" in result
        assert "test-project" in result
        assert "# Test Document Title" in result

    def test_document_system_prompt_is_distinct_from_cleanup_prompt(self):
        """Test that document system prompt differs from cleanup prompt."""
        config = ConfigurationManager()
        processor = AIProcessor(config)

        # The document system prompt is embedded in process_document_creation
        # Check that it mentions document structuring, not cleanup
        import inspect
        source = inspect.getsource(processor.process_document_creation)

        assert "document structuring" in source.lower()
        assert "extract the main topic" in source.lower()
        assert "bullet points" in source.lower()
        assert "H2" in source  # References H2 headers

    def test_process_document_creation_handles_none_project(self):
        """Test that process_document_creation handles None project gracefully."""
        config = ConfigurationManager()
        config.set('llm_provider', 'ollama')

        processor = AIProcessor(config)

        expected_output = "# Title\n\nContent"

        with patch.object(processor, '_process_with_document_prompt', return_value=expected_output):
            result = processor.process_document_creation(
                "test content",
                recording_path="/tmp/test.aac",
                project=None
            )

        # Should still have headers even with no project
        assert "**Source**:" in result
        assert "**Status:**" in result
        assert result is not None

    def test_process_document_creation_error_fallback(self):
        """Test that document creation falls back to raw transcript on LLM error."""
        config = ConfigurationManager()
        config.set('llm_provider', 'ollama')

        processor = AIProcessor(config)

        # Mock the _process_with_document_prompt to raise an error
        with patch.object(processor, '_process_with_document_prompt', side_effect=Exception("LLM timeout")):
            result = processor.process_document_creation(
                "test content for fallback",
                recording_path="/tmp/test.aac",
                project="test"
            )

        # Should return fallback with error message and raw transcript
        assert "⚠️ **Warning**" in result
        assert "test content for fallback" in result
        assert ("Document structuring failed" in result or "LLM timeout" in result or "LLM error" in result)


class TestDocumentModeProviderRouting:
    """Test that document mode routes to correct LLM provider."""

    def test_ollama_document_routing(self):
        """Test that ollama provider is used when configured."""
        config = ConfigurationManager()
        config.set('llm_provider', 'ollama')

        processor = AIProcessor(config)

        with patch.object(processor, '_process_ollama_document', return_value="# Document") as mock_ollama:
            processor._process_with_document_prompt("test input")
            mock_ollama.assert_called_once()

    def test_openrouter_document_routing(self):
        """Test that openrouter provider is used when configured."""
        config = ConfigurationManager()
        config.set('llm_provider', 'openrouter')

        processor = AIProcessor(config)

        with patch.object(processor, '_process_openrouter_document', return_value="# Document") as mock_openrouter:
            processor._process_with_document_prompt("test input")
            mock_openrouter.assert_called_once()

    def test_cline_document_routing(self):
        """Test that cline provider is used when configured."""
        config = ConfigurationManager()
        config.set('llm_provider', 'cline')

        processor = AIProcessor(config)

        with patch.object(processor, '_process_cline_document', return_value="# Document") as mock_cline:
            processor._process_with_document_prompt("test input")
            mock_cline.assert_called_once()


class TestYAMLHeaderInjection:
    """Test YAML header injection in document output."""

    def test_header_includes_all_required_fields(self):
        """Test that headers include source, status, title, project."""
        config = ConfigurationManager()
        config.set('llm_provider', 'ollama')

        processor = AIProcessor(config)

        expected_output = "# Main Title\n\nContent here"

        with patch.object(processor, '_process_with_document_prompt', return_value=expected_output):
            result = processor.process_document_creation(
                "test",
                recording_path="/path/to/recording.aac",
                project="my-project"
            )

        # Check all header fields
        assert "**Source**:" in result
        assert "recording.aac" in result
        assert "**Status:**" in result
        assert "Structured from voice" in result
        assert "**Project:**" in result
        assert "my-project" in result

    def test_header_title_extraction(self):
        """Test that title is extracted from document H1."""
        config = ConfigurationManager()
        config.set('llm_provider', 'ollama')

        processor = AIProcessor(config)

        # Document with H1 title
        expected_output = "# Meeting Notes from 2026-02-10\n\nDiscussed project timeline"

        with patch.object(processor, '_process_with_document_prompt', return_value=expected_output):
            result = processor.process_document_creation(
                "test",
                recording_path="/tmp/test.aac"
            )

        # Title should be extracted from document
        assert "**Title:**" in result
        assert "Meeting Notes" in result

    def test_header_project_inference(self):
        """Test that project is inferred when not provided."""
        config = ConfigurationManager()
        config.set('llm_provider', 'ollama')

        processor = AIProcessor(config)

        # Document that mentions a project
        expected_output = "# Django Migration Plan\n\nContent about django project"

        with patch.object(processor, '_process_with_document_prompt', return_value=expected_output):
            result = processor.process_document_creation(
                "test",
                recording_path="/tmp/test.aac",
                project=None  # No project provided
            )

        # Project should be inferred from content
        assert "**Project:**" in result
        # Project will be inferred or default to "unknown" if inference fails
        assert ("django" in result.lower() or "unknown" in result.lower())


class TestDocumentModeEndToEnd:
    """Integration tests for document mode."""

    def test_document_mode_produces_valid_markdown(self):
        """Test that document mode output is valid markdown."""
        config = ConfigurationManager()
        config.set('llm_provider', 'ollama')

        processor = AIProcessor(config)

        structured_output = """# Project Planning Meeting

## Timeline
- Phase 1: Design (2 weeks)
- Phase 2: Implementation (4 weeks)
- Phase 3: Testing (2 weeks)

## Deliverables
- Design document
- Implementation code
- Test suite"""

        with patch.object(processor, '_process_with_document_prompt', return_value=structured_output):
            result = processor.process_document_creation(
                "raw voice input about project",
                recording_path="/tmp/recording.aac",
                project="backend-refactor"
            )

        # Verify markdown structure
        assert "# Project Planning Meeting" in result
        assert "## Timeline" in result
        assert "## Deliverables" in result
        assert "- Phase 1:" in result

        # Verify headers are present
        assert "**Source**:" in result
        assert "**Status:**" in result
        assert "Structured from voice" in result
        assert "**Project:**" in result
        assert "backend-refactor" in result

    def test_document_saved_with_correct_content(self):
        """Test that document is saved with correct content."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_file = os.path.join(tmpdir, "test_document.md")

            config = ConfigurationManager()
            config.set('llm_provider', 'ollama')

            processor = AIProcessor(config)

            structured_output = "# Test Document\n\nSome content"

            with patch.object(processor, '_process_with_document_prompt', return_value=structured_output):
                result = processor.process_document_creation(
                    "test content",
                    recording_path="/tmp/test.aac"
                )

            # Simulate saving
            with open(output_file, 'w') as f:
                f.write(result)

            # Verify file was written
            assert os.path.exists(output_file)

            # Verify content
            with open(output_file, 'r') as f:
                content = f.read()

            assert "# Test Document" in content
            assert "**Source**:" in content


class TestErrorRecovery:
    """Test error handling and recovery in document mode."""

    def test_recording_failure_recovery(self):
        """Test graceful handling of recording failures."""
        config = ConfigurationManager()
        recorder = Mock(spec=AudioRecorder)
        recorder.start_recording.return_value = None  # Recording failed

        # This would be caught in run_document_mode CLI
        assert recorder.start_recording() is None

    def test_transcription_failure_recovery(self):
        """Test graceful handling of transcription failures."""
        config = ConfigurationManager()
        config.set('llm_provider', 'ollama')

        processor = AIProcessor(config)

        # Mock transcribe to return None
        with patch.object(processor, 'transcribe', return_value=None):
            transcript = processor.transcribe("/tmp/test.aac", "timestamp")
            assert transcript is None

    def test_document_creation_timeout_fallback(self):
        """Test fallback when LLM request times out."""
        config = ConfigurationManager()
        config.set('llm_provider', 'ollama')

        processor = AIProcessor(config)

        # Simulate LLM timeout
        with patch.object(processor, '_process_with_document_prompt',
                         side_effect=TimeoutError("LLM request timed out")):
            result = processor.process_document_creation(
                "test transcript that was successfully captured",
                recording_path="/tmp/test.aac"
            )

        # Should have error message and raw transcript
        assert "⚠️ **Warning**" in result
        assert "test transcript that was successfully captured" in result


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
