# Project Plan: AAC Support & Whisper Output Recovery

**Status:** 🔵 Ready for Implementation
**Last Updated:** 2026-01-26
**Estimated Phases:** 5
**Priority:** High

---

## 📋 Executive Summary

Enhance Second Voice to:
1. Process `.aac` audio files (resolves: "Error: Invalid audio file")
2. Preserve whisper transcriptions for recovery and debugging
3. Add structured metadata headers to track audio sources and processing status

**Key Changes:**
- Add AAC format support via mutagen/pydub
- Timestamp all temporary files for audit trail
- Create fallback mechanism for LLM failures
- Inject/verify metadata headers in outputs

---

## 🎯 Goals & Success Criteria

### Primary Goals
✅ Accept `.aac` files without error
✅ Preserve whisper output for recovery
✅ Add structured metadata headers
✅ Maintain backward compatibility

### Success Metrics
- [ ] `python src/cli/run.py --file samples/recording.aac` processes successfully
- [ ] `tmp/recording-2026-01-26_HH-MM-SS.aac` created and protected
- [ ] `tmp/whisper-2026-01-26_HH-MM-SS.txt` created with raw transcription
- [ ] Output contains valid metadata headers
- [ ] 100% test pass rate (no regressions)

---

## 📊 Current State Analysis

### ✅ Already Working
1. CLI argument parsing (`--file`, `--keep-files`)
2. Temporary file cleanup logic
3. Audio format detection (WAV, FLAC, OGG, MP3, AIFF)
4. Mode-based file processing (TUI, Menu, GUI)

### ❌ Gaps to Address
1. **No AAC support** - `soundfile` doesn't handle AAC natively
2. **Unnamed temp files** - No timestamps, hard to track
3. **No whisper output preservation** - Transcription discarded on failure
4. **No metadata headers** - Output lacks source/date/status context
5. **No fallback on LLM failure** - Whisper output not used as backup

### 🔧 Library Support (Research Summary)

**Mutagen:**
- ✅ Supports AAC metadata reading
- ✅ Pure Python, cross-platform
- ✅ Version 1.46+

**pydub:**
- ✅ AAC conversion to WAV
- ⚠️ Requires FFmpeg binary
- ✅ Version 0.25+

**FFmpeg:**
- ✅ System dependency for AAC decoding
- ✅ Widely available (apt, brew, choco)
- ✅ Already used indirectly by some audio tools

---

## 🏗️ Implementation Plan

### Phase 1: Add AAC Support (Dependencies & Detection)

**Timeline:** Tasks 1-3 (foundation)

#### Task 1.1: Update Dependencies
**File:** `requirements.txt`

**Changes:**
```diff
+ mutagen>=1.46
+ pydub>=0.25
```

**Testing:**
```bash
pip install -r requirements.txt
python -c "from mutagen.mp4 import MP4; from pydub import AudioSegment; print('✓ AAC libraries imported')"
```

**Success:** Both imports succeed without error

---

#### Task 1.2: Create AAC Detection & Validation Module
**File:** `src/second_voice/audio/aac_handler.py` (NEW)

**Purpose:** Handle AAC-specific operations

```python
"""AAC audio file handling and conversion."""

import os
import tempfile
from pathlib import Path
from typing import Tuple, Optional
import logging

logger = logging.getLogger(__name__)

class AACHandler:
    """Handle AAC files with fallback conversion support."""

    SUPPORTED_EXTENSIONS = ('.aac', '.m4a')

    @staticmethod
    def is_aac_file(file_path: str) -> bool:
        """Check if file is AAC format by extension."""
        return Path(file_path).suffix.lower() in AACHandler.SUPPORTED_EXTENSIONS

    @staticmethod
    def validate_aac_file(file_path: str) -> Tuple[bool, Optional[str]]:
        """Validate AAC file readability and format.

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

        # Try to parse as AAC using mutagen
        try:
            from mutagen.mp4 import MP4
            mp4_file = MP4(file_path)
            duration = mp4_file.info.length
            logger.debug(f"AAC file valid: {duration:.1f}s duration")
            return True, None
        except Exception as e:
            return False, f"Invalid AAC file: {str(e)}"

    @staticmethod
    def convert_to_wav(aac_path: str, output_path: Optional[str] = None) -> str:
        """Convert AAC to WAV using pydub + FFmpeg.

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
                # Create temp WAV file with same timestamp
                output_path = aac_path.replace('.aac', '_converted.wav').replace('.m4a', '_converted.wav')

            audio.export(output_path, format="wav")
            logger.info(f"Conversion complete: {output_path}")
            return output_path

        except FileNotFoundError:
            raise RuntimeError("FFmpeg not found. Install with: apt-get install ffmpeg (Linux) or brew install ffmpeg (macOS)")
        except Exception as e:
            raise RuntimeError(f"Conversion failed: {str(e)}")

    @staticmethod
    def get_duration(file_path: str) -> Optional[float]:
        """Get duration of AAC file in seconds."""
        try:
            from mutagen.mp4 import MP4
            mp4_file = MP4(file_path)
            return float(mp4_file.info.length)
        except Exception as e:
            logger.warning(f"Could not read AAC duration: {e}")
            return None
```

**Testing:**
```bash
# Test detection
python -c "from src.second_voice.audio.aac_handler import AACHandler; print(AACHandler.is_aac_file('test.aac'))"

# Test validation (with real AAC file)
python -c "from src.second_voice.audio.aac_handler import AACHandler; valid, msg = AACHandler.validate_aac_file('tmp/recording.aac'); print(f'Valid: {valid}')"
```

