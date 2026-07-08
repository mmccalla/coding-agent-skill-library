"""Tests for deterministic Skills KG routing helpers."""

from __future__ import annotations

import unittest

from scripts.lib.retrieval import retrieve_skills_hybrid
from scripts.lib.routing import skills_router


class SkillsRouterCanonicalIdTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.plan = retrieve_skills_hybrid.fixture_load_plan()

    def test_canonical_skill_id_accepts_prefixed_id(self) -> None:
        self.assertEqual(
            "skill:knowledge-graph-rag",
            skills_router.canonical_skill_id(self.plan, "skill:knowledge-graph-rag"),
        )

    def test_canonical_skill_id_accepts_bare_slug(self) -> None:
        self.assertEqual(
            "skill:knowledge-graph-rag",
            skills_router.canonical_skill_id(self.plan, "knowledge-graph-rag"),
        )

    def test_canonical_skill_id_rejects_aliases(self) -> None:
        self.assertIsNone(skills_router.canonical_skill_id(self.plan, "kg-enabled-rag"))

    def test_canonical_skill_id_rejects_unknown_skill(self) -> None:
        self.assertIsNone(skills_router.canonical_skill_id(self.plan, "not-a-real-skill"))

    def test_get_skill_execution_guide_accepts_bare_slug(self) -> None:
        response = skills_router.get_skill_execution_guide(self.plan, "knowledge-graph-rag")

        self.assertEqual("ok", response["status"])
        self.assertEqual("skill:knowledge-graph-rag", response["skill_id"])
        self.assertTrue(response["procedure"])


if __name__ == "__main__":
    unittest.main()
