#!/usr/bin/env python3
"""
Document Integrity Scanner

Automated verification of documentation correctness and consistency.
See docs/system-prompts/processes/document-integrity-scan.md for detailed process.

Checks:
1. Referential Correctness - All links point to existing files
2. Architectural Constraints - system-prompts doesn't reference back to project files
3. Naming Conventions - Files follow established patterns
4. Directory Structure - Tool guides in correct locations
5. Coverage - All documentation relationships captured

Usage:
    python3 docscan.py                              # Run full scan
    python3 docscan.py --check broken-links         # Only broken links
    python3 docscan.py --check back-references      # Only back-references
    python3 docscan.py --verbose                    # Verbose output
    python3 docscan.py --strict                     # Fail on warnings
"""

import argparse
import re
import sys
from pathlib import Path
from collections import defaultdict
from typing import List, Dict, Tuple

# Configuration
CONDITIONAL_MARKERS = {
    "(if present)",
    "(if exists)",
    "(optional)",
    "if this file exists",
    "if you have",
    "if your project",
}

# Safe targets from system-prompts (entry points that always exist in AGENTS.md projects)
ENTRY_POINTS = {
    "AGENTS.md",
    "CLAUDE.md",
    "GEMINI.md",
    "AIDER.md",
    "AGENTS.md",
}