**Success:** Module imports, detects AAC, validates format

---

#### Task 1.3: Update Audio Reader to Support AAC
**File:** `src/second_voice/core/recorder.py`

**Changes (around line ~30, in imports):**
```python
# Add AAC handler import
from ..audio.aac_handler import AACHandler
```

**Changes (add new method to Recorder class, ~line 50):**
```python
def read_audio_with_aac_fallback(self, file_path: str) -> Tuple[np.ndarray, int]:
    """Read audio file, converting AAC if needed.

    Args:
        file_path: Path to audio file

    Returns:
        Tuple[audio_data, sample_rate]
    """
    file_path = os.path.abspath(file_path)

    try:
        # Try soundfile first (faster, native formats)
        audio_data, sample_rate = sf.read(file_path)
        return audio_data, sample_rate
    except Exception as soundfile_error:
        # Check if it's AAC
        if AACHandler.is_aac_file(file_path):
            logger.info("soundfile couldn't read AAC, attempting conversion...")
            try:
                wav_path = AACHandler.convert_to_wav(file_path)
                audio_data, sample_rate = sf.read(wav_path)
                # Clean up temp WAV
                os.unlink(wav_path)
                return audio_data, sample_rate
            except Exception as aac_error:
                raise RuntimeError(
                    f"Failed to read audio file: {soundfile_error}\n"
                    f"AAC conversion also failed: {aac_error}\n"
                    f"Ensure FFmpeg is installed: apt-get install ffmpeg"
                )
        else:
            raise RuntimeError(f"Failed to read audio file: {soundfile_error}")
```

**Update existing file read call (find `sf.read()` in recorder.py, ~line 145):**
```python
# OLD:
# audio_data, sample_rate = sf.read(file_path)

# NEW:
audio_data, sample_rate = self.read_audio_with_aac_fallback(file_path)
```

**Testing:**
```bash
python src/cli/run.py --file samples/test.aac --no-edit
```

**Success:** AAC files read without error, converted and processed

---

### Phase 2: Timestamped Temporary Files

**Timeline:** Tasks 2.1-2.3

#### Task 2.1: Create Timestamp Utility Module
**File:** `src/second_voice/utils/timestamp.py` (NEW)

```python
"""Timestamp utilities for file naming and logging."""

from datetime import datetime
from pathlib import Path
import os

def get_timestamp() -> str:
    """Get current timestamp in format YYYY-MM-DD_HH-MM-SS."""
    return datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

def create_recording_filename(tmp_dir: str, format: str = "wav") -> str:
    """Create timestamped recording filename.

    Args:
        tmp_dir: Temporary directory path
        format: Audio format (default: 'wav')

    Returns:
        str: Full path to recording file
        Example: /tmp/recording-2026-01-26_14-30-45.wav
    """
    timestamp = get_timestamp()
    filename = f"recording-{timestamp}.{format}"
    return os.path.join(tmp_dir, filename)

def create_whisper_filename(tmp_dir: str, timestamp: str) -> str:
    """Create timestamped whisper output filename.

    Args:
        tmp_dir: Temporary directory path
        timestamp: Recording timestamp (for matching)

    Returns:
        str: Full path to whisper output file
        Example: /tmp/whisper-2026-01-26_14-30-45.txt
    """
    filename = f"whisper-{timestamp}.txt"
    return os.path.join(tmp_dir, filename)

def extract_timestamp_from_filename(filename: str) -> str:
    """Extract timestamp from recording filename.

    Args:
        filename: Recording filename

    Returns:
        str: Timestamp in YYYY-MM-DD_HH-MM-SS format
        Example: "2026-01-26_14-30-45" from "recording-2026-01-26_14-30-45.wav"
    """
    # Extract pattern: recording-<TIMESTAMP>.ext
    name_only = Path(filename).stem  # Remove extension
    if name_only.startswith('recording-'):
        return name_only[10:]  # Remove 'recording-' prefix
    return None

def find_matching_whisper_file(recording_path: str) -> str:
    """Find whisper output file matching a recording.

    Args:
        recording_path: Path to recording file

    Returns:
        str: Path to matching whisper file, or None if not found
    """
    timestamp = extract_timestamp_from_filename(recording_path)
    if not timestamp:
        return None

    tmp_dir = os.path.dirname(recording_path)
    whisper_path = create_whisper_filename(tmp_dir, timestamp)

    return whisper_path if os.path.exists(whisper_path) else None
```

**Testing:**
```python
from src.second_voice.utils.timestamp import get_timestamp, create_recording_filename

ts = get_timestamp()
print(f"Timestamp format: {ts}")  # Should print: 2026-01-26_HH-MM-SS

recording = create_recording_filename("/tmp", "aac")
print(f"Recording file: {recording}")  # Should print: /tmp/recording-2026-01-26_HH-MM-SS.aac
```

**Success:** Timestamps generated correctly, filenames formatted properly

---

#### Task 2.2: Update Recorder to Create Timestamped Files
**File:** `src/second_voice/core/recorder.py`

**Changes (in `record_audio` method, around line ~110):**

```python
# OLD:
# output_file = os.path.join(self.tmp_dir, f"tmp-audio-{int(time.time())}.wav")

# NEW:
from ..utils.timestamp import create_recording_filename
output_file = create_recording_filename(self.tmp_dir, format="wav")

logger.info(f"Recording to: {output_file}")
```

