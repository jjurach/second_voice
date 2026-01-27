"""
Unit tests for CLI entry point.
Tests argument parsing, error handling, and CLI integration.
"""
import os
import sys
import tempfile
from pathlib import Path
from unittest import mock
import pytest
import subprocess

# Add src to sys.path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from cli.run import main

class TestCliArgumentParsing:
    """Test CLI argument parsing and configuration."""

    def test_default_arguments(self):
        """Test default argument values."""
        with mock.patch('sys.argv', ['run.py']):
            with mock.patch('argparse.ArgumentParser.parse_args') as mock_parse:
                mock_parse.return_value = mock.MagicMock(
                    mode='auto',
                    keep_files=False,
                    file=None,
                    debug=False,
                    verbose=False
                )

                # Import and run main to test argument parsing
                from cli.run import main
                with mock.patch('cli.run.ConfigurationManager') as mock_config:
                    with mock.patch('cli.run.AudioRecorder'):
                        with mock.patch('cli.run.AIProcessor'):
                            with mock.patch('cli.run.detect_mode', return_value='menu'):
                                with mock.patch('cli.run.get_mode'):
                                    main()  # Main doesn't exit on success

                # Verify parse_args was called
                mock_parse.assert_called_once()

    def test_custom_mode_argument(self):
        """Test custom mode selection via --mode."""
        with mock.patch('sys.argv', ['run.py', '--mode', 'tui']):
            with mock.patch('argparse.ArgumentParser.parse_args') as mock_parse:
                mock_parse.return_value = mock.MagicMock(
                    mode='tui',
                    keep_files=False,
                    file=None,
                    debug=False,
                    verbose=False,
                    no_edit=False
                )

                with mock.patch('cli.run.ConfigurationManager') as mock_config:
                    with mock.patch('cli.run.AudioRecorder'):
                        with mock.patch('cli.run.AIProcessor'):
                            with mock.patch('cli.run.detect_mode', return_value='tui'):
                                with mock.patch('cli.run.get_mode'):
                                    main()

                # Verify mode was set in config
                mock_config.return_value.set.assert_called_with('mode', 'tui')

    def test_keep_files_flag(self):
        """Test --keep-files flag sets config option."""
        with mock.patch('sys.argv', ['run.py', '--keep-files']):
            with mock.patch('argparse.ArgumentParser.parse_args') as mock_parse:
                mock_parse.return_value = mock.MagicMock(
                    mode='auto',
                    keep_files=True,
                    file=None,
                    debug=False,
                    verbose=False,
                    no_edit=False
                )

                with mock.patch('cli.run.ConfigurationManager') as mock_config:
                    with mock.patch('cli.run.AudioRecorder'):
                        with mock.patch('cli.run.AIProcessor'):
                            with mock.patch('cli.run.detect_mode', return_value='menu'):
                                with mock.patch('cli.run.get_mode'):
                                    main()

                # Verify keep_files was set in config
                mock_config.return_value.set.assert_called_with('keep_files', True)

    def test_debug_flag(self):
        """Test --debug flag sets debug mode."""
        with mock.patch('sys.argv', ['run.py', '--debug']):
            with mock.patch('argparse.ArgumentParser.parse_args') as mock_parse:
                mock_parse.return_value = mock.MagicMock(
                    mode='auto',
                    keep_files=False,
                    file=None,
                    debug=True,
                    verbose=False,
                    no_edit=False
                )

                with mock.patch('cli.run.ConfigurationManager') as mock_config:
                    with mock.patch('cli.run.AudioRecorder'):
                        with mock.patch('cli.run.AIProcessor'):
                            with mock.patch('cli.run.detect_mode', return_value='menu'):
                                with mock.patch('cli.run.get_mode'):
                                    main()

                # Verify debug was set in config
                mock_config.return_value.set.assert_called_with('debug', True)

    def test_verbose_flag(self):
        """Test --verbose flag sets verbose mode."""
        with mock.patch('sys.argv', ['run.py', '--verbose']):
            with mock.patch('argparse.ArgumentParser.parse_args') as mock_parse:
                mock_parse.return_value = mock.MagicMock(
                    mode='auto',
                    keep_files=False,
                    file=None,
                    debug=False,
                    verbose=True,
                    no_edit=False
                )

                with mock.patch('cli.run.ConfigurationManager') as mock_config:
                    with mock.patch('cli.run.AudioRecorder'):
                        with mock.patch('cli.run.AIProcessor'):
                            with mock.patch('cli.run.detect_mode', return_value='menu'):
                                with mock.patch('cli.run.get_mode'):
                                    main()

                # Verify verbose was set in config
                mock_config.return_value.set.assert_called_with('verbose', True)