class DocumentScanner:
    """Scan documentation for integrity issues."""

    def __init__(self, project_root: Path, options: argparse.Namespace):
        self.project_root = project_root
        self.options = options
        self.violations = []

    def run(self) -> int:
        """Execute scan and return exit code."""
        print("=" * 80)
        print("DOCUMENT INTEGRITY SCAN")
        print("=" * 80)

        if not self.options.check or "broken-links" in self.options.check:
            self._check_broken_links()

        if not self.options.check or "back-references" in self.options.check:
            self._check_back_references()

        if not self.options.check or "tool-organization" in self.options.check:
            self._check_tool_organization()

        if not self.options.check or "naming" in self.options.check:
            self._check_naming_conventions()

        if not self.options.check or "coverage" in self.options.check:
            self._check_reference_coverage()

        # Print results
        self._print_results()

        # Determine exit code
        if self.violations:
            error_count = sum(1 for v in self.violations if v["severity"] == "error")
            warning_count = sum(1 for v in self.violations if v["severity"] == "warning")

            if self.options.strict and warning_count > 0:
                return 1
            if error_count > 0:
                return 1

        print("\n" + "=" * 80)
        print("SCAN COMPLETE")
        print("=" * 80)
        return 0

    def _check_broken_links(self):
        """Check Layer 1: Ensure all links point to existing files."""
        print("\n### Checking for Broken Links...")

        link_pattern = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")
        all_md_files = list(self.project_root.rglob("*.md"))

        for md_file in all_md_files:
            if ".git" in str(md_file):
                continue

            relative_path = str(md_file.relative_to(self.project_root))
            with open(md_file, "r", encoding="utf-8") as f:
                content = f.read()

            # Remove code blocks before scanning (backtick-delimited)
            content_without_code = re.sub(r"```[\s\S]*?```", "", content)
            content_without_code = re.sub(r"`[^`]+`", "", content_without_code)

            for match in link_pattern.finditer(content_without_code):
                link_text = match.group(1)
                link_target = match.group(2)

                # Skip external URLs and anchors
                if link_target.startswith(("http://", "https://", "#", "mailto:")):
                    continue

                # Skip placeholder-like targets (single word, not a path)
                if "/" not in link_target and not link_target.endswith(".md"):
                    continue

                # Resolve relative paths
                if link_target.startswith("/"):
                    target_file = self.project_root / link_target.lstrip("/")
                else:
                    target_file = (md_file.parent / link_target).resolve()

                # Check if target exists
                if not target_file.exists():
                    self.violations.append(
                        {
                            "file": relative_path,
                            "type": "broken-link",
                            "severity": "error",
                            "message": f"Broken link: {link_target}",
                            "target": str(target_file.relative_to(self.project_root)),
                        }
                    )
                    if self.options.verbose:
                        print(f"  ❌ {relative_path}: {link_target}")

    def _check_back_references(self):
        """Check Layer 2: System-prompts shouldn't reference outside without marking."""
        print("\n### Checking for Problematic Back-References...")

        system_prompts_dir = self.project_root / "docs" / "system-prompts"
        if not system_prompts_dir.exists():
            return

        link_pattern = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")

        for md_file in system_prompts_dir.rglob("*.md"):
            relative_path = str(md_file.relative_to(self.project_root))
            with open(md_file, "r", encoding="utf-8") as f:
                content = f.read()

            for match in link_pattern.finditer(content):
                link_text = match.group(1)
                link_target = match.group(2)

                # Skip safe references
                if link_target.startswith(("http://", "https://", "#")):
                    continue
                if any(entry in link_target for entry in ENTRY_POINTS):
                    continue
                if "system-prompts" in link_target:
                    continue
                if not link_target.endswith(".md"):
                    continue

                # Skip relative references within same directory (e.g., ./filename.md)
                if link_target.startswith("./"):
                    continue

                # Check if it's a back-reference (outside system-prompts)
                if "system-prompts" not in link_target:
                    # Check if marked as conditional
                    is_conditional = any(
                        marker.lower() in content[max(0, match.start() - 200) : match.end() + 200].lower()
                        for marker in CONDITIONAL_MARKERS
                    )

                    if not is_conditional:
                        self.violations.append(
                            {
                                "file": relative_path,
                                "type": "back-reference",
                                "severity": "warning",
                                "message": f"Back-reference to project file without conditional marking: {link_target}",
                            }
                        )
                        if self.options.verbose:
                            print(f"  ⚠️  {relative_path}: {link_target} (not marked conditional)")

    def _check_tool_organization(self):
        """Check Layer 3: Tool guides in correct locations."""
        print("\n### Checking Tool Guide Organization...")

        # Check generic vs project-specific
        tools_dir = self.project_root / "docs" / "system-prompts" / "tools"
        tool_specific_dir = self.project_root / "docs" / "tool-specific-guides"

        if tools_dir.exists():
            for guide_file in tools_dir.glob("*.md"):
                if guide_file.name == "README.md":
                    continue

                with open(guide_file, "r", encoding="utf-8") as f:
                    content = f.read()

                # Generic guides shouldn't heavily reference project implementation
                # (some mentions in examples are OK, but shouldn't be main focus)
                src_second_voice_refs = len(re.findall(r"src/second_voice", content))
                processor_refs = len(re.findall(r"processor\.py", content))

                if src_second_voice_refs > 2 or processor_refs > 2:
                    self.violations.append(
                        {
                            "file": str(guide_file.relative_to(self.project_root)),
                            "type": "tool-organization",
                            "severity": "warning",
                            "message": "Generic tool guide contains many project-specific references",
                        }
                    )

        if tool_specific_dir.exists():
            for guide_file in tool_specific_dir.glob("*.md"):
                with open(guide_file, "r", encoding="utf-8") as f:
                    content = f.read()

                # Check if it's actually generic (shouldn't be here)
                # Generic guides explain tool + AGENTS.md but don't explain project integration
                has_project_specifics = any(
                    term in content for term in ["src/second_voice", "processor", "settings.json"]
                )

                if not has_project_specifics and guide_file.name != "README.md":
                    self.violations.append(
                        {
                            "file": str(guide_file.relative_to(self.project_root)),
                            "type": "tool-organization",
                            "severity": "warning",
                            "message": "Project-specific guide appears to be generic (should be in system-prompts/tools/)",
                        }
                    )

    def _check_naming_conventions(self):
        """Check Layer 4: Files follow naming conventions."""
        print("\n### Checking Naming Conventions...")

        docs_dir = self.project_root / "docs"
        if not docs_dir.exists():
            return

        kebab_pattern = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*\.md$")

        for md_file in docs_dir.rglob("*.md"):
            if ".git" in str(md_file):
                continue

            filename = md_file.name
            relative_path = str(md_file.relative_to(self.project_root))

            # Skip system-prompts/tools/ (already documented separately)
            if "system-prompts/tools" in relative_path:
                continue

            # Skip dev_notes/ (uses timestamp format)
            if "dev_notes" in relative_path:
                continue

            # Check lowercase-kebab convention
            if not kebab_pattern.match(filename):
                # Allow some exceptions
                if filename not in ["README.md"]:
                    self.violations.append(
                        {
                            "file": relative_path,
                            "type": "naming",
                            "severity": "warning",
                            "message": f"File doesn't follow lowercase-kebab.md convention: {filename}",
                        }
                    )

    def _check_reference_coverage(self):
        """Check Layer 5: All tool guides are referenced appropriately."""
        print("\n### Checking Reference Coverage...")

        # Find all generic tool guides (project-specific ones don't need to be in README)
        tools_dir = self.project_root / "docs" / "system-prompts" / "tools"

        guides_found = {}

        if tools_dir.exists():
            for guide_file in sorted(tools_dir.glob("*.md")):
                if guide_file.name == "README.md":
                    continue
                guides_found[guide_file.name] = str(guide_file.relative_to(self.project_root))

        # Check if guides are referenced from README.md
        readme_file = self.project_root / "README.md"
        if readme_file.exists():
            with open(readme_file, "r", encoding="utf-8") as f:
                readme_content = f.read()

            for guide_name, guide_path in guides_found.items():
                base_name = guide_name.replace(".md", "")
                if base_name not in readme_content:
                    self.violations.append(
                        {
                            "file": "README.md",
                            "type": "coverage",
                            "severity": "warning",
                            "message": f"Generic tool guide '{guide_name}' not referenced in README.md",
                        }
                    )

    def _print_results(self):
        """Print scan results."""
        if not self.violations:
            print("\n✅ All checks passed!")
            return

        print("\n### VIOLATIONS FOUND\n")

        # Group by severity
        errors = [v for v in self.violations if v["severity"] == "error"]
        warnings = [v for v in self.violations if v["severity"] == "warning"]

        if errors:
            print(f"❌ Errors ({len(errors)}):")
            for violation in errors:
                print(f"  {violation['file']}")
                print(f"    → {violation['message']}")
                if "target" in violation:
                    print(f"       Target: {violation['target']}")
                print()

        if warnings:
            print(f"⚠️  Warnings ({len(warnings)}):")
            for violation in warnings:
                print(f"  {violation['file']}")
                print(f"    → {violation['message']}")
                print()


def main():
    parser = argparse.ArgumentParser(
        description="Document Integrity Scanner",
        epilog="See docs/system-prompts/processes/document-integrity-scan.md for details.",
    )

    parser.add_argument(
        "--check",
        action="append",
        choices=["broken-links", "back-references", "tool-organization", "naming", "coverage"],
        help="Run specific checks (default: run all)",
    )

    parser.add_argument(
        "--verbose", "-v", action="store_true", help="Verbose output showing all checks"
    )

    parser.add_argument(
        "--strict",
        action="store_true",
        help="Fail on warnings (not just errors)",
    )

    parser.add_argument(
        "--project-root",
        type=Path,
        default=Path.cwd(),
        help="Project root directory (default: current directory)",
    )

    args = parser.parse_args()

    # Find project root if running from subdirectory
    if not (args.project_root / "AGENTS.md").exists():
        # Try parent directories
        for parent in args.project_root.parents:
            if (parent / "AGENTS.md").exists():
                args.project_root = parent
                break

    scanner = DocumentScanner(args.project_root, args)
    exit_code = scanner.run()
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
