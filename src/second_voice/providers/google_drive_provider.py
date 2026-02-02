"""Google Drive input provider for second-voice."""

import os
import re
import logging
from pathlib import Path
from typing import Optional
from datetime import datetime

from .drive_client import DriveClient

logger = logging.getLogger(__name__)


def sanitize_filename(original: str) -> str:
    """Sanitize filename by removing spaces and special characters.

    Args:
        original: Original filename.

    Returns:
        Sanitized filename with extension preserved.
    """
    # Split filename and extension
    name, ext = os.path.splitext(original)

    # Replace spaces with hyphens
    name = name.replace(" ", "-")

    # Remove or replace special characters
    # Keep only alphanumeric, hyphens, underscores, and dots
    name = re.sub(r'[<>:"/\\|?*()]', '', name)

    return name + ext


class GoogleDriveProvider:
    """Fetches voice recordings from Google Drive."""

    def __init__(self, config, keep_remote: bool = False):
        """Initialize Google Drive provider.

        Args:
            config: ConfigurationManager instance from second_voice.core.config
            keep_remote: If True, keep remote file after download.
        """
        self.config = config
        self.keep_remote = keep_remote
        self.drive_client = DriveClient(config)
        self.inbox_dir = Path(config.get('google_drive.inbox_dir', 'dev_notes/inbox'))
        self.archive_dir = Path(config.get('google_drive.archive_dir', 'dev_notes/inbox-archive'))

    def fetch_and_archive(self) -> Optional[Path]:
        """Fetch earliest file from Drive, download to inbox, move to archive.

        Main entry point workflow:
        1. Get earliest file from Drive folder
        2. Download to inbox with remote file's timestamp
        3. Delete remote file (unless keep_remote)
        4. Move from inbox to archive
        5. Return archive path for transcription

        Returns:
            Path to archived file, or None if no files available.
        """
        self._ensure_directories()

        # Get earliest file from Google Drive
        folder_path = self.config.get('google_drive.folder', '/Voice Recordings')
        logger.info(f"Fetching earliest file from {folder_path}")

        file_metadata = self.drive_client.get_earliest_file(folder_path)
        if not file_metadata:
            logger.info("No files found in Google Drive folder")
            return None

        file_id = file_metadata['id']
        original_name = file_metadata['name']
        modified_time_str = file_metadata['modifiedTime']

        logger.info(f"Found file: {original_name} (ID: {file_id})")

        # Parse modified time
        try:
            # Google Drive returns ISO 8601 format: 2026-02-01T18:55:09.000Z
            modified_time = datetime.fromisoformat(modified_time_str.replace('Z', '+00:00'))
        except Exception as e:
            logger.warning(f"Could not parse modified time '{modified_time_str}': {e}. Using current time.")
            modified_time = datetime.now()

        # Generate timestamped filename
        timestamped_name = self._generate_timestamped_filename(original_name, modified_time)

        # Download to inbox
        inbox_path = self.inbox_dir / timestamped_name
        inbox_path = self._ensure_unique_filename(inbox_path)

        logger.info(f"Downloading to inbox: {inbox_path}")
        success = self.drive_client.download_file(file_id, inbox_path)
        if not success:
            logger.error("Failed to download file from Google Drive")
            return None

        # Delete remote file unless keep_remote is set
        if not self.keep_remote:
            logger.info(f"Deleting remote file: {original_name}")
            self.drive_client.delete_file(file_id)

        # Move from inbox to archive
        archive_path = self.archive_dir / inbox_path.name
        archive_path = self._ensure_unique_filename(archive_path)

        logger.info(f"Moving to archive: {archive_path}")
        inbox_path.rename(archive_path)

        return archive_path

    def _generate_timestamped_filename(self, original_name: str, modified_time: datetime) -> str:
        """Generate filename with timestamp from remote file.

        Args:
            original_name: Original filename from Google Drive.
            modified_time: Modified time from Google Drive metadata.

        Returns:
            Timestamped filename in format: YYYY-MM-DD_HH-MM-SS_sanitized-name.ext
        """
        sanitized = sanitize_filename(original_name)
        timestamp = modified_time.strftime("%Y-%m-%d_%H-%M-%S")

        # Split filename and extension
        name, ext = os.path.splitext(sanitized)

        return f"{timestamp}_{name}{ext}"

    def _ensure_unique_filename(self, path: Path) -> Path:
        """Ensure filename is unique by adding counter suffix if needed.

        Args:
            path: Desired file path.

        Returns:
            Unique file path (original if not exists, or with -N suffix).
        """
        if not path.exists():
            return path

        # File exists, add counter
        stem = path.stem
        suffix = path.suffix
        parent = path.parent
        counter = 1

        while True:
            new_path = parent / f"{stem}-{counter}{suffix}"
            if not new_path.exists():
                return new_path
            counter += 1

    def _ensure_directories(self):
        """Create inbox and archive directories if they don't exist."""
        self.inbox_dir.mkdir(parents=True, exist_ok=True)
        self.archive_dir.mkdir(parents=True, exist_ok=True)
        logger.debug(f"Ensured directories exist: {self.inbox_dir}, {self.archive_dir}")