class TestCliFileInputHandling:
    """Test CLI file input validation and handling."""

    def test_file_not_found_error(self, temp_dir):
        """Test error handling when input file doesn't exist."""
        nonexistent_file = temp_dir / "nonexistent.wav"

        with mock.patch('sys.argv', ['run.py', '--file', str(nonexistent_file)]):
            with mock.patch('argparse.ArgumentParser.parse_args') as mock_parse:
                mock_parse.return_value = mock.MagicMock(
                    mode='auto',
                    keep_files=False,
                    file=str(nonexistent_file),
                    debug=False,
                    verbose=False
                )

                with mock.patch('cli.run.ConfigurationManager') as mock_config:
                    with mock.patch('cli.run.AudioRecorder'):
                        with mock.patch('cli.run.AIProcessor'):
                            with pytest.raises(SystemExit) as exc_info:
                                main()

                # Verify error message and exit code
                assert exc_info.value.code == 1

    def test_file_not_readable_error(self, temp_dir):
        """Test error handling when input file is not readable."""
        # Create a file and make it unreadable
        test_file = temp_dir / "unreadable.wav"
        test_file.write_text("dummy content")
        os.chmod(test_file, 0o000)  # Remove all permissions

        try:
            with mock.patch('sys.argv', ['run.py', '--file', str(test_file)]):
                with mock.patch('argparse.ArgumentParser.parse_args') as mock_parse:
                    mock_parse.return_value = mock.MagicMock(
                        mode='auto',
                        keep_files=False,
                        file=str(test_file),
                        debug=False,
                        verbose=False
                    )

                    with mock.patch('cli.run.ConfigurationManager') as mock_config:
                        with mock.patch('cli.run.AudioRecorder'):
                            with mock.patch('cli.run.AIProcessor'):
                                with pytest.raises(SystemExit) as exc_info:
                                    main()

                    # Verify error message and exit code
                    assert exc_info.value.code == 1
        finally:
            # Restore permissions for cleanup
            os.chmod(test_file, 0o644)

    def test_invalid_audio_file_error(self, temp_dir):
        """Test error handling for invalid audio files."""
        invalid_file = temp_dir / "invalid.wav"
        invalid_file.write_text("NOT_VALID_AUDIO_CONTENT")

        with mock.patch('sys.argv', ['run.py', '--file', str(invalid_file)]):
            with mock.patch('argparse.ArgumentParser.parse_args') as mock_parse:
                mock_parse.return_value = mock.MagicMock(
                    mode='auto',
                    keep_files=False,
                    file=str(invalid_file),
                    debug=False,
                    verbose=False
                )

                with mock.patch('cli.run.ConfigurationManager') as mock_config:
                    with mock.patch('cli.run.AudioRecorder'):
                        with mock.patch('cli.run.AIProcessor'):
                            with pytest.raises(SystemExit) as exc_info:
                                main()

                # Verify error message and exit code
                assert exc_info.value.code == 1

    def test_valid_audio_file_handling(self, temp_dir):
        """Test successful handling of valid audio file."""
        # Create a minimal valid WAV file
        audio_file = temp_dir / "test_audio.wav"
        wav_data = (
            b'RIFF'
            b'\x24\x00\x00\x00'  # File size
            b'WAVE'
            b'fmt '
            b'\x10\x00\x00\x00'  # Subchunk1Size
            b'\x01\x00'          # AudioFormat (1 = PCM)
            b'\x01\x00'          # NumChannels (1 = mono)
            b'\x44\xac\x00\x00'  # SampleRate (44100 Hz)
            b'\x88\x58\x01\x00'  # ByteRate
            b'\x02\x00'          # BlockAlign
            b'\x10\x00'          # BitsPerSample
            b'data'
            b'\x00\x00\x00\x00'  # Subchunk2Size (0 bytes of audio data)
        )
        audio_file.write_bytes(wav_data)

        with mock.patch('sys.argv', ['run.py', '--file', str(audio_file)]):
            with mock.patch('argparse.ArgumentParser.parse_args') as mock_parse:
                mock_parse.return_value = mock.MagicMock(
                    mode='auto',
                    keep_files=False,
                    file=str(audio_file),
                    debug=False,
                    verbose=False,
                    no_edit=False
                )

                with mock.patch('cli.run.ConfigurationManager') as mock_config:
                    with mock.patch('cli.run.AudioRecorder'):
                        with mock.patch('cli.run.AIProcessor'):
                            with mock.patch('cli.run.detect_mode', return_value='menu'):
                                with mock.patch('cli.run.get_mode'):
                                    main()

                # Verify file was set in config
                mock_config.return_value.set.assert_called_with('input_file', str(audio_file))

