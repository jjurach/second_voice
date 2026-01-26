#!/usr/bin/env python3
"""
Agent Kernel Bootstrap Tool

Manages injection and maintenance of system-prompts content into AGENTS.md.
Detects project language, compares sections, and applies safe updates.
"""

import sys
import os
import argparse
import re
from pathlib import Path


class Bootstrap:
    """Manages system prompts integration into AGENTS.md."""

    def __init__(self, project_root: str = None, dry_run: bool = True):
        """
        Initialize bootstrap tool.

        Args:
            project_root: Path to project root (auto-detected if None)
            dry_run: If True, don't write files (default: True for safety)
        """
        self.project_root = project_root or self._detect_project_root()
        self.dry_run = dry_run
        self.agents_file = os.path.join(self.project_root, "AGENTS.md")
        self.system_prompts_dir = os.path.join(
            self.project_root, "docs", "system-prompts"
        )

    def _detect_project_root(self) -> str:
        """
        Detect project root directory.

        Checks for README.md, .git, or language markers (pyproject.toml, package.json).
        """
        current = Path.cwd()
        while current != current.parent:
            if any(
                (current / marker).exists()
                for marker in ["README.md", ".git", "pyproject.toml", "package.json"]
            ):
                return str(current)
            current = current.parent

        return str(Path.cwd())

    def _detect_language(self) -> str:
        """Detect project primary language."""
        root = Path(self.project_root)
        if (root / "pyproject.toml").exists() or (root / "requirements.txt").exists():
            return "python"
        if (root / "package.json").exists():
            return "javascript"
        return "unknown"

    def _read_file(self, path: str) -> str:
        """Read file content safely."""
        try:
            with open(path, "r", encoding="utf-8") as f:
                return f.read()
        except FileNotFoundError:
            return ""

    def _write_file(self, path: str, content: str) -> None:
        """Write file content (respects dry_run mode)."""
        if self.dry_run:
            print(f"[DRY RUN] Would write: {path}")
            return

        # Ensure directory exists
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"✓ Wrote: {path}")

    def _extract_section(self, content: str, section_name: str) -> str:
        """Extract section content from markdown."""
        pattern = f"<!-- SECTION: {section_name} -->(.*?)<!-- END-SECTION -->"
        match = re.search(pattern, content, re.DOTALL)
        if match:
            return match.group(1).strip()
        return ""

    def _update_section(
        self, content: str, section_name: str, new_content: str, force: bool = False
    ) -> tuple[str, bool]:
        """
        Update or insert section in content.

        Returns:
            (updated_content, was_modified)
        """
        pattern = f"<!-- SECTION: {section_name} -->(.*?)<!-- END-SECTION -->"
        match = re.search(pattern, content, re.DOTALL)

        new_content_stripped = new_content.strip()

        if not match:
            # Append section
            content += (
                f"\n\n<!-- SECTION: {section_name} -->\n{new_content_stripped}\n<!-- END-SECTION -->"
            )
            return content, True

        current_content = match.group(1).strip()

        if current_content == new_content_stripped:
            # No change needed
            return content, False

        # Content differs
        if not force:
            print(
                f"⚠️  WARNING: Section '{section_name}' is locally modified."
            )
            print(f"   Use --force to overwrite.")
            return content, False

        # Replace section
        new_section = f"<!-- SECTION: {section_name} -->\n{new_content_stripped}\n<!-- END-SECTION -->"
        updated = re.sub(pattern, new_section, content, flags=re.DOTALL)
        return updated, True

    def load_system_prompt(self, section_name: str, language: str = None) -> str:
        """Load ideal state from system-prompts directory."""
        if language is None:
            language = self._detect_language()

        # Map section names to file paths
        section_map = {
            "CORE-WORKFLOW": "workflow/core.md",
            "PRINCIPLES": "principles/definition-of-done.md",
            "PYTHON-DOD": f"languages/python/definition-of-done.md",
            "PROMPT-PATTERNS": "patterns/prompt-patterns.md",
        }

        if section_name not in section_map:
            print(f"ERROR: Unknown section: {section_name}")
            return ""

        file_path = os.path.join(self.system_prompts_dir, section_map[section_name])
        content = self._read_file(file_path)
        if not content:
            print(f"WARNING: Could not read: {file_path}")
        return content

    def sync_agents_file(self, force: bool = False) -> bool:
        """
        Synchronize AGENTS.md with system-prompts.

        Returns:
            True if changes were made
        """
        # Read current AGENTS.md
        agents_content = self._read_file(self.agents_file)
        if not agents_content:
            print(
                f"ERROR: Could not read {self.agents_file}"
            )
            return False

        language = self._detect_language()
        changed = False

        # Sections to sync
        sections = [
            ("CORE-WORKFLOW", "workflow/core.md"),
            ("PRINCIPLES", "principles/definition-of-done.md"),
        ]

        # Add language-specific sections
        if language == "python":
            sections.append(("PYTHON-DOD", "languages/python/definition-of-done.md"))

        # Sync each section
        for section_name, _ in sections:
            ideal_content = self.load_system_prompt(section_name, language)
            if not ideal_content:
                print(f"SKIP: Could not load {section_name}")
                continue

            updated_agents, section_changed = self._update_section(
                agents_content, section_name, ideal_content, force=force
            )
            if section_changed:
                agents_content = updated_agents
                changed = True
                print(f"✓ Updated section: {section_name}")

        # Write result
        if changed:
            self._write_file(self.agents_file, agents_content)
            if self.dry_run:
                print("\n[DRY RUN] Changes would be applied. Use --commit to save.")
            else:
                print(f"\n✓ Successfully synced {self.agents_file}")
        else:
            print("No changes needed.")

        return changed

    def show_diff(self) -> None:
        """Show what would change (dry run mode)."""
        # This is a simplified version - a full diff would be more complex
        agents_content = self._read_file(self.agents_file)
        language = self._detect_language()

        print(f"Project language: {language}")
        print(f"Project root: {self.project_root}")
        print(f"AGENTS.md path: {self.agents_file}")
        print(f"System prompts dir: {self.system_prompts_dir}")

        sections = [
            ("CORE-WORKFLOW", "workflow/core.md"),
            ("PRINCIPLES", "principles/definition-of-done.md"),
        ]

        if language == "python":
            sections.append(("PYTHON-DOD", "languages/python/definition-of-done.md"))

        print(f"\nSections to sync ({len(sections)}):")
        for section_name, file_path in sections:
            exists = (
                Path(self.system_prompts_dir) / file_path
            ).exists()
            current = self._extract_section(agents_content, section_name)
            status = "✓ Found" if current else "✗ Missing"
            file_status = "✓ Exists" if exists else "✗ Missing"
            print(f"  - {section_name}: {status} in AGENTS.md, {file_status} in system-prompts")


