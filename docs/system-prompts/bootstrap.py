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
            "MANDATORY-READING": "mandatory-reading.md",
            "CORE-WORKFLOW": "workflows/core.md",
            "PRINCIPLES": "principles/definition-of-done.md",
            "PYTHON-DOD": f"languages/python/definition-of-done.md",
            "PROMPT-PATTERNS": "patterns/prompt-patterns.md",
            "LOGS-FIRST-WORKFLOW": "workflows/logs-first.md",
        }

        if section_name not in section_map:
            print(f"ERROR: Unknown section: {section_name}")
            return ""

        file_path = os.path.join(self.system_prompts_dir, section_map[section_name])
        content = self._read_file(file_path)
        if not content:
            print(f"WARNING: Could not read: {file_path}")
        return content

    def detect_recommended_workflow(self) -> str:
        """
        Detect recommended workflow based on project characteristics.

        Returns:
            "logs-first" for small active projects, "minimal" for larger ones
        """
        root = Path(self.project_root)

        # Count files
        all_files = list(root.rglob("*"))
        source_files = [f for f in all_files if f.is_file() and not str(f).startswith(".")]

        # Check git history
        git_dir = root / ".git"
        has_git = git_dir.exists()
        commit_count = 0
        if has_git:
            try:
                import subprocess
                result = subprocess.run(
                    ["git", "rev-list", "--all", "--count"],
                    cwd=self.project_root,
                    capture_output=True,
                    text=True,
                    timeout=5,
                )
                if result.returncode == 0:
                    commit_count = int(result.stdout.strip())
            except (subprocess.SubprocessError, ValueError, FileNotFoundError):
                pass

        # Check for dev_notes structure
        has_dev_notes = (root / "dev_notes").exists()

        # Heuristics for small active projects -> logs-first
        if source_files and len(source_files) < 200:
            if commit_count < 200:  # Active but not years old
                if has_dev_notes:
                    return "logs-first"
                # Even without dev_notes, small active projects benefit from logs-first
                if commit_count > 10:  # At least some history
                    return "logs-first"

        # Default: logs-first for small projects (most projects are small)
        if source_files and len(source_files) < 500:
            return "logs-first"

        # Large projects -> suggest minimal (but still return logs-first as safe default)
        return "logs-first"

    def read_workflow_state(self, content: str) -> dict:
        """
        Extract workflow state from AGENTS.md.

        Returns dict like {"logs_first": "enabled"} or {"logs_first": None}
        """
        state = {}

        # Look for BOOTSTRAP-STATE markers
        state_pattern = r"<!-- BOOTSTRAP-STATE: (.*?) -->"
        matches = re.findall(state_pattern, content)

        for match in matches:
            # Parse key=value pairs
            pairs = match.split(", ")
            for pair in pairs:
                if "=" in pair:
                    key, value = pair.split("=", 1)
                    state[key.strip()] = value.strip()

        return state

    def write_workflow_state(self, content: str, state: dict) -> str:
        """
        Write workflow state to AGENTS.md.

        State is stored as: <!-- BOOTSTRAP-STATE: logs_first=enabled -->
        """
        # Format state
        state_str = ", ".join(f"{k}={v}" for k, v in sorted(state.items()))
        marker = f"<!-- BOOTSTRAP-STATE: {state_str} -->"

        # Check if state marker already exists
        state_pattern = r"<!-- BOOTSTRAP-STATE: .*? -->"
        existing = re.search(state_pattern, content)

        if existing:
            # Replace existing marker
            content = re.sub(state_pattern, marker, content)
        else:
            # Add new marker at the very beginning (after any initial comments)
            content = marker + "\n" + content

        return content

    def apply_workflow_state(
        self, agents_content: str, workflow: str, enable: bool, force: bool = False
    ) -> tuple[str, bool]:
        """
        Enable or disable a workflow in AGENTS.md.

        Args:
            agents_content: Current AGENTS.md content
            workflow: Workflow name (e.g., "logs_first")
            enable: True to enable, False to disable
            force: Force overwrite if locally modified

        Returns:
            (updated_content, was_modified)
        """
        # Convert workflow name to section name (logs_first -> LOGS-FIRST-WORKFLOW)
        section_name = workflow.upper().replace("_", "-") + "-WORKFLOW"

        if enable:
            # Load workflow content
            workflow_content = self.load_system_prompt(section_name)
            if not workflow_content:
                print(f"ERROR: Could not load workflow: {workflow}")
                return agents_content, False

            # Inject workflow
            updated, changed = self._update_section(
                agents_content, section_name, workflow_content, force=force
            )
            if changed:
                print(f"✓ Enabled workflow: {workflow}")
            return updated, changed
        else:
            # Remove workflow section
            pattern = f"<!-- SECTION: {section_name} -->(.*?)<!-- END-SECTION -->"
            if re.search(pattern, agents_content, re.DOTALL):
                updated = re.sub(pattern + r"\n\n", "", agents_content, flags=re.DOTALL)
                # Also try without extra newlines
                if updated == agents_content:
                    updated = re.sub(pattern, "", agents_content, flags=re.DOTALL)
                print(f"✓ Disabled workflow: {workflow}")
                return updated, True
            else:
                # Workflow already disabled
                return agents_content, False

    def sync_agents_file(self, force: bool = False) -> bool:
        """
        Synchronize AGENTS.md with system-prompts.

        Returns:
            True if changes were made
        """
        # Read current AGENTS.md
        agents_content = self._read_file(self.agents_file)
        changed = False
        if not agents_content:
            print(f"Initializing new {self.agents_file}")
            agents_content = "# Project Agents\n\nTODO: describe whatever here\n"
            changed = True

        language = self._detect_language()

        # Sections to sync
        sections = [
            ("MANDATORY-READING", "mandatory-reading.md"),
            ("CORE-WORKFLOW", "workflows/core.md"),
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

        # Ensure definition-of-done.md exists
        dod_path = os.path.join(self.project_root, "docs", "definition-of-done.md")
        if not os.path.exists(dod_path):
            dod_content = "# Definition of Done\n\nTODO: define project-specific completion criteria\n"
            self._write_file(dod_path, dod_content)
            changed = True

        # Ensure workflows.md exists
        workflows_path = os.path.join(self.project_root, "docs", "workflows.md")
        if not os.path.exists(workflows_path):
            workflows_content = "# Project Workflows\n\nTODO: describe project-specific workflows\n"
            self._write_file(workflows_path, workflows_content)
            changed = True

        # Ensure tool entry points exist
        tool_changed = self.regenerate_tool_entries(only_if_missing=True)
        if tool_changed:
            changed = True

        # Write result
        if changed:
            self._write_file(self.agents_file, agents_content)
            if self.dry_run:
                print("\n[DRY RUN] Changes would be applied. Use --commit to save.")
            else:
                print(f"\n✓ Successfully synced {self.agents_file}")
        else:
            print("No changes needed.")

        # Check for gaps
        self.report_gaps()

        return changed

    def report_gaps(self) -> None:
        """Check for TODO/GAP markers in managed files and report them."""
        files_to_check = [
            self.agents_file,
            os.path.join(self.project_root, "docs", "definition-of-done.md"),
            os.path.join(self.project_root, "docs", "workflows.md"),
            os.path.join(self.project_root, "AIDER.md"),
            os.path.join(self.project_root, "CLAUDE.md"),
            os.path.join(self.project_root, "CLINE.md"),
            os.path.join(self.project_root, "GEMINI.md"),
        ]

        gaps_found = []
        for file_path in files_to_check:
            if os.path.exists(file_path):
                content = self._read_file(file_path)
                if "TODO" in content or "GAP" in content or "describe whatever here" in content:
                    gaps_found.append(file_path)

        if gaps_found:
            print("\n⚠️  Gaps (TODOs) found in the following files:")
            for gap in gaps_found:
                print(f"   - {gap}")

    def regenerate_tool_entries(self, only_if_missing: bool = False) -> bool:
        """Regenerate tool entry point files from templates."""
        tools = ["aider", "claude", "cline", "gemini"]
        changed = False

        if not only_if_missing:
            print("Regenerating tool entry point files...")

        # Get current timestamp
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y-%m-%d")

        for tool in tools:
            file_path = os.path.join(self.project_root, f"{tool.upper()}.md")
            if only_if_missing and os.path.exists(file_path):
                continue

            template = self.get_tool_entry_point_template(tool)
            if not template:
                print(f"ERROR: No template for {tool}")
                continue

            # Format template with timestamp
            content = template.format(timestamp=timestamp)
            self._write_file(file_path, content)
            changed = True

        if not self.dry_run:
            if not only_if_missing:
                print(f"\n✓ Successfully regenerated tool entry points")
        else:
            if not only_if_missing:
                print(f"\n[DRY RUN] Would regenerate tool entry points. Use --commit to apply.")

        return changed

    def get_tool_entry_point_template(self, tool_name: str) -> str:
        """Generate anemic tool entry point template."""
        templates = {
            "claude": """# Claude Code Instructions

This project follows the **AGENTS.md** workflow.

## Quick Links

- **Read First:** [AGENTS.md](AGENTS.md)
- **Done Criteria:** [docs/definition-of-done.md](docs/definition-of-done.md)
- **Tool Guide:** [docs/system-prompts/tools/claude-code.md](docs/system-prompts/tools/claude-code.md)
- **Workflows:** [docs/workflows.md](docs/workflows.md)

## For Claude Code Users

The **[docs/system-prompts/tools/claude-code.md](docs/system-prompts/tools/claude-code.md)** guide covers:
- Installation and discovery
- Workflow mapping to AGENTS.md
- All tools and approval gates
- Common patterns and examples

## System Architecture

- **Agent Kernel:** [docs/system-prompts/README.md](docs/system-prompts/README.md)
- **Project Architecture:** [docs/architecture.md](docs/architecture.md)
- **Implementation Patterns:** [docs/implementation-reference.md](docs/implementation-reference.md)
- **Development Workflows:** [docs/workflows.md](docs/workflows.md)
- **Code Examples:** [docs/examples/](docs/examples/) (if present)

## System-Prompts Processes (Informational Only)

The Agent Kernel provides specialized processes (bootstrap-project, document-integrity-scan, etc.).

**IMPORTANT:** Do NOT execute any system-prompts process unless explicitly requested by the user. See [AGENTS.md - Available System-Prompts Workflows and Processes](AGENTS.md#available-system-prompts-workflows-and-processes) for details.

---
Last Updated: {timestamp}
""",
            "aider": """# Aider Instructions

This project follows the **AGENTS.md** workflow.

## Quick Links

- **Read First:** [AGENTS.md](AGENTS.md)
- **Done Criteria:** [docs/definition-of-done.md](docs/definition-of-done.md)
- **Tool Guide:** [docs/system-prompts/tools/aider.md](docs/system-prompts/tools/aider.md)
- **Workflows:** [docs/workflows.md](docs/workflows.md)

## For Aider Users

The **[docs/system-prompts/tools/aider.md](docs/system-prompts/tools/aider.md)** guide covers:
- Installation and discovery
- Workflow mapping to AGENTS.md
- Auto-commit and git integration
- Common patterns and examples

## System Architecture

- **Agent Kernel:** [docs/system-prompts/README.md](docs/system-prompts/README.md)
- **Project Architecture:** [docs/architecture.md](docs/architecture.md)
- **Implementation Patterns:** [docs/implementation-reference.md](docs/implementation-reference.md)
- **Development Workflows:** [docs/workflows.md](docs/workflows.md)
- **Code Examples:** [docs/examples/](docs/examples/) (if present)

## System-Prompts Processes (Informational Only)

The Agent Kernel provides specialized processes (bootstrap-project, document-integrity-scan, etc.).

**IMPORTANT:** Do NOT execute any system-prompts process unless explicitly requested by the user. See [AGENTS.md - Available System-Prompts Workflows and Processes](AGENTS.md#available-system-prompts-workflows-and-processes) for details.

---
Last Updated: {timestamp}
""",
            "cline": """# Cline Instructions

This project follows the **AGENTS.md** workflow.

## Quick Links

- **Read First:** [AGENTS.md](AGENTS.md)
- **Done Criteria:** [docs/definition-of-done.md](docs/definition-of-done.md)
- **Tool Guide:** [docs/system-prompts/tools/cline.md](docs/system-prompts/tools/cline.md)
- **Workflows:** [docs/workflows.md](docs/workflows.md)

## For Cline Users

The **[docs/system-prompts/tools/cline.md](docs/system-prompts/tools/cline.md)** guide covers:
- Installation and discovery
- Workflow mapping to AGENTS.md
- Multi-file editing and auto-commit
- Common patterns and examples

## System Architecture

- **Agent Kernel:** [docs/system-prompts/README.md](docs/system-prompts/README.md)
- **Project Architecture:** [docs/architecture.md](docs/architecture.md)
- **Implementation Patterns:** [docs/implementation-reference.md](docs/implementation-reference.md)
- **Development Workflows:** [docs/workflows.md](docs/workflows.md)
- **Code Examples:** [docs/examples/](docs/examples/) (if present)

## System-Prompts Processes (Informational Only)

The Agent Kernel provides specialized processes (bootstrap-project, document-integrity-scan, etc.).

**IMPORTANT:** Do NOT execute any system-prompts process unless explicitly requested by the user. See [AGENTS.md - Available System-Prompts Workflows and Processes](AGENTS.md#available-system-prompts-workflows-and-processes) for details.

---
Last Updated: {timestamp}
""",
            "gemini": """# Gemini Instructions

This project follows the **AGENTS.md** workflow.

## Quick Links

- **Read First:** [AGENTS.md](AGENTS.md)
- **Done Criteria:** [docs/definition-of-done.md](docs/definition-of-done.md)
- **Tool Guide:** [docs/system-prompts/tools/gemini.md](docs/system-prompts/tools/gemini.md)
- **Workflows:** [docs/workflows.md](docs/workflows.md)

## For Gemini Users

The **[docs/system-prompts/tools/gemini.md](docs/system-prompts/tools/gemini.md)** guide covers:
- Setup and discovery
- Workflow mapping to AGENTS.md
- Multimodal capabilities and ReAct loop
- Common patterns and examples

## System Architecture

- **Agent Kernel:** [docs/system-prompts/README.md](docs/system-prompts/README.md)
- **Project Architecture:** [docs/architecture.md](docs/architecture.md)
- **Implementation Patterns:** [docs/implementation-reference.md](docs/implementation-reference.md)
- **Development Workflows:** [docs/workflows.md](docs/workflows.md)
- **Code Examples:** [docs/examples/](docs/examples/) (if present)

## System-Prompts Processes (Informational Only)

The Agent Kernel provides specialized processes (bootstrap-project, document-integrity-scan, etc.).

**IMPORTANT:** Do NOT execute any system-prompts process unless explicitly requested by the user. See [AGENTS.md - Available System-Prompts Workflows and Processes](AGENTS.md#available-system-prompts-workflows-and-processes) for details.

---
Last Updated: {timestamp}
""",
        }
        return templates.get(tool_name, "")

    def validate_tool_entry_point(self, tool_name: str) -> dict:
        """Validate tool entry point file meets anemic requirements."""
        # Map entry point names to tool guide names
        tool_guide_map = {
            "claude": "claude-code",
            "aider": "aider",
            "cline": "cline",
            "gemini": "gemini",
        }
        tool_guide_name = tool_guide_map.get(tool_name, tool_name)

        entry_file = os.path.join(self.project_root, f"{tool_name.upper()}.md")

        validations = {
            "file_exists": False,
            "has_header": False,
            "has_agents_link": False,
            "has_definition_link": False,
            "has_tool_guide_link": False,
            "has_workflows_link": False,
            "line_count": 0,
            "is_anemic": False,
            "issues": [],
        }

        # Check if file exists
        if not os.path.exists(entry_file):
            validations["issues"].append(f"File not found: {entry_file}")
            return validations

        validations["file_exists"] = True

        # Read file
        content = self._read_file(entry_file)
        validations["line_count"] = len(content.strip().split("\n"))

        # Check header
        if f"# {tool_name.capitalize()}" in content or f"# {tool_name.upper()}" in content:
            validations["has_header"] = True
        else:
            validations["issues"].append("Missing proper header (e.g., '# Claude Code Instructions')")

        # Check required links
        if "[AGENTS.md]" in content and "(AGENTS.md)" in content:
            validations["has_agents_link"] = True
        else:
            validations["issues"].append("Missing link to AGENTS.md")

        if "definition-of-done.md" in content:
            validations["has_definition_link"] = True
        else:
            validations["issues"].append("Missing link to definition-of-done.md")

        if f"system-prompts/tools/{tool_guide_name}.md" in content:
            validations["has_tool_guide_link"] = True
        else:
            validations["issues"].append(f"Missing link to tool guide (docs/system-prompts/tools/{tool_guide_name}.md)")

        if "docs/workflows.md" in content:
            validations["has_workflows_link"] = True
        else:
            validations["issues"].append("Missing link to workflows.md")

        # Check line count (should be anemic: 10-20 lines)
        if validations["line_count"] <= 20:
            validations["is_anemic"] = True
        else:
            validations["issues"].append(f"File is {validations['line_count']} lines (should be ≤20 for anemic format)")

        # Check for forbidden patterns
        forbidden = [
            ("## Available Tools", "Tool lists should be in tool guide"),
            ("## Development Environment", "Dev environment details belong in README"),
            ("## Key Concepts", "Key Concepts should reference AGENTS.md"),
            ("## Key Commands", "Commands should be in tool guide"),
            ("### File Operations", "File operation details belong in tool guide"),
        ]

        for pattern, reason in forbidden:
            if pattern in content:
                validations["issues"].append(f"Contains '{pattern}' section - {reason}")

        return validations

    def validate_all_tool_entries(self) -> int:
        """Validate all tool entry points meet anemic requirements."""
        tools = ["claude", "aider", "cline", "gemini"]
        all_valid = True

        print("Validating tool entry points...")
        for tool in tools:
            result = self.validate_tool_entry_point(tool)

            if result["issues"]:
                all_valid = False
                print(f"\n⚠️  {tool.upper()}.md:")
                for issue in result["issues"]:
                    print(f"   - {issue}")
            else:
                print(f"✓ {tool.upper()}.md: Valid anemic format ({result['line_count']} lines)")

        if all_valid:
            print("\n✅ All tool entry points are valid!")
        else:
            print("\n❌ Some tool entry points need fixes")

        return 0 if all_valid else 1

    def analyze_workflow(self) -> None:
        """Analyze and display workflow configuration."""
        agents_content = self._read_file(self.agents_file)
        language = self._detect_language()
        state = self.read_workflow_state(agents_content)

        print(f"Project language: {language}")
        print(f"Project root: {self.project_root}")
        print(f"AGENTS.md path: {self.agents_file}")

        # Get recommendation
        recommended = self.detect_recommended_workflow()
        print(f"\n📊 Workflow Analysis:")
        print(f"  Recommended: {recommended}")

        # Show current state
        logs_first_state = state.get("logs_first", "disabled")
        print(f"  Current state: logs_first={logs_first_state}")

        # Show available workflows
        print(f"\n📋 Available workflows:")
        print(f"  • logs-first (documented development)")
        print(f"  • custom (create your own - see custom-template.md)")

        # Show commands
        print(f"\n💡 Commands:")
        if logs_first_state == "enabled":
            print(f"  Enable: Already enabled")
            print(f"  Disable: python3 bootstrap.py --disable-logs-first --commit")
        else:
            print(f"  Enable: python3 bootstrap.py --enable-logs-first --commit")
            print(f"  Disable: Already disabled")

    def show_diff(self) -> None:
        """Show what would change (dry run mode)."""
        # This is a simplified version - a full diff would be more complex
        agents_content = self._read_file(self.agents_file)
        language = self._detect_language()

        print(f"Project language: {language}")
        print(f"Project root: {self.project_root}")
        print(f"AGENTS.md path: {self.agents_file}")
        print(f"System prompts dir: {self.system_prompts_dir}")

        # Sections to sync
        sections = [
            ("CORE-WORKFLOW", "workflows/core.md"),
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
  # Analyze workflow configuration
  python3 bootstrap.py --analyze-workflow

  # Enable logs-first workflow
  python3 bootstrap.py --enable-logs-first --commit

  # Disable logs-first workflow
  python3 bootstrap.py --disable-logs-first --commit

  # Validate tool entry point files
  python3 bootstrap.py --validate-tool-entries

  # Regenerate tool entry point files
  python3 bootstrap.py --regenerate-tool-entries --commit

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
        "--analyze-workflow",
        action="store_true",
        help="Analyze and show workflow configuration",
    )
    parser.add_argument(
        "--enable-logs-first",
        action="store_true",
        help="Enable logs-first workflow",
    )
    parser.add_argument(
        "--disable-logs-first",
        action="store_true",
        help="Disable logs-first workflow",
    )
    parser.add_argument(
        "--root",
        help="Project root directory (auto-detected if not specified)",
    )
    parser.add_argument(
        "--validate-tool-entries",
        action="store_true",
        help="Validate all tool entry point files meet anemic requirements",
    )
    parser.add_argument(
        "--regenerate-tool-entries",
        action="store_true",
        help="Regenerate anemic tool entry point files from canonical templates",
    )

    args = parser.parse_args()

    # Create bootstrap instance
    dry_run = not args.commit
    bootstrap = Bootstrap(project_root=args.root, dry_run=dry_run)

    # Verify system-prompts directory exists
    if not os.path.exists(bootstrap.system_prompts_dir):
        print(f"ERROR: System prompts directory not found: {bootstrap.system_prompts_dir}")
        sys.exit(1)

    # Handle tool entry point commands
    if args.validate_tool_entries:
        exit_code = bootstrap.validate_all_tool_entries()
        sys.exit(exit_code)

    if args.regenerate_tool_entries:
        exit_code = bootstrap.regenerate_tool_entries()
        sys.exit(exit_code)

    # Handle workflow commands
    if args.analyze_workflow:
        bootstrap.analyze_workflow()
        sys.exit(0)

    if args.enable_logs_first or args.disable_logs_first:
        agents_content = bootstrap._read_file(bootstrap.agents_file)
        if not agents_content:
            print(f"ERROR: Could not read {bootstrap.agents_file}")
            sys.exit(1)

        enable = args.enable_logs_first
        updated_content, changed = bootstrap.apply_workflow_state(
            agents_content, "logs_first", enable, force=args.force
        )

        # Update workflow state marker
        state = bootstrap.read_workflow_state(updated_content)
        state["logs_first"] = "enabled" if enable else "disabled"
        updated_content = bootstrap.write_workflow_state(updated_content, state)

        if changed or (state.get("logs_first") != ("enabled" if enable else "disabled")):
            bootstrap._write_file(bootstrap.agents_file, updated_content)
            if not args.commit:
                print("[DRY RUN] Changes would be applied. Use --commit to save.")
            else:
                print(f"✓ Workflow state updated in {bootstrap.agents_file}")
        sys.exit(0)

    # Show analysis or sync
    if args.analyze:
        bootstrap.show_diff()
    else:
        success = bootstrap.sync_agents_file(force=args.force)
        sys.exit(0 if success or not args.commit else 1)


if __name__ == "__main__":
    main()
