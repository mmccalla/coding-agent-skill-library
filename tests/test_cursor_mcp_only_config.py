"""Tests for Cursor exclusive skills-kg MCP workspace configuration."""

from __future__ import annotations

import json
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
VSCODE_SETTINGS_EXAMPLE = REPO_ROOT / "configs" / "cursor" / "vscode-settings.mcp-only.example.json"
CURSOR_RULES_DIR = REPO_ROOT / "configs" / "cursor" / "rules"
CURSOR_RULE = CURSOR_RULES_DIR / "skills-kg-mcp-only.mdc"
PROJECT_CONTEXT_RULE = CURSOR_RULES_DIR / "project-context.mdc"
GETTING_STARTED = REPO_ROOT / "skills_docs" / "GETTING_STARTED.md"
CURSOR_SETUP = REPO_ROOT / "skills_docs" / "CURSOR_IDE_SETUP.md"
RUNBOOK = REPO_ROOT / "skills_docs" / "SKILLS_KG_MCP_RUNBOOK.md"
GITIGNORE = REPO_ROOT / ".gitignore"


class CursorMcpOnlyConfigTests(unittest.TestCase):
    def test_vscode_settings_disable_repo_filesystem_skills(self) -> None:
        settings = json.loads(VSCODE_SETTINGS_EXAMPLE.read_text(encoding="utf-8"))
        locations = settings.get("chat.agentSkillsLocations", {})

        disabled_skills_paths = [
            path for path, enabled in locations.items() if path.endswith("/skills") and not enabled
        ]
        self.assertTrue(
            disabled_skills_paths,
            msg="Committed MCP-only example must disable at least one skills/ location",
        )

    def test_cursor_directory_is_gitignored(self) -> None:
        text = GITIGNORE.read_text(encoding="utf-8")
        self.assertRegex(text, r"(?m)^/\.cursor$")

    def test_cursor_rule_enforces_mcp_only_workflow(self) -> None:
        text = CURSOR_RULE.read_text(encoding="utf-8")

        self.assertIn("alwaysApply: true", text)
        for marker in (
            "route_skill_query",
            "resolve_skill",
            "get_skill",
            "recommend_skills",
            "get_skill_context",
            "get_skill_execution_guide",
            "skills://contract",
            "apply-laws-of-ai",
            "AGENTIC_CODING_GLOBAL_SAFETY.md",
            "SECURE_AGENTIC_DEVELOPMENT.md",
        ):
            self.assertIn(marker, text)

    def test_getting_started_links_cursor_setup_guide(self) -> None:
        text = GETTING_STARTED.read_text(encoding="utf-8")

        self.assertIn("CURSOR_IDE_SETUP.md", text)

    def test_project_context_is_project_rule_not_user_rule(self) -> None:
        text = PROJECT_CONTEXT_RULE.read_text(encoding="utf-8")

        self.assertIn("project rule", text.lower())
        self.assertIn("not", text.lower())
        setup = CURSOR_SETUP.read_text(encoding="utf-8")
        self.assertIn("project-context.mdc", setup)
        self.assertIn("Project rules vs user-level", setup)

    def test_cursor_setup_documents_both_modes(self) -> None:
        text = CURSOR_SETUP.read_text(encoding="utf-8")

        for marker in (
            "Mode A — skills-kg MCP only",
            "Mode B — filesystem skills only",
            "discover-local-skills",
            "chat.agentSkillsLocations",
            "skills-kg-mcp-only.mdc",
            "route_skill_query",
            "HOW_TO_FIND_THE_RIGHT_SKILL.md",
            "apply-laws-of-ai",
            "configs/cursor/rules",
        ):
            self.assertIn(marker, text)

    def test_runbook_links_cursor_setup_guide(self) -> None:
        text = RUNBOOK.read_text(encoding="utf-8")

        self.assertIn("CURSOR_IDE_SETUP.md", text)


if __name__ == "__main__":
    unittest.main()
