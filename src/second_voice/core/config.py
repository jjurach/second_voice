import os
import json
import pathlib

class ConfigurationManager:
    """Manage application configuration with multiple sources of truth."""

    DEFAULT_CONFIG = {
        'mode': 'auto',  # default mode
        'stt_provider': 'groq',
        'llm_provider': 'openrouter',
        'openrouter_llm_model': 'openai/gpt-oss-120b:free',
        'groq_stt_model': 'whisper-large-v3',
        'temp_dir': './tmp',
        'audio_config': {
            'sample_rate': 16000,
            'channels': 1,
            'device': None  # auto-select
        }
    }

    def __init__(self, config_path=None):
        """
        Initialize configuration.

        :param config_path: Optional path to configuration file.
                             Defaults to ~/.config/second_voice/settings.json
        """
        self.config_path = config_path or os.path.expanduser('~/.config/second_voice/settings.json')
        self.config = self._load_config()

    def _load_config(self):
        """
        Load configuration from file, environment variables, and defaults.

        Precedence: Environment Variables > Config File > Default Config
        """
        # Start with default config
        config = self.DEFAULT_CONFIG.copy()

        # Try to load from config file
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r') as f:
                    file_config = json.load(f)
                    config.update(file_config)
        except (json.JSONDecodeError, PermissionError):
            # Silently fall back to defaults if config is invalid
            pass

        # Override with environment variables
        config['mode'] = os.environ.get('SECOND_VOICE_MODE', config['mode'])
        config['stt_provider'] = os.environ.get('SECOND_VOICE_STT_PROVIDER', config['stt_provider'])
        config['llm_provider'] = os.environ.get('SECOND_VOICE_LLM_PROVIDER', config['llm_provider'])

        # Ensure temp directory exists and is writable
        temp_dir = config['temp_dir']
        pathlib.Path(temp_dir).mkdir(parents=True, exist_ok=True)

        return config

    def save(self):
        """Save current configuration to config file."""
        os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
        with open(self.config_path, 'w') as f:
            json.dump(self.config, f, indent=4)

    def get(self, key, default=None):
        """Get a configuration value."""
        return self.config.get(key, default)

    def set(self, key, value):
        """Set a configuration value."""
        self.config[key] = value

    def __getitem__(self, key):
        """Allow dictionary-style access to config."""
        return self.config[key]
