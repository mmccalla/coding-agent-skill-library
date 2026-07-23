"""Map SKILL.md sections to governed task intents, constraints and dependencies."""

from __future__ import annotations

import re
from collections.abc import Sequence
from typing import NamedTuple

GOVERNED_TASK_INTENT_IDS: frozenset[str] = frozenset(
    {
        "accessibility-audit",
        "behaviour-change",
        "ci-pipeline-change",
        "code-review",
        "debug-with-verification",
        "defect-fix-with-tests",
        "feature-implementation",
        "git-workflow",
        "krag-architecture",
        "library-function-creation",
        "mcp-server-design",
        "plan-before-build",
        "post-artefact-review",
        "refactor-with-tests",
        "security-hardening",
        "safety-law-hierarchy",
        "spec-before-build",
        "test-harness-bootstrap",
    }
)

PROMOTION_READY_SOURCES: frozenset[str] = frozenset(
    {"when_to_use", "description", "skill_registry"}
)

# Curated primary intents for high-traffic eval and agent skills (Phase 2b registry).
SKILL_PRIMARY_INTENTS: dict[str, str] = {
    "apply-laws-of-ai": "safety-law-hierarchy",
    "cognitive-bias-review": "post-artefact-review",
    "logical-fallacy-review": "post-artefact-review",
    "knowledge-graph-rag": "krag-architecture",
    "krag-system-design": "krag-architecture",
    "krag-ingestion-graph-construction": "krag-architecture",
    "krag-retrieval-answering": "krag-architecture",
    "krag-evaluation-governance": "post-artefact-review",
    "knowledge-retrieval-rag": "krag-architecture",
    "human-in-the-loop": "security-hardening",
    "accessibility-wcag": "accessibility-audit",
    "guardrails-safety-patterns": "security-hardening",
    "evaluation-and-monitoring": "post-artefact-review",
    "exception-handling-and-recovery": "debug-with-verification",
    "goal-setting-and-monitoring": "plan-before-build",
    "inter-agent-communication-a2a": "feature-implementation",
    "mcp-server-design": "mcp-server-design",
    "prioritization": "plan-before-build",
    "reasoning-techniques": "debug-with-verification",
    "resource-aware-optimization": "feature-implementation",
    "context-engineering": "feature-implementation",
    "idea-refinement": "spec-before-build",
    "incremental-implementation": "feature-implementation",
    "learning-and-adaptation": "feature-implementation",
    "memory-management": "feature-implementation",
    "multi-agent-collaboration": "feature-implementation",
    "prompt-chaining": "feature-implementation",
    "requirements-elicitation": "spec-before-build",
    "routing": "feature-implementation",
    "skill-discovery-and-selection": "plan-before-build",
    "source-driven-development": "spec-before-build",
    "tool-use-and-function-calling": "feature-implementation",
    "uncertainty-driven-development": "plan-before-build",
    "lakehouse-and-medallion-architecture": "feature-implementation",
    "event-streaming-platform-design": "feature-implementation",
    "stream-processing-patterns": "feature-implementation",
    "streaming-operations-and-slos": "feature-implementation",
    "event-driven-architecture": "feature-implementation",
    "ci-cd-and-automation": "ci-pipeline-change",
    "code-review-and-quality": "code-review",
    "browser-testing-with-devtools": "debug-with-verification",
    "business-capability-modeling": "plan-before-build",
    "business-information-concept-modeling": "plan-before-build",
    "capability-maturity-assessment": "post-artefact-review",
    "operating-model-design": "plan-before-build",
    "organization-and-role-design": "plan-before-build",
    "process-modeling": "plan-before-build",
    "bdd-practice": "spec-before-build",
    "conceptual-data-modeling": "plan-before-build",
    "data-contract-design": "spec-before-build",
    "data-integration-and-interoperability": "feature-implementation",
    "data-lifecycle-and-retention-management": "plan-before-build",
    "data-lineage-and-provenance": "post-artefact-review",
    "data-product-dashboard-design": "feature-implementation",
    "data-product-design": "plan-before-build",
    "data-security-and-privacy-architecture": "security-hardening",
    "ddd-practice": "feature-implementation",
    "deprecation-and-migration": "plan-before-build",
    "design-system-practice": "feature-implementation",
    "documentation-and-adrs": "post-artefact-review",
    "dry-principle": "refactor-with-tests",
    "event-governance-and-lineage": "post-artefact-review",
    "event-modeling": "spec-before-build",
    "incident-response-and-postmortems": "debug-with-verification",
    "kiss-principle": "refactor-with-tests",
    "logical-data-modeling": "plan-before-build",
    "master-and-reference-data-management": "plan-before-build",
    "metadata-management": "plan-before-build",
    "release-engineering-and-progressive-delivery": "ci-pipeline-change",
    "schema-registry-and-contracts": "spec-before-build",
    "slo-error-budget-management": "post-artefact-review",
    "solid-principles": "refactor-with-tests",
    "sre-practice": "debug-with-verification",
    "strategy-to-execution-traceability": "plan-before-build",
    "toil-reduction-and-automation": "ci-pipeline-change",
    "value-stream-modeling": "plan-before-build",
    "message-based-integration-design": "feature-implementation",
    "message-channel-design": "feature-implementation",
    "integration-message-construction": "spec-before-build",
    "message-routing-design": "feature-implementation",
    "message-transformation-design": "feature-implementation",
    "message-endpoint-design": "feature-implementation",
    "messaging-system-management": "post-artefact-review",
    "eip-integration-validation": "post-artefact-review",
    "threat-modeling": "security-hardening",
    "secure-sdlc-and-supply-chain": "security-hardening",
    "api-design-and-lifecycle": "spec-before-build",
    "ai-model-governance": "post-artefact-review",
    "solution-architecture": "plan-before-build",
    "test-strategy": "plan-before-build",
    "risk-management": "plan-before-build",
    "finops-practice": "plan-before-build",
    "cloud-platform-architecture": "plan-before-build",
    "performance-engineering": "post-artefact-review",
    "infrastructure-as-code": "ci-pipeline-change",
    "technical-debt-management": "plan-before-build",
}

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
    ("krag-architecture", "krag or graphrag"),
    ("krag-architecture", "graph-augmented retrieval"),
    ("krag-architecture", "designing the end-to-end architecture"),
    ("krag-architecture", "knowledge graph-augmented retrieval"),
    ("safety-law-hierarchy", "material AI risk"),
    ("safety-law-hierarchy", "dangerous instruction"),
    ("safety-law-hierarchy", "safety law hierarchy"),
    ("safety-law-hierarchy", "asimov-inspired"),
    ("accessibility-audit", "wcag"),
    ("accessibility-audit", "accessible ui"),
    ("accessibility-audit", "keyboard"),
    ("mcp-server-design", "model context protocol"),
    ("ci-pipeline-change", "ci/cd"),
    ("ci-pipeline-change", "continuous integration"),
    ("security-hardening", "approval"),
    ("security-hardening", "guardrails"),
    ("security-hardening", "high-impact"),
    ("security-hardening", "human judgement"),
    ("security-hardening", "human review"),
    ("security-hardening", "destructive command"),
    ("code-review", "code review"),
    ("plan-before-build", "decomposing work"),
    ("plan-before-build", "multi-step implementation"),
    ("post-artefact-review", "evaluation"),
    ("post-artefact-review", "monitoring"),
    ("debug-with-verification", "debugging"),
    ("debug-with-verification", "recovery"),
    ("feature-implementation", "streaming"),
    ("feature-implementation", "event-driven"),
    ("feature-implementation", "lakehouse"),
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

