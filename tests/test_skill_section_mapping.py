"""Tests for deterministic SKILL.md section → semantic mapping."""

from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
MAPPER = REPO_ROOT / "scripts" / "skill_section_mapping.py"
FIXTURES = REPO_ROOT / "tests" / "fixtures" / "skill_mapping"


def load_mapper_module():
    spec = importlib.util.spec_from_file_location("skill_section_mapping", MAPPER)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def read_fixture(name: str) -> str:
    return (FIXTURES / name).read_text(encoding="utf-8")


class SkillSectionMappingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.module = load_mapper_module()

    def test_governed_task_intent_slugs_include_phase_vocabulary(self) -> None:
        governed = self.module.GOVERNED_TASK_INTENT_IDS
        for slug in (
            "defect-fix-with-tests",
            "post-artefact-review",
            "spec-before-build",
            "feature-implementation",
            "refactor-with-tests",
            "behaviour-change",
        ):
            self.assertIn(slug, governed)

    def test_tdd_when_to_use_maps_task_intents_with_evidence(self) -> None:
        markdown = read_fixture("tdd-practice-excerpt.md")
        mappings = self.module.map_when_to_use_task_intents(markdown)

        by_intent = {mapping.task_intent_id: mapping for mapping in mappings}
        self.assertIn("feature-implementation", by_intent)
        self.assertIn("defect-fix-with-tests", by_intent)
        self.assertIn("refactor-with-tests", by_intent)

        feature = by_intent["feature-implementation"]
        self.assertEqual(feature.matched_phrase, "adding behaviour")
        self.assertEqual(feature.evidence.line_start, 5)
        self.assertEqual(feature.evidence.line_end, 5)
        self.assertEqual(feature.section_heading, "When to use")

        defect = by_intent["defect-fix-with-tests"]
        self.assertEqual(defect.matched_phrase, "fixing a defect")
        self.assertEqual(defect.evidence.line_start, 5)
        self.assertEqual(defect.evidence.line_end, 5)

    def test_reflection_when_to_use_maps_post_artefact_review(self) -> None:
        markdown = read_fixture("reflection-and-verification-excerpt.md")
        mappings = self.module.map_when_to_use_task_intents(markdown)

        by_intent = {mapping.task_intent_id: mapping for mapping in mappings}
        self.assertIn("post-artefact-review", by_intent)

        review = by_intent["post-artefact-review"]
        self.assertEqual(review.matched_phrase, "after an initial implementation")
        self.assertEqual(review.evidence.line_start, 5)
        self.assertEqual(review.evidence.line_end, 5)

    def test_spec_when_to_use_maps_spec_before_build_and_feature(self) -> None:
        markdown = read_fixture("spec-driven-development-excerpt.md")
        mappings = self.module.map_when_to_use_task_intents(markdown)

        by_intent = {mapping.task_intent_id: mapping for mapping in mappings}
        self.assertIn("spec-before-build", by_intent)
        self.assertIn("feature-implementation", by_intent)
        self.assertIn("behaviour-change", by_intent)

        spec = by_intent["spec-before-build"]
        self.assertIn("specification before code", spec.matched_phrase)
        # Fixture has a blank line after "## When to use" (markdownlint MD022).
        self.assertEqual(spec.evidence.line_start, 5)
        self.assertEqual(spec.evidence.line_end, 5)

    def test_when_not_to_use_maps_constraints_with_evidence(self) -> None:
        markdown = (
            "# Sample\n\n"
            "## When not to use\n\n"
            "Do not use this skill before an artefact exists or when deterministic "
            "verification is unnecessary.\n"
        )
        mappings = self.module.map_when_not_to_use_constraints(markdown)

        by_constraint = {mapping.constraint_id: mapping for mapping in mappings}
        self.assertIn("requires-prior-artefact", by_constraint)
        self.assertIn("requires-deterministic-verification", by_constraint)

        artefact = by_constraint["requires-prior-artefact"]
        self.assertEqual(artefact.matched_phrase, "before an artefact exists")
        self.assertEqual(artefact.evidence.line_start, 5)
        self.assertEqual(artefact.evidence.line_end, 5)
        self.assertEqual(artefact.section_heading, "When not to use")

    def test_when_not_to_use_missing_returns_empty_tuple(self) -> None:
        markdown = read_fixture("tdd-practice-excerpt.md")
        self.assertEqual(self.module.map_when_not_to_use_constraints(markdown), ())

    def test_related_skills_parse_typed_dependencies_with_evidence(self) -> None:
        markdown = read_fixture("tdd-practice-excerpt.md")
        known_skills = {
            "code-review-and-quality",
            "reflection-and-verification",
            "bdd-practice",
        }
        dependencies = self.module.map_related_skill_dependencies(
            markdown,
            known_skill_ids=known_skills,
        )

        by_target = {dependency.target_skill_id: dependency for dependency in dependencies}
        self.assertEqual(
            set(by_target),
            {"code-review-and-quality", "reflection-and-verification", "bdd-practice"},
        )

        review = by_target["code-review-and-quality"]
        self.assertEqual(review.dependency_type, "validates")
        self.assertEqual(review.rationale, "review after tests pass")
        self.assertEqual(review.evidence.line_start, 9)
        self.assertEqual(review.evidence.line_end, 9)

        reflection = by_target["reflection-and-verification"]
        self.assertEqual(reflection.dependency_type, "complements")
        self.assertEqual(reflection.rationale, "repair loop when checks fail")
        self.assertEqual(reflection.evidence.line_start, 10)
        self.assertEqual(reflection.evidence.line_end, 10)

    def test_reflection_related_skills_infer_precedes_for_verification_first(self) -> None:
        markdown = read_fixture("reflection-and-verification-excerpt.md")
        dependencies = self.module.map_related_skill_dependencies(
            markdown,
            known_skill_ids={
                "tdd-practice",
                "code-review-and-quality",
                "apply-laws-of-ai",
            },
        )

        by_target = {dependency.target_skill_id: dependency for dependency in dependencies}
        self.assertEqual(by_target["tdd-practice"].dependency_type, "precedes")
        self.assertEqual(by_target["code-review-and-quality"].dependency_type, "validates")

    def test_spec_related_skills_infer_precedes_for_implementation_slices(self) -> None:
        markdown = read_fixture("spec-driven-development-excerpt.md")
        dependencies = self.module.map_related_skill_dependencies(
            markdown,
            known_skill_ids={
                "bdd-practice",
                "incremental-implementation",
                "planning-and-task-decomposition",
            },
        )

        by_target = {dependency.target_skill_id: dependency for dependency in dependencies}
        self.assertEqual(by_target["incremental-implementation"].dependency_type, "precedes")
        self.assertEqual(by_target["bdd-practice"].dependency_type, "complements")

    def test_related_skills_ignore_unknown_targets(self) -> None:
        markdown = read_fixture("tdd-practice-excerpt.md")
        dependencies = self.module.map_related_skill_dependencies(
            markdown,
            known_skill_ids={"code-review-and-quality"},
        )
        self.assertEqual(len(dependencies), 1)
        self.assertEqual(dependencies[0].target_skill_id, "code-review-and-quality")

    def test_related_skills_parse_table_rows_with_optional_header(self) -> None:
        markdown = (
            "# Sample\n\n"
            "## Related skills\n\n"
            "| Skill | Type | Rationale |\n"
            "| --- | --- | --- |\n"
            "| `incremental-implementation` | precedes | implement spec in verifiable slices |\n"
            "| `bdd-practice` | complements | acceptance scenarios for external behaviour |\n"
        )
        dependencies = self.module.map_related_skill_dependencies(
            markdown,
            known_skill_ids={"incremental-implementation", "bdd-practice"},
        )

        by_target = {dependency.target_skill_id: dependency for dependency in dependencies}
        self.assertEqual(
            set(by_target),
            {"incremental-implementation", "bdd-practice"},
        )
        self.assertEqual(by_target["incremental-implementation"].dependency_type, "precedes")
        self.assertEqual(by_target["bdd-practice"].dependency_type, "complements")
        self.assertEqual(
            by_target["incremental-implementation"].rationale,
            "implement spec in verifiable slices",
        )
        self.assertEqual(by_target["incremental-implementation"].evidence.line_start, 7)
        self.assertEqual(by_target["bdd-practice"].evidence.line_start, 8)

    def test_related_skills_parse_table_rows_without_header(self) -> None:
        markdown = (
            "# Sample\n\n"
            "## Related skills\n\n"
            "| `code-review-and-quality` | validates | review after tests pass |\n"
        )
        dependencies = self.module.map_related_skill_dependencies(
            markdown,
            known_skill_ids={"code-review-and-quality"},
        )

        self.assertEqual(len(dependencies), 1)
        dependency = dependencies[0]
        self.assertEqual(dependency.target_skill_id, "code-review-and-quality")
        self.assertEqual(dependency.dependency_type, "validates")
        self.assertEqual(dependency.rationale, "review after tests pass")
        self.assertEqual(dependency.evidence.line_start, 5)

    def test_related_skills_bullets_take_precedence_over_table_rows(self) -> None:
        markdown = (
            "# Sample\n\n"
            "## Related skills\n\n"
            "- `code-review-and-quality` — review after tests pass\n"
            "| `code-review-and-quality` | precedes | conflicting table row |\n"
        )
        dependencies = self.module.map_related_skill_dependencies(
            markdown,
            known_skill_ids={"code-review-and-quality"},
        )

        self.assertEqual(len(dependencies), 1)
        self.assertEqual(dependencies[0].dependency_type, "validates")

    def test_map_skill_sections_composes_all_section_mappers(self) -> None:
        markdown = read_fixture("tdd-practice-excerpt.md")
        result = self.module.map_skill_sections(
            markdown,
            known_skill_ids={
                "code-review-and-quality",
                "reflection-and-verification",
                "bdd-practice",
            },
        )

        self.assertGreater(len(result.task_intents), 0)
        self.assertGreater(len(result.dependencies), 0)
        self.assertEqual(result.constraints, ())
        self.assertTrue(
            all(
                mapping.task_intent_id in self.module.GOVERNED_TASK_INTENT_IDS
                for mapping in result.task_intents
            )
        )

    def test_only_governed_task_intent_ids_are_emitted(self) -> None:
        markdown = (
            "# Sample\n\n## When to use\n\nUse when deploying to production with canary releases.\n"
        )
        mappings = self.module.map_when_to_use_task_intents(markdown)
        self.assertEqual(mappings, ())


if __name__ == "__main__":
    unittest.main()
