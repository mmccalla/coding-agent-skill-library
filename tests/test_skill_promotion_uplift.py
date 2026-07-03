"""Tests for Phase 2b promotion uplift."""

from __future__ import annotations

import importlib.util
import json
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
MAPPER = REPO_ROOT / "scripts" / "skill_section_mapping.py"
EXTRACTOR = REPO_ROOT / "scripts" / "extract_skills_graph.py"
GOLDEN = REPO_ROOT / "tests" / "fixtures" / "retrieval_evaluation" / "golden_queries.json"

MIN_PROMOTED_SKILLS = 30
MIN_GOLDEN_PROMOTED_CASES = 150


def load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class SkillPromotionUpliftTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.mapper = load_module(MAPPER, "skill_section_mapping")
        cls.extractor = load_module(EXTRACTOR, "extract_skills_graph")

    def test_krag_system_design_maps_via_description_or_registry(self) -> None:
        text = (REPO_ROOT / "skills" / "krag-system-design" / "SKILL.md").read_text(
            encoding="utf-8"
        )
        mapping = self.mapper.map_skill_sections(text, skill_name="krag-system-design")
        ready = self.mapper.promotion_ready_task_intents(mapping.task_intents)
        intent_ids = {intent.task_intent_id for intent in ready}
        self.assertIn("krag-architecture", intent_ids)

    def test_apply_laws_maps_session_baseline(self) -> None:
        text = (REPO_ROOT / "skills" / "apply-laws-of-ai" / "SKILL.md").read_text(encoding="utf-8")
        mapping = self.mapper.map_skill_sections(text, skill_name="apply-laws-of-ai")
        ready = self.mapper.promotion_ready_task_intents(mapping.task_intents)
        self.assertTrue(any(intent.task_intent_id == "session-baseline" for intent in ready))

    def test_library_meets_promoted_skill_count_gate(self) -> None:
        records = self.extractor.extract_skills_graph_records(REPO_ROOT / "skills")
        promoted = [skill for skill in records["skills"] if skill["promotion_status"] == "promoted"]
        self.assertGreaterEqual(len(promoted), MIN_PROMOTED_SKILLS, promoted)

    def test_golden_queries_hit_promoted_skills_gate(self) -> None:
        records = self.extractor.extract_skills_graph_records(REPO_ROOT / "skills")
        promoted_ids = {
            skill["id"] for skill in records["skills"] if skill["promotion_status"] == "promoted"
        }
        cases = json.loads(GOLDEN.read_text(encoding="utf-8"))
        hits = 0
        for case in cases:
            expected = set(case.get("expected_skill_ids", []) + case.get("required_skill_ids", []))
            if expected & promoted_ids:
                hits += 1
        self.assertGreaterEqual(hits, MIN_GOLDEN_PROMOTED_CASES)


if __name__ == "__main__":
    unittest.main()