**Changes (add method to Recorder class for processing external files):**
```python
def process_external_file(self, file_path: str) -> Tuple[str, str, Optional[str]]:
    """Process external audio file, returns paths for tracking.

    Args:
        file_path: Path to input audio file

    Returns:
        Tuple[audio_data_path, timestamp, source_format]
        Example: ('/tmp/recording-2026-01-26_14-30-45.wav', '2026-01-26_14-30-45', 'aac')
    """
    from ..utils.timestamp import create_recording_filename, get_timestamp

    input_format = Path(file_path).suffix.lstrip('.').lower()
    timestamp = get_timestamp()

    # If input is AAC, convert it
    if AACHandler.is_aac_file(file_path):
        # Convert to WAV and save with timestamp
        wav_path = create_recording_filename(self.tmp_dir, format="wav")
        self.read_audio_with_aac_fallback(file_path)  # Validates
        audio_data, sr = sf.read(file_path)  # After conversion
        sf.write(wav_path, audio_data, sr)
        return wav_path, timestamp, input_format
    else:
        # Copy/symlink existing file with timestamp
        wav_path = create_recording_filename(self.tmp_dir, format="wav")
        audio_data, sr = sf.read(file_path)
        sf.write(wav_path, audio_data, sr)
        return wav_path, timestamp, input_format
```

**Testing:**
```bash
ls -ltr /tmp/recording-*.wav  # Should show timestamped files
```

**Success:** Timestamped files created, old tmp-audio-*.wav pattern phased out

---

#### Task 2.3: Add Whisper Output Logging
**File:** `src/second_voice/core/processor.py`

**Changes (add imports at top, ~line 5):**
```python
import os
from pathlib import Path
from datetime import datetime
from ..utils.timestamp import create_whisper_filename
```

**Changes (in transcribe method, around line ~60):**

```python
def transcribe_audio(self, audio_data: np.ndarray, sample_rate: int,
                    recording_timestamp: Optional[str] = None) -> str:
    """Transcribe audio to text.

    Args:
        audio_data: Audio samples
        sample_rate: Sample rate in Hz
        recording_timestamp: Timestamp from recording for matching whisper file

    Returns:
        str: Transcribed text
    """
    # ... existing transcription code ...
    transcript = self._call_whisper_api(audio_data, sample_rate)

    # Save whisper output for recovery
    if recording_timestamp:
        whisper_path = create_whisper_filename(self.tmp_dir, recording_timestamp)
        try:
            with open(whisper_path, 'w', encoding='utf-8') as f:
                f.write(transcript)
            logger.info(f"Whisper output saved: {whisper_path}")
        except Exception as e:
            logger.warning(f"Could not save whisper output: {e}")

    return transcript
```

**Testing:**
```bash
# Run with input file
python src/cli/run.py --file samples/test.wav --keep-files

# Check for whisper output
ls -la /tmp/whisper-*.txt
```

**Success:** Whisper output files created with correct timestamps, matching recordings

---

### Phase 3: Whisper Output Recovery & Fallback

**Timeline:** Tasks 3.1-3.2

#### Task 3.1: Implement Fallback on LLM Failure
**File:** `src/second_voice/core/processor.py`

**Changes (in process method, around line ~100):**

```python
def process_with_fallback(self, transcript: str, context: str = "") -> str:
    """Process transcript with LLM, fallback to raw transcript on failure.

    Args:
        transcript: Whisper output
        context: Previous context from session

    Returns:
        str: Processed output or raw transcript on failure
    """
    try:
        # Attempt LLM processing (existing code)
        result = self.process(transcript, context)
        logger.info("LLM processing successful")
        return result
    except Exception as e:
        logger.error(f"LLM processing failed: {e}")
        logger.info("Falling back to raw whisper output")

        # Return raw transcript as fallback
        fallback_msg = (
            "⚠️ **Warning**: LLM processing failed, returning raw transcript.\n\n"
            f"Error: {str(e)}\n\n"
            f"---\n\n"
            f"{transcript}"
        )
        return fallback_msg
```

**Testing:**
```bash
# Simulate failure by interrupting LLM
python src/cli/run.py --file samples/test.wav --keep-files
# Ctrl+C during LLM processing
# Should see fallback message
```

**Success:** Fallback triggers on LLM error, returns raw whisper output

---

#### Task 3.2: Add Recovery Script for Orphaned Files
**File:** `scripts/recover_whisper_output.py` (NEW)

```python
#!/usr/bin/env python3
"""
Recover whisper output from temporary files.

Usage:
    python scripts/recover_whisper_output.py [--tmp-dir /path/to/tmp]
"""

import os
import sys
import glob
import argparse
from pathlib import Path
from datetime import datetime, timedelta

def find_orphaned_whisper_files(tmp_dir: str, age_hours: int = 24) -> list:
    """Find whisper output files without matching recording.

    Args:
        tmp_dir: Temporary directory to scan
        age_hours: Only find files older than this many hours

    Returns:
        list: Paths to orphaned whisper files
    """
    whisper_files = glob.glob(os.path.join(tmp_dir, "whisper-*.txt"))
    cutoff_time = datetime.now() - timedelta(hours=age_hours)

    orphaned = []
    for whisper_path in whisper_files:
        mtime = datetime.fromtimestamp(os.path.getmtime(whisper_path))
        if mtime < cutoff_time:
            orphaned.append(whisper_path)

    return orphaned

def main():
    parser = argparse.ArgumentParser(description="Recover whisper output from temp files")
    parser.add_argument("--tmp-dir", default="./tmp", help="Temporary directory (default: ./tmp)")
    parser.add_argument("--age-hours", type=int, default=24, help="Age threshold in hours (default: 24)")
    parser.add_argument("--recover", action="store_true", help="Copy orphaned files to recovery directory")
    parser.add_argument("--recovery-dir", default="./recovery", help="Recovery directory (default: ./recovery)")

    args = parser.parse_args()

    orphaned = find_orphaned_whisper_files(args.tmp_dir, args.age_hours)

    if not orphaned:
        print(f"✓ No orphaned whisper files in {args.tmp_dir}")
        return 0

    print(f"Found {len(orphaned)} orphaned whisper file(s):\n")
    for path in orphaned:
        size = os.path.getsize(path)
        mtime = datetime.fromtimestamp(os.path.getmtime(path))
        print(f"  {path} ({size} bytes, modified {mtime})")

    if args.recover:
        os.makedirs(args.recovery_dir, exist_ok=True)
        for path in orphaned:
            dest = os.path.join(args.recovery_dir, os.path.basename(path))
            import shutil
            shutil.copy2(path, dest)
            print(f"✓ Recovered: {dest}")

    return 0

if __name__ == "__main__":
    sys.exit(main())
```

