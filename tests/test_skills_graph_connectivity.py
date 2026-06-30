"""Tests for skills graph connectivity validation."""

from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
EXPECTED_SKILL_COUNT = len(tuple((REPO_ROOT / "skills").glob("*/SKILL.md")))
VALIDATOR = REPO_ROOT / "scripts" / "validate_skills_graph.py"
CONNECTIVITY_CYPHER = REPO_ROOT / "neo4j" / "skills_connectivity_checks.cypher"
GDS_CONNECTIVITY_CYPHER = REPO_ROOT / "neo4j" / "skills_gds_connectivity_checks.cypher"


def load_validator_module():
    spec = importlib.util.spec_from_file_location("validate_skills_graph", VALIDATOR)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def connected_fixture() -> dict[str, object]:
    records = {
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
                "id": "skill:skill-discovery-and-selection",
                "name": "skill-discovery-and-selection",
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
                "target": "skill:skill-discovery-and-selection",
                "source_path": "fixture",
                "mapping_rule_id": "fixture",
                "confidence": 1.0,
                "rationale": "Fixture curated relationship.",
                "source_scope": "fixture",
                "source_ref": "fixture",
            }
        ],
        "bridges": [
            {
                "id": "skill:apply-laws-of-ai:bridge:task_shape:session-start",
                "skill_id": "skill:apply-laws-of-ai",
                "kind": "task_shape",
                "value": "session-start",
                "source": "skill:apply-laws-of-ai:bridge:task_shape:session-start",
                "rule_id": "skill:apply-laws-of-ai:bridge:task_shape:session-start",
                "path": "fixture",
                "source_path": "fixture",
                "confidence": 1.0,
                "rationale": "Fixture-derived task shape.",
                "source_scope": "skill",
                "source_ref": "apply-laws-of-ai",
            },
            {
                "id": "skill:apply-laws-of-ai:bridge:workflow_stage:startup",
                "skill_id": "skill:apply-laws-of-ai",
                "kind": "workflow_stage",
                "value": "startup",
                "source": "skill:apply-laws-of-ai:bridge:workflow_stage:startup",
                "rule_id": "skill:apply-laws-of-ai:bridge:workflow_stage:startup",
                "path": "fixture",
                "source_path": "fixture",
                "confidence": 1.0,
                "rationale": "Fixture-derived workflow stage.",
                "source_scope": "skill",
                "source_ref": "apply-laws-of-ai",
            },
            {
                "id": "skill:apply-laws-of-ai:bridge:capability:safety-baseline",
                "skill_id": "skill:apply-laws-of-ai",
                "kind": "capability",
                "value": "safety-baseline",
                "source": "skill:apply-laws-of-ai:bridge:capability:safety-baseline",
                "rule_id": "skill:apply-laws-of-ai:bridge:capability:safety-baseline",
                "path": "fixture",
                "source_path": "fixture",
                "confidence": 1.0,
                "rationale": "Fixture-derived capability.",
                "source_scope": "skill",
                "source_ref": "apply-laws-of-ai",
            },
            {
                "id": "skill:apply-laws-of-ai:bridge:control_theme:ai-safety",
                "skill_id": "skill:apply-laws-of-ai",
                "kind": "control_theme",
                "value": "ai-safety",
                "source": "skill:apply-laws-of-ai:bridge:control_theme:ai-safety",
                "rule_id": "skill:apply-laws-of-ai:bridge:control_theme:ai-safety",
                "path": "fixture",
                "source_path": "fixture",
                "confidence": 1.0,
                "rationale": "Fixture-derived control theme.",
                "source_scope": "skill",
                "source_ref": "apply-laws-of-ai",
            },
            {
                "id": "skill:apply-laws-of-ai:bridge:knowledge_domain:agent-control",
                "skill_id": "skill:apply-laws-of-ai",
                "kind": "knowledge_domain",
                "value": "agent-control",
                "source": "skill:apply-laws-of-ai:bridge:knowledge_domain:agent-control",
                "rule_id": "skill:apply-laws-of-ai:bridge:knowledge_domain:agent-control",
                "path": "fixture",
                "source_path": "fixture",
                "confidence": 1.0,
                "rationale": "Fixture-derived knowledge domain.",
                "source_scope": "skill",
                "source_ref": "apply-laws-of-ai",
            },
            {
                "id": "skill:skill-discovery-and-selection:bridge:task_shape:skill-routing",
                "skill_id": "skill:skill-discovery-and-selection",
                "kind": "task_shape",
                "value": "skill-routing",
                "source": "skill:skill-discovery-and-selection:bridge:task_shape:skill-routing",
                "rule_id": "skill:skill-discovery-and-selection:bridge:task_shape:skill-routing",
                "path": "fixture",
                "source_path": "fixture",
                "confidence": 1.0,
                "rationale": "Fixture-derived task shape.",
                "source_scope": "skill",
                "source_ref": "skill-discovery-and-selection",
            },
            {
                "id": "skill:skill-discovery-and-selection:bridge:workflow_stage:routing",
                "skill_id": "skill:skill-discovery-and-selection",
                "kind": "workflow_stage",
                "value": "routing",
                "source": "skill:skill-discovery-and-selection:bridge:workflow_stage:routing",
                "rule_id": "skill:skill-discovery-and-selection:bridge:workflow_stage:routing",
                "path": "fixture",
                "source_path": "fixture",
                "confidence": 1.0,
                "rationale": "Fixture-derived workflow stage.",
                "source_scope": "skill",
                "source_ref": "skill-discovery-and-selection",
            },
            {
                "id": "skill:skill-discovery-and-selection:bridge:capability:skill-discovery",
                "skill_id": "skill:skill-discovery-and-selection",
                "kind": "capability",
                "value": "skill-discovery",
                "source": "skill:skill-discovery-and-selection:bridge:capability:skill-discovery",
                "rule_id": "skill:skill-discovery-and-selection:bridge:capability:skill-discovery",
                "path": "fixture",
                "source_path": "fixture",
                "confidence": 1.0,
                "rationale": "Fixture-derived capability.",
                "source_scope": "skill",
                "source_ref": "skill-discovery-and-selection",
            },
            {
                "id": "skill:skill-discovery-and-selection:bridge:control_theme:context-governance",
                "skill_id": "skill:skill-discovery-and-selection",
                "kind": "control_theme",
                "value": "context-governance",
                "source": "skill:skill-discovery-and-selection:bridge:control_theme:context-governance",
                "rule_id": "skill:skill-discovery-and-selection:bridge:control_theme:context-governance",
                "path": "fixture",
                "source_path": "fixture",
                "confidence": 1.0,
                "rationale": "Fixture-derived control theme.",
                "source_scope": "skill",
                "source_ref": "skill-discovery-and-selection",
            },
            {
                "id": "skill:skill-discovery-and-selection:bridge:knowledge_domain:agentic-patterns",
                "skill_id": "skill:skill-discovery-and-selection",
                "kind": "knowledge_domain",
                "value": "agentic-patterns",
                "source": "skill:skill-discovery-and-selection:bridge:knowledge_domain:agentic-patterns",
                "rule_id": "skill:skill-discovery-and-selection:bridge:knowledge_domain:agentic-patterns",
                "path": "fixture",
                "source_path": "fixture",
                "confidence": 1.0,
                "rationale": "Fixture-derived knowledge domain.",
                "source_scope": "skill",
                "source_ref": "skill-discovery-and-selection",
            },
        ],
    }
    for bridge in records["bridges"]:
        source = bridge["source"]
        bridge["source_path"] = "fixture"
        bridge["rule_id"] = source
        bridge["source_scope"] = "fixture"
        bridge["source_ref"] = "fixture"
        bridge["rationale"] = "Fixture bridge assertion."
    return records


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
        records["bridges"].extend(
            [
                {
                    "id": "skill:shipping-and-launch:bridge:task_shape:release",
                    "skill_id": "skill:shipping-and-launch",
                    "kind": "task_shape",
                    "value": "release",
                    "source": "fixture",
                    "confidence": 1.0,
                },
                {
                    "id": "skill:shipping-and-launch:bridge:workflow_stage:release",
                    "skill_id": "skill:shipping-and-launch",
                    "kind": "workflow_stage",
                    "value": "release",
                    "source": "fixture",
                    "confidence": 1.0,
                },
                {
                    "id": "skill:shipping-and-launch:bridge:capability:launch-readiness",
                    "skill_id": "skill:shipping-and-launch",
                    "kind": "capability",
                    "value": "launch-readiness",
                    "source": "fixture",
                    "confidence": 1.0,
                },
                {
                    "id": "skill:shipping-and-launch:bridge:control_theme:release-safety",
                    "skill_id": "skill:shipping-and-launch",
                    "kind": "control_theme",
                    "value": "release-safety",
                    "source": "fixture",
                    "confidence": 1.0,
                },
                {
                    "id": "skill:shipping-and-launch:bridge:knowledge_domain:reliability-and-delivery",
                    "skill_id": "skill:shipping-and-launch",
                    "kind": "knowledge_domain",
                    "value": "reliability-and-delivery",
                    "source": "fixture",
                    "confidence": 1.0,
                },
            ]
        )
        for bridge in records["bridges"]:
            bridge.setdefault("source_path", "fixture")
            bridge.setdefault("rule_id", bridge["source"])
            bridge.setdefault("source_scope", "fixture")
            bridge.setdefault("source_ref", "fixture")
            bridge.setdefault("rationale", "Fixture bridge assertion.")

        result = module.validate_graph_records(records)

        self.assertFalse(result.valid)
        self.assertTrue(any("unreachable from root" in e for e in result.errors))

    def test_unproven_bridge_values_fail_validation(self) -> None:
        module = load_validator_module()
        records = connected_fixture()
        records["bridges"] = []

        result = module.validate_graph_records(records)

        self.assertFalse(result.valid)
        self.assertTrue(any("missing bridge provenance" in e for e in result.errors))

    def test_malformed_bridge_provenance_fails_validation(self) -> None:
        module = load_validator_module()
        records = connected_fixture()
        del records["bridges"][0]["confidence"]

        result = module.validate_graph_records(records)

        self.assertFalse(result.valid)
        self.assertTrue(any("invalid bridge provenance" in e for e in result.errors))

    def test_spoofed_bridge_identity_fails_validation(self) -> None:
        module = load_validator_module()
        records = module.build_records_from_skills(REPO_ROOT / "skills")
        records["bridges"][0]["id"] = "skill:other:bridge:task_shape:spoofed"
        records["bridges"][0]["source_path"] = "skills/spoofed/SKILL.md"
        records["bridges"][0]["path"] = "skills/spoofed/SKILL.md"

        result = module.validate_graph_records(records)

        self.assertFalse(result.valid)
        self.assertTrue(any("invalid bridge provenance" in e for e in result.errors))

    def test_missing_related_skill_relationship_provenance_fails_validation(self) -> None:
        extractor = load_module(
            REPO_ROOT / "scripts" / "extract_skills_graph.py", "extract_skills_graph"
        )
        module = load_validator_module()
        records = extractor.extract_skills_graph_records(REPO_ROOT / "skills")
        relationship = next(
            relationship
            for relationship in records["relationships"]
            if relationship["type"] == "RELATED_TO"
        )
        del relationship["source_section_id"]

        result = module.validate_graph_records(records)

        self.assertFalse(result.valid)
        self.assertTrue(any("invalid relationship provenance" in e for e in result.errors))

    def test_category_derived_bridges_do_not_mask_same_category_orphan(self) -> None:
        module = load_validator_module()
        records = connected_fixture()
        records["skills"].append(
            {
                "id": "skill:isolated-agentic",
                "name": "isolated-agentic",
                "category": "agentic-patterns",
                "task_shapes": ["isolated-task"],
                "workflow_stages": ["isolated-stage"],
                "capabilities": ["isolated-capability"],
                "control_themes": ["agentic-patterns"],
                "knowledge_domains": ["agentic-patterns"],
            }
        )
        records["bridges"].extend(
            [
                {
                    "id": "skill:isolated-agentic:bridge:task_shape:isolated-task",
                    "skill_id": "skill:isolated-agentic",
                    "kind": "task_shape",
                    "value": "isolated-task",
                    "source": "fixture",
                    "rule_id": "fixture",
                    "source_scope": "fixture",
                    "source_ref": "fixture",
                    "rationale": "Fixture bridge assertion.",
                    "source_path": "fixture",
                    "confidence": 1.0,
                },
                {
                    "id": "skill:isolated-agentic:bridge:workflow_stage:isolated-stage",
                    "skill_id": "skill:isolated-agentic",
                    "kind": "workflow_stage",
                    "value": "isolated-stage",
                    "source": "fixture",
                    "rule_id": "fixture",
                    "source_scope": "fixture",
                    "source_ref": "fixture",
                    "rationale": "Fixture bridge assertion.",
                    "source_path": "fixture",
                    "confidence": 1.0,
                },
                {
                    "id": "skill:isolated-agentic:bridge:capability:isolated-capability",
                    "skill_id": "skill:isolated-agentic",
                    "kind": "capability",
                    "value": "isolated-capability",
                    "source": "fixture",
                    "rule_id": "fixture",
                    "source_scope": "fixture",
                    "source_ref": "fixture",
                    "rationale": "Fixture bridge assertion.",
                    "source_path": "fixture",
                    "confidence": 1.0,
                },
                {
                    "id": "skill:isolated-agentic:bridge:control_theme:agentic-patterns",
                    "skill_id": "skill:isolated-agentic",
                    "kind": "control_theme",
                    "value": "agentic-patterns",
                    "source": "fixture",
                    "rule_id": "fixture",
                    "source_scope": "category",
                    "source_ref": "agentic-patterns",
                    "rationale": "Fixture category bridge assertion.",
                    "source_path": "fixture",
                    "confidence": 0.9,
                },
                {
                    "id": "skill:isolated-agentic:bridge:knowledge_domain:agentic-patterns",
                    "skill_id": "skill:isolated-agentic",
                    "kind": "knowledge_domain",
                    "value": "agentic-patterns",
                    "source": "fixture",
                    "rule_id": "fixture",
                    "source_scope": "category",
                    "source_ref": "agentic-patterns",
                    "rationale": "Fixture category bridge assertion.",
                    "source_path": "fixture",
                    "confidence": 0.9,
                },
            ]
        )

        result = module.validate_graph_records(records)

        self.assertFalse(result.valid)
        self.assertTrue(any("isolated-agentic: unreachable from root" in e for e in result.errors))

    def test_repository_skills_export_to_one_connected_graph(self) -> None:
        module = load_validator_module()

        records = module.build_records_from_skills(REPO_ROOT / "skills")
        result = module.validate_graph_records(records)

        self.assertEqual(len(records["skills"]), EXPECTED_SKILL_COUNT)
        self.assertTrue(result.valid, "\n".join(result.errors))

    def test_local_ci_runs_skills_graph_validation(self) -> None:
        ci_text = (REPO_ROOT / "scripts" / "ci_local.sh").read_text(encoding="utf-8")

        self.assertIn("python3 scripts/validate_skills_graph.py", ci_text)

    def test_connectivity_cypher_contains_required_checks(self) -> None:
        text = CONNECTIVITY_CYPHER.read_text(encoding="utf-8")

        for marker in (
            "missing task/capability bridge",
            "missing workflow stage",
            "missing bridge assertion",
            "invalid bridge assertion provenance",
            "invalid relationship provenance",
            "COMPLEMENTS",
            "GOVERNS",
            "trim(r.source_path)",
            "trim(b.source)",
            "unreachable from root",
        ):
            self.assertIn(marker, text)
        self.assertNotIn("SUPPORTS", text)
        self.assertNotIn("SPECIALISES", text)
        self.assertNotIn("gds.wcc.stream", text)

    def test_gds_connectivity_cypher_is_optional(self) -> None:
        text = GDS_CONNECTIVITY_CYPHER.read_text(encoding="utf-8")

        self.assertIn("weakly connected", text)
        self.assertIn("gds.wcc.stream", text)


if __name__ == "__main__":
    unittest.main()