RELATED_SKILL_TABLE_ROW_PATTERN = re.compile(
    r"^\|\s*`([-a-z0-9]+)`\s*\|\s*(complements|precedes|validates)\s*\|\s*(.+?)\s*\|\s*$",
    flags=re.MULTILINE | re.IGNORECASE,
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
    """A governed task intent promoted from SKILL.md metadata or sections."""

    task_intent_id: str
    matched_phrase: str
    evidence: EvidenceCoordinates
    section_heading: str
    mapping_source: str = "when_to_use"
    confidence: float = 0.95


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


def _frontmatter_description(markdown: str) -> str:
    if not markdown.startswith("---\n"):
        return ""
    end = markdown.find("\n---\n", 4)
    if end == -1:
        return ""
    frontmatter = markdown[4:end]
    match = re.search(r"^description:[ \t]*(.+)$", frontmatter, flags=re.MULTILINE)
    return match.group(1).strip() if match else ""


def _merge_task_intent_mappings(
    *groups: Sequence[TaskIntentMapping],
) -> tuple[TaskIntentMapping, ...]:
    merged: list[TaskIntentMapping] = []
    seen: set[str] = set()
    for group in groups:
        for mapping in group:
            if mapping.task_intent_id in seen:
                continue
            merged.append(mapping)
            seen.add(mapping.task_intent_id)
    return tuple(merged)


def promotion_ready_task_intents(
    mappings: Sequence[TaskIntentMapping],
) -> tuple[TaskIntentMapping, ...]:
    """Return task intents that satisfy Phase 2b promotion-ready sources."""

    return tuple(
        mapping for mapping in mappings if mapping.mapping_source in PROMOTION_READY_SOURCES
    )


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
            mapping_source="when_to_use",
            confidence=0.95,
        )
        for task_intent_id, matched_phrase, evidence, section_heading in raw_mappings
    )


