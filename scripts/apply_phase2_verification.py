#!/usr/bin/env python3
"""Apply Phase 2: standardise Verification checklists and Related skills sections."""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1] / "skills"

STANDARD_ARCHITECTURE_VERIFICATION = """## Verification

- [ ] Required artefacts produced and linked to scope.
- [ ] Decisions, assumptions and risks stated explicitly.
- [ ] Quality checks or validation performed.
- [ ] Files changed reported with traceability preserved."""

ONTOLOGY_VERIFICATION = """## Verification

- [ ] Ontology or graph artefacts produced with key decisions documented.
- [ ] Assumptions, trade-offs and unresolved issues stated.
- [ ] Validation performed against modelling rules.
- [ ] Files changed reported with traceability preserved."""

KG_RAG_VERIFICATION = """## Verification

- [ ] Files changed reported.
- [ ] Commands and validations run with results stated.
- [ ] Behaviour intentionally changed described.
- [ ] Assumptions and residual risks or follow-up work stated."""

VERIFICATION_BY_SKILL: dict[str, str] = {
    "apply-laws-of-ai": """## Verification

- [ ] All six quality gates evaluated (Humanity, Human Safety, Authority, Security, Proportionality, Auditability).
- [ ] Refusals, constraints or escalations reported where applicable.
- [ ] Confirmation that this skill ran before all other reasoning.""",
    "skill-discovery-and-selection": """## Verification

- [ ] `apply-laws-of-ai` execution confirmed.
- [ ] Selected skill(s) and selection rationale reported.
- [ ] Intentionally excluded skills noted.
- [ ] Remaining ambiguity or re-check triggers stated.""",
    "spec-driven-development": """## Verification

- [ ] Final behaviour and acceptance criteria captured.
- [ ] Edge cases and constraints documented.
- [ ] Out-of-scope behaviour stated.
- [ ] Compatibility or rollout concerns noted where relevant.""",
    "tdd-practice": """## Verification

- [ ] Failing test added before production change.
- [ ] Production change made and targeted tests pass.
- [ ] Refactor performed only with tests green.
- [ ] Remaining untested risks stated.""",
    "incremental-implementation": """## Verification

- [ ] Slice scope and acceptance criteria stated.
- [ ] Validation run for the completed slice.
- [ ] Behaviour change and rollback path described.
- [ ] Next slice or residual risks noted.""",
    "idea-refinement": """## Verification

- [ ] Refined problem statement and proposed approach stated.
- [ ] Constraints, assumptions and open questions listed.
- [ ] Success criteria or falsifiable hypotheses captured.
- [ ] Recommendation for spec, interview or implementation next step.""",
    "requirements-elicitation": """## Verification

- [ ] Clarifying questions asked or assumptions stated explicitly.
- [ ] User goal, constraints and success criteria captured.
- [ ] Scope boundaries and out-of-scope items noted.
- [ ] Ready-to-proceed signal or remaining gaps stated.""",
    "context-engineering": """## Verification

- [ ] Context sources selected and justified.
- [ ] Excluded or truncated context noted.
- [ ] Token or noise trade-offs stated.
- [ ] Residual context gaps or risks reported.""",
    "source-driven-development": """## Verification

- [ ] Authoritative sources cited.
- [ ] Claims mapped to source evidence.
- [ ] Gaps where sources are silent or conflicting stated.
- [ ] Implementation or documentation aligned to sources.""",
    "uncertainty-driven-development": """## Verification

- [ ] Doubts, assumptions and failure modes logged.
- [ ] Evidence sought or experiments defined.
- [ ] Proceed, constrain or escalate decision stated.
- [ ] Residual uncertainty reported.""",
    "code-review-and-quality": """## Verification

- [ ] Findings listed with severity and evidence.
- [ ] Tests or checks run reported.
- [ ] Correctness assessed before style concerns.
- [ ] Residual risks requiring follow-up stated.""",
    "git-workflow-and-versioning": """## Verification

- [ ] Logical change boundaries described.
- [ ] Working tree state reported.
- [ ] Versioning or compatibility considerations noted.
- [ ] Reversibility of the change confirmed.""",
    "bdd-practice": """## Verification

- [ ] Scenarios added or updated in business-readable form.
- [ ] Acceptance tests run with results stated.
- [ ] Implemented behaviour matches scenarios.
- [ ] Stakeholder confirmation gaps noted.""",
    "ddd-practice": """## Verification

- [ ] Bounded context and key domain terms stated.
- [ ] Aggregate or boundary decisions documented.
- [ ] Invariants protected identified.
- [ ] Modelling assumptions requiring business validation noted.""",
    "solid-principles": """## Verification

- [ ] SOLID issue addressed identified.
- [ ] Design boundary change described.
- [ ] Tests or checks run reported.
- [ ] Residual risks or assumptions stated.""",
    "kiss-principle": """## Verification

- [ ] Simplification described with rationale.
- [ ] Retained complexity justified.
- [ ] Tests or checks run reported.
- [ ] Residual risks or assumptions stated.""",
    "dry-principle": """## Verification

- [ ] Duplication removed or deliberately retained with reason.
- [ ] Any new abstraction justified as safe.
- [ ] Tests or checks run reported.
- [ ] Residual risks or assumptions stated.""",
    "accessibility-wcag": """## Verification

- [ ] Keyboard interaction checked.
- [ ] Labels, accessible names and focus states checked.
- [ ] Colour-only meaning avoided.
- [ ] Table or chart accessibility considered.
- [ ] Tests or manual checks performed and residual risks stated.""",
    "ux-design-principles": """## Verification

- [ ] User role and primary task stated.
- [ ] Key screens or flow steps changed listed.
- [ ] States handled and accessibility considerations noted.
- [ ] Tests or manual checks and residual UX risks reported.""",
    "ui-component-design": """## Verification

- [ ] Component purpose and interface changes stated.
- [ ] States and variants handled documented.
- [ ] Accessibility checks performed.
- [ ] Tests added or updated; residual risks stated.""",
    "frontend-state-and-interaction-design": """## Verification

- [ ] States and transitions implemented listed.
- [ ] Recovery options and high-risk controls documented.
- [ ] Tests or manual checks performed.
- [ ] Residual interaction risks stated.""",
    "design-system-practice": """## Verification

- [ ] Design-system artefacts changed listed.
- [ ] Tokens or components added or updated with rationale.
- [ ] Accessibility notes and examples or tests updated.
- [ ] Residual consistency risks stated.""",
    "data-product-dashboard-design": """## Verification

- [ ] Dashboard user and decision stated.
- [ ] Metrics, filters and drill-downs documented.
- [ ] Evidence links and accessibility considerations noted.
- [ ] Residual dashboard risks stated.""",
    "agentic-ux-patterns": """## Verification

- [ ] Agent action and risk level stated.
- [ ] Evidence, approval mechanism and uncertainty display documented.
- [ ] Auditability considered.
- [ ] Residual safety or UX risks stated.""",
    "user-research-and-usability-testing": """## Verification

- [ ] User roles and scenarios considered stated.
- [ ] Success criteria and findings or expected findings captured.
- [ ] Design changes made listed.
- [ ] Residual research gaps noted.""",
    "sre-practice": """## Verification

- [ ] User impact and SLI/SLO or operational signal addressed.
- [ ] Reliability controls added or changed described.
- [ ] Tests, checks and observability evidence reported.
- [ ] Runbook updates and residual reliability risk stated.""",
    "slo-error-budget-management": """## Verification

- [ ] SLI, SLO target and measurement window stated.
- [ ] Error budget policy and burn-rate alerting defined.
- [ ] Telemetry source and release impact noted.
- [ ] Residual measurement risk stated.""",
    "release-engineering-and-progressive-delivery": """## Verification

- [ ] Release risk classification and rollout strategy stated.
- [ ] Pre-release checks and rollback path documented.
- [ ] Health signals and tests or checks run reported.
- [ ] Residual release risk stated.""",
    "observability-and-telemetry": """## Verification

- [ ] Telemetry added or changed listed.
- [ ] User journey or SLO coverage stated.
- [ ] Sensitive-data handling considered.
- [ ] Validation performed and observability gaps noted.""",
    "incident-response-and-postmortems": """## Verification

- [ ] Incident type and user impact stated.
- [ ] Mitigation or recovery actions documented.
- [ ] Evidence preserved and postmortem or runbook updates noted.
- [ ] Corrective actions and follow-up stated.""",
    "dora-four-keys": """## Verification

- [ ] Metric affected and measurement source stated.
- [ ] Bottleneck or failure pattern identified.
- [ ] Improvement proposed or implemented described.
- [ ] Safety controls preserved; residual measurement risk noted.""",
    "toil-reduction-and-automation": """## Verification

- [ ] Toil reduced and expected benefit stated.
- [ ] Safeguards, dry-run or rollback path documented.
- [ ] Tests or checks run reported.
- [ ] Audit or telemetry added; residual automation risk stated.""",
    "ci-cd-and-automation": """## Verification

- [ ] Pipeline or automation change scope stated.
- [ ] Permissions and safety controls preserved.
- [ ] Tests or checks run reported.
- [ ] Rollback path and residual delivery risk noted.""",
    "documentation-and-adrs": """## Verification

- [ ] Documentation or ADR artefacts produced listed.
- [ ] Decision, context and consequences captured.
- [ ] Alternatives considered noted.
- [ ] Residual documentation gaps stated.""",
    "shipping-and-launch": """## Verification

- [ ] Launch scope and rollout plan stated.
- [ ] Pre-launch checks and monitoring plan documented.
- [ ] Rollback or mitigation path defined.
- [ ] Residual launch risks stated.""",
    "deprecation-and-migration": """## Verification

- [ ] Deprecated surface and timeline stated.
- [ ] Migration path and consumer communication documented.
- [ ] Compatibility or dual-run period noted.
- [ ] Residual migration risks stated.""",
    "browser-testing-with-devtools": """## Verification

- [ ] Browser flows exercised listed.
- [ ] DOM, console, network or performance evidence captured.
- [ ] Defects or regressions reported with reproduction steps.
- [ ] Residual untested browser risks stated.""",
}