def main():
    """Command-line entry point."""
    parser = argparse.ArgumentParser(
        description="Agent Kernel Bootstrap Tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Dry run (default) - shows what would happen
  python3 bootstrap.py

  # Commit changes to AGENTS.md
  python3 bootstrap.py --commit

  # Overwrite locally modified sections
  python3 bootstrap.py --commit --force

  # Show analysis without changes
  python3 bootstrap.py --analyze
        """,
    )

    parser.add_argument(
        "--commit",
        action="store_true",
        help="Actually write changes (default is dry-run)",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Overwrite locally modified sections",
    )
    parser.add_argument(
        "--analyze",
        action="store_true",
        help="Show analysis without making changes",
    )
    parser.add_argument(
        "--root",
        help="Project root directory (auto-detected if not specified)",
    )

    args = parser.parse_args()

    # Create bootstrap instance
    dry_run = not args.commit
    bootstrap = Bootstrap(project_root=args.root, dry_run=dry_run)

    # Verify system-prompts directory exists
    if not os.path.exists(bootstrap.system_prompts_dir):
        print(f"ERROR: System prompts directory not found: {bootstrap.system_prompts_dir}")
        sys.exit(1)

    # Show analysis or sync
    if args.analyze:
        bootstrap.show_diff()
    else:
        success = bootstrap.sync_agents_file(force=args.force)
        sys.exit(0 if success or not args.commit else 1)


if __name__ == "__main__":
    main()
