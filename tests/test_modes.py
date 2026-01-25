import unittest
from unittest.mock import MagicMock, patch
import os
import sys
import numpy as np

# Add src to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from second_voice.modes import detect_mode, get_mode, MenuMode

class TestModes(unittest.TestCase):
    def setUp(self):
        self.config = MagicMock()
        self.recorder = MagicMock()
        self.processor = MagicMock()

    @patch('os.environ.get')
    @patch('second_voice.modes.supports_gui')
    @patch('sys.stdout.isatty')
    def test_detect_mode_gui(self, mock_isatty, mock_supports_gui, mock_env_get):
        # Setup for GUI detection
        mock_env_get.return_value = ':0'
        mock_supports_gui.return_value = True
        mock_isatty.return_value = True
        self.config.get.return_value = 'auto'

        from second_voice.modes import GUIMode
        if GUIMode:
            self.assertEqual(detect_mode(self.config), 'gui')

    @patch('os.environ.get')
    @patch('second_voice.modes.supports_gui')
    @patch('second_voice.modes.supports_tui')
    @patch('sys.stdout.isatty')
    def test_detect_mode_tui(self, mock_isatty, mock_supports_tui, mock_supports_gui, mock_env_get):
        # Setup for TUI detection (no GUI, but TTY and TUI support)
        mock_env_get.return_value = None
        mock_supports_gui.return_value = False
        mock_supports_tui.return_value = True
        mock_isatty.return_value = True
        self.config.get.return_value = 'auto'

        from second_voice.modes import TUIMode
        if TUIMode:
            self.assertEqual(detect_mode(self.config), 'tui')

    @patch('os.environ.get')
    @patch('sys.stdout.isatty')
    def test_detect_mode_menu_fallback(self, mock_isatty, mock_env_get):
        # Setup for menu fallback (no TTY)
        mock_env_get.return_value = None
        mock_isatty.return_value = False
        self.config.get.return_value = 'auto'

        self.assertEqual(detect_mode(self.config), 'menu')

    def test_detect_mode_override(self):
        # Setup for explicit override
        self.config.get.side_effect = lambda k, d=None: 'tui' if k == 'mode' else d
        self.assertEqual(detect_mode(self.config), 'tui')

    def test_get_mode_menu(self):
        mode = get_mode('menu', self.config, self.recorder, self.processor)
        self.assertIsInstance(mode, MenuMode)

    def test_get_mode_tui(self):
        from second_voice.modes import TUIMode
        if TUIMode:
            mode = get_mode('tui', self.config, self.recorder, self.processor)
            self.assertIsInstance(mode, TUIMode)
        else:
            self.skipTest("Rich not installed, skipping TUIMode test")

    def test_get_mode_invalid(self):
        with self.assertRaises(ValueError):
            get_mode('invalid_mode', self.config, self.recorder, self.processor)

from second_voice.core.recorder import AudioRecorder
from second_voice.core.processor import AIProcessor

class TestCore(unittest.TestCase):
    def setUp(self):
        self.config = MagicMock()
        def get_side_effect(key, default=None):
            if key == 'temp_dir': return './tmp'
            if key == 'audio_config': return {}
            return default
        self.config.get.side_effect = get_side_effect

    @patch('sounddevice.InputStream')
    def test_recorder_start_stop(self, mock_input_stream):
        recorder = AudioRecorder(self.config)
        path = recorder.start_recording()
        self.assertIsNotNone(path)
        
        # Simulate some audio data
        recorder._audio_data = [np.zeros((1024, 1))]
        recorder._recording = True
        
        with patch('soundfile.write'):
            saved_path = recorder.stop_recording()
            self.assertIsNotNone(saved_path)

if __name__ == '__main__':
    unittest.main()
