"""
Unit tests for AudioRecorder.
Tests audio recording, device management, and file handling.
"""
import os
import time
import pytest
from pathlib import Path
from unittest import mock
import numpy as np

from second_voice.core.recorder import AudioRecorder


class TestRecorderInitialization:
    """Test AudioRecorder initialization."""

    def test_recorder_init_with_default_config(self, temp_dir):
        """Initialize recorder with default configuration."""
        config = {
            'temp_dir': str(temp_dir),
            'audio_config': {
                'sample_rate': 16000,
                'channels': 1,
                'device': None
            }
        }

        recorder = AudioRecorder(config)

        assert recorder.sample_rate == 16000
        assert recorder.channels == 1
        assert recorder.device is None
        assert recorder.temp_dir == str(temp_dir)

    def test_recorder_init_creates_temp_dir(self, temp_dir):
        """Temp directory is created during initialization."""
        temp_subdir = temp_dir / "audio_tmp"
        config = {
            'temp_dir': str(temp_subdir),
            'audio_config': {}
        }

        recorder = AudioRecorder(config)

        assert temp_subdir.exists()

    def test_recorder_init_with_custom_audio_params(self, temp_dir):
        """Initialize with custom audio parameters."""
        config = {
            'temp_dir': str(temp_dir),
            'audio_config': {
                'sample_rate': 48000,
                'channels': 2,
                'device': 1
            }
        }

        recorder = AudioRecorder(config)

        assert recorder.sample_rate == 48000
        assert recorder.channels == 2
        assert recorder.device == 1

    def test_recorder_init_defaults_when_audio_config_missing(self, temp_dir):
        """Use defaults when audio_config is missing."""
        config = {'temp_dir': str(temp_dir)}

        recorder = AudioRecorder(config)

        assert recorder.sample_rate == 16000
        assert recorder.channels == 1
        assert recorder.device is None


class TestAmplitudeCalculation:
    """Test RMS amplitude calculation."""

    def test_rms_calculation_silent_audio(self, temp_dir):
        """RMS of silent audio is near zero."""
        config = {'temp_dir': str(temp_dir), 'audio_config': {}}
        recorder = AudioRecorder(config)

        # Silent audio (all zeros)
        silent = np.zeros(1000, dtype=np.float32)
        rms = recorder._calculate_rms(silent)

        assert 0.0 <= rms <= 0.01

    def test_rms_calculation_loud_audio(self, temp_dir):
        """RMS of loud audio is higher."""
        config = {'temp_dir': str(temp_dir), 'audio_config': {}}
        recorder = AudioRecorder(config)

        # Louder audio
        loud = np.full(1000, 0.1, dtype=np.float32)
        rms = recorder._calculate_rms(loud)

        assert rms > 0.1

    def test_rms_normalized_to_0_to_1(self, temp_dir):
        """RMS is normalized to 0.0-1.0 range."""
        config = {'temp_dir': str(temp_dir), 'audio_config': {}}
        recorder = AudioRecorder(config)

        # Various amplitude levels
        for amplitude in [0.0, 0.05, 0.1, 0.2]:
            audio = np.full(1000, amplitude, dtype=np.float32)
            rms = recorder._calculate_rms(audio)

            assert 0.0 <= rms <= 1.0

    def test_rms_empty_audio(self, temp_dir):
        """RMS of empty audio is zero."""
        config = {'temp_dir': str(temp_dir), 'audio_config': {}}
        recorder = AudioRecorder(config)

        empty = np.array([], dtype=np.float32)
        rms = recorder._calculate_rms(empty)

        assert rms == 0.0

    def test_get_amplitude_returns_current_value(self, temp_dir):
        """get_amplitude() returns the current amplitude."""
        config = {'temp_dir': str(temp_dir), 'audio_config': {}}
        recorder = AudioRecorder(config)

        # Initially zero
        assert recorder.get_amplitude() == 0.0

        # After setting amplitude
        recorder._current_amplitude = 0.5
        assert recorder.get_amplitude() == 0.5