STANDARD_ARCHITECTURE_SKILLS = {
    "business-capability-modeling",
    "business-information-concept-modeling",
    "capability-maturity-assessment",
    "operating-model-design",
    "organization-and-role-design",
    "process-modeling",
    "strategy-to-execution-traceability",
    "value-stream-modeling",
    "conceptual-data-modeling",
    "data-contract-design",
    "data-governance-and-quality",
    "data-integration-and-interoperability",
    "data-lifecycle-and-retention-management",
    "data-lineage-and-provenance",
    "data-product-design",
    "data-security-and-privacy-architecture",
    "lakehouse-and-medallion-architecture",
    "logical-data-modeling",
    "master-and-reference-data-management",
    "metadata-management",
    "cdc-and-source-to-stream-ingestion",
    "event-driven-architecture",
    "event-governance-and-lineage",
    "event-modeling",
    "event-streaming-platform-design",
    "streaming-operations-and-slos",
    "schema-registry-and-contracts",
    "stream-processing-patterns",
}

ALREADY_CHECKLIST_SKILLS = {
    "reflection-and-verification",
    "multi-agent-collaboration",
    "planning-and-task-decomposition",
    "parallelization",
    "guardrails-safety-patterns",
    "goal-setting-and-monitoring",
    "resource-aware-optimization",
    "evaluation-and-monitoring",
    "routing",
    "exception-handling-and-recovery",
    "human-in-the-loop",
    "reasoning-techniques",
    "prompt-chaining",
    "prioritization",
    "mcp-server-design",
    "tool-use-and-function-calling",
    "knowledge-retrieval-rag",
    "inter-agent-communication-a2a",
    "memory-management",
    "learning-and-adaptation",
}

