import os
import sounddevice as sd
import soundfile as sf
import numpy as np
import time
import threading

class AudioRecorder:
    """
    A cross-platform audio recorder using sounddevice.

    Supports configurable recording parameters and safe temporary file handling.
    """

    def __init__(self, config):
        """
        Initialize the audio recorder with configuration.

        :param config: Configuration dictionary with audio settings
        """
        self.config = config
        self._audio_config = config.get('audio_config', {})

        # Default audio recording parameters
        self.sample_rate = self._audio_config.get('sample_rate', 16000)
        self.channels = self._audio_config.get('channels', 1)
        self.device = self._audio_config.get('device', None)

        # Temporary audio storage
        self.temp_dir = config.get('temp_dir', './tmp')
        os.makedirs(self.temp_dir, exist_ok=True)

        # Recording state
        self._recording = False
        self._audio_data = []
        self._record_thread = None
        self._current_amplitude = 0.0

    def get_amplitude(self) -> float:
        """
        Get the latest calculated RMS amplitude (0.0 to 1.0).
        
        :return: Normalized amplitude
        """
        return self._current_amplitude

    def _calculate_rms(self, audio_data):
        """
        Calculates Root Mean Square (RMS) amplitude from NumPy array.
        Returns a float between 0 and 1 (normalized).
        """
        if len(audio_data) == 0:
            return 0.0
        
        # RMS Formula: sqrt(mean(s^2))
        rms = np.sqrt(np.mean(audio_data**2))
        
        # Normalize based on typical max (e.g., 0.1 to 0.3 for normal speech with float32)
        # We'll use a sensitivity factor to make it reactive
        normalized = min(1.0, rms * 5.0)
        return float(normalized)

    def _create_temp_audio_path(self, extension='wav'):

        """
        Create a unique temporary audio file path.

        :param extension: File extension (default: wav)
        :return: Absolute path to temporary audio file
        """
        timestamp = int(time.time())
        return os.path.join(self.temp_dir, f'tmp-audio-{timestamp}.{extension}')

    def start_recording(self, duration=None):
        """
        Start recording audio.

        :param duration: Optional recording duration in seconds.
                         If None, records until manually stopped.
        :return: Absolute path to the temporary audio file
        """
        self._recording = True
        self._audio_data = []
        temp_path = self._create_temp_audio_path()

        def callback(indata, frames, time, status):
            """Callback function to handle recording."""
            if status:
                print(f"Recording status: {status}")
            if self._recording:
                self._audio_data.append(indata.copy())
                self._current_amplitude = self._calculate_rms(indata)

        try:
            # Start the stream
            self.stream = sd.InputStream(
                samplerate=self.sample_rate,
                channels=self.channels,
                device=self.device,
                callback=callback
            )
            self.stream.start()

            # If duration specified, stop after that time
            if duration:
                time.sleep(duration)
                self.stop_recording()

            return temp_path
        except Exception as e:
            print(f"Error during recording: {e}")
            self._recording = False
            return None

    def stop_recording(self):
        """
        Stop recording and save audio to file.

        :return: Absolute path to saved audio file, or None if no recording
        """
        if hasattr(self, 'stream') and self.stream:
            self.stream.stop()
            self.stream.close()
            self.stream = None

        if not self._recording:
            return None

        self._recording = False

        # Concatenate recorded audio data
        if not self._audio_data:
            return None

        audio_data = np.concatenate(self._audio_data, axis=0)

        # Create temporary file path
        temp_path = self._create_temp_audio_path()

        # Save audio to file
        sf.write(temp_path, audio_data, self.sample_rate)

        return temp_path

    def get_audio_devices(self):
        """
        List available audio input devices.

        :return: List of available input device names
        """
        devices = sd.query_devices()
        return [device['name'] for device in devices if device['max_input_channels'] > 0]

    def cleanup_temp_files(self, max_age_hours=24):
        """
        Clean up temporary audio files older than specified age.

        :param max_age_hours: Maximum age of files to keep (default: 24 hours)
        """
        current_time = time.time()
        for filename in os.listdir(self.temp_dir):
            if filename.startswith('tmp-audio-') and filename.endswith('.wav'):
                filepath = os.path.join(self.temp_dir, filename)
                file_age = current_time - os.path.getctime(filepath)
                if file_age > (max_age_hours * 3600):
                    os.remove(filepath)

    def __del__(self):
        """
        Cleanup method to ensure resources are released.
        """
        if hasattr(self, '_recording') and self._recording:
            self.stop_recording()
