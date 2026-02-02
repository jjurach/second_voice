import os
import json
import pathlib

class ConfigurationManager:
    """Manage application configuration with multiple sources of truth."""

    DEFAULT_CONFIG = {
        'mode': 'auto',  # default mode
        'stt_provider': 'local_whisper',
        'llm_provider': 'ollama',
        'openrouter_llm_model': 'openai/gpt-oss-120b:free',
        'groq_stt_model': 'whisper-large-v3',
        'local_whisper_url': 'http://localhost:9090/v1/audio/transcriptions',
        'local_whisper_timeout': 300,  # 5 minutes timeout
        'ollama_url': 'http://localhost:11434/api/generate',
        'ollama_model': 'llama-pro:latest',
        'cline_llm_model': 'default-model',  # Added Cline CLI model config
        'cline_api_key': None,  # Optional API key for Cline CLI
        'temp_dir': './tmp',
        'audio_config': {
            'sample_rate': 16000,
            'channels': 1,
            'device': None  # auto-select
        },
        'google_drive': {
            'profile': 'default',
            'folder': '/Voice Recordings',
            'inbox_dir': 'dev_notes/inbox',
            'archive_dir': 'dev_notes/inbox-archive'
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

        # Google Drive environment variable overrides
        if 'SECOND_VOICE_GOOGLE_PROFILE' in os.environ:
            config['google_drive']['profile'] = os.environ['SECOND_VOICE_GOOGLE_PROFILE']
        if 'SECOND_VOICE_GOOGLE_FOLDER' in os.environ:
            config['google_drive']['folder'] = os.environ['SECOND_VOICE_GOOGLE_FOLDER']
        if 'SECOND_VOICE_INBOX_DIR' in os.environ:
            config['google_drive']['inbox_dir'] = os.environ['SECOND_VOICE_INBOX_DIR']
        if 'SECOND_VOICE_ARCHIVE_DIR' in os.environ:
            config['google_drive']['archive_dir'] = os.environ['SECOND_VOICE_ARCHIVE_DIR']

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
        """
        Get a configuration value.
        Supports dot notation for nested values (e.g., 'google_drive.profile').
        """
        if '.' in key:
            keys = key.split('.')
            value = self.config
            for k in keys:
                if isinstance(value, dict):
                    value = value.get(k)
                    if value is None:
                        return default
                else:
                    return default
            return value
        return self.config.get(key, default)

    def set(self, key, value):
        """Set a configuration value."""
        self.config[key] = value

    def __getitem__(self, key):
        """Allow dictionary-style access to config."""
        return self.config[key]
