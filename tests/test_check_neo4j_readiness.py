"""Tests for live Neo4j readiness checks."""

from __future__ import annotations

import unittest

from scripts.check_neo4j_readiness import collect_readiness
from scripts.skills_config import Neo4jSettings


class FakeSession:
    def __init__(self, indexes: tuple[dict[str, object], ...]) -> None:
        self.indexes = indexes

    def __enter__(self) -> FakeSession:
        return self

    def __exit__(self, *_args: object) -> None:
        return None

    def run(self, query: str, **_parameters: object) -> tuple[dict[str, object], ...]:
        if query.startswith("SHOW CONSTRAINTS"):
            return (
                {"name": "skill_id_unique"},
                {"name": "skill_name_unique"},
                {"name": "skill_section_id_unique"},
                {"name": "skill_chunk_id_unique"},
                {"name": "skill_category_id_unique"},
                {"name": "task_shape_id_unique"},
                {"name": "workflow_stage_id_unique"},
                {"name": "capability_id_unique"},
                {"name": "control_theme_id_unique"},
                {"name": "knowledge_domain_id_unique"},
                {"name": "bridge_assertion_id_unique"},
                {"name": "source_id_unique"},
                {"name": "reference_document_id_unique"},
                {"name": "validation_rule_id_unique"},
            )
        if query.startswith("SHOW INDEXES"):
            return self.indexes
        if "db.index.vector.queryNodes" in query:
            return ({"chunk_id": "chunk-1", "score": 0.9},)
        raise AssertionError(f"Unexpected query: {query}")


class FakeDriver:
    def __init__(self, indexes: tuple[dict[str, object], ...]) -> None:
        self.indexes = indexes
        self.database = ""

    def session(self, *, database: str) -> FakeSession:
        self.database = database
        return FakeSession(self.indexes)


class Neo4jReadinessTests(unittest.TestCase):
    def test_readiness_passes_when_schema_indexes_and_vector_query_are_available(self) -> None:
        driver = FakeDriver(
            (
                {"name": "skill_category_lookup", "state": "ONLINE", "type": "RANGE"},
                {"name": "skill_path_lookup", "state": "ONLINE", "type": "RANGE"},
                {"name": "bridge_assertion_source_lookup", "state": "ONLINE", "type": "RANGE"},
                {"name": "skill_chunk_source_lookup", "state": "ONLINE", "type": "RANGE"},
                {"name": "skill_metadata_fulltext", "state": "ONLINE", "type": "FULLTEXT"},
                {"name": "skill_chunk_text_fulltext", "state": "ONLINE", "type": "FULLTEXT"},
                {"name": "skill_chunk_embedding_vector", "state": "ONLINE", "type": "VECTOR"},
            )
        )

        report = collect_readiness(driver, Neo4jSettings(database="skills", embedding_dimensions=3))

        self.assertTrue(report.ready)
        self.assertEqual("skills", driver.database)
        self.assertTrue(report.vector_query_ok)
        self.assertEqual((), report.errors)

    def test_readiness_fails_when_vector_index_is_missing(self) -> None:
        driver = FakeDriver(
            (
                {"name": "skill_category_lookup", "state": "ONLINE", "type": "RANGE"},
                {"name": "skill_path_lookup", "state": "ONLINE", "type": "RANGE"},
                {"name": "bridge_assertion_source_lookup", "state": "ONLINE", "type": "RANGE"},
                {"name": "skill_chunk_source_lookup", "state": "ONLINE", "type": "RANGE"},
                {"name": "skill_metadata_fulltext", "state": "ONLINE", "type": "FULLTEXT"},
                {"name": "skill_chunk_text_fulltext", "state": "ONLINE", "type": "FULLTEXT"},
            )
        )

        report = collect_readiness(driver, Neo4jSettings(database="skills", embedding_dimensions=3))

        self.assertFalse(report.ready)
        self.assertIn("missing index: skill_chunk_embedding_vector", report.errors)


if __name__ == "__main__":
    unittest.main()
