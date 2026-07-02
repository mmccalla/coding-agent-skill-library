"""Map SKILL.md sections to governed task intents, constraints and dependencies."""

from __future__ import annotations

import re
from collections.abc import Sequence
from typing import NamedTuple

GOVERNED_TASK_INTENT_IDS: frozenset[str] = frozenset(
    {
        "behaviour-change",
        "debug-with-verification",
        "defect-fix-with-tests",
        "feature-implementation",
        "library-function-creation",
        "plan-before-build",
        "post-artefact-review",
        "refactor-with-tests",
        "spec-before-build",
        "test-harness-bootstrap",
    }
)

GOVERNED_CONSTRAINT_IDS: frozenset[str] = frozenset(
    {
        "requires-deterministic-verification",
        "requires-prior-artefact",
        "requires-test-harness",
    }
)

ALLOWED_DEPENDENCY_TYPES: frozenset[str] = frozenset({"complements", "precedes", "validates"})

TASK_INTENT_PHRASE_RULES: tuple[tuple[str, str], ...] = (
    ("spec-before-build", "clear specification before code or skill edits are made"),
    ("spec-before-build", "specification before code"),
    ("post-artefact-review", "after an initial implementation"),
    ("post-artefact-review", "generated artefact exists"),
    ("post-artefact-review", "quality matters"),
    ("defect-fix-with-tests", "fixing a defect"),
    ("refactor-with-tests", "refactoring risky code"),
    ("behaviour-change", "changing externally visible behaviour"),
    ("feature-implementation", "starting a new feature"),
    ("feature-implementation", "adding behaviour"),
    ("library-function-creation", "creating library functions"),
    ("plan-before-build", "planning"),
    ("debug-with-verification", "debugging"),
    ("test-harness-bootstrap", "executable tests"),
)

CONSTRAINT_PHRASE_RULES: tuple[tuple[str, str], ...] = (
    ("requires-prior-artefact", "before an artefact exists"),
    ("requires-deterministic-verification", "deterministic verification is unnecessary"),
    ("requires-test-harness", "no viable test harness"),
)

DEPENDENCY_TYPE_RULES: tuple[tuple[tuple[str, ...], str], ...] = (
    (("verification first", "executable verification first"), "precedes"),
    (("review after", "after tests pass", "review loop"), "validates"),
    (("repair loop", "when checks fail", "repair"), "complements"),
    (("implement spec", "verifiable slices", "implement"), "precedes"),
    (("acceptance scenarios", "acceptance"), "complements"),
    (("break large specs", "decomposition", "ordered work"), "complements"),
    (("safety gates",), "complements"),
)


class EvidenceCoordinates(NamedTuple):
    """Source-grounded line coordinates for a mapped fragment."""

    line_start: int
    line_end: int


class SectionExcerpt(NamedTuple):
    """A markdown section body with coordinates in the parent document."""

    heading: str
    text: str
    line_start: int
    line_end: int


class TaskIntentMapping(NamedTuple):
    """A governed task intent promoted from `## When to use`."""

    task_intent_id: str
    matched_phrase: str
    evidence: EvidenceCoordinates
    section_heading: str


class ConstraintMapping(NamedTuple):
    """A governed constraint promoted from `## When not to use`."""

    constraint_id: str
    matched_phrase: str
    evidence: EvidenceCoordinates
    section_heading: str


class SkillDependencyMapping(NamedTuple):
    """A typed dependency promoted from `## Related skills`."""

    target_skill_id: str
    dependency_type: str
    rationale: str
    evidence: EvidenceCoordinates
    section_heading: str


class SkillSectionMapping(NamedTuple):
    """Combined semantic mapping for the supported SKILL.md sections."""

    task_intents: tuple[TaskIntentMapping, ...]
    constraints: tuple[ConstraintMapping, ...]
    dependencies: tuple[SkillDependencyMapping, ...]


def _line_number_at(text: str, index: int) -> int:
    return text.count("\n", 0, index) + 1


def _evidence_for_phrase(text: str, phrase: str, *, base_line: int) -> EvidenceCoordinates:
    lowered_text = text.lower()
    lowered_phrase = phrase.lower()
    start = lowered_text.find(lowered_phrase)
    if start == -1:
        return EvidenceCoordinates(line_start=base_line, line_end=base_line)
    line_offset = base_line - 1
    line_start = _line_number_at(text, start) + line_offset
    line_end = _line_number_at(text, start + len(phrase) - 1) + line_offset
    return EvidenceCoordinates(line_start=line_start, line_end=line_end)


