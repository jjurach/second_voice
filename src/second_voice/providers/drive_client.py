"""Google Drive client for second-voice input provider."""

import os
import io
import json
import logging
from pathlib import Path
from typing import Dict, List, Optional
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.exceptions import RefreshError
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload

logger = logging.getLogger(__name__)

# Google Drive API scopes
SCOPES = [
    "https://www.googleapis.com/auth/drive.readonly",
    "https://www.googleapis.com/auth/drive.file",
]


class DriveClient:
    """Google Drive client for listing and downloading files."""

    def __init__(self, config):
        """Initialize Drive client with authentication.

        Args:
            config: ConfigurationManager instance from second_voice.core.config

        Raises:
            ValueError: If authentication fails.
        """
        self.config = config
        self.service = None
        self._folder_id_cache: Dict[str, str] = {}
        self._authenticate()

    def _get_profile_dir(self) -> Path:
        """Get the profile directory path.

        Returns:
            Path to the google-personal-mcp profile directory.
        """
        profile_name = self.config.get('google_drive.profile', 'default')
        return Path.home() / ".config" / "google-personal-mcp" / "profiles" / profile_name

    def _authenticate(self) -> None:
        """Authenticate with Google Drive API.

        Raises:
            ValueError: If authentication fails.
        """
        profile_dir = self._get_profile_dir()
        credentials_path = profile_dir / "credentials.json"
        token_path = profile_dir / "token.json"

        if not credentials_path.exists():
            raise ValueError(
                f"credentials.json not found at {credentials_path}. "
                f"Please set up Google authentication using google-personal-mcp."
            )

        creds = None

        # Load existing token if available
        if token_path.exists():
            creds = Credentials.from_authorized_user_file(
                str(token_path), SCOPES
            )

        # Refresh token if expired
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
            except RefreshError as e:
                logger.warning(f"Failed to refresh token: {e}. Re-authenticating.")
                creds = None

        # If no valid credentials, run the authentication flow
        if not creds or not creds.valid:
            flow = InstalledAppFlow.from_client_secrets_file(
                str(credentials_path), SCOPES
            )
            creds = flow.run_local_server(port=0)

            # Save the credentials for future use
            with open(token_path, "w") as token_file:
                token_file.write(creds.to_json())

        self.service = build("drive", "v3", credentials=creds)
        logger.info("Successfully authenticated with Google Drive")

    def authenticate(self) -> bool:
        """Public authentication method.

        Returns:
            True if authentication successful, False otherwise.
        """
        try:
            if not self.service:
                self._authenticate()
            return self.service is not None
        except Exception as e:
            logger.error(f"Authentication failed: {e}")
            return False

    def get_earliest_file(self, folder_path: str) -> Optional[Dict]:
        """Get metadata for lexicographically earliest file in folder.

        Args:
            folder_path: Path to folder (e.g., "/Voice Recordings").

        Returns:
            File metadata dict with keys: id, name, mimeType, modifiedTime
            or None if no files found.
        """
        files = self.list_folder_files(folder_path)
        if not files:
            return None

        # Sort by name lexicographically
        files.sort(key=lambda f: f['name'])
        return files[0]

    def list_folder_files(self, folder_path: str) -> List[Dict]:
        """List files in a Google Drive folder.

        Args:
            folder_path: Path to folder (e.g., "/Voice Recordings").

        Returns:
            List of file metadata dicts with keys: id, name, mimeType, modifiedTime.
        """
        if not self.service:
            raise ValueError("Not authenticated with Google Drive")

        # Get folder ID
        folder_id = self._get_folder_id(folder_path)
        if not folder_id:
            logger.warning(f"Folder not found: {folder_path}")
            return []

        # List files in folder
        try:
            results = self.service.files().list(
                q=f"'{folder_id}' in parents and trashed=false",
                spaces="drive",
                fields="files(id, name, mimeType, modifiedTime)",
                pageSize=1000,
            ).execute()

            files = results.get("files", [])
            logger.info(f"Found {len(files)} files in {folder_path}")
            return files
        except Exception as e:
            logger.error(f"Error listing files in {folder_path}: {e}")
            return []

    def _get_folder_id(self, folder_path: str) -> Optional[str]:
        """Resolve folder path to folder ID.

        Args:
            folder_path: Path to folder (e.g., "/Voice Recordings").

        Returns:
            Folder ID or None if not found.
        """
        # Check cache first
        if folder_path in self._folder_id_cache:
            return self._folder_id_cache[folder_path]

        if not self.service:
            return None

        # Split path into parts
        parts = [p for p in folder_path.split("/") if p]

        parent_id = "root"
        current_path = ""

        for part in parts:
            current_path += "/" + part

            # Check if we've already resolved this part
            if current_path in self._folder_id_cache:
                parent_id = self._folder_id_cache[current_path]
                continue

            # Query for folder
            try:
                query = f"name='{part}' and '{parent_id}' in parents and mimeType='application/vnd.google-apps.folder' and trashed=false"
                results = self.service.files().list(
                    q=query,
                    spaces="drive",
                    fields="files(id, name)",
                    pageSize=1,
                ).execute()

                files = results.get("files", [])
                if files:
                    parent_id = files[0]["id"]
                    self._folder_id_cache[current_path] = parent_id
                else:
                    logger.warning(f"Folder not found: {current_path}")
                    return None
            except Exception as e:
                logger.error(f"Error resolving folder {current_path}: {e}")
                return None

        self._folder_id_cache[folder_path] = parent_id
        return parent_id

    def download_file(self, file_id: str, destination: Path) -> bool:
        """Download a file from Google Drive.

        Args:
            file_id: Google Drive file ID.
            destination: Local file path to save to.

        Returns:
            True if download successful, False otherwise.
        """
        if not self.service:
            raise ValueError("Not authenticated with Google Drive")

        try:
            request = self.service.files().get_media(fileId=file_id)
            fh = io.FileIO(str(destination), "wb")
            downloader = MediaIoBaseDownload(fh, request)
            done = False

            while not done:
                status, done = downloader.next_chunk()

            fh.close()
            logger.info(f"Downloaded file {file_id} to {destination}")
            return True
        except Exception as e:
            logger.error(f"Error downloading file {file_id}: {e}")
            return False

    def delete_file(self, file_id: str) -> bool:
        """Delete a file from Google Drive.

        Args:
            file_id: Google Drive file ID.

        Returns:
            True if deletion successful, False otherwise.
        """
        if not self.service:
            raise ValueError("Not authenticated with Google Drive")

        try:
            self.service.files().delete(fileId=file_id).execute()
            logger.info(f"Deleted file {file_id} from Google Drive")
            return True
        except Exception as e:
            logger.error(f"Error deleting file {file_id}: {e}")
            return False

    def get_file_metadata(self, file_id: str) -> Optional[Dict]:
        """Get metadata for a file.

        Args:
            file_id: Google Drive file ID.

        Returns:
            File metadata dict with keys: id, name, mimeType, modifiedTime, size
            or None if not found.
        """
        if not self.service:
            return None

        try:
            file = self.service.files().get(
                fileId=file_id,
                fields="id, name, mimeType, modifiedTime, size",
            ).execute()
            return file
        except Exception as e:
            logger.error(f"Error getting metadata for file {file_id}: {e}")
            return None
