"""Tests for Neo4j skills graph schema scripts."""

from __future__ import annotations

import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SCHEMA = REPO_ROOT / "neo4j" / "skills_schema.cypher"
CONFIG = REPO_ROOT / "configs" / "skills_kg.yaml"


class Neo4jSchemaTests(unittest.TestCase):
    def test_schema_defines_required_uniqueness_constraints(self) -> None:
        text = SCHEMA.read_text(encoding="utf-8")

        for label, property_name in (
            ("Skill", "id"),
            ("Skill", "name"),
            ("SkillSection", "id"),
            ("SkillChunk", "id"),
            ("SkillCategory", "id"),
            ("TaskShape", "id"),
            ("WorkflowStage", "id"),
            ("Capability", "id"),
            ("ControlTheme", "id"),
            ("KnowledgeDomain", "id"),
            ("BridgeAssertion", "id"),
            ("Source", "id"),
            ("ReferenceDocument", "id"),
            ("ValidationRule", "id"),
        ):
            self.assertIn(f"FOR (n:{label}) REQUIRE n.{property_name} IS UNIQUE", text)

    def test_schema_defines_lookup_and_range_indexes(self) -> None:
        text = SCHEMA.read_text(encoding="utf-8")

        for index_name, label, property_name in (
            ("skill_category_lookup", "Skill", "category"),
            ("skill_path_lookup", "Skill", "path"),
            ("bridge_assertion_source_lookup", "BridgeAssertion", "source"),
            ("skill_chunk_source_lookup", "SkillChunk", "source_path"),
        ):
            self.assertIn(f"CREATE INDEX {index_name} IF NOT EXISTS", text)
            self.assertIn(f"FOR (n:{label}) ON (n.{property_name})", text)

    def test_schema_defines_fulltext_indexes(self) -> None:
        text = SCHEMA.read_text(encoding="utf-8")

        self.assertIn("skill_metadata_fulltext", text)
        self.assertIn("Skill", text)
        self.assertIn("title", text)
        self.assertIn("description", text)
        self.assertIn("skill_chunk_text_fulltext", text)
        self.assertIn("SkillChunk", text)
        self.assertIn("text", text)

    def test_schema_defines_vector_index_for_chunk_embeddings(self) -> None:
        text = SCHEMA.read_text(encoding="utf-8")
        config_text = CONFIG.read_text(encoding="utf-8")

        self.assertIn("skill_chunk_embedding_vector", text)
        self.assertIn("FOR (n:SkillChunk) ON (n.embedding)", text)
        self.assertIn("vector.dimensions", text)
        self.assertIn("$embedding_dimensions", text)
        self.assertIn("embedding_dimensions: 1536", config_text)
        self.assertIn(":param embedding_dimensions => 1536;", text)
        self.assertIn("vector.similarity_function", text)
        self.assertIn("vector_similarity_function: cosine", config_text)
        self.assertIn("cosine", text)

    def test_schema_is_idempotent_where_supported(self) -> None:
        text = SCHEMA.read_text(encoding="utf-8")

        for statement in text.split(";"):
            stripped = statement.strip()
            if stripped.startswith("CREATE "):
                self.assertIn("IF NOT EXISTS", stripped)


if __name__ == "__main__":
    unittest.main()