def extract_section(markdown: str, heading: str) -> SectionExcerpt | None:
    """Return a level-2 section body and its coordinates."""

    pattern = re.compile(
        rf"^## {re.escape(heading)}\s*\n(.*?)(?=^## |\Z)",
        flags=re.MULTILINE | re.DOTALL,
    )
    match = pattern.search(markdown)
    if not match:
        return None

    body = match.group(1).strip()
    section_start = match.start(1)
    while section_start < len(markdown) and markdown[section_start] in {"\n", "\r"}:
        section_start += 1
    section_end = match.end(1)
    while section_end > section_start and markdown[section_end - 1] in {"\n", "\r"}:
        section_end -= 1

    line_start = _line_number_at(markdown, section_start if body else match.start())
    line_end = _line_number_at(markdown, max(section_start, section_end - 1))
    return SectionExcerpt(
        heading=heading,
        text=body,
        line_start=line_start,
        line_end=line_end if body else line_start,
    )


def _map_phrase_rules(
    section: SectionExcerpt,
    rules: Sequence[tuple[str, str]],
    *,
    governed_ids: frozenset[str],
    section_heading: str,
) -> tuple[tuple[str, str, EvidenceCoordinates, str], ...]:
    lowered_text = section.text.lower()
    mappings: list[tuple[str, str, EvidenceCoordinates, str]] = []
    seen_ids: set[str] = set()

    for concept_id, phrase in rules:
        if concept_id not in governed_ids or concept_id in seen_ids:
            continue
        if phrase.lower() not in lowered_text:
            continue
        evidence = _evidence_for_phrase(section.text, phrase, base_line=section.line_start)
        mappings.append((concept_id, phrase, evidence, section_heading))
        seen_ids.add(concept_id)

    return tuple(mappings)


def map_when_to_use_task_intents(markdown: str) -> tuple[TaskIntentMapping, ...]:
    """Map `## When to use` prose to governed task intent ids."""

    section = extract_section(markdown, "When to use")
    if not section or not section.text:
        return ()

    raw_mappings = _map_phrase_rules(
        section,
        TASK_INTENT_PHRASE_RULES,
        governed_ids=GOVERNED_TASK_INTENT_IDS,
        section_heading=section.heading,
    )
    return tuple(
        TaskIntentMapping(
            task_intent_id=task_intent_id,
            matched_phrase=matched_phrase,
            evidence=evidence,
            section_heading=section_heading,
        )
        for task_intent_id, matched_phrase, evidence, section_heading in raw_mappings
    )


def map_when_not_to_use_constraints(markdown: str) -> tuple[ConstraintMapping, ...]:
    """Map `## When not to use` prose to governed constraint ids."""

    section = extract_section(markdown, "When not to use")
    if not section or not section.text:
        return ()

    raw_mappings = _map_phrase_rules(
        section,
        CONSTRAINT_PHRASE_RULES,
        governed_ids=GOVERNED_CONSTRAINT_IDS,
        section_heading=section.heading,
    )
    return tuple(
        ConstraintMapping(
            constraint_id=constraint_id,
            matched_phrase=matched_phrase,
            evidence=evidence,
            section_heading=section_heading,
        )
        for constraint_id, matched_phrase, evidence, section_heading in raw_mappings
    )


def _infer_dependency_type(rationale: str) -> str:
    lowered = rationale.lower()
    for phrases, dependency_type in DEPENDENCY_TYPE_RULES:
        if any(phrase in lowered for phrase in phrases):
            return dependency_type
    return "complements"


def map_related_skill_dependencies(
    markdown: str,
    *,
    known_skill_ids: set[str] | None = None,
) -> tuple[SkillDependencyMapping, ...]:
    """Parse `## Related skills` bullets into typed dependency assertions."""

    section = extract_section(markdown, "Related skills")
    if not section or not section.text:
        return ()

    dependencies: list[SkillDependencyMapping] = []
    for match in re.finditer(
        r"^-\s+`([-a-z0-9]+)`\s+[—-]\s+(.+?)\s*$",
        section.text,
        flags=re.MULTILINE,
    ):
        target_skill_id = match.group(1)
        if known_skill_ids is not None and target_skill_id not in known_skill_ids:
            continue

        rationale = match.group(2).strip()
        absolute_start = section.line_start + section.text[: match.start()].count("\n")
        absolute_end = section.line_start + section.text[: match.end()].count("\n")
        dependency_type = _infer_dependency_type(rationale)
        if dependency_type not in ALLOWED_DEPENDENCY_TYPES:
            dependency_type = "complements"

        dependencies.append(
            SkillDependencyMapping(
                target_skill_id=target_skill_id,
                dependency_type=dependency_type,
                rationale=rationale,
                evidence=EvidenceCoordinates(
                    line_start=absolute_start,
                    line_end=absolute_end,
                ),
                section_heading=section.heading,
            )
        )

    return tuple(dependencies)


def map_skill_sections(
    markdown: str,
    *,
    known_skill_ids: set[str] | None = None,
) -> SkillSectionMapping:
    """Map supported SKILL.md sections to governed semantic assertions."""

    return SkillSectionMapping(
        task_intents=map_when_to_use_task_intents(markdown),
        constraints=map_when_not_to_use_constraints(markdown),
        dependencies=map_related_skill_dependencies(markdown, known_skill_ids=known_skill_ids),
    )
