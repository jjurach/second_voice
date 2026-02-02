"""Unit tests for DriveClient."""

import pytest
from unittest.mock import Mock, patch, MagicMock, mock_open
from pathlib import Path
from google.auth.exceptions import RefreshError

from second_voice.providers.drive_client import DriveClient


class MockConfig:
    """Mock configuration for testing."""
    def __init__(self, profile='default'):
        self.profile = profile

    def get(self, key, default=None):
        if key == 'google_drive.profile':
            return self.profile
        return default


@pytest.fixture
def mock_config():
    """Fixture for mock configuration."""
    return MockConfig()


@pytest.fixture
def mock_credentials_path(tmp_path):
    """Fixture for mock credentials path."""
    profile_dir = tmp_path / ".config" / "google-personal-mcp" / "profiles" / "default"
    profile_dir.mkdir(parents=True, exist_ok=True)
    credentials_file = profile_dir / "credentials.json"
    credentials_file.write_text('{"client_id": "test"}')
    token_file = profile_dir / "token.json"
    return profile_dir, credentials_file, token_file


class TestDriveClient:
    """Test suite for DriveClient."""

    @patch('second_voice.providers.drive_client.Path.home')
    @patch('second_voice.providers.drive_client.build')
    @patch('second_voice.providers.drive_client.Credentials.from_authorized_user_file')
    def test_initialization_with_valid_token(self, mock_creds_from_file, mock_build, mock_home, tmp_path):
        """Test DriveClient initialization with valid token."""
        # Setup
        mock_home.return_value = tmp_path
        profile_dir = tmp_path / ".config" / "google-personal-mcp" / "profiles" / "default"
        profile_dir.mkdir(parents=True, exist_ok=True)
        (profile_dir / "credentials.json").write_text('{"client_id": "test"}')
        (profile_dir / "token.json").write_text('{"token": "test"}')

        mock_creds = MagicMock()
        mock_creds.expired = False
        mock_creds.valid = True
        mock_creds_from_file.return_value = mock_creds

        # Execute
        config = MockConfig()
        client = DriveClient(config)

        # Assert
        assert client.service is not None
        mock_build.assert_called_once()

    @patch('second_voice.providers.drive_client.Path.home')
    def test_initialization_without_credentials(self, mock_home, tmp_path):
        """Test DriveClient initialization fails without credentials."""
        # Setup
        mock_home.return_value = tmp_path
        config = MockConfig()

        # Execute & Assert
        with pytest.raises(ValueError, match="credentials.json not found"):
            DriveClient(config)

    @patch('second_voice.providers.drive_client.Path.home')
    @patch('second_voice.providers.drive_client.build')
    @patch('second_voice.providers.drive_client.Credentials.from_authorized_user_file')
    def test_get_earliest_file(self, mock_creds_from_file, mock_build, mock_home, tmp_path):
        """Test getting earliest file from folder."""
        # Setup
        mock_home.return_value = tmp_path
        profile_dir = tmp_path / ".config" / "google-personal-mcp" / "profiles" / "default"
        profile_dir.mkdir(parents=True, exist_ok=True)
        (profile_dir / "credentials.json").write_text('{"client_id": "test"}')
        (profile_dir / "token.json").write_text('{"token": "test"}')

        mock_creds = MagicMock()
        mock_creds.expired = False
        mock_creds.valid = True
        mock_creds_from_file.return_value = mock_creds

        # Mock service
        mock_service = MagicMock()
        mock_build.return_value = mock_service

        # Mock folder listing
        mock_files_list = MagicMock()
        mock_files_list.execute.return_value = {
            'files': [
                {'id': 'id3', 'name': 'c-file.mp3', 'mimeType': 'audio/mpeg', 'modifiedTime': '2023-01-03T10:00:00Z'},
                {'id': 'id1', 'name': 'a-file.mp3', 'mimeType': 'audio/mpeg', 'modifiedTime': '2023-01-01T10:00:00Z'},
                {'id': 'id2', 'name': 'b-file.mp3', 'mimeType': 'audio/mpeg', 'modifiedTime': '2023-01-02T10:00:00Z'},
            ]
        }
        mock_service.files.return_value.list.return_value = mock_files_list

        # Execute
        config = MockConfig()
        client = DriveClient(config)
        earliest = client.get_earliest_file('/Voice Recordings')

        # Assert
        assert earliest is not None
        assert earliest['name'] == 'a-file.mp3'
        assert earliest['id'] == 'id1'

    @patch('second_voice.providers.drive_client.Path.home')
    @patch('second_voice.providers.drive_client.build')
    @patch('second_voice.providers.drive_client.Credentials.from_authorized_user_file')
    def test_download_file(self, mock_creds_from_file, mock_build, mock_home, tmp_path):
        """Test file download."""
        # Setup
        mock_home.return_value = tmp_path
        profile_dir = tmp_path / ".config" / "google-personal-mcp" / "profiles" / "default"
        profile_dir.mkdir(parents=True, exist_ok=True)
        (profile_dir / "credentials.json").write_text('{"client_id": "test"}')
        (profile_dir / "token.json").write_text('{"token": "test"}')

        mock_creds = MagicMock()
        mock_creds.expired = False
        mock_creds.valid = True
        mock_creds_from_file.return_value = mock_creds

        # Mock service
        mock_service = MagicMock()
        mock_build.return_value = mock_service

        # Mock download
        mock_request = MagicMock()
        mock_service.files.return_value.get_media.return_value = mock_request

        with patch('second_voice.providers.drive_client.MediaIoBaseDownload') as mock_downloader:
            mock_downloader_instance = MagicMock()
            mock_downloader_instance.next_chunk.side_effect = [
                (MagicMock(progress=lambda: 0.5), False),
                (MagicMock(progress=lambda: 1.0), True),
            ]
            mock_downloader.return_value = mock_downloader_instance

            with patch('second_voice.providers.drive_client.io.FileIO'):
                # Execute
                config = MockConfig()
                client = DriveClient(config)
                destination = tmp_path / "download.mp3"
                success = client.download_file('file123', destination)

                # Assert
                assert success is True

    @patch('second_voice.providers.drive_client.Path.home')
    @patch('second_voice.providers.drive_client.build')
    @patch('second_voice.providers.drive_client.Credentials.from_authorized_user_file')
    def test_delete_file(self, mock_creds_from_file, mock_build, mock_home, tmp_path):
        """Test file deletion."""
        # Setup
        mock_home.return_value = tmp_path
        profile_dir = tmp_path / ".config" / "google-personal-mcp" / "profiles" / "default"
        profile_dir.mkdir(parents=True, exist_ok=True)
        (profile_dir / "credentials.json").write_text('{"client_id": "test"}')
        (profile_dir / "token.json").write_text('{"token": "test"}')

        mock_creds = MagicMock()
        mock_creds.expired = False
        mock_creds.valid = True
        mock_creds_from_file.return_value = mock_creds

        # Mock service
        mock_service = MagicMock()
        mock_build.return_value = mock_service

        # Mock delete
        mock_delete = MagicMock()
        mock_service.files.return_value.delete.return_value = mock_delete
        mock_delete.execute.return_value = {}

        # Execute
        config = MockConfig()
        client = DriveClient(config)
        success = client.delete_file('file123')

        # Assert
        assert success is True
        mock_service.files.return_value.delete.assert_called_once_with(fileId='file123')

    @patch('second_voice.providers.drive_client.Path.home')
    @patch('second_voice.providers.drive_client.build')
    @patch('second_voice.providers.drive_client.Credentials.from_authorized_user_file')
    def test_get_file_metadata(self, mock_creds_from_file, mock_build, mock_home, tmp_path):
        """Test getting file metadata."""
        # Setup
        mock_home.return_value = tmp_path
        profile_dir = tmp_path / ".config" / "google-personal-mcp" / "profiles" / "default"
        profile_dir.mkdir(parents=True, exist_ok=True)
        (profile_dir / "credentials.json").write_text('{"client_id": "test"}')
        (profile_dir / "token.json").write_text('{"token": "test"}')

        mock_creds = MagicMock()
        mock_creds.expired = False
        mock_creds.valid = True
        mock_creds_from_file.return_value = mock_creds

        # Mock service
        mock_service = MagicMock()
        mock_build.return_value = mock_service

        # Mock metadata
        expected_metadata = {
            'id': 'file123',
            'name': 'test.mp3',
            'mimeType': 'audio/mpeg',
            'modifiedTime': '2023-01-01T10:00:00Z',
            'size': '12345'
        }
        mock_get = MagicMock()
        mock_service.files.return_value.get.return_value = mock_get
        mock_get.execute.return_value = expected_metadata

        # Execute
        config = MockConfig()
        client = DriveClient(config)
        metadata = client.get_file_metadata('file123')

        # Assert
        assert metadata == expected_metadata
        mock_service.files.return_value.get.assert_called_once()
