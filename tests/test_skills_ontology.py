"""Tests for the skills knowledge graph ontology contract."""

from __future__ import annotations

import importlib.util
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
ONTOLOGY_DIR = REPO_ROOT / "skills_docs" / "ontology"
ONTOLOGY_VALIDATOR = REPO_ROOT / "scripts" / "validate_skills_ontology.py"
CANONICAL_CORE_SHAPES = ONTOLOGY_DIR / "canonical-core.shacl.ttl"
RETRIEVAL_PROJECTION_SHAPES = ONTOLOGY_DIR / "retrieval-projection.shacl.ttl"
RUNTIME_SELECTION_SHAPES = ONTOLOGY_DIR / "runtime-selection.shacl.ttl"


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def load_validator_module():
    spec = importlib.util.spec_from_file_location("validate_skills_ontology", ONTOLOGY_VALIDATOR)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class SkillsOntologyTests(unittest.TestCase):
    def test_ontology_contract_documents_current_krag_model(self) -> None:
        text = read(ONTOLOGY_DIR / "SKILLS_ONTOLOGY.md")

        for heading in (
            "## Purpose",
            "## Design Principles",
            "## Competency Questions",
            "## Canonical Layers",
            "## Controlled Vocabulary Pattern",
            "## Core Relationships",
            "## Canonical Property Policy",
            "## Property Graph Mapping",
            "## KRAG-Specific Rules",
            "## Open Decisions",
        ):
            self.assertIn(heading, text)

        for concept in (
            "SkillPack",
            "Skill",
            "SkillVersion",
            "IngestionRun",
            "SourceResource",
            "StructuralElement",
            "EvidenceAnchor",
            "RetrievalUnit",
            "SkillSelectionRun",
            "SkillSelectionRequest",
            "SelectionCandidate",
            "SkillSelectionDecision",
            "Citation",
            "BridgeConcept",
            "BridgeAssertion",
            "SkillDependencyAssertion",
            "SemanticAssertion",
            "InvocationCondition",
            "Tool",
            "AgentRuntime",
            "EvaluationDataset",
            "EvaluationTask",
            "ExpectedSkillVersion",
            "ObservedSelection",
            "EvaluationRun",
            "FailureMode",
        ):
            self.assertIn(f"`{concept}`", text)

    def test_turtle_ontology_defines_current_core_classes_and_properties(self) -> None:
        text = read(ONTOLOGY_DIR / "skills.ttl")

        for class_name in (
            "SkillPack",
            "Skill",
            "SkillVersion",
            "IngestionRun",
            "SourceResource",
            "ReferenceDocument",
            "StructuralElement",
            "SkillSection",
            "EvidenceAnchor",
            "RetrievalUnit",
            "SkillSelectionRun",
            "SkillSelectionRequest",
            "SelectionCandidate",
            "SkillSelectionDecision",
            "Citation",
            "BridgeConcept",
            "BridgeAssertion",
            "SkillDependencyAssertion",
            "SemanticAssertion",
            "InvocationCondition",
            "Tool",
            "AgentRuntime",
            "EvaluationDataset",
            "EvaluationTask",
            "ExpectedSkillVersion",
            "ObservedSelection",
            "EvaluationRun",
            "FailureMode",
        ):
            self.assertIn(f"skills:{class_name} a owl:Class", text)

        for predicate in (
            "containsSkill",
            "hasVersion",
            "currentVersion",
            "versionOf",
            "belongsToCategory",
            "hasSourceResource",
            "hasSection",
            "hasEvidenceAnchor",
            "assertionFor",
            "bridgeTarget",
            "supportedBy",
            "projectsFrom",
            "citesEvidence",
            "hasSelectionRequest",
            "hasSelectionCandidate",
            "hasSelectionDecision",
            "candidateSkillVersion",
            "selectedSkillVersion",
            "rejectedSkillVersion",
            "selectionSupportedBy",
            "dependencySourceVersion",
            "dependencyTargetVersion",
            "notForTaskShape",
            "excludedWhen",
            "requiresTool",
            "incompatibleWithTool",
            "compatibleWithRuntime",
            "incompatibleWithRuntime",
            "supersededBy",
            "hasEvaluationTask",
            "evaluatedDataset",
            "expectsSkillVersion",
            "expectedSkillVersion",
            "observedSkillVersion",
            "evaluatedTask",
            "recordedSelection",
            "hasFailureMode",
        ):
            self.assertIn(f"skills:{predicate} a owl:ObjectProperty", text)

        for datatype_property in (
            "name",
            "path",
            "sourcePath",
            "headingPath",
            "heading",
            "text",
            "retrievalText",
            "retrievalUnitType",
            "lexicalBoostTerms",
            "semanticAliases",
            "priorityWeight",
            "embeddingModel",
            "embeddingVersion",
            "vectorDimension",
            "retrievalProfile",
            "contentHash",
            "checksum",
            "versionIdentifier",
            "ordinal",
            "lineStart",
            "lineEnd",
            "charStart",
            "charEnd",
            "anchorRole",
            "confidence",
            "selectionScore",
            "selectionReason",
            "rejectionReason",
            "requiresHumanApproval",
            "rationale",
            "dependencyType",
            "precisionAt1",
            "recallAtK",
            "meanReciprocalRank",
            "ndcgAtK",
            "graphLiftRecallAtK",
            "p95LatencyMs",
            "citationCoverage",
            "exclusionAccuracy",
            "tokenCostPerSelection",
        ):
            self.assertIn(f"skills:{datatype_property} a owl:DatatypeProperty", text)

    def test_shacl_shapes_capture_current_ontology_constraints(self) -> None:
        text = read(ONTOLOGY_DIR / "skills.shacl.ttl")

        for shape in (
            "SkillPackShape",
            "SkillShape",
            "SkillVersionShape",
            "IngestionRunShape",
            "SourceResourceShape",
            "SkillSectionShape",
            "EvidenceAnchorShape",
            "RetrievalUnitShape",
            "BridgeConceptShape",
            "BridgeConceptLifecycleShape",
            "BridgeConceptHierarchyShape",
            "SkillCategorySchemeShape",
            "TaskShapeSchemeShape",
            "WorkflowStageSchemeShape",
            "CapabilitySchemeShape",
            "ControlThemeSchemeShape",
            "KnowledgeDomainSchemeShape",
            "BridgeAssertionShape",
            "SkillDependencyAssertionShape",
            "DirectTaskShapeDerivationShape",
            "DirectCapabilityDerivationShape",
            "DirectWorkflowStageDerivationShape",
            "DirectControlThemeDerivationShape",
            "DirectKnowledgeDomainDerivationShape",
            "SkillSelectionRunShape",
            "SkillSelectionRequestShape",
            "SelectionCandidateShape",
            "SkillSelectionDecisionShape",
            "CitationShape",
            "EvaluationDatasetShape",
            "EvaluationTaskShape",
            "ExpectedSkillVersionShape",
            "ObservedSelectionShape",
            "EvaluationRunShape",
            "FailureModeShape",
        ):
            self.assertIn(f"skills:{shape} a sh:NodeShape", text)

        for required_path in (
            "skills:name",
            "skills:versionIdentifier",
            "skills:containsSkill",
            "skills:belongsToCategory",
            "skills:hasVersion",
            "skills:versionOf",
            "prov:wasGeneratedBy",
            "skills:sourcePath",
            "skills:headingPath",
            "skills:lineStart",
            "skills:lineEnd",
            "skills:anchorRole",
            "skills:hasSourceResource",
            "skills:hasSection",
            "skills:heading",
            "skills:ordinal",
            "skills:derivedFromElement",
            "skills:projectsFrom",
            "skills:assertionFor",
            "skills:bridgeTarget",
            "skills:supportedBy",
            "skills:dependencySourceVersion",
            "skills:dependencyTargetVersion",
            "skills:dependencyType",
            "skills:hasSelectionRequest",
            "skills:hasSelectionDecision",
            "skills:candidateSkillVersion",
            "skills:selectedSkillVersion",
            "skills:rejectedSkillVersion",
            "skills:selectionSupportedBy",
            "skills:selectionScore",
            "skills:selectionReason",
            "skills:rejectionReason",
            "skills:citesEvidence",
            "dcterms:isReplacedBy",
            "skills:hasEvaluationTask",
            "skills:evaluatedDataset",
            "skills:expectsSkillVersion",
            "skills:expectedSkillVersion",
            "skills:observedSkillVersion",
            "skills:evaluatedTask",
            "skills:recordedSelection",
            "skills:hasFailureMode",
            "skills:precisionAt1",
            "skills:recallAtK",
            "skills:meanReciprocalRank",
            "skills:ndcgAtK",
            "skills:graphLiftRecallAtK",
            "skills:p95LatencyMs",
            "skills:citationCoverage",
            "skills:exclusionAccuracy",
            "skills:tokenCostPerSelection",
        ):
            self.assertIn(f"sh:path {required_path}", text)

    def test_split_shacl_profiles_exist_with_expected_focus(self) -> None:
        canonical_text = read(CANONICAL_CORE_SHAPES)
        retrieval_text = read(RETRIEVAL_PROJECTION_SHAPES)
        runtime_text = read(RUNTIME_SELECTION_SHAPES)

        self.assertIn("skills:SkillPackShape a sh:NodeShape", canonical_text)
        self.assertIn("skills:BridgeAssertionShape a sh:NodeShape", canonical_text)
        self.assertIn("skills:SkillDependencyAssertionShape a sh:NodeShape", canonical_text)
        self.assertIn("skills:BridgeConceptLifecycleShape a sh:NodeShape", canonical_text)
        self.assertNotIn("skills:SkillSelectionRunShape a sh:NodeShape", canonical_text)

        self.assertIn("skills:RetrievalUnitShape a sh:NodeShape", retrieval_text)
        self.assertIn("skills:DirectTaskShapeDerivationShape a sh:NodeShape", retrieval_text)
        self.assertIn("sh:path skills:retrievalText", retrieval_text)
        self.assertIn("sh:path skills:priorityWeight", retrieval_text)
        self.assertNotIn("skills:SkillPackShape a sh:NodeShape", retrieval_text)

        self.assertIn("skills:SkillSelectionRunShape a sh:NodeShape", runtime_text)
        self.assertIn("skills:CitationShape a sh:NodeShape", runtime_text)
        self.assertIn("skills:EvaluationRunShape a sh:NodeShape", runtime_text)
        self.assertIn("skills:FailureModeShape a sh:NodeShape", runtime_text)
        self.assertNotIn("skills:RetrievalUnitShape a sh:NodeShape", runtime_text)

    def test_repo_native_ontology_validator_passes(self) -> None:
        result = subprocess.run(
            [sys.executable, str(ONTOLOGY_VALIDATOR)],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0, msg=result.stdout + result.stderr)
        self.assertIn("SHACL PASS", result.stdout)

    def test_repo_native_ontology_validator_supports_named_profile(self) -> None:
        result = subprocess.run(
            [sys.executable, str(ONTOLOGY_VALIDATOR), "--profile", "canonical-core"],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0, msg=result.stdout + result.stderr)
        self.assertIn("canonical-core.shacl.ttl", result.stdout)
        self.assertIn("SHACL PASS", result.stdout)

    def test_repo_native_ontology_validator_supports_all_profiles(self) -> None:
        result = subprocess.run(
            [sys.executable, str(ONTOLOGY_VALIDATOR), "--profile", "all"],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0, msg=result.stdout + result.stderr)
        for profile in (
            "combined",
            "canonical-core",
            "retrieval-projection",
            "runtime-selection",
        ):
            self.assertIn(f"[profile: {profile}]", result.stdout)
        self.assertIn("SHACL PASS", result.stdout)

    def test_repo_native_ontology_validator_reports_missing_file(self) -> None:
        result = subprocess.run(
            [sys.executable, str(ONTOLOGY_VALIDATOR), "missing.ttl"],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(result.returncode, 1, msg=result.stdout + result.stderr)
        self.assertIn("missing file", result.stdout)

    def test_repo_native_ontology_validator_fails_invalid_shapes(self) -> None:
        module = load_validator_module()
        with tempfile.TemporaryDirectory() as tmpdir:
            bad_shapes = Path(tmpdir) / "bad.shacl.ttl"
            bad_shapes.write_text(
                "@prefix skills: <urn:coding-agent-skill-library:ontology:skills#> .\n"
                "@prefix sh: <http://www.w3.org/ns/shacl#> .\n"
                "@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .\n\n"
                "skills:BrokenShape a sh:NodeShape ;\n"
                "    sh:targetNode skills:Ontology ;\n"
                "    sh:property [\n"
                "        sh:path skills:name ;\n"
                "        sh:minCount 1 ;\n"
                "    ] .\n",
                encoding="utf-8",
            )

            result = module.validate_skills_ontology(
                ONTOLOGY_DIR / "skills.ttl",
                bad_shapes,
            )

            self.assertFalse(result.valid)
            self.assertIn("SHACL FAIL", result.report)


if __name__ == "__main__":
    unittest.main()
