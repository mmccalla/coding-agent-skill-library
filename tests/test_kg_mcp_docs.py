"""Tests for Skills KG/MCP documentation and offline CI coverage."""

from __future__ import annotations

import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
README = REPO_ROOT / "README.md"
GUIDE = REPO_ROOT / "skills_docs" / "SKILLS_KG_MCP_RUNBOOK.md"
CI = REPO_ROOT / "scripts" / "ci_local.sh"


class SkillsKgMcpDocsTests(unittest.TestCase):
    def test_readme_links_kg_mcp_runbook(self) -> None:
        readme = README.read_text(encoding="utf-8")

        self.assertIn("skills_docs/SKILLS_KG_MCP_RUNBOOK.md", readme)

    def test_runbook_documents_end_to_end_workflow_and_boundaries(self) -> None:
        text = GUIDE.read_text(encoding="utf-8")

        for marker in (
            "python3 scripts/extract_skills_graph.py",
            "python3 scripts/map_skills_bridges.py",
            "neo4j/skills_schema.cypher",
            "python3 scripts/load_skills_neo4j.py",
            "python3 scripts/embed_skill_chunks.py",
            "python3 scripts/retrieve_skills_hybrid.py",
            "python3 scripts/skills_mcp_server.py",
            "python3 scripts/skills_mcp_server.py --sdk-stdio",
            "python3 scripts/check_neo4j_readiness.py --json",
            "python3 scripts/evaluate_skill_retrieval.py --limit 3",
            "python3 scripts/validate_skills_graph.py",
            "python3 -m uvicorn scripts.skills_api:create_app --factory",
            "placeholder",
            "ready: true",
            "official MCP client",
            "FastAPI",
            "retrieval evaluation gate",
            "connectedness failure",
            "mapping_rule_id",
            "read-only",
        ):
            self.assertIn(marker, text)

    def test_ci_includes_offline_kg_mcp_smoke_checks_without_live_apply(self) -> None:
        text = CI.read_text(encoding="utf-8")

        self.assertIn("python3 scripts/skills_mcp_server.py --list-tools", text)
        self.assertIn("python3 scripts/embed_skill_chunks.py --query", text)
        self.assertIn("python3 scripts/evaluate_skill_retrieval.py --limit 3", text)
        self.assertNotIn("--apply", text)


if __name__ == "__main__":
    unittest.main()
