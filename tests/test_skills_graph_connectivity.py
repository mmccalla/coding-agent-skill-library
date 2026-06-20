"""Tests for skills graph connectivity validation."""

from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
VALIDATOR = REPO_ROOT / "scripts" / "validate_skills_graph.py"
CONNECTIVITY_CYPHER = REPO_ROOT / "neo4j" / "skills_connectivity_checks.cypher"


def load_validator_module():
    spec = importlib.util.spec_from_file_location("validate_skills_graph", VALIDATOR)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def connected_fixture() -> dict[str, object]:
    return {
        "root_skill": "apply-laws-of-ai",
        "skills": [
            {
                "id": "skill:apply-laws-of-ai",
                "name": "apply-laws-of-ai",
                "category": "agent-control-patterns",
                "task_shapes": ["session-start"],
                "workflow_stages": ["startup"],
                "capabilities": ["safety-baseline"],
                "control_themes": ["ai-safety"],
                "knowledge_domains": ["agent-control"],
            },
            {
                "id": "skill:using-agent-skills",
                "name": "using-agent-skills",
                "category": "agentic-patterns",
                "task_shapes": ["skill-routing"],
                "workflow_stages": ["routing"],
                "capabilities": ["skill-discovery"],
                "control_themes": ["context-governance"],
                "knowledge_domains": ["agentic-patterns"],
            },
        ],
        "relationships": [
            {
                "source": "skill:apply-laws-of-ai",
                "type": "PRECEDES",
                "target": "skill:using-agent-skills",
            }
        ],
    }


class SkillsGraphConnectivityTests(unittest.TestCase):
    def test_connected_graph_passes_validation(self) -> None:
        module = load_validator_module()

        result = module.validate_graph_records(connected_fixture())

        self.assertTrue(result.valid)
        self.assertEqual(result.errors, ())

    def test_missing_bridge_relationships_fail_validation(self) -> None:
        module = load_validator_module()
        records = connected_fixture()
        records["skills"] = [
            {
                "id": "skill:orphan",
                "name": "orphan",
                "category": "agentic-patterns",
                "task_shapes": [],
                "workflow_stages": [],
                "capabilities": [],
                "control_themes": [],
                "knowledge_domains": [],
            }
        ]

        result = module.validate_graph_records(records)

        self.assertFalse(result.valid)
        self.assertTrue(any("missing task/capability bridge" in e for e in result.errors))
        self.assertTrue(any("missing workflow stage" in e for e in result.errors))

    def test_unreachable_skill_fails_validation(self) -> None:
        module = load_validator_module()
        records = connected_fixture()
        records["skills"].append(
            {
                "id": "skill:shipping-and-launch",
                "name": "shipping-and-launch",
                "category": "reliability-and-delivery",
                "task_shapes": ["release"],
                "workflow_stages": ["release"],
                "capabilities": ["launch-readiness"],
                "control_themes": ["release-safety"],
                "knowledge_domains": ["reliability-and-delivery"],
            }
        )

        result = module.validate_graph_records(records)

        self.assertFalse(result.valid)
        self.assertTrue(any("unreachable from root" in e for e in result.errors))

    def test_repository_skills_export_to_one_connected_graph(self) -> None:
        module = load_validator_module()

        records = module.build_records_from_skills(REPO_ROOT / "skills")
        result = module.validate_graph_records(records)

        self.assertEqual(len(records["skills"]), 87)
        self.assertTrue(result.valid, "\n".join(result.errors))

    def test_local_ci_runs_skills_graph_validation(self) -> None:
        ci_text = (REPO_ROOT / "scripts" / "ci_local.sh").read_text(encoding="utf-8")

        self.assertIn("python3 scripts/validate_skills_graph.py", ci_text)

    def test_connectivity_cypher_contains_required_checks(self) -> None:
        text = CONNECTIVITY_CYPHER.read_text(encoding="utf-8")

        for marker in (
            "missing task/capability bridge",
            "missing workflow stage",
            "unreachable from root",
            "weakly connected",
        ):
            self.assertIn(marker, text)


if __name__ == "__main__":
    unittest.main()
