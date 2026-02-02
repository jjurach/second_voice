"""Unit tests for GoogleDriveProvider."""

import pytest
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path
from datetime import datetime

from second_voice.providers.google_drive_provider import GoogleDriveProvider, sanitize_filename


class MockConfig:
    """Mock configuration for testing."""
    def __init__(self):
        self.config = {
            'google_drive': {
                'profile': 'default',
                'folder': '/Voice Recordings',
                'inbox_dir': 'test_inbox',
                'archive_dir': 'test_archive'
            }
        }

    def get(self, key, default=None):
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


@pytest.fixture
def mock_config():
    """Fixture for mock configuration."""
    return MockConfig()


@pytest.fixture
def mock_drive_client():
    """Fixture for mock DriveClient."""
    mock_client = MagicMock()
    return mock_client


class TestSanitizeFilename:
    """Test suite for sanitize_filename function."""

    def test_sanitize_spaces(self):
        """Test replacing spaces with hyphens."""
        assert sanitize_filename("my file.txt") == "my-file.txt"

    def test_sanitize_special_chars(self):
        """Test removing special characters."""
        assert sanitize_filename('file<>:"|?*().txt') == "file.txt"

    def test_preserve_extension(self):
        """Test preserving file extension."""
        assert sanitize_filename("file.mp3") == "file.mp3"

    def test_already_clean(self):
        """Test already clean filename."""
        assert sanitize_filename("clean-file.txt") == "clean-file.txt"