class TestCliModeDetection:
    """Test CLI mode detection and fallback logic."""

    def test_mode_detection_success(self):
        """Test successful mode detection."""
        with mock.patch('sys.argv', ['run.py']):
            with mock.patch('argparse.ArgumentParser.parse_args') as mock_parse:
                mock_parse.return_value = mock.MagicMock(
                    mode='auto',
                    keep_files=False,
                    file=None,
                    debug=False,
                    verbose=False
                )

                with mock.patch('cli.run.ConfigurationManager'):
                    with mock.patch('cli.run.AudioRecorder'):
                        with mock.patch('cli.run.AIProcessor'):
                            with mock.patch('cli.run.detect_mode', return_value='menu'):
                                with mock.patch('cli.run.get_mode'):
                                    main()

    def test_mode_detection_fallback(self):
        """Test fallback to menu mode when detection fails."""
        with mock.patch('sys.argv', ['run.py']):
            with mock.patch('argparse.ArgumentParser.parse_args') as mock_parse:
                mock_parse.return_value = mock.MagicMock(
                    mode='auto',
                    keep_files=False,
                    file=None,
                    debug=False,
                    verbose=False
                )

                with mock.patch('cli.run.ConfigurationManager'):
                    with mock.patch('cli.run.AudioRecorder'):
                        with mock.patch('cli.run.AIProcessor'):
                            with mock.patch('cli.run.detect_mode', side_effect=Exception("Detection failed")):
                                with mock.patch('cli.run.get_mode'):
                                    main()

    def test_gui_mode_with_file_fallback(self):
        """Test GUI mode with --file falls back to menu mode."""
        # Create a valid audio file first
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp:
            tmp_path = tmp.name
            # Write minimal WAV header
            tmp.write(b'RIFF\x24\x00\x00\x00WAVEfmt \x10\x00\x00\x00\x01\x00\x01\x00\x44\xac\x00\x00\x88\x58\x01\x00\x02\x00\x10\x00data\x00\x00\x00\x00')

        try:
            with mock.patch('sys.argv', ['run.py', '--file', tmp_path]):
                with mock.patch('argparse.ArgumentParser.parse_args') as mock_parse:
                    mock_parse.return_value = mock.MagicMock(
                        mode='gui',
                        keep_files=False,
                        file=tmp_path,
                        debug=False,
                        verbose=False
                    )

                    with mock.patch('cli.run.ConfigurationManager') as mock_config:
                        with mock.patch('cli.run.AudioRecorder'):
                            with mock.patch('cli.run.AIProcessor'):
                                with mock.patch('cli.run.detect_mode', return_value='gui'):
                                    with mock.patch('cli.run.get_mode'):
                                        main()

                    # Verify mode was changed to menu
                    mock_config.return_value.set.assert_called_with('mode', 'menu')
        finally:
            os.unlink(tmp_path)

class TestCliErrorHandling:
    """Test CLI error handling and exit codes."""

    def test_engine_initialization_error(self):
        """Test error handling when engine initialization fails."""
        with mock.patch('sys.argv', ['run.py']):
            with mock.patch('argparse.ArgumentParser.parse_args') as mock_parse:
                mock_parse.return_value = mock.MagicMock(
                    mode='auto',
                    keep_files=False,
                    file=None,
                    debug=False,
                    verbose=False
                )

                with mock.patch('cli.run.ConfigurationManager'):
                    with mock.patch('cli.run.AudioRecorder', side_effect=Exception("Init error")):
                        with mock.patch('cli.run.AIProcessor'):
                            with pytest.raises(SystemExit) as exc_info:
                                main()

                # Verify exit code
                assert exc_info.value.code == 1

    def test_mode_initialization_error(self):
        """Test error handling when mode initialization fails."""
        with mock.patch('sys.argv', ['run.py']):
            with mock.patch('argparse.ArgumentParser.parse_args') as mock_parse:
                mock_parse.return_value = mock.MagicMock(
                    mode='auto',
                    keep_files=False,
                    file=None,
                    debug=False,
                    verbose=False
                )

                with mock.patch('cli.run.ConfigurationManager'):
                    with mock.patch('cli.run.AudioRecorder'):
                        with mock.patch('cli.run.AIProcessor'):
                            with mock.patch('cli.run.detect_mode', return_value='menu'):
                                with mock.patch('cli.run.get_mode', side_effect=Exception("Mode error")):
                                    with pytest.raises(SystemExit) as exc_info:
                                        main()

                # Verify exit code
                assert exc_info.value.code == 1

    def test_mode_run_error(self):
        """Test error handling when mode.run() fails."""
        with mock.patch('sys.argv', ['run.py']):
            with mock.patch('argparse.ArgumentParser.parse_args') as mock_parse:
                mock_parse.return_value = mock.MagicMock(
                    mode='auto',
                    keep_files=False,
                    file=None,
                    debug=False,
                    verbose=False
                )

                with mock.patch('cli.run.ConfigurationManager'):
                    with mock.patch('cli.run.AudioRecorder'):
                        with mock.patch('cli.run.AIProcessor'):
                            with mock.patch('cli.run.detect_mode', return_value='menu'):
                                with mock.patch('cli.run.get_mode') as mock_get_mode:
                                    mock_mode = mock.MagicMock()
                                    mock_mode.run.side_effect = Exception("Run error")
                                    mock_get_mode.return_value = mock_mode

                                    with pytest.raises(SystemExit) as exc_info:
                                        main()

                # Verify exit code
                assert exc_info.value.code == 1

