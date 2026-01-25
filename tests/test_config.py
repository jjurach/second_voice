"""
Unit tests for ConfigurationManager.
Tests configuration loading, persistence, and priority precedence.
"""
import os
import json
import pytest
from pathlib import Path
from unittest import mock

from second_voice.core.config import ConfigurationManager


class TestConfigurationDefaults:
    """Test default configuration values."""

    def test_default_config_contains_required_keys(self):
        """Verify default config has all expected keys."""
        with mock.patch("os.path.exists", return_value=False):
            config = ConfigurationManager()

            assert config.get("mode") == "auto"
            assert config.get("stt_provider") == "local_whisper"
            assert config.get("llm_provider") == "ollama"
            assert config.get("temp_dir") == "./tmp"
            assert "audio_config" in config.config

    def test_default_audio_config(self):
        """Verify default audio configuration values."""
        with mock.patch("os.path.exists", return_value=False):
            config = ConfigurationManager()
            audio_config = config.get("audio_config")

            assert audio_config["sample_rate"] == 16000
            assert audio_config["channels"] == 1
            assert audio_config["device"] is None

    def test_default_whisper_url(self):
        """Verify default Whisper service URL."""
        with mock.patch("os.path.exists", return_value=False):
            config = ConfigurationManager()
            assert config.get("local_whisper_url") == "http://localhost:9090/v1/audio/transcriptions"

    def test_default_ollama_url(self):
        """Verify default Ollama service URL."""
        with mock.patch("os.path.exists", return_value=False):
            config = ConfigurationManager()
            assert config.get("ollama_url") == "http://localhost:11434/api/generate"


class TestConfigFileLoading:
    """Test loading configuration from files."""

    def test_load_valid_config_file(self, mock_config_file):
        """Load valid configuration from JSON file."""
        config = ConfigurationManager(config_path=str(mock_config_file))

        assert config.get("provider") == "groq"
        assert config.get("mode") == "menu"

    def test_merge_file_config_with_defaults(self, mock_config_file):
        """File config merges with defaults, not replaces them."""
        config = ConfigurationManager(config_path=str(mock_config_file))

        # Values from file
        assert config.get("provider") == "groq"

        # Values from defaults (not in file)
        assert config.get("stt_provider") == "local_whisper"
        assert config.get("temp_dir") == "./tmp"

    def test_load_nonexistent_config_file(self, temp_dir):
        """Gracefully handle missing config files (use defaults)."""
        nonexistent = temp_dir / "nonexistent.json"

        with mock.patch("pathlib.Path.mkdir"):
            config = ConfigurationManager(config_path=str(nonexistent))

        # Should fall back to defaults
        assert config.get("mode") == "auto"
        assert config.get("stt_provider") == "local_whisper"

    def test_load_invalid_json_config(self, temp_dir):
        """Handle invalid JSON gracefully (use defaults)."""
        bad_json = temp_dir / "bad.json"
        bad_json.write_text("{ invalid json ]")

        with mock.patch("pathlib.Path.mkdir"):
            config = ConfigurationManager(config_path=str(bad_json))

        # Should fall back to defaults
        assert config.get("mode") == "auto"

    def test_load_empty_config_file(self, temp_dir):
        """Handle empty config files."""
        empty_file = temp_dir / "empty.json"
        empty_file.write_text("{}")

        with mock.patch("pathlib.Path.mkdir"):
            config = ConfigurationManager(config_path=str(empty_file))

        # Should use defaults for missing keys
        assert config.get("mode") == "auto"


class TestEnvironmentVariableOverrides:
    """Test environment variable configuration precedence."""

    def test_env_var_overrides_mode(self, temp_dir):
        """SECOND_VOICE_MODE env var overrides config file and defaults."""
        config_file = temp_dir / "config.json"
        config_file.write_text('{"mode": "menu"}')

        with mock.patch.dict(os.environ, {"SECOND_VOICE_MODE": "gui"}):
            with mock.patch("pathlib.Path.mkdir"):
                config = ConfigurationManager(config_path=str(config_file))

        assert config.get("mode") == "gui"

    def test_env_var_overrides_stt_provider(self, temp_dir):
        """SECOND_VOICE_STT_PROVIDER env var overrides other sources."""
        with mock.patch.dict(os.environ, {"SECOND_VOICE_STT_PROVIDER": "groq"}):
            with mock.patch("pathlib.Path.mkdir"):
                with mock.patch("os.path.exists", return_value=False):
                    config = ConfigurationManager()

        assert config.get("stt_provider") == "groq"

    def test_env_var_overrides_llm_provider(self, temp_dir):
        """SECOND_VOICE_LLM_PROVIDER env var overrides other sources."""
        with mock.patch.dict(os.environ, {"SECOND_VOICE_LLM_PROVIDER": "openrouter"}):
            with mock.patch("pathlib.Path.mkdir"):
                with mock.patch("os.path.exists", return_value=False):
                    config = ConfigurationManager()

        assert config.get("llm_provider") == "openrouter"

    def test_precedence_env_over_file_over_defaults(self, temp_dir):
        """Environment variables have highest precedence."""
        config_file = temp_dir / "config.json"
        config_file.write_text('{"mode": "menu", "stt_provider": "groq"}')

        with mock.patch.dict(os.environ, {"SECOND_VOICE_MODE": "gui"}):
            with mock.patch("pathlib.Path.mkdir"):
                config = ConfigurationManager(config_path=str(config_file))

        # Env var override for mode
        assert config.get("mode") == "gui"

        # File value for stt_provider
        assert config.get("stt_provider") == "groq"

        # Default for llm_provider
        assert config.get("llm_provider") == "ollama"


