"""
Unit tests for CLI pipeline modes and new workflow options.
Tests --record-only, --transcribe-only, --translate-only, --no-edit, and file parameters.
"""
import os
import sys
import tempfile
import pytest
from pathlib import Path
from unittest import mock

# Add src to sys.path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from cli.run import (
    validate_pipeline_mode_args,
    validate_output_file,
    resolve_file_path,
    invoke_editor,
    run_record_only,
    run_transcribe_only,
    run_translate_only,
)


class TestValidatePipelineArgs:
    """Test pipeline mode argument validation."""

    def test_transcribe_only_requires_audio_file(self):
        """Test --transcribe-only requires --audio-file."""
        args = mock.MagicMock(
            transcribe_only=True,
            translate_only=False,
            audio_file=None,
            text_file=None
        )

        with pytest.raises(SystemExit) as exc_info:
            validate_pipeline_mode_args(args)
        assert exc_info.value.code == 3

    def test_translate_only_requires_text_file(self):
        """Test --translate-only requires --text-file."""
        args = mock.MagicMock(
            transcribe_only=False,
            translate_only=True,
            audio_file=None,
            text_file=None
        )

        with pytest.raises(SystemExit) as exc_info:
            validate_pipeline_mode_args(args)
        assert exc_info.value.code == 3

    def test_valid_transcribe_only_args(self):
        """Test --transcribe-only with required --audio-file."""
        args = mock.MagicMock(
            transcribe_only=True,
            translate_only=False,
            record_only=False,
            audio_file='/path/to/audio.wav',
            text_file=None,
            input_provider='default',
            keep_remote=False
        )

        # Should not raise
        validate_pipeline_mode_args(args)

    def test_valid_translate_only_args(self):
        """Test --translate-only with required --text-file."""
        args = mock.MagicMock(
            transcribe_only=False,
            translate_only=True,
            record_only=False,
            audio_file=None,
            text_file='/path/to/text.txt',
            input_provider='default',
            keep_remote=False
        )

        # Should not raise
        validate_pipeline_mode_args(args)

    def test_no_pipeline_modes(self):
        """Test when no pipeline mode specified."""
        args = mock.MagicMock(
            transcribe_only=False,
            translate_only=False,
            record_only=False,
            audio_file=None,
            text_file=None,
            input_provider='default',
            keep_remote=False
        )

        # Should not raise
        validate_pipeline_mode_args(args)


class TestValidateOutputFile:
    """Test output file validation and overwrite protection."""

    def test_overwrite_protection_prevents_file_overwrite(self):
        """Test that validation prevents overwriting existing file."""
        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            existing_file = tmp.name

        try:
            with pytest.raises(SystemExit) as exc_info:
                validate_output_file(existing_file, "record-only")
            assert exc_info.value.code == 2
        finally:
            os.unlink(existing_file)

    def test_allows_nonexistent_output_file(self):
        """Test that validation allows nonexistent file."""
        nonexistent_file = '/tmp/nonexistent_file_xyz_12345.txt'

        # Clean up if it exists
        if os.path.exists(nonexistent_file):
            os.unlink(nonexistent_file)

        # Should not raise
        validate_output_file(nonexistent_file, "record-only")


class TestResolveFilePath:
    """Test file path resolution and validation."""

    def test_resolve_absolute_path(self):
        """Test resolving absolute path."""
        path = '/tmp/test.txt'
        resolved = resolve_file_path(path)
        assert resolved == os.path.abspath(path)

    def test_resolve_relative_path(self):
        """Test resolving relative path."""
        path = './test.txt'
        resolved = resolve_file_path(path)
        assert resolved == os.path.abspath(path)

    def test_resolve_none_returns_none(self):
        """Test that None input returns None."""
        resolved = resolve_file_path(None)
        assert resolved is None

    def test_resolve_invalid_parent_directory(self):
        """Test that invalid parent directory raises error."""
        path = '/nonexistent_directory_xyz_12345/test.txt'

        with pytest.raises(SystemExit) as exc_info:
            resolve_file_path(path)
        assert exc_info.value.code == 1