def map_description_task_intents(markdown: str) -> tuple[TaskIntentMapping, ...]:
    """Map YAML description and section prose to governed task intents."""

    description = _frontmatter_description(markdown)
    when_section = extract_section(markdown, "When to use")
    combined_parts = [description]
    if when_section and when_section.text:
        combined_parts.append(when_section.text)
    combined = "\n".join(part for part in combined_parts if part).strip()
    if not combined:
        return ()

    pseudo_section = SectionExcerpt(
        heading="description",
        text=combined,
        line_start=1,
        line_end=max(1, combined.count("\n") + 1),
    )
    raw_mappings = _map_phrase_rules(
        pseudo_section,
        TASK_INTENT_PHRASE_RULES,
        governed_ids=GOVERNED_TASK_INTENT_IDS,
        section_heading="description",
    )
    return tuple(
        TaskIntentMapping(
            task_intent_id=task_intent_id,
            matched_phrase=matched_phrase,
            evidence=evidence,
            section_heading=section_heading,
            mapping_source="description",
            confidence=0.85,
        )
        for task_intent_id, matched_phrase, evidence, section_heading in raw_mappings
    )


def map_registry_task_intents(skill_name: str) -> tuple[TaskIntentMapping, ...]:
    """Map curated registry entries for high-traffic skills."""

    task_intent_id = SKILL_PRIMARY_INTENTS.get(skill_name)
    if not task_intent_id or task_intent_id not in GOVERNED_TASK_INTENT_IDS:
        return ()
    return (
        TaskIntentMapping(
            task_intent_id=task_intent_id,
            matched_phrase=f"skill_registry:{skill_name}",
            evidence=EvidenceCoordinates(line_start=1, line_end=1),
            section_heading="skill_registry",
            mapping_source="skill_registry",
            confidence=0.80,
        ),
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
    """Parse `## Related skills` bullets and table rows into typed dependency assertions."""

    section = extract_section(markdown, "Related skills")
    if not section or not section.text:
        return ()

    dependencies: list[SkillDependencyMapping] = []
    seen_targets: set[str] = set()
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
        seen_targets.add(target_skill_id)

    for match in RELATED_SKILL_TABLE_ROW_PATTERN.finditer(section.text):
        target_skill_id = match.group(1)
        if target_skill_id in seen_targets:
            continue
        if known_skill_ids is not None and target_skill_id not in known_skill_ids:
            continue

        dependency_type = match.group(2).lower()
        if dependency_type not in ALLOWED_DEPENDENCY_TYPES:
            dependency_type = "complements"
        rationale = match.group(3).strip()
        absolute_start = section.line_start + section.text[: match.start()].count("\n")
        absolute_end = section.line_start + section.text[: match.end()].count("\n")
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
        seen_targets.add(target_skill_id)

    return tuple(dependencies)


def map_skill_sections(
    markdown: str,
    *,
    skill_name: str = "",
    known_skill_ids: set[str] | None = None,
) -> SkillSectionMapping:
    """Map supported SKILL.md sections to governed semantic assertions."""

    task_intents = _merge_task_intent_mappings(
        map_when_to_use_task_intents(markdown),
        map_description_task_intents(markdown),
        map_registry_task_intents(skill_name),
    )
    return SkillSectionMapping(
        task_intents=task_intents,
        constraints=map_when_not_to_use_constraints(markdown),
        dependencies=map_related_skill_dependencies(markdown, known_skill_ids=known_skill_ids),
    )
