"""Tests for the skills knowledge graph ontology contract."""

from __future__ import annotations

import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
ONTOLOGY_DIR = REPO_ROOT / "skills_docs" / "ontology"


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


class SkillsOntologyTests(unittest.TestCase):
    def test_ontology_contract_documents_required_concepts(self) -> None:
        text = read(ONTOLOGY_DIR / "SKILLS_ONTOLOGY.md")

        for heading in (
            "## Purpose",
            "## Competency Questions",
            "## Core Classes",
            "## Core Relationships",
            "## Property Graph Mapping",
            "## Open Decisions",
        ):
            self.assertIn(heading, text)

        for concept in (
            "Skill",
            "SkillCategory",
            "SkillSection",
            "SkillChunk",
            "ReferenceDocument",
            "ValidationRule",
            "TaskShape",
            "WorkflowStage",
            "Capability",
            "ControlTheme",
            "KnowledgeDomain",
            "BridgeAssertion",
        ):
            self.assertIn(f"`{concept}`", text)

    def test_turtle_ontology_defines_core_classes_and_properties(self) -> None:
        text = read(ONTOLOGY_DIR / "skills.ttl")

        for class_name in (
            "Skill",
            "SkillCategory",
            "SkillSection",
            "SkillChunk",
            "ReferenceDocument",
            "TaskShape",
            "WorkflowStage",
            "Capability",
            "ControlTheme",
            "KnowledgeDomain",
            "BridgeAssertion",
        ):
            self.assertIn(f"skills:{class_name} a owl:Class", text)

        for predicate in (
            "belongsToCategory",
            "hasSection",
            "hasChunk",
            "supportsTaskShape",
            "operatesInStage",
            "enablesCapability",
            "governedBy",
            "partOfDomain",
            "assertsBridge",
        ):
            self.assertIn(f"skills:{predicate} a owl:ObjectProperty", text)

        for datatype_property in (
            "title",
            "contentHash",
            "wordCount",
            "lineCount",
            "isBaselineSkill",
            "source",
            "confidence",
        ):
            self.assertIn(f"skills:{datatype_property} a owl:DatatypeProperty", text)

    def test_shacl_shapes_capture_required_skill_constraints(self) -> None:
        text = read(ONTOLOGY_DIR / "skills.shacl.ttl")

        for shape in (
            "SkillShape",
            "SkillSectionShape",
            "SkillChunkShape",
            "BridgeCoverageShape",
            "BridgeAssertionShape",
        ):
            self.assertIn(f"skills:{shape} a sh:NodeShape", text)

        for required_path in (
            "skills:name",
            "skills:title",
            "skills:path",
            "skills:contentHash",
            "skills:wordCount",
            "skills:lineCount",
            "skills:isBaselineSkill",
            "skills:belongsToCategory",
            "skills:supportsTaskShape",
            "skills:enablesCapability",
            "skills:assertsBridge",
            "skills:source",
            "skills:confidence",
        ):
            self.assertIn(f"sh:path {required_path}", text)


if __name__ == "__main__":
    unittest.main()