class TestInvokeEditor:
    """Test editor invocation with resolution chain."""

    def test_editor_command_cli_override(self):
        """Test --editor-command overrides config and env."""
        config = mock.MagicMock()
        config.get.return_value = 'vim'
        args = mock.MagicMock(editor_command='nano')

        with mock.patch('subprocess.run') as mock_run:
            with mock.patch.dict(os.environ, {'EDITOR': 'emacs'}):
                invoke_editor('/tmp/test.txt', config, args)

                # Verify CLI command was used
                mock_run.assert_called_once()
                call_args = mock_run.call_args[0][0]
                assert 'nano' in call_args

    def test_editor_command_config_override(self):
        """Test config editor overrides env."""
        config = mock.MagicMock()
        config.get.return_value = 'vim'
        args = mock.MagicMock(editor_command=None)

        with mock.patch('subprocess.run') as mock_run:
            with mock.patch.dict(os.environ, {'EDITOR': 'emacs'}):
                invoke_editor('/tmp/test.txt', config, args)

                # Verify config command was used
                mock_run.assert_called_once()
                call_args = mock_run.call_args[0][0]
                assert 'vim' in call_args

    def test_editor_env_variable_fallback(self):
        """Test environment variable fallback."""
        config = mock.MagicMock()
        config.get.return_value = None
        args = mock.MagicMock(editor_command=None)

        with mock.patch('subprocess.run') as mock_run:
            with mock.patch.dict(os.environ, {'EDITOR': 'emacs'}):
                invoke_editor('/tmp/test.txt', config, args)

                # Verify env variable was used
                mock_run.assert_called_once()
                call_args = mock_run.call_args[0][0]
                assert 'emacs' in call_args

    def test_editor_default_fallback(self):
        """Test default editor fallback."""
        config = mock.MagicMock()
        config.get.return_value = None
        args = mock.MagicMock(editor_command=None)

        with mock.patch('subprocess.run') as mock_run:
            # Remove EDITOR env variable
            with mock.patch.dict(os.environ, {}, clear=True):
                invoke_editor('/tmp/test.txt', config, args)

                # Verify default was used
                mock_run.assert_called_once()
                call_args = mock_run.call_args[0][0]
                assert 'nano' in call_args


class TestRecordOnlyMode:
    """Test --record-only pipeline mode."""

    def test_record_only_creates_output_file(self):
        """Test record-only mode creates audio file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_file = os.path.join(tmpdir, 'test_recording.wav')

            config = mock.MagicMock()
            config.get.return_value = tmpdir

            args = mock.MagicMock(audio_file=output_file)
            recorder = mock.MagicMock()

            with mock.patch('builtins.print'):
                exit_code = run_record_only(config, args, recorder)

            assert exit_code == 0
            recorder.record.assert_called_once_with(output_file)

    def test_record_only_handles_recorder_error(self):
        """Test record-only mode handles recording error."""
        config = mock.MagicMock()
        args = mock.MagicMock(audio_file='/tmp/test.wav')
        recorder = mock.MagicMock()
        recorder.record.side_effect = Exception("Recording failed")

        with mock.patch('builtins.print'):
            exit_code = run_record_only(config, args, recorder)

        assert exit_code == 1


class TestTranscribeOnlyMode:
    """Test --transcribe-only pipeline mode."""

    def test_transcribe_only_creates_output_file(self):
        """Test transcribe-only mode creates text file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create input audio file
            input_file = os.path.join(tmpdir, 'test.wav')
            Path(input_file).write_text('fake audio')

            output_file = os.path.join(tmpdir, 'test.txt')

            config = mock.MagicMock()
            config.get.return_value = tmpdir

            args = mock.MagicMock(audio_file=input_file, text_file=output_file)
            processor = mock.MagicMock()
            processor.transcribe.return_value = "Transcribed text"

            with mock.patch('builtins.print'):
                exit_code = run_transcribe_only(config, args, processor)

            assert exit_code == 0
            assert os.path.exists(output_file)
            assert Path(output_file).read_text() == "Transcribed text"

    def test_transcribe_only_handles_processor_error(self):
        """Test transcribe-only mode handles transcription error."""
        config = mock.MagicMock()
        args = mock.MagicMock(audio_file='/tmp/test.wav', text_file=None)
        processor = mock.MagicMock()
        processor.transcribe.side_effect = Exception("Transcription failed")

        with mock.patch('builtins.print'):
            exit_code = run_transcribe_only(config, args, processor)

        assert exit_code == 1

    def test_transcribe_only_handles_empty_transcript(self):
        """Test transcribe-only mode handles empty transcript."""
        config = mock.MagicMock()
        config.get.return_value = '/tmp'
        args = mock.MagicMock(audio_file='/tmp/test.wav', text_file=None)
        processor = mock.MagicMock()
        processor.transcribe.return_value = None

        with mock.patch('builtins.print'):
            exit_code = run_transcribe_only(config, args, processor)

        assert exit_code == 1