**Make script executable:**
```bash
chmod +x scripts/recover_whisper_output.py
```

**Testing:**
```bash
python scripts/recover_whisper_output.py
python scripts/recover_whisper_output.py --recover --recovery-dir ./recovered_whisper
ls -la ./recovered_whisper/
```

**Success:** Recovery script identifies and can restore whisper output

---

### Phase 4: Output Headers with Metadata

**Timeline:** Tasks 4.1-4.3

#### Task 4.1: Create Header Builder Module
**File:** `src/second_voice/utils/headers.py` (NEW)

```python
"""Output header generation and validation."""

from datetime import datetime
from typing import Optional, Tuple
import re

class Header:
    """Metadata header for audio/transcript tracking."""

    def __init__(self, source: str, date: Optional[str] = None,
                 status: str = "Awaiting transformation",
                 title: Optional[str] = None,
                 project: Optional[str] = None):
        self.source = source
        self.date = date or datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.status = status
        self.title = title
        self.project = project

    def to_string(self, include_title: bool = False, include_project: bool = False) -> str:
        """Render header as markdown."""
        lines = [
            f"**Source**: {self.source}",
            f"**Date:** {self.date}",
            f"**Status:** {self.status}",
        ]

        if include_title and self.title:
            lines.append(f"**Title:** {self.title}")

        if include_project and self.project:
            lines.append(f"**Project:** {self.project}")

        return "\n".join(lines)

    @staticmethod
    def from_string(text: str) -> Optional['Header']:
        """Parse header from markdown text.

        Returns:
            Header object or None if no valid header found
        """
        patterns = {
            'source': r'\*\*Source\*\*:\s*(.+)',
            'date': r'\*\*Date:\*\*\s*(.+)',
            'status': r'\*\*Status:\*\*\s*(.+)',
            'title': r'\*\*Title:\*\*\s*(.+)',
            'project': r'\*\*Project:\*\*\s*(.+)',
        }

        matches = {}
        for key, pattern in patterns.items():
            match = re.search(pattern, text, re.MULTILINE)
            if match:
                matches[key] = match.group(1).strip()

        if 'source' not in matches:
            return None  # No valid header found

        return Header(
            source=matches.get('source'),
            date=matches.get('date'),
            status=matches.get('status', "Awaiting transformation"),
            title=matches.get('title'),
            project=matches.get('project'),
        )

def infer_project_name(text: str) -> str:
    """Infer project name from content.

    Simple heuristic: look for common project keywords.
    Falls back to "unknown" if no match found.
    """
    text_lower = text.lower()

    # Common project keywords (customize for your environment)
    keywords = {
        'second-voice': ['voice', 'audio', 'transcript', 'whisper'],
        'docs': ['document', 'markdown', 'readme', 'manual'],
        'api': ['endpoint', 'rest', 'http', 'request', 'response'],
        'ui': ['button', 'interface', 'design', 'component', 'react'],
        'database': ['query', 'sql', 'database', 'table', 'schema'],
    }

    for project, keywords_list in keywords.items():
        if any(kw in text_lower for kw in keywords_list):
            return project

    return "unknown"

def generate_title(text: str, max_length: int = 60) -> str:
    """Auto-generate title from content.

    Takes first significant line(s) and truncates to max_length.
    """
    lines = text.split('\n')

    # Find first non-empty line
    title_parts = []
    char_count = 0

    for line in lines:
        line = line.strip()
        if not line or line.startswith('**'):  # Skip headers
            continue

        words = line.split()
        for word in words:
            if char_count + len(word) + 1 <= max_length:
                title_parts.append(word)
                char_count += len(word) + 1
            else:
                break

        if char_count > 0:
            break

    title = ' '.join(title_parts)
    return title[:max_length].rstrip('.')
```

**Testing:**
```python
from src.second_voice.utils.headers import Header, infer_project_name, generate_title

# Test header creation
header = Header("tmp/recording-01.aac", status="Awaiting transformation")
print(header.to_string())

# Test inference
project = infer_project_name("I need to fix the voice transcription API")
print(f"Inferred project: {project}")

# Test title generation
title = generate_title("This is a long sentence that describes what the user wants")
print(f"Generated title: {title}")
```

**Success:** Headers generated correctly, projects inferred, titles auto-generated

---

#### Task 4.2: Update System Prompt for Header Awareness
**File:** `src/second_voice/prompts/system_prompt.md` (UPDATE)

**Add to prompt (after instruction about context handling):**