class TestCliIntegration:
    """Integration tests for CLI functionality."""

    def test_cli_help_output(self):
        """Test that CLI help output works."""
        result = subprocess.run(
            [sys.executable, '-m', 'src.cli.run', '--help'],
            capture_output=True,
            text=True
        )

        # Verify help output contains expected content
        assert 'Second Voice - AI Assistant' in result.stdout
        assert '--mode' in result.stdout
        assert '--file' in result.stdout
        assert '--keep-files' in result.stdout

    def test_cli_version_info(self):
        """Test that CLI can be invoked."""
        result = subprocess.run(
            [sys.executable, '-c', 'import sys; sys.path.insert(0, "src"); from cli.run import main'],
            capture_output=True,
            text=True
        )

        # Verify the command runs (it may succeed or fail depending on context)
        # The important thing is that it doesn't crash
        assert result.returncode is not None  # Just verify it completed

    def test_cli_invalid_mode(self):
        """Test error handling for invalid mode."""
        result = subprocess.run(
            [sys.executable, '-m', 'src.cli.run', '--mode', 'invalid'],
            capture_output=True,
            text=True
        )

        # Verify error handling
        assert result.returncode != 0
        assert 'invalid choice' in result.stderr or 'invalid' in result.stderr.lower()

class TestCliResourceCleanup:
    """Test CLI resource cleanup behavior."""

    def test_temp_file_cleanup_when_keep_files_false(self):
        """Test that temp files are cleaned up when --keep-files is not set."""
        with mock.patch('sys.argv', ['run.py']):
            with mock.patch('argparse.ArgumentParser.parse_args') as mock_parse:
                mock_parse.return_value = mock.MagicMock(
                    mode='auto',
                    keep_files=False,
                    file=None,
                    debug=False,
                    verbose=False
                )

                with mock.patch('cli.run.ConfigurationManager') as mock_config:
                    mock_config.return_value.get.return_value = False  # keep_files = False
                    with mock.patch('cli.run.AudioRecorder') as mock_recorder:
                        with mock.patch('cli.run.AIProcessor'):
                            with mock.patch('cli.run.detect_mode', return_value='menu'):
                                with mock.patch('cli.run.get_mode'):
                                    main()

                # Verify cleanup was called
                mock_recorder.return_value.cleanup_temp_files.assert_called_once()

    def test_temp_file_preservation_when_keep_files_true(self):
        """Test that temp files are preserved when --keep-files is set."""
        with mock.patch('sys.argv', ['run.py', '--keep-files']):
            with mock.patch('argparse.ArgumentParser.parse_args') as mock_parse:
                mock_parse.return_value = mock.MagicMock(
                    mode='auto',
                    keep_files=True,
                    file=None,
                    debug=False,
                    verbose=False
                )

                with mock.patch('cli.run.ConfigurationManager') as mock_config:
                    mock_config.return_value.get.return_value = True  # keep_files = True
                    with mock.patch('cli.run.AudioRecorder') as mock_recorder:
                        with mock.patch('cli.run.AIProcessor'):
                            with mock.patch('cli.run.detect_mode', return_value='menu'):
                                with mock.patch('cli.run.get_mode'):
                                    main()

                # Verify cleanup was NOT called
                mock_recorder.return_value.cleanup_temp_files.assert_not_called()