class TestTranslateOnlyMode:
    """Test --translate-only pipeline mode."""

    def test_translate_only_creates_output_file(self):
        """Test translate-only mode creates output file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create input text file
            input_file = os.path.join(tmpdir, 'input.txt')
            Path(input_file).write_text("Input text")

            output_file = os.path.join(tmpdir, 'output.md')

            config = mock.MagicMock()
            config.get.return_value = tmpdir

            args = mock.MagicMock(text_file=input_file, output_file=output_file)
            processor = mock.MagicMock()
            # Use side_effect to ensure return value is set regardless of call args
            processor.process_with_headers_and_fallback = mock.MagicMock(return_value="Processed output")

            with mock.patch('builtins.print'):
                exit_code = run_translate_only(config, args, processor)

            assert exit_code == 0
            assert os.path.exists(output_file)
            assert Path(output_file).read_text() == "Processed output"

    def test_translate_only_handles_file_read_error(self):
        """Test translate-only mode handles file read error."""
        config = mock.MagicMock()
        args = mock.MagicMock(text_file='/nonexistent/file.txt', output_file=None)
        processor = mock.MagicMock()

        with mock.patch('builtins.print'):
            exit_code = run_translate_only(config, args, processor)

        assert exit_code == 1

    def test_translate_only_handles_processor_error(self):
        """Test translate-only mode handles processing error."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create input text file
            input_file = os.path.join(tmpdir, 'input.txt')
            Path(input_file).write_text("Input text")

            config = mock.MagicMock()
            config.get.return_value = tmpdir

            args = mock.MagicMock(text_file=input_file, output_file=None)
            processor = mock.MagicMock()
            processor.process_with_headers_and_fallback.side_effect = Exception("Processing failed")

            with mock.patch('builtins.print'):
                exit_code = run_translate_only(config, args, processor)

            assert exit_code == 1


class TestPipelineIntegration:
    """Integration tests for pipeline workflows."""

    def test_full_pipeline_workflow(self):
        """Test complete pipeline: record → transcribe → translate."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Phase 1: Record audio
            audio_file = os.path.join(tmpdir, 'recording.wav')
            config = mock.MagicMock()
            config.get.return_value = tmpdir
            args_record = mock.MagicMock(audio_file=audio_file)
            recorder = mock.MagicMock()

            with mock.patch('builtins.print'):
                exit1 = run_record_only(config, args_record, recorder)
            assert exit1 == 0

            # Phase 2: Transcribe audio
            Path(audio_file).write_text('fake audio data')
            text_file = os.path.join(tmpdir, 'transcript.txt')
            args_transcribe = mock.MagicMock(audio_file=audio_file, text_file=text_file)
            processor = mock.MagicMock()
            processor.transcribe.return_value = "Hello world"

            with mock.patch('builtins.print'):
                exit2 = run_transcribe_only(config, args_transcribe, processor)
            assert exit2 == 0
            assert Path(text_file).read_text() == "Hello world"

            # Phase 3: Translate/process text
            output_file = os.path.join(tmpdir, 'final.md')
            args_translate = mock.MagicMock(text_file=text_file, output_file=output_file)
            # Configure return value for phase 3
            processor.process_with_headers_and_fallback = mock.MagicMock(return_value="# Final Output")

            with mock.patch('builtins.print'):
                exit3 = run_translate_only(config, args_translate, processor)
            assert exit3 == 0
            assert Path(output_file).read_text() == "# Final Output"
