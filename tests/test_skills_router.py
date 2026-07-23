"""Tests for deterministic Skills KG routing helpers."""

from __future__ import annotations

import unittest

from scripts.graph.build import embed_skill_chunks
from scripts.lib.config import skills_config
from scripts.lib.retrieval import retrieve_skills_hybrid
from scripts.lib.routing import skills_router


class SkillsRouterCanonicalIdTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.plan = retrieve_skills_hybrid.fixture_load_plan()
        settings = skills_config.load_settings()
        embedder = embed_skill_chunks.resolve_embedding_provider(
            settings,
            force_deterministic=True,
        )
        cls.full_plan = embed_skill_chunks.build_embedded_repository_load_plan(embedder=embedder)

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

    def test_resolve_skill_keeps_exact_incident_response_alias(self) -> None:
        response = skills_router.resolve_skill(self.full_plan, "incident response")

        self.assertEqual("ok", response["status"])
        self.assertEqual("skill:incident-response-and-postmortems", response["skill_id"])
        self.assertEqual("exact", response["match_type"])

    def test_route_skill_query_does_not_embed_incident_alias_in_sre_task(self) -> None:
        """Long SRE-shaped queries must not become direct_lookup via a short alias phrase."""
        query = (
            "production reliability service ownership resilience toil reduction incident response"
        )
        resolved = skills_router.resolve_skill(self.full_plan, query)
        routed = skills_router.route_skill_query(self.full_plan, query)

        self.assertEqual("error", resolved["status"])
        self.assertEqual("recommendation", routed["route"])
        self.assertIsNone(routed["resolved_skill_id"])


if __name__ == "__main__":
    unittest.main()