RELATED_SKILLS: dict[str, list[tuple[str, str]]] = {
    "apply-laws-of-ai": [
        ("skill-discovery-and-selection", "route to task skills after baseline gates pass"),
        ("guardrails-safety-patterns", "layered deterministic controls"),
        ("human-in-the-loop", "escalation when gates constrain action"),
    ],
    "skill-discovery-and-selection": [
        ("apply-laws-of-ai", "mandatory baseline before routing"),
        ("planning-and-task-decomposition", "multi-step work decomposition"),
        ("requirements-elicitation", "underspecified requests"),
    ],
    "guardrails-safety-patterns": [
        ("apply-laws-of-ai", "immutable safety baseline"),
        ("human-in-the-loop", "approval for high-risk actions"),
        ("tool-use-and-function-calling", "least-privilege tool execution"),
    ],
    "spec-driven-development": [
        ("bdd-practice", "business-readable acceptance scenarios"),
        ("incremental-implementation", "implement spec in verifiable slices"),
        ("planning-and-task-decomposition", "break large specs into ordered work"),
    ],
    "tdd-practice": [
        ("code-review-and-quality", "review after tests pass"),
        ("reflection-and-verification", "repair loop when checks fail"),
        ("bdd-practice", "acceptance scenarios for external behaviour"),
    ],
    "planning-and-task-decomposition": [
        ("incremental-implementation", "execute plan as small slices"),
        ("spec-driven-development", "decision-complete spec before coding"),
        ("skill-discovery-and-selection", "select supporting skills per step"),
    ],
    "incremental-implementation": [
        ("planning-and-task-decomposition", "ordered plan before slicing"),
        ("tdd-practice", "verify each slice with tests"),
        ("reflection-and-verification", "quality gate per slice"),
    ],
    "reflection-and-verification": [
        ("tdd-practice", "executable verification first"),
        ("code-review-and-quality", "human or agent review loop"),
        ("apply-laws-of-ai", "safety gates before claiming completion"),
    ],
    "mcp-server-design": [
        ("tool-use-and-function-calling", "direct tool calling when MCP is unnecessary"),
        ("guardrails-safety-patterns", "auth, validation and least privilege"),
        ("knowledge-retrieval-rag", "document grounding alongside tools"),
    ],
    "knowledge-retrieval-rag": [
        ("knowledge-graph-rag", "graph-native retrieval when Neo4j applies"),
        ("context-engineering", "assemble retrieval context efficiently"),
        ("guardrails-safety-patterns", "validate retrieved and generated content"),
    ],
    "human-in-the-loop": [
        ("apply-laws-of-ai", "escalation aligned with safety laws"),
        ("guardrails-safety-patterns", "policy gates before human review"),
        ("agentic-ux-patterns", "approval and evidence UI patterns"),
    ],
    "code-review-and-quality": [
        ("tdd-practice", "tests as review evidence"),
        ("git-workflow-and-versioning", "reviewable atomic changes"),
        ("guardrails-safety-patterns", "security findings in review"),
    ],
    "bdd-practice": [
        ("spec-driven-development", "spec before scenarios"),
        ("tdd-practice", "executable tests from scenarios"),
        ("ddd-practice", "domain language in scenarios"),
    ],
    "ddd-practice": [
        ("bdd-practice", "scenarios using ubiquitous language"),
        ("spec-driven-development", "bounded context in specs"),
        ("conceptual-data-modeling", "link domain concepts to data models"),
    ],
    "accessibility-wcag": [
        ("ux-design-principles", "task-centred design before a11y checks"),
        ("ui-component-design", "accessible component primitives"),
        ("frontend-state-and-interaction-design", "keyboard and state accessibility"),
    ],
}