class TestConfigurationAccess:
    """Test different ways to access configuration values."""

    def test_get_method(self):
        """Test .get() method for accessing config values."""
        with mock.patch("os.path.exists", return_value=False):
            config = ConfigurationManager()

        assert config.get("mode") == "auto"
        assert config.get("nonexistent") is None
        assert config.get("nonexistent", "default") == "default"

    def test_dictionary_style_access(self):
        """Test dictionary-style access with []."""
        with mock.patch("os.path.exists", return_value=False):
            config = ConfigurationManager()

        assert config["mode"] == "auto"
        assert config["stt_provider"] == "local_whisper"

    def test_set_method(self):
        """Test .set() method for updating config values."""
        with mock.patch("os.path.exists", return_value=False):
            config = ConfigurationManager()

        config.set("mode", "gui")
        assert config.get("mode") == "gui"
        assert config["mode"] == "gui"

    def test_set_new_key(self):
        """Test setting a new configuration key."""
        with mock.patch("os.path.exists", return_value=False):
            config = ConfigurationManager()

        config.set("custom_key", "custom_value")
        assert config.get("custom_key") == "custom_value"


class TestConfigurationPersistence:
    """Test saving and loading configuration from disk."""

    def test_save_configuration(self, temp_dir):
        """Save current configuration to file."""
        config_file = temp_dir / "config.json"

        with mock.patch("pathlib.Path.mkdir"):
            config = ConfigurationManager(config_path=str(config_file))
            config.set("mode", "gui")
            config.save()

        # Verify file was created
        assert config_file.exists()

        # Verify saved data
        with open(config_file) as f:
            saved = json.load(f)

        assert saved["mode"] == "gui"

    def test_save_creates_parent_directories(self, temp_dir):
        """save() creates parent directories if needed."""
        config_file = temp_dir / "nested" / "dir" / "config.json"

        config = ConfigurationManager(config_path=str(config_file))
        config.set("mode", "tui")
        config.save()

        assert config_file.exists()
        assert config_file.parent.exists()

    def test_load_after_save(self, temp_dir):
        """Load configuration previously saved to file."""
        config_file = temp_dir / "config.json"

        # Create and save config
        with mock.patch("pathlib.Path.mkdir"):
            config1 = ConfigurationManager(config_path=str(config_file))
            config1.set("mode", "gui")
            config1.set("stt_provider", "groq")
            config1.save()

        # Load config
        with mock.patch("pathlib.Path.mkdir"):
            config2 = ConfigurationManager(config_path=str(config_file))

        assert config2.get("mode") == "gui"
        assert config2.get("stt_provider") == "groq"


class TestTempDirectoryCreation:
    """Test temporary directory handling."""

    def test_temp_dir_created_on_init(self, temp_dir):
        """Temporary directory is created during initialization."""
        temp_location = temp_dir / "tmp"

        with mock.patch("os.path.exists", return_value=False):
            with mock.patch("pathlib.Path.mkdir") as mock_mkdir:
                config = ConfigurationManager()

        # Path.mkdir should be called with parents=True, exist_ok=True
        mock_mkdir.assert_called()

    def test_custom_temp_dir_path(self, temp_dir):
        """Custom temp directory path can be configured."""
        custom_temp = temp_dir / "custom_tmp"

        with mock.patch("os.path.exists", return_value=False):
            with mock.patch("pathlib.Path.mkdir"):
                config = ConfigurationManager()
                config.set("temp_dir", str(custom_temp))

        assert config.get("temp_dir") == str(custom_temp)


class TestDefaultConfigPath:
    """Test default configuration path resolution."""

    def test_default_config_path_expansion(self):
        """Default config path uses ~/.config/second_voice/settings.json."""
        with mock.patch("os.path.expanduser") as mock_expand:
            mock_expand.return_value = "/home/user/.config/second_voice/settings.json"
            with mock.patch("os.path.exists", return_value=False):
                config = ConfigurationManager()

            mock_expand.assert_called_with("~/.config/second_voice/settings.json")

    def test_custom_config_path(self, temp_dir):
        """Custom config path can be provided."""
        config_file = temp_dir / "custom_config.json"

        with mock.patch("pathlib.Path.mkdir"):
            config = ConfigurationManager(config_path=str(config_file))

        # Config path should be set correctly
        assert config.config_path == str(config_file)


class TestConfigurationMerging:
    """Test how configurations from different sources merge."""

    def test_nested_config_replaces_defaults(self, temp_dir):
        """Nested objects from file completely replace defaults (not deep merge)."""
        config_file = temp_dir / "config.json"
        config_file.write_text('{"audio_config": {"sample_rate": 48000}}')

        with mock.patch("pathlib.Path.mkdir"):
            config = ConfigurationManager(config_path=str(config_file))

        # File value replaces defaults entirely
        audio_config = config.get("audio_config")
        assert audio_config["sample_rate"] == 48000
        assert "channels" not in audio_config  # Default was replaced
