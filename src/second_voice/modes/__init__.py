import os
import sys

from .menu_mode import MenuMode

# Optional imports with graceful degradation
try:
    from .tui_mode import TUIMode
except ImportError:
    TUIMode = None

try:
    from .gui_mode import GUIMode
except ImportError:
    GUIMode = None

def supports_gui():
    """Check if GUI (Tkinter) is available."""
    try:
        import tkinter
        return True
    except ImportError:
        return False

def supports_tui():
    """Check if TUI (rich/curses) is available."""
    try:
        # Try importing rich first
        import rich
        return True
    except ImportError:
        # Fallback to standard curses
        try:
            import curses
            return True
        except ImportError:
            return False

def detect_mode(config):
    """
    Auto-detect appropriate mode based on environment.

    Fallback order: gui → tui → menu

    :param config: Configuration dictionary
    :return: Detected mode name
    """
    # Explicit mode override
    if config.get('mode', 'auto') != 'auto':
        return config['mode']

    # Check for GUI capability
    if os.environ.get('DISPLAY') and supports_gui() and GUIMode:
        return 'gui'

    # Check for TUI capability
    if sys.stdout.isatty() and supports_tui() and TUIMode:
        return 'tui'

    # Default to menu mode (always available)
    return 'menu'

def get_mode(mode_name, config, recorder, processor):
    """
    Get mode instance based on mode name.

    :param mode_name: Mode name (gui, tui, menu)
    :param config: Configuration manager
    :param recorder: Audio recorder
    :param processor: AI processor
    :return: Instantiated mode object
    """
    mode_mapping = {
        'menu': MenuMode,
        'tui': TUIMode,
        'gui': GUIMode
    }

    if mode_name not in mode_mapping or mode_mapping[mode_name] is None:
        raise ValueError(f"Mode {mode_name} not supported or missing dependencies.")

    return mode_mapping[mode_name](config, recorder, processor)
