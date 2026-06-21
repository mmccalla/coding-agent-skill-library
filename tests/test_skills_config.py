"""Tests for typed Skills KG configuration."""

from __future__ import annotations

import unittest
from pathlib import Path

from scripts.skills_config import load_settings


class SkillsConfigTests(unittest.TestCase):
    def test_loads_yaml_defaults_and_shared_limits(self) -> None:
        settings = load_settings(Path("configs/skills_kg.yaml"), environ={})

        self.assertEqual(1536, settings.neo4j.embedding_dimensions)
        self.assertEqual("deterministic-test-embedding", settings.neo4j.embedding_provider)
        self.assertEqual("skill_chunk_embedding_vector", settings.neo4j.vector_index)
        self.assertEqual(10, settings.mcp.recommend_limit_max)
        self.assertEqual(1200, settings.retrieval.default_token_budget)

    def test_environment_overrides_connection_without_leaking_password(self) -> None:
        settings = load_settings(
            Path("configs/skills_kg.yaml"),
            environ={
                "NEO4J_URI": "bolt://localhost:7687",
                "NEO4J_USER": "neo4j",
                "NEO4J_PASSWORD": "super-secret",
                "NEO4J_DATABASE": "skills",
            },
        )

        self.assertEqual("bolt://localhost:7687", settings.neo4j.uri)
        self.assertEqual("neo4j", settings.neo4j.user)
        self.assertEqual("super-secret", settings.neo4j.password)
        self.assertEqual("skills", settings.neo4j.database)
        self.assertNotIn("super-secret", repr(settings))
        self.assertNotIn("super-secret", str(settings.model_dump()))


if __name__ == "__main__":
    unittest.main()