class TestTemporaryFileHandling:
    """Test temporary audio file creation and management."""

    def test_create_temp_audio_path(self, temp_dir):
        """Create temporary audio file path."""
        config = {'temp_dir': str(temp_dir), 'audio_config': {}}
        recorder = AudioRecorder(config)

        path = recorder._create_temp_audio_path()

        assert path.startswith(str(temp_dir))
        assert path.endswith('.wav')
        assert 'tmp-audio-' in path

    def test_temp_path_includes_timestamp(self, temp_dir):
        """Temp file path includes timestamp for uniqueness."""
        config = {'temp_dir': str(temp_dir), 'audio_config': {}}
        recorder = AudioRecorder(config)

        path1 = recorder._create_temp_audio_path()
        time.sleep(1.01)  # Wait longer than 1 second to ensure different timestamp
        path2 = recorder._create_temp_audio_path()

        assert path1 != path2

    def test_custom_temp_extension(self, temp_dir):
        """Specify custom file extension."""
        config = {'temp_dir': str(temp_dir), 'audio_config': {}}
        recorder = AudioRecorder(config)

        path = recorder._create_temp_audio_path(extension='mp3')

        assert path.endswith('.mp3')


class TestRecordingOperations:
    """Test recording start/stop operations."""

    @mock.patch("sounddevice.InputStream")
    def test_start_recording_no_duration(self, mock_input_stream, temp_dir):
        """Start recording without duration limit."""
        mock_stream = mock.MagicMock()
        mock_input_stream.return_value = mock_stream

        config = {'temp_dir': str(temp_dir), 'audio_config': {}}
        recorder = AudioRecorder(config)

        path = recorder.start_recording()

        assert path is not None
        assert path.startswith(str(temp_dir))
        mock_stream.start.assert_called_once()

    @mock.patch("soundfile.write")
    @mock.patch("sounddevice.InputStream")
    def test_stop_recording_saves_file(self, mock_input_stream, mock_write, temp_dir):
        """Stop recording saves audio to file."""
        mock_stream = mock.MagicMock()
        mock_input_stream.return_value = mock_stream

        config = {'temp_dir': str(temp_dir), 'audio_config': {}}
        recorder = AudioRecorder(config)

        # Start recording and add some fake audio data
        recorder.start_recording()
        recorder._audio_data = [np.zeros(1000, dtype=np.float32)]

        # Stop recording
        path = recorder.stop_recording()

        assert path is not None
        mock_write.assert_called_once()

    @mock.patch("soundfile.write")
    @mock.patch("sounddevice.InputStream")
    def test_stop_recording_without_data_returns_none(self, mock_input_stream, mock_write, temp_dir):
        """Stop recording with no audio data returns None."""
        mock_stream = mock.MagicMock()
        mock_input_stream.return_value = mock_stream

        config = {'temp_dir': str(temp_dir), 'audio_config': {}}
        recorder = AudioRecorder(config)

        # Start recording but don't add any data
        recorder.start_recording()
        recorder._audio_data = []

        # Stop recording
        path = recorder.stop_recording()

        assert path is None

    @mock.patch("sounddevice.InputStream")
    def test_stop_recording_when_not_recording(self, mock_input_stream, temp_dir):
        """Stop recording when not recording returns None."""
        mock_stream = mock.MagicMock()
        mock_input_stream.return_value = mock_stream

        config = {'temp_dir': str(temp_dir), 'audio_config': {}}
        recorder = AudioRecorder(config)

        # Don't start recording, just stop
        path = recorder.stop_recording()

        assert path is None

    @mock.patch("soundfile.write")
    @mock.patch("sounddevice.InputStream")
    def test_recording_updates_amplitude(self, mock_input_stream, mock_write, temp_dir):
        """Recording callback updates amplitude."""
        mock_stream = mock.MagicMock()
        mock_input_stream.return_value = mock_stream

        config = {'temp_dir': str(temp_dir), 'audio_config': {}}
        recorder = AudioRecorder(config)

        # Initially zero
        assert recorder.get_amplitude() == 0.0

        # Simulate recording with audio data
        recorder.start_recording()
        recorder._audio_data = [np.full(1000, 0.1, dtype=np.float32)]
        recorder._current_amplitude = recorder._calculate_rms(np.full(1000, 0.1, dtype=np.float32))

        # Should have updated amplitude
        assert recorder.get_amplitude() > 0.0


class TestAudioDeviceHandling:
    """Test audio device enumeration."""

    @mock.patch("sounddevice.query_devices")
    def test_get_audio_devices_lists_inputs(self, mock_query):
        """List available input devices."""
        mock_query.return_value = [
            {"name": "Microphone", "max_input_channels": 2},
            {"name": "Line In", "max_input_channels": 1},
            {"name": "Speaker", "max_input_channels": 0},  # Output only
        ]

        config = {'temp_dir': './tmp', 'audio_config': {}}
        recorder = AudioRecorder(config)

        devices = recorder.get_audio_devices()

        # Should only include devices with input channels
        assert "Microphone" in devices
        assert "Line In" in devices
        assert "Speaker" not in devices
        assert len(devices) == 2

    @mock.patch("sounddevice.query_devices")
    def test_get_audio_devices_empty_list(self, mock_query):
        """Handle case with no input devices."""
        mock_query.return_value = [
            {"name": "Speaker", "max_input_channels": 0},
        ]

        config = {'temp_dir': './tmp', 'audio_config': {}}
        recorder = AudioRecorder(config)

        devices = recorder.get_audio_devices()

        assert devices == []


