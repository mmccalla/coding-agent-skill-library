"""Tests for governed vocabulary instance graphs."""

from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path

from rdflib import Graph, Namespace
from rdflib.namespace import RDF, SKOS

REPO_ROOT = Path(__file__).resolve().parents[1]
INSTANCES_DIR = REPO_ROOT / "skills_docs" / "ontology" / "instances"
TASK_INTENTS = INSTANCES_DIR / "task-intents.ttl"
WORKFLOW_STAGES = INSTANCES_DIR / "workflow-stages.ttl"
ONTOLOGY_VALIDATOR = REPO_ROOT / "scripts/validators/validate_skills_ontology.py"
MAPPING_MODULE = REPO_ROOT / "scripts/lib/routing/skill_section_mapping.py"

SKILLS = Namespace("urn:coding-agent-skill-library:ontology:skills#")


def _load_graph(path: Path) -> Graph:
    graph = Graph()
    graph.parse(data=path.read_text(encoding="utf-8"), format="turtle")
    return graph


def _load_mapping_intent_ids() -> set[str]:
    spec = importlib.util.spec_from_file_location("skill_section_mapping", MAPPING_MODULE)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return set(module.GOVERNED_TASK_INTENT_IDS)


def _load_validator_module():
    spec = importlib.util.spec_from_file_location("validate_skills_ontology", ONTOLOGY_VALIDATOR)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class GovernedVocabularyTests(unittest.TestCase):
    def setUp(self) -> None:
        self.task_graph = _load_graph(TASK_INTENTS)
        self.stage_graph = _load_graph(WORKFLOW_STAGES)

    def test_task_intent_concepts_have_required_fields(self) -> None:
        subjects = list(self.task_graph.subjects(RDF.type, SKILLS.TaskShape))
        self.assertGreaterEqual(len(subjects), 15)
        for subject in subjects:
            self.assertTrue(
                list(self.task_graph.objects(subject, SKOS.prefLabel)),
                f"{subject} missing skos:prefLabel",
            )
            self.assertTrue(
                list(self.task_graph.objects(subject, SKOS.definition)),
                f"{subject} missing skos:definition",
            )
            schemes = list(self.task_graph.objects(subject, SKOS.inScheme))
            self.assertEqual(schemes, [SKILLS.TaskShapeScheme])

    def test_task_intent_pref_labels_unique_within_scheme(self) -> None:
        labels: list[str] = []
        for subject in self.task_graph.subjects(RDF.type, SKILLS.TaskShape):
            for label in self.task_graph.objects(subject, SKOS.prefLabel):
                labels.append(str(label))
        self.assertEqual(len(labels), len(set(labels)))

    def test_near_neighbour_task_intents_exist(self) -> None:
        slugs = {
            str(node).rsplit("task-intent-", 1)[-1]
            for node in self.task_graph.subjects(RDF.type, SKILLS.TaskShape)
        }
        for required in (
            "defect-fix-with-tests",
            "post-artefact-review",
            "spec-before-build",
            "code-review",
        ):
            self.assertIn(required, slugs)

    def test_mapping_task_intent_ids_have_ttl_instances(self) -> None:
        slugs = {
            str(node).rsplit("task-intent-", 1)[-1]
            for node in self.task_graph.subjects(RDF.type, SKILLS.TaskShape)
        }
        for intent_id in _load_mapping_intent_ids():
            self.assertIn(intent_id, slugs, f"missing TTL instance for {intent_id}")

    def test_workflow_stages_have_required_fields(self) -> None:
        subjects = list(self.stage_graph.subjects(RDF.type, SKILLS.WorkflowStage))
        self.assertEqual(len(subjects), 7)
        for subject in subjects:
            self.assertTrue(list(self.stage_graph.objects(subject, SKOS.prefLabel)))
            self.assertTrue(list(self.stage_graph.objects(subject, SKOS.definition)))
            self.assertEqual(
                list(self.stage_graph.objects(subject, SKOS.inScheme)),
                [SKILLS.WorkflowStageScheme],
            )

    def test_instance_graphs_pass_shacl_with_ontology(self) -> None:
        validator = _load_validator_module()
        result = validator.validate_skills_ontology(include_instances=True)
        self.assertTrue(result.valid, result.report)


if __name__ == "__main__":
    unittest.main()