def skill_path(name: str) -> Path | None:
    matches = list(ROOT.rglob(f"*/{name}/SKILL.md"))
    if len(matches) != 1:
        return None
    return matches[0]


def replace_verification(text: str, new_section: str) -> str:
    return re.sub(
        r"^## Verification\s*\n.*?(?=^## |\Z)",
        new_section + "\n\n",
        text,
        count=1,
        flags=re.S | re.M,
    )


def insert_related_skills(text: str, entries: list[tuple[str, str]]) -> str:
    if "## Related skills" in text:
        return text
    lines = ["## Related skills", ""]
    for skill_name, note in entries:
        lines.append(f"- `{skill_name}` — {note}")
    lines.append("")
    block = "\n".join(lines)
    return re.sub(
        r"^(## Verification\s*)",
        block + r"\1",
        text,
        count=1,
        flags=re.M,
    )


def has_checklist_verification(text: str) -> bool:
    match = re.search(r"^## Verification\s*\n(.*?)(?=^## |\Z)", text, re.S | re.M)
    if not match:
        return False
    return bool(re.search(r"^- \[ \]", match.group(1), re.M))


def main() -> int:
    updated_verification = 0
    updated_related = 0

    for skill_name in sorted(
        STANDARD_ARCHITECTURE_SKILLS | set(VERIFICATION_BY_SKILL) | {"ontology-and-knowledge-graph-modeling", "knowledge-graph-rag"}
    ):
        path = skill_path(skill_name)
        if path is None:
            print(f"SKIP missing: {skill_name}")
            continue
        if skill_name in ALREADY_CHECKLIST_SKILLS:
            continue
        text = path.read_text(encoding="utf-8")
        if has_checklist_verification(text) and skill_name != "knowledge-graph-rag":
            continue
        if skill_name in VERIFICATION_BY_SKILL:
            new_v = VERIFICATION_BY_SKILL[skill_name]
        elif skill_name == "ontology-and-knowledge-graph-modeling":
            new_v = ONTOLOGY_VERIFICATION
        elif skill_name == "knowledge-graph-rag":
            new_v = KG_RAG_VERIFICATION
        elif skill_name in STANDARD_ARCHITECTURE_SKILLS:
            new_v = STANDARD_ARCHITECTURE_VERIFICATION
        else:
            continue
        text = replace_verification(text, new_v)
        path.write_text(text, encoding="utf-8")
        updated_verification += 1
        print(f"verification OK {skill_name}")

    for skill_name, entries in RELATED_SKILLS.items():
        path = skill_path(skill_name)
        if path is None:
            print(f"SKIP related missing: {skill_name}")
            continue
        text = path.read_text(encoding="utf-8")
        text = insert_related_skills(text, entries)
        path.write_text(text, encoding="utf-8")
        updated_related += 1
        print(f"related OK {skill_name}")

    print(f"Updated verification: {updated_verification}, related: {updated_related}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