```markdown
## Processing Metadata Headers

Input text will contain metadata headers in this format:
```
**Source**: tmp/recording-1.aac
**Date:** 2026-01-25 22:46:00
**Status:** Awaiting transformation
```

These headers are METADATA about the audio source, NOT content the user has spoken.

Your output MUST contain an enhanced version of these headers:
```
**Source**: second-voice from tmp/recording-1.aac
**Date:** [Current time]
**Status:** Awaiting ingest
**Title:** [Auto-generated from content, max 60 chars]
**Project:** [Inferred from content or "unknown"]
```

If input headers are missing, infer them from context. If output headers are incomplete, Second Voice will attempt to complete them.
```

**Testing:**
```bash
# Verify prompt loads
python -c "from src.second_voice.prompts import system_prompt; print(system_prompt[:100])"
```

**Success:** System prompt updated, LLM aware of header semantics

---

#### Task 4.3: Inject Headers into LLM Processing
**File:** `src/second_voice/core/processor.py`

**Changes (in process method, around line ~70):**

```python
def process_with_headers(self, transcript: str, recording_path: Optional[str] = None,
                        context: str = "") -> str:
    """Process transcript with header injection.

    Args:
        transcript: Raw whisper output
        recording_path: Path to recording (for source header)
        context: Session context

    Returns:
        str: LLM output with headers
    """
    from ..utils.headers import Header, generate_title, infer_project_name
    from pathlib import Path

    # Parse existing headers if present
    existing_header = Header.from_string(transcript)

    if not existing_header:
        # Build new header
        source = Path(recording_path).name if recording_path else "unknown"
        title = generate_title(transcript)
        project = infer_project_name(transcript)

        header = Header(
            source=source,
            status="Awaiting transformation",
            title=title,
            project=project
        )
    else:
        header = existing_header

    # Prepend header to input
    header_text = header.to_string(include_title=False, include_project=False)
    augmented_transcript = f"{header_text}\n\n{transcript}"

    try:
        # Process with LLM
        result = self.process(augmented_transcript, context)

        # Ensure output has headers
        output_header = Header.from_string(result)
        if not output_header:
            # Inject headers into output
            result_header = Header(
                source=f"second-voice from {header.source}",
                status="Awaiting ingest",
                title=generate_title(result),
                project=infer_project_name(result)
            )
            result = f"{result_header.to_string(True, True)}\n\n{result}"

        return result
    except Exception as e:
        raise RuntimeError(f"LLM processing failed: {e}")
```

**Testing:**
```bash
python src/cli/run.py --file samples/test.wav --no-edit
# Check output contains headers like:
# **Source**: recording-...
# **Date:** ...
# **Status:** Awaiting ingest
```

**Success:** Headers injected into input and output, metadata preserved

---

### Phase 4.5: Test Fixture Preparation

**Timeline:** Task 4.5 (one-time setup before Phase 5)

#### Task 4.5: Extract Test AAC Fixture

