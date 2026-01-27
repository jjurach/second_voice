"""AAC audio file handling and conversion."""

import os
import tempfile
from pathlib import Path
from typing import Tuple, Optional
import logging

logger = logging.getLogger(__name__)


class AACHandler:
    """Handle AAC files with fallback conversion support."""

    SUPPORTED_EXTENSIONS = ('.aac', '.m4a', '.acc')

    @staticmethod
    def is_aac_file(file_path: str) -> bool:
        """Check if file is AAC format by extension."""
        return Path(file_path).suffix.lower() in AACHandler.SUPPORTED_EXTENSIONS

    @staticmethod
    def validate_aac_file(file_path: str) -> Tuple[bool, Optional[str]]:
        """Validate AAC file readability and format.

        Supports both MP4 (m4a) and ADTS (aac, acc) formats.

        Returns:
            Tuple[bool, Optional[str]]: (is_valid, error_message)
        """
        file_path = os.path.abspath(file_path)

        # Check existence
        if not os.path.exists(file_path):
            return False, f"File not found: {file_path}"

        # Check readability
        if not os.access(file_path, os.R_OK):
            return False, f"File not readable: {file_path}"

        # Try to parse as MP4 (m4a format)
        try:
            from mutagen.mp4 import MP4
            mp4_file = MP4(file_path)
            duration = mp4_file.info.length
            logger.debug(f"AAC file valid (MP4): {duration:.1f}s duration")
            return True, None
        except Exception as mp4_error:
            # Try to validate as ADTS AAC using pydub
            try:
                from pydub import AudioSegment
                audio = AudioSegment.from_file(file_path, format="aac")
                duration = len(audio) / 1000.0
                logger.debug(f"AAC file valid (ADTS): {duration:.1f}s duration")
                return True, None
            except Exception as adts_error:
                return False, f"Invalid AAC file: {str(adts_error)}"

    @staticmethod
    def convert_to_wav(aac_path: str, output_path: Optional[str] = None) -> str:
        """Convert AAC to WAV using pydub + FFmpeg.

        Supports both MP4 (m4a) and ADTS (aac, acc) formats.

        Args:
            aac_path: Path to AAC file
            output_path: Optional explicit output path

        Returns:
            str: Path to converted WAV file

        Raises:
            RuntimeError: If FFmpeg not available or conversion fails
        """
        try:
            from pydub import AudioSegment
            from pydub.exceptions import CouldNotDecodeError
        except ImportError:
            raise RuntimeError("pydub not installed. Install with: pip install pydub")

        try:
            logger.info(f"Converting AAC to WAV: {aac_path}")
            audio = AudioSegment.from_file(aac_path, format="aac")

            if output_path is None:
                # Create temp WAV file with same timestamp, handling multiple AAC extensions
                output_path = (aac_path
                    .replace('.aac', '_converted.wav')
                    .replace('.m4a', '_converted.wav')
                    .replace('.acc', '_converted.wav'))

            audio.export(output_path, format="wav")
            logger.info(f"Conversion complete: {output_path}")
            return output_path

        except FileNotFoundError:
            raise RuntimeError("FFmpeg not found. Install with: apt-get install ffmpeg (Linux) or brew install ffmpeg (macOS)")
        except Exception as e:
            raise RuntimeError(f"Conversion failed: {str(e)}")

    @staticmethod
    def get_duration(file_path: str) -> Optional[float]:
        """Get duration of AAC file in seconds.

        Supports both MP4 (m4a) and ADTS (aac, acc) formats.
        """
        # Try MP4 format first
        try:
            from mutagen.mp4 import MP4
            mp4_file = MP4(file_path)
            return float(mp4_file.info.length)
        except Exception:
            pass

        # Try ADTS format with pydub
        try:
            from pydub import AudioSegment
            audio = AudioSegment.from_file(file_path, format="aac")
            return len(audio) / 1000.0
        except Exception as e:
            logger.warning(f"Could not read AAC duration: {e}")
            return None
