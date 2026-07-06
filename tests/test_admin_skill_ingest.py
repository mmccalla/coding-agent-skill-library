"""Tests for admin skill ingest orchestration."""

from __future__ import annotations

import shutil
import tempfile
import unittest
from pathlib import Path

from fastapi.testclient import TestClient

from scripts.graph.build import admin_skill_ingest
from scripts.runtime.api.skills_api import create_app
from scripts.runtime.mcp.skills_mcp_server import SkillsMcpServer
from scripts.validators.validate_skill_trust import validate_skill_trust_file

REPO_ROOT = Path(__file__).resolve().parents[1]
TRUST_FIXTURES = REPO_ROOT / "tests" / "fixtures" / "skill_trust"
BENIGN_SKILL = """---
name: admin-ingest-fixture
description: Use when validating admin ingest writes a trusted skill to the repository.
---

# Admin Ingest Fixture

## When to use

Use when testing admin ingest.

## Procedure

1. Upload through the admin ingest endpoint.
2. Confirm the skill resolves through MCP.

## Verification

- [ ] Admin ingest persists SKILL.md and reloads the graph plan.

## Related skills

- `apply-laws-of-ai`
"""


def seed_minimal_skills_root(root: Path) -> None:
    shutil.copy(
        REPO_ROOT / "skills" / "PACK_METADATA.json",
        root / "PACK_METADATA.json",
    )
    for skill_name in ("apply-laws-of-ai",):
        source = REPO_ROOT / "skills" / skill_name
        destination = root / skill_name
        shutil.copytree(source, destination)


class AdminSkillIngestTests(unittest.TestCase):
    def test_trust_hash_is_stable_for_same_report(self) -> None:
        path = TRUST_FIXTURES / "benign" / "guardrails-teaching.md"
        report_a = validate_skill_trust_file(str(path))
        report_b = validate_skill_trust_file(str(path))
        self.assertEqual(
            admin_skill_ingest.trust_report_hash(report_a),
            admin_skill_ingest.trust_report_hash(report_b),
        )

    def test_run_admin_ingest_rejects_malicious_fixture(self) -> None:
        content = (TRUST_FIXTURES / "malicious" / "instruction-override.md").read_text(
            encoding="utf-8"
        )
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            seed_minimal_skills_root(root)
            result = admin_skill_ingest.run_admin_skill_ingest(
                content=content,
                actor="tester",
                skills_root=root,
            )
            self.assertEqual("rejected", result.outcome)
            self.assertFalse(result.persisted)

    def test_run_admin_ingest_persists_and_resolves(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            seed_minimal_skills_root(root)
            result = admin_skill_ingest.run_admin_skill_ingest(
                content=BENIGN_SKILL,
                actor="tester",
                skills_root=root,
            )
            self.assertEqual("success", result.outcome)
            self.assertTrue(result.persisted)
            self.assertTrue((root / "admin-ingest-fixture" / "SKILL.md").is_file())

            server = SkillsMcpServer.from_repository(root)
            resolved = server.call_tool("resolve_skill", {"name": "admin-ingest-fixture"})
            self.assertEqual("ok", resolved["status"])
            self.assertEqual("skill:admin-ingest-fixture", resolved["skill_id"])

    def test_admin_api_ingest_requires_auth(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            seed_minimal_skills_root(root)
            config = admin_skill_ingest.AdminIngestConfig(
                api_key="secret-key",
                write_mode="direct",
                write_root=root,
            )
            server = SkillsMcpServer.from_repository(root)
            client = TestClient(create_app(server=server, admin_config=config, skills_root=root))
            response = client.post(
                "/skills/admin/ingest",
                files={"file": ("SKILL.md", BENIGN_SKILL.encode(), "text/markdown")},
            )
            self.assertEqual(403, response.status_code)

    def test_admin_api_ingest_persists_and_resolves(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            seed_minimal_skills_root(root)
            config = admin_skill_ingest.AdminIngestConfig(
                api_key="secret-key",
                write_mode="direct",
                write_root=root,
            )
            server = SkillsMcpServer.from_repository(root)
            client = TestClient(create_app(server=server, admin_config=config, skills_root=root))
            response = client.post(
                "/skills/admin/ingest",
                headers={"X-Skills-Admin-Key": "secret-key"},
                files={"file": ("SKILL.md", BENIGN_SKILL.encode(), "text/markdown")},
            )
            self.assertEqual(200, response.status_code)
            payload = response.json()
            self.assertTrue(payload["persisted"])
            self.assertEqual("admin-ingest-fixture", payload["skill_name"])

            resolved = server.call_tool("resolve_skill", {"name": "admin-ingest-fixture"})
            self.assertEqual("skill:admin-ingest-fixture", resolved["skill_id"])

            audit = client.get(
                "/skills/admin/ingests",
                headers={"X-Skills-Admin-Key": "secret-key"},
            )
            self.assertEqual(200, audit.status_code)
            self.assertGreaterEqual(len(audit.json()["ingests"]), 1)


if __name__ == "__main__":
    unittest.main()