**Context:**
A large AAC file exists at `tmp/recording-2.aac` that can be used as test input. However, this file should NOT be committed to the source tree (it's too large for regression testing in CI/CD).

**Task:**
Create a throwaway Python script that extracts the first 30 seconds of `tmp/recording-2.aac` and saves it as `samples/test.aac` for use in regression tests.

**Script:** `scripts/extract_test_aac.py` (THROWAWAY - delete after use)

```python
#!/usr/bin/env python3
"""
Extract first 30 seconds of tmp/recording-2.aac for regression testing.

This is a ONE-TIME script to create samples/test.aac.
After running, this script can be deleted.

Usage:
    python scripts/extract_test_aac.py
"""

import os
from pydub import AudioSegment
from pathlib import Path

def extract_test_fixture():
    """Extract first 30 seconds of recording for testing."""

    source_file = "tmp/recording-2.aac"
    output_file = "samples/test.aac"

    # Check source exists
    if not os.path.exists(source_file):
        print(f"Error: {source_file} not found")
        return False

    print(f"Loading {source_file}...")
    audio = AudioSegment.from_file(source_file, format="aac")

    # Extract first 30 seconds (30000 milliseconds)
    duration_ms = len(audio)
    extracted = audio[:30000]

    print(f"Original duration: {duration_ms/1000:.1f}s")
    print(f"Extracted duration: {len(extracted)/1000:.1f}s")

    # Ensure output directory exists
    os.makedirs(os.path.dirname(output_file), exist_ok=True)

    # Export as AAC
    print(f"Exporting to {output_file}...")
    extracted.export(output_file, format="aac")

    # Verify
    if os.path.exists(output_file):
        size = os.path.getsize(output_file)
        print(f"✓ Created {output_file} ({size/1024:.1f} KB)")
        return True
    else:
        print(f"✗ Failed to create {output_file}")
        return False

if __name__ == "__main__":
    success = extract_test_fixture()
    exit(0 if success else 1)
```

**Execution Instructions for Implementor:**

```bash
# Prerequisites: pydub and FFmpeg must be installed
pip install pydub
ffmpeg -version  # Verify FFmpeg is available

# Run extraction (one-time)
python scripts/extract_test_aac.py

# Verify output was created
ls -lh samples/test.aac
ffprobe samples/test.aac  # Check duration is ~30s

# Delete the throwaway script
rm scripts/extract_test_aac.py

# Verify the test file can be used
python src/cli/run.py --file samples/test.aac --no-edit
```

**Important Notes:**
- ✅ `samples/test.aac` (30-second excerpt) **SHOULD** be committed to source tree
- ❌ `tmp/recording-2.aac` (original large file) **SHOULD NOT** be committed
- 🗑️ `scripts/extract_test_aac.py` is temporary and should be deleted after execution
- The resulting `samples/test.aac` should be ~500KB-2MB depending on bitrate

**Success Criteria:**
- [ ] `samples/test.aac` exists and is 30 seconds long
- [ ] File size is reasonable for regression testing (<5MB)
- [ ] File can be processed by `python src/cli/run.py --file samples/test.aac`
- [ ] Script has been deleted after use
- [ ] No large files in `tmp/` are committed to git

---

### Phase 5: Testing & Documentation

**Timeline:** Tasks 5.1-5.3 (depends on Phase 4.5)

#### Task 5.1: Unit Tests for New Modules
**File:** `tests/test_aac_handler.py` (NEW)

```python
"""Tests for AAC audio handling."""

import pytest
import os
from pathlib import Path
from src.second_voice.audio.aac_handler import AACHandler

class TestAACHandler:

    def test_is_aac_file(self):
        """Test AAC file detection."""
        assert AACHandler.is_aac_file("recording.aac")
        assert AACHandler.is_aac_file("song.m4a")
        assert not AACHandler.is_aac_file("audio.wav")
        assert not AACHandler.is_aac_file("audio.mp3")

    def test_validate_nonexistent_file(self):
        """Test validation of missing file."""
        valid, msg = AACHandler.validate_aac_file("/nonexistent/file.aac")
        assert not valid
        assert "not found" in msg.lower()

    # Additional tests for conversion, duration, etc.
```

**File:** `tests/test_headers.py` (NEW)

```python
"""Tests for metadata headers."""

import pytest
from src.second_voice.utils.headers import Header, generate_title, infer_project_name

class TestHeaders:

    def test_header_creation(self):
        """Test header object creation."""
        header = Header("recording-01.aac", status="Awaiting transformation")
        assert "recording-01.aac" in header.to_string()
        assert "Awaiting transformation" in header.to_string()

    def test_generate_title(self):
        """Test title generation."""
        text = "Please implement a new API endpoint for user authentication"
        title = generate_title(text)
        assert len(title) <= 60
        assert title.startswith("Please")

    def test_infer_project(self):
        """Test project inference."""
        assert infer_project_name("fix the voice transcription system") == "second-voice"
        assert infer_project_name("I need a REST API") == "api"
        assert infer_project_name("completely unrelated topic xyz") == "unknown"

    # Additional tests...
```

**File:** `tests/test_timestamp.py` (NEW)

```python
"""Tests for timestamp utilities."""

import pytest
from src.second_voice.utils.timestamp import (
    get_timestamp, create_recording_filename, create_whisper_filename,
    extract_timestamp_from_filename
)

class TestTimestamp:

    def test_timestamp_format(self):
        """Test timestamp format is YYYY-MM-DD_HH-MM-SS."""
        ts = get_timestamp()
        assert len(ts) == 19  # YYYY-MM-DD_HH-MM-SS
        assert ts[4] == '-'
        assert ts[7] == '-'
        assert ts[10] == '_'

    def test_recording_filename(self):
        """Test recording filename creation."""
        path = create_recording_filename("/tmp", "aac")
        assert "recording-" in path
        assert ".aac" in path
        assert "/tmp/" in path

    def test_extract_timestamp(self):
        """Test timestamp extraction from filename."""
        filename = "recording-2026-01-26_14-30-45.wav"
        ts = extract_timestamp_from_filename(filename)
        assert ts == "2026-01-26_14-30-45"
```

**Run Tests:**
```bash
pytest tests/test_aac_handler.py -v
pytest tests/test_headers.py -v
pytest tests/test_timestamp.py -v
pytest tests/ -v --cov=src
```

**Success Criteria:**
- [ ] All new tests pass
- [ ] Coverage > 80% for new modules
- [ ] No regression in existing tests

---

#### Task 5.2: Integration Tests
**File:** `tests/test_aac_integration.py` (NEW)

**Prerequisite:** This task depends on Phase 4.5 (extract test AAC fixture). Ensure `samples/test.aac` exists before running these tests.

```python
"""Integration tests for AAC support and whisper recovery."""

import pytest
import os
import tempfile
from pathlib import Path

class TestAACIntegration:

    @pytest.fixture
    def aac_test_file(self):
        """Provide path to test AAC file."""
        aac_path = Path("samples/test.aac")
        if not aac_path.exists():
            pytest.skip("samples/test.aac not found. Run Phase 4.5 to extract test fixture.")
        return str(aac_path.absolute())

    def test_process_aac_file(self, aac_test_file):
        """Test processing AAC file from start to finish.

        Uses samples/test.aac (30-second fixture extracted in Phase 4.5)
        """
        # Would test:
        # 1. File acceptance (aac_test_file)
        # 2. AAC detection
        # 3. Conversion to WAV
        # 4. Whisper transcription
        # 5. Header injection
        # 6. LLM processing
        pass

    def test_whisper_file_creation(self, aac_test_file):
        """Test whisper output file is created and matches timestamp.

        Uses samples/test.aac fixture for consistent results
        """
        # Test:
        # 1. Recording timestamp created
        # 2. Whisper file created with matching timestamp
        # 3. Files linked correctly
        pass

    def test_keep_files_flag(self, aac_test_file):
        """Test --keep-files preserves whisper output.

        Uses samples/test.aac fixture
        """
        # Test:
        # 1. --keep-files flag respected
        # 2. Both audio and text files retained
        # 3. Normal operation still cleans up
        pass

    def test_fallback_on_llm_error(self, aac_test_file):
        """Test fallback to whisper output on LLM failure.

        Uses samples/test.aac fixture with mocked LLM error
        """
        # Test:
        # 1. Simulate LLM error
        # 2. Verify fallback triggered
        # 3. Raw whisper output returned
        pass
```

**Run Integration Tests:**
```bash
# Verify test fixture exists first
ls -lh samples/test.aac

# Run tests
pytest tests/test_aac_integration.py -v
```

**Success Criteria:**
- [ ] Test fixture `samples/test.aac` exists (~500KB-2MB, 30 seconds)
- [ ] AAC files process end-to-end using test fixture
- [ ] Whisper files created and timestamped
- [ ] Keep-files flag works correctly
- [ ] Fallback mechanism functions
- [ ] Tests work in CI/CD (small file size)

---

#### Task 5.3: Documentation Updates
**File:** `README.md` (UPDATE)

**Add to "Supported Audio Formats" section:**

```markdown
**Supported Audio Formats:**
- WAV, FLAC, OGG, MP3, AIFF, AU, CAF (via soundfile)
- **AAC, M4A** (via mutagen + FFmpeg conversion)
- And 25+ additional formats supported by `soundfile`

**AAC Support Requirements:**
To process AAC files, install FFmpeg:
- Linux: `apt-get install ffmpeg`
- macOS: `brew install ffmpeg`
- Windows: `choco install ffmpeg` or download from ffmpeg.org
```

**Add new section after "Testing":**

```markdown
### Whisper Output Recovery

On failure or with the `--keep-files` flag, Second Voice preserves:
- **Recording files**: `tmp/recording-YYYY-MM-DD_HH-MM-SS.{format}`
- **Whisper transcripts**: `tmp/whisper-YYYY-MM-DD_HH-MM-SS.txt`

This allows you to:
1. Review raw transcriptions if LLM processing fails
2. Recover transcripts from crashes
3. Audit the processing pipeline

**Example recovery:**
```bash
# Keep files with --keep-files flag
python src/cli/run.py --file recording.aac --keep-files

# Later, recover the whisper output
python scripts/recover_whisper_output.py --recover
```
```

**File:** `docs/aac-support.md` (NEW)

```markdown
# AAC Audio Format Support

## Overview

Second Voice now supports `.aac` (Advanced Audio Coding) and `.m4a` audio files. This allows you to process modern audio formats without pre-conversion.

## Requirements

FFmpeg is required for AAC decoding. Install it:

```bash
# Ubuntu/Debian
sudo apt-get install ffmpeg

# macOS
brew install ffmpeg

# Windows
choco install ffmpeg
```

## Usage

Process AAC files just like any other format:

```bash
python src/cli/run.py --file recording.aac
python src/cli/run.py --file song.m4a --mode tui
```

## How It Works

1. Audio format is detected by file extension
2. If AAC, the file is converted to WAV internally
3. Whisper transcription proceeds as normal
4. No temporary files are left behind (unless `--keep-files` is used)

## Troubleshooting

### "Error: FFmpeg not found"

Install FFmpeg as described above. Verify:

```bash
ffmpeg -version
```

### "Invalid AAC file" error

The file may be corrupted. Try:

```bash
# Check file with ffmpeg
ffprobe recording.aac
```

## Libraries Used

- **mutagen** - AAC format validation and metadata
- **pydub** - Audio conversion
- **FFmpeg** - AAC decoder (system dependency)
```

**Update TESTING.md with AAC examples:**

```markdown
### Testing with AAC Files

```bash
# Generate test AAC file (requires FFmpeg)
ffmpeg -i samples/test.wav -c:a aac samples/test.aac

# Test in TUI mode
python src/cli/run.py --file samples/test.aac --mode tui

# Test with keep-files
python src/cli/run.py --file samples/test.aac --keep-files

# Verify whisper output was saved
ls -la tmp/whisper-*.txt
```
```

**Success Criteria:**
- [ ] AAC section in README
- [ ] docs/aac-support.md created with examples
- [ ] TESTING.md updated with AAC tests
- [ ] All documentation links work

---

### Phase 6: Cleanup & Verification

**Timeline:** Tasks 6.1-6.2 (depends on Phase 4.5)

#### Task 6.1: Update requirements.txt
**File:** `requirements.txt`

Ensure these are added:
```
mutagen>=1.46
pydub>=0.25
```

Install and verify:
```bash
pip install -r requirements.txt
python -c "from mutagen.mp4 import MP4; from pydub import AudioSegment; print('✓ OK')"
```

---

#### Task 6.2: Final Verification Checklist
Run through all success criteria:

```bash
# ✓ AAC Support
python src/cli/run.py --file samples/test.aac --no-edit

# ✓ Timestamped Files
ls -lt tmp/recording-*.* | head -1

# ✓ Whisper Output
ls -lt tmp/whisper-*.txt | head -1

# ✓ Headers in Output
grep "Source" /tmp/second_voice_output.txt

# ✓ Tests Pass
pytest tests/ -v --tb=short

# ✓ No Regressions
python src/cli/run.py --file samples/test.wav --mode menu

# ✓ Recovery Script Works
python scripts/recover_whisper_output.py
```

---

## 📅 Implementation Timeline

| Phase | Duration | Tasks | Priority | Notes |
|-------|----------|-------|----------|-------|
| 1: AAC Support | 2-3 hrs | 1.1-1.3 | 🔴 Critical | Foundation |
| 2: Timestamped Files | 2-3 hrs | 2.1-2.3 | 🔴 Critical | Core feature |
| 3: Whisper Recovery | 1-2 hrs | 3.1-3.2 | 🟠 High | Fallback mechanism |
| 4: Output Headers | 2-3 hrs | 4.1-4.3 | 🟠 High | Metadata tracking |
| 4.5: Test Fixture | 0.5 hrs | 4.5 | 🟡 Medium | One-time setup; throwaway script |
| 5: Testing | 2-3 hrs | 5.1-5.3 | 🟡 Medium | Depends on Phase 4.5 |
| 6: Verification | 1 hr | 6.1-6.2 | 🟡 Medium | Depends on Phase 4.5 |

**Total Estimated Time:** 11-16 hours (includes one-time test fixture extraction)

---

## 🔗 Dependencies & Blockers

```
Phase 1 (AAC) ───────┬─> Phase 2 (Timestamps) ───┬─> Phase 3 (Recovery)
                     │                            │
                     └────────────────────────────┴─> Phase 4 (Headers)
                                                      │
                                                      └─> Phase 4.5 (Test Fixture)
                                                            │
                                                            ├─> Phase 5 (Tests)
                                                            │       │
                                                            │       └─> Phase 6 (Verify)
                                                            │
                                                            └─> [CI/CD regression testing]
```

**Dependencies:**
- Phase 4.5 is a **one-time setup task** (extract test fixture from tmp/recording-2.aac)
- Phase 5 and 6 **depend on Phase 4.5** (need samples/test.aac to exist)
- No external blockers; all dependencies are internal and sequential
- Phase 4.5 can run in parallel with earlier phases but must complete before Phase 5

**Important Note on Artifacts:**
- ❌ `tmp/recording-2.aac` (source) - **DO NOT** commit to source tree
- ✅ `samples/test.aac` (30-sec extract) - **DO** commit to source tree
- 🗑️ `scripts/extract_test_aac.py` (throwaway) - Delete after execution

---

## ⚠️ Risks & Mitigation

| Risk | Severity | Mitigation |
|------|----------|-----------|
| FFmpeg not installed | High | Clear error message + docs + install script |
| AAC file corruption | Medium | Validate with mutagen before processing |
| Timestamp collision (unlikely) | Low | Use microseconds if needed |
| Orphaned temp files on crash | Medium | Cleanup script provided |
| LLM doesn't respect headers | Medium | Post-process output to inject if missing |
| Regression in WAV handling | High | Comprehensive test suite before merge |

---

## ✅ Success Criteria Summary

- [ ] **Test Fixture**: `samples/test.aac` exists (30-second extract, <5MB, from tmp/recording-2.aac)
- [ ] **AAC Files**: `--file samples/test.aac` and `--file tmp/recording.aac` work without error
- [ ] **Timestamps**: All temp files follow `recording-YYYY-MM-DD_HH-MM-SS` pattern
- [ ] **Whisper Files**: `tmp/whisper-*.txt` created and preserved with `--keep-files`
- [ ] **Fallback**: On LLM error, raw whisper output returned with warning
- [ ] **Headers**: Input and output contain valid metadata headers
- [ ] **Tests**: All tests pass, >80% coverage on new code (using samples/test.aac)
- [ ] **Docs**: README, TESTING.md, and new guides updated with examples
- [ ] **No Regressions**: Existing functionality unchanged and tested
- [ ] **Recovery**: `scripts/recover_whisper_output.py` works correctly
- [ ] **FFmpeg Guidance**: Clear error messages if FFmpeg not installed
- [ ] **Source Tree**: Only samples/test.aac committed; tmp/recording-2.aac excluded; extract script deleted

---

## 📝 Deliverables

- [x] Spec document: `dev_notes/specs/2026-01-26_23-00-24_aac-support-and-whisper-recovery.md`
- [x] Project plan: `dev_notes/project_plans/2026-01-26_23-00-24_aac-support-and-whisper-recovery.md`
- [ ] Test fixture:
  - [ ] `scripts/extract_test_aac.py` (Phase 4.5 - create then delete)
  - [ ] `samples/test.aac` (Phase 4.5 result - commit to source tree)
- [ ] New modules:
  - [ ] `src/second_voice/audio/aac_handler.py`
  - [ ] `src/second_voice/utils/timestamp.py`
  - [ ] `src/second_voice/utils/headers.py`
  - [ ] `scripts/recover_whisper_output.py`
- [ ] Updated modules:
  - [ ] `src/second_voice/core/recorder.py`
  - [ ] `src/second_voice/core/processor.py`
  - [ ] `src/second_voice/prompts/system_prompt.md`
  - [ ] `requirements.txt`
- [ ] New tests:
  - [ ] `tests/test_aac_handler.py`
  - [ ] `tests/test_headers.py`
  - [ ] `tests/test_timestamp.py`
  - [ ] `tests/test_aac_integration.py`
- [ ] Documentation:
  - [ ] Updated: `README.md`
  - [ ] New: `docs/aac-support.md`
  - [ ] Updated: `TESTING.md`

---

## 🚀 Next Steps

1. **Review & Approve** this plan
2. **Create branch** for feature: `feature/aac-support-whisper-recovery`
3. **Execute Phase 4.5** (Extract test fixture):
   - Run `scripts/extract_test_aac.py` to create `samples/test.aac`
   - Verify file is ~30 seconds and <5MB
   - Delete the extraction script
4. **Implement Phase 1** (AAC Support Foundation)
5. **Implement Phase 2** (Timestamped Files)
6. **Implement Phase 3-4** (Recovery & Headers)
7. **Run Phases 5-6** (Testing & Verification using samples/test.aac)
8. **Create PR** with all changes:
   - Include `samples/test.aac` in commit
   - Exclude `tmp/recording-2.aac` (add to .gitignore if needed)
   - Ensure extract script is not committed