class TestGoogleDriveProvider:
    """Test suite for GoogleDriveProvider."""

    @patch('second_voice.providers.google_drive_provider.DriveClient')
    def test_initialization(self, mock_drive_client_class, mock_config, tmp_path):
        """Test GoogleDriveProvider initialization."""
        # Setup
        mock_config.config['google_drive']['inbox_dir'] = str(tmp_path / 'inbox')
        mock_config.config['google_drive']['archive_dir'] = str(tmp_path / 'archive')

        # Execute
        provider = GoogleDriveProvider(mock_config, keep_remote=True)

        # Assert
        assert provider.keep_remote is True
        assert provider.inbox_dir == Path(tmp_path / 'inbox')
        assert provider.archive_dir == Path(tmp_path / 'archive')
        mock_drive_client_class.assert_called_once_with(mock_config)

    @patch('second_voice.providers.google_drive_provider.DriveClient')
    def test_fetch_and_archive_no_files(self, mock_drive_client_class, mock_config, tmp_path):
        """Test fetch_and_archive when no files available."""
        # Setup
        mock_config.config['google_drive']['inbox_dir'] = str(tmp_path / 'inbox')
        mock_config.config['google_drive']['archive_dir'] = str(tmp_path / 'archive')

        mock_client = MagicMock()
        mock_client.get_earliest_file.return_value = None
        mock_drive_client_class.return_value = mock_client

        # Execute
        provider = GoogleDriveProvider(mock_config)
        result = provider.fetch_and_archive()

        # Assert
        assert result is None
        mock_client.get_earliest_file.assert_called_once()

    @patch('second_voice.providers.google_drive_provider.DriveClient')
    def test_fetch_and_archive_success(self, mock_drive_client_class, mock_config, tmp_path):
        """Test successful fetch and archive workflow."""
        # Setup
        inbox_dir = tmp_path / 'inbox'
        archive_dir = tmp_path / 'archive'
        mock_config.config['google_drive']['inbox_dir'] = str(inbox_dir)
        mock_config.config['google_drive']['archive_dir'] = str(archive_dir)

        mock_client = MagicMock()
        file_metadata = {
            'id': 'file123',
            'name': 'Recording 1.aac',
            'modifiedTime': '2026-02-01T18:55:09.000Z'
        }
        mock_client.get_earliest_file.return_value = file_metadata

        # Mock download to actually create the file
        def mock_download(file_id, destination):
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_text('fake audio data')
            return True

        mock_client.download_file.side_effect = mock_download
        mock_client.delete_file.return_value = True
        mock_drive_client_class.return_value = mock_client

        # Execute
        provider = GoogleDriveProvider(mock_config, keep_remote=False)
        result = provider.fetch_and_archive()

        # Assert
        assert result is not None
        assert result.parent == archive_dir
        assert result.name == '2026-02-01_18-55-09_Recording-1.aac'
        assert result.exists()
        mock_client.download_file.assert_called_once()
        mock_client.delete_file.assert_called_once_with('file123')

    @patch('second_voice.providers.google_drive_provider.DriveClient')
    def test_fetch_and_archive_keep_remote(self, mock_drive_client_class, mock_config, tmp_path):
        """Test fetch and archive with keep_remote flag."""
        # Setup
        inbox_dir = tmp_path / 'inbox'
        archive_dir = tmp_path / 'archive'
        mock_config.config['google_drive']['inbox_dir'] = str(inbox_dir)
        mock_config.config['google_drive']['archive_dir'] = str(archive_dir)

        mock_client = MagicMock()
        file_metadata = {
            'id': 'file123',
            'name': 'Recording 1.aac',
            'modifiedTime': '2026-02-01T18:55:09.000Z'
        }
        mock_client.get_earliest_file.return_value = file_metadata

        # Mock download to actually create the file
        def mock_download(file_id, destination):
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_text('fake audio data')
            return True

        mock_client.download_file.side_effect = mock_download
        mock_drive_client_class.return_value = mock_client

        # Execute
        provider = GoogleDriveProvider(mock_config, keep_remote=True)
        result = provider.fetch_and_archive()

        # Assert
        assert result is not None
        assert result.exists()
        mock_client.download_file.assert_called_once()
        mock_client.delete_file.assert_not_called()

    @patch('second_voice.providers.google_drive_provider.DriveClient')
    def test_generate_timestamped_filename(self, mock_drive_client_class, mock_config):
        """Test timestamped filename generation."""
        # Setup
        provider = GoogleDriveProvider(mock_config)
        modified_time = datetime(2026, 2, 1, 18, 55, 9)

        # Execute
        result = provider._generate_timestamped_filename('Recording 1.aac', modified_time)

        # Assert
        assert result == '2026-02-01_18-55-09_Recording-1.aac'

    @patch('second_voice.providers.google_drive_provider.DriveClient')
    def test_ensure_unique_filename(self, mock_drive_client_class, mock_config, tmp_path):
        """Test unique filename generation."""
        # Setup
        test_file = tmp_path / 'test.txt'
        test_file.write_text('existing')

        # Execute
        provider = GoogleDriveProvider(mock_config)
        unique_path = provider._ensure_unique_filename(test_file)

        # Assert
        assert unique_path == tmp_path / 'test-1.txt'
        assert not unique_path.exists()

    @patch('second_voice.providers.google_drive_provider.DriveClient')
    def test_ensure_unique_filename_no_conflict(self, mock_drive_client_class, mock_config, tmp_path):
        """Test unique filename with no conflict."""
        # Setup
        test_file = tmp_path / 'new-file.txt'

        # Execute
        provider = GoogleDriveProvider(mock_config)
        unique_path = provider._ensure_unique_filename(test_file)

        # Assert
        assert unique_path == test_file

    @patch('second_voice.providers.google_drive_provider.DriveClient')
    def test_ensure_directories(self, mock_drive_client_class, mock_config, tmp_path):
        """Test directory creation."""
        # Setup
        inbox_dir = tmp_path / 'inbox'
        archive_dir = tmp_path / 'archive'
        mock_config.config['google_drive']['inbox_dir'] = str(inbox_dir)
        mock_config.config['google_drive']['archive_dir'] = str(archive_dir)

        # Execute
        provider = GoogleDriveProvider(mock_config)
        provider._ensure_directories()

        # Assert
        assert inbox_dir.exists()
        assert archive_dir.exists()

    @patch('second_voice.providers.google_drive_provider.DriveClient')
    def test_fetch_and_archive_download_failure(self, mock_drive_client_class, mock_config, tmp_path):
        """Test fetch and archive when download fails."""
        # Setup
        inbox_dir = tmp_path / 'inbox'
        archive_dir = tmp_path / 'archive'
        mock_config.config['google_drive']['inbox_dir'] = str(inbox_dir)
        mock_config.config['google_drive']['archive_dir'] = str(archive_dir)

        mock_client = MagicMock()
        file_metadata = {
            'id': 'file123',
            'name': 'Recording 1.aac',
            'modifiedTime': '2026-02-01T18:55:09.000Z'
        }
        mock_client.get_earliest_file.return_value = file_metadata
        mock_client.download_file.return_value = False
        mock_drive_client_class.return_value = mock_client

        # Execute
        provider = GoogleDriveProvider(mock_config)
        result = provider.fetch_and_archive()

        # Assert
        assert result is None
        mock_client.download_file.assert_called_once()
        mock_client.delete_file.assert_not_called()