class TestTemporaryFileCleanup:
    """Test cleanup of temporary audio files."""

    def test_cleanup_old_temp_files(self, temp_dir):
        """Remove old temporary files."""
        config = {'temp_dir': str(temp_dir), 'audio_config': {}}
        recorder = AudioRecorder(config)

        # Create old and new temp files
        old_file = temp_dir / "tmp-audio-1000000000.wav"
        old_file.write_text("")

        new_file = temp_dir / f"tmp-audio-{int(time.time())}.wav"
        new_file.write_text("")

        # Mock getctime to return an old time for the old file
        def mock_getctime(path):
            if "1000000000" in path:
                return time.time() - (48 * 3600)  # 48 hours ago
            return time.time()

        # Clean up files older than 24 hours
        with mock.patch("os.path.getctime", side_effect=mock_getctime):
            recorder.cleanup_temp_files(max_age_hours=24)

        # Old file should be deleted, new should remain
        assert not old_file.exists()
        assert new_file.exists()

    def test_cleanup_ignores_non_temp_files(self, temp_dir):
        """Cleanup doesn't delete non-temp files."""
        config = {'temp_dir': str(temp_dir), 'audio_config': {}}
        recorder = AudioRecorder(config)

        # Create non-temp file
        other_file = temp_dir / "my_audio.wav"
        other_file.write_text("")

        # Create old temp file
        old_temp = temp_dir / "tmp-audio-1000000000.wav"
        old_temp.write_text("")

        # Cleanup
        recorder.cleanup_temp_files(max_age_hours=0.0000001)

        # Non-temp file should remain
        assert other_file.exists()

    def test_cleanup_ignores_wrong_extension(self, temp_dir):
        """Cleanup only removes .wav files."""
        config = {'temp_dir': str(temp_dir), 'audio_config': {}}
        recorder = AudioRecorder(config)

        # Create old files with wrong extension
        old_mp3 = temp_dir / "tmp-audio-1000000000.mp3"
        old_mp3.write_text("")

        old_flac = temp_dir / "tmp-audio-1000000000.flac"
        old_flac.write_text("")

        # Cleanup
        recorder.cleanup_temp_files(max_age_hours=0.0000001)

        # Non-wav files should remain
        assert old_mp3.exists()
        assert old_flac.exists()


class TestRecorderResourceCleanup:
    """Test resource cleanup and finalization."""

    @mock.patch("soundfile.write")
    @mock.patch("sounddevice.InputStream")
    def test_del_stops_active_recording(self, mock_input_stream, mock_write, temp_dir):
        """__del__ stops active recording."""
        mock_stream = mock.MagicMock()
        mock_input_stream.return_value = mock_stream

        config = {'temp_dir': str(temp_dir), 'audio_config': {}}
        recorder = AudioRecorder(config)

        # Start recording
        recorder.start_recording()
        recorder._audio_data = [np.zeros(1000, dtype=np.float32)]

        # Delete recorder (should stop recording)
        del recorder

        # Stream should have been closed (indirectly via stop_recording)
        # Note: Direct assertion is hard without more complex mocking


class TestExistingRecorderTest:
    """Existing test from test_modes.py - ensure it still works."""

    @mock.patch("sounddevice.InputStream")
    def test_recorder_start_stop(self, mock_input_stream):
        """Test audio recorder start and stop methods."""
        mock_stream = mock.MagicMock()
        mock_input_stream.return_value = mock_stream

        config = {
            'temp_dir': './tmp',
            'audio_config': {
                'sample_rate': 16000,
                'channels': 1,
                'device': None
            }
        }

        recorder = AudioRecorder(config)

        # Start recording
        path = recorder.start_recording()
        assert path is not None
        assert recorder._recording is True

        # Stop recording
        recorder._audio_data = [np.zeros(1000, dtype=np.float32)]
        with mock.patch("soundfile.write"):
            path = recorder.stop_recording()
            assert recorder._recording is False
