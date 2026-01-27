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
