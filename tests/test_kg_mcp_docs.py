"""Tests for Skills KG/MCP documentation and offline CI coverage."""

from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
README = REPO_ROOT / "README.md"
GUIDE = REPO_ROOT / "skills_docs" / "SKILLS_KG_MCP_RUNBOOK.md"
CI = REPO_ROOT / "scripts/dev_workflow/ci_local.sh"
LEGACY_MCP_SHIM = REPO_ROOT / "scripts/skills_mcp_server.py"


class SkillsKgMcpDocsTests(unittest.TestCase):
    def test_readme_links_kg_mcp_runbook(self) -> None:
        readme = README.read_text(encoding="utf-8")

        self.assertIn("skills_docs/SKILLS_KG_MCP_RUNBOOK.md", readme)

    def test_runbook_documents_end_to_end_workflow_and_boundaries(self) -> None:
        text = GUIDE.read_text(encoding="utf-8")

        for marker in (
            "python3 scripts/graph/build/extract_skills_graph.py",
            "neo4j/skills_schema.cypher",
            "python3 scripts/graph/load/load_skills_neo4j.py",
            "python3 scripts/graph/build/embed_skill_chunks.py",
            "python3 scripts/lib/retrieval/retrieve_skills_hybrid.py",
            "python3 scripts/runtime/mcp/skills_mcp_server.py",
            "python3 scripts/runtime/mcp/skills_mcp_server.py --sdk-stdio",
            "python3 scripts/runtime/docker/check_neo4j_readiness.py --json",
            "python3 scripts/lib/retrieval/evaluate_skill_retrieval.py --limit 3",
            "python3 scripts/validators/validate_skills_graph.py",
            "python3 -m uvicorn scripts.runtime.api.skills_api:create_app --factory",
            "GET /ollama/models",
            "POST /skills/route",
            "GET /skills/resolve",
            "GET /skills/{skill_id}/execution-guide",
            "POST /skills/query",
            "route_skill_query",
            "resolve_skill",
            "get_skill_execution_guide",
            "direct_lookup",
            "execution-plan",
            "http://127.0.0.1:11434",
            "placeholder",
            "ready: true",
            "official MCP client",
            "FastAPI",
            "retrieval evaluation gate",
            "connectedness failure",
            "source_section_id",
            "RetrievalUnit",
            "read-only",
        ):
            self.assertIn(marker, text)

    def test_ci_includes_offline_kg_mcp_smoke_checks_without_live_apply(self) -> None:
        text = CI.read_text(encoding="utf-8")

        self.assertIn("python3 scripts/runtime/mcp/skills_mcp_server.py --list-tools", text)
        self.assertIn("python3 scripts/graph/build/embed_skill_chunks.py --query", text)
        self.assertIn("python3 scripts/utils/ci/ci_ingest_gate.py", text)
        self.assertIn("run_library_validators.sh", text)
        self.assertIn("-m eval_pr", text)
        self.assertNotIn("--apply", text)
        self.assertNotIn("python3 scripts/lib/retrieval/evaluate_skill_retrieval.py", text)

    def test_legacy_mcp_entrypoint_shim_lists_tools(self) -> None:
        self.assertTrue(
            LEGACY_MCP_SHIM.is_file(), "legacy MCP shim must exist after scripts reorganisation"
        )
        result = subprocess.run(
            [sys.executable, str(LEGACY_MCP_SHIM), "--list-tools", "--fixture"],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(0, result.returncode, msg=result.stderr)
        payload = json.loads(result.stdout)
        tool_names = {item["name"] for item in payload}
        self.assertIn("get_skill", tool_names)
        self.assertIn("recommend_skills", tool_names)


if __name__ == "__main__":
    unittest.main()
