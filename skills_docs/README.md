# Coding Agent Skill Library

A structured, portable skill library for repository-aware coding agents such as Claude Code, Codex-style agents and other assistants that can read repository guidance and `SKILL.md` files.

The library separates agentic workflow patterns, agent control patterns, engineering delivery practices, user experience, reliability, event-driven data, business architecture and data architecture so that skills can be loaded selectively rather than treated as one large monolithic instruction set.

## Current status

This repository currently contains 70 `SKILL.md` files across eight skill categories.

- `skills/agentic-patterns/` and `skills/agent-control-patterns/` provide the agent workflow and control patterns.
- `skills/engineering-practices/`, `skills/user-experience/`, `skills/reliability-and-delivery/`, `skills/event-driven-and-real-time-data/`, `skills/business-architecture/` and `skills/data-architecture/` are fully populated.
- `skills/MANIFEST.md` is the canonical inventory for the full library.

## Recommended directory structure

```text
coding-agent-skill-library/
├── AGENTS.md
├── CLAUDE.md
├── README.md
├── docs/
│   └── DIRECTORY_PLACEMENT.md
└── skills/
    ├── MANIFEST.md
    ├── agentic-patterns/
    │   ├── prompt-chaining/
    │   ├── routing/
    │   ├── parallelisation/
    │   ├── reflection-and-verification/
    │   ├── tool-use-function-calling/
    │   ├── planning-and-task-decomposition/
    │   ├── multi-agent-collaboration/
    │   ├── memory-management/
    │   ├── learning-and-adaptation/
    │   └── mcp-server-design/
    ├── agent-control-patterns/
    │   ├── goal-setting-and-monitoring/
    │   ├── exception-handling-and-recovery/
    │   ├── human-in-the-loop/
    │   ├── knowledge-retrieval-rag/
    │   ├── inter-agent-communication-a2a/
    │   ├── resource-aware-optimisation/
    │   ├── reasoning-techniques/
    │   ├── guardrails-safety-patterns/
    │   ├── evaluation-and-monitoring/
    │   └── prioritisation/
    ├── engineering-practices/
    │   ├── kiss-principle/
    │   ├── solid-principles/
    │   ├── dry-principle/
    │   ├── tdd-practice/
    │   ├── bdd-practice/
    │   └── ddd-practice/
    ├── user-experience/
    │   ├── MANIFEST.md
    │   ├── ux-design-principles/
    │   ├── accessibility-wcag/
    │   ├── ui-component-design/
    │   ├── frontend-state-and-interaction-design/
    │   ├── data-product-dashboard-design/
    │   ├── design-system-practice/
    │   ├── user-research-and-usability-testing/
    │   └── agentic-ux-patterns/
    ├── reliability-and-delivery/
    │   ├── MANIFEST.md
    │   ├── sre-practice/
    │   ├── slo-error-budget-management/
    │   ├── incident-response-and-postmortems/
    │   ├── observability-and-telemetry/
    │   ├── toil-reduction-and-automation/
    │   ├── release-engineering-and-progressive-delivery/
    │   └── dora-four-keys/
    ├── event-driven-and-real-time-data/
    │   ├── MANIFEST.md
    │   ├── event-driven-architecture/
    │   ├── event-modelling/
    │   ├── event-streaming-platform-design/
    │   ├── schema-registry-and-contracts/
    │   ├── cdc-and-source-to-stream-ingestion/
    │   ├── stream-processing-patterns/
    │   ├── event-governance-and-lineage/
    │   └── real-time-operability/
    ├── business-architecture/
    │   ├── MANIFEST.md
    │   ├── business-capability-modelling/
    │   ├── value-stream-modelling/
    │   ├── process-modelling/
    │   ├── operating-model-design/
    │   ├── strategy-to-execution-traceability/
    │   ├── capability-maturity-assessment/
    │   ├── business-information-concept-modelling/
    │   └── organisation-and-role-design/
    └── data-architecture/
        ├── MANIFEST.md
        ├── conceptual-data-modelling/
        ├── logical-data-modelling/
        ├── data-product-design/
        ├── data-contract-design/
        ├── metadata-management/
        ├── data-governance-and-quality/
        ├── data-security-and-privacy-architecture/
        ├── data-lifecycle-and-retention-management/
        ├── data-integration-and-interoperability/
        ├── lakehouse-and-medallion-architecture/
        ├── master-and-reference-data-management/
        ├── ontology-and-knowledge-graph-modelling/
        └── data-lineage-and-provenance/
```

## Installation into a project

For a new project, copy the contents of this directory into the root of the target repository:

```text
my-project/
├── AGENTS.md
├── CLAUDE.md
├── skills/
│   ├── MANIFEST.md
│   ├── agentic-patterns/
│   ├── agent-control-patterns/
│   ├── engineering-practices/
│   ├── user-experience/
│   ├── reliability-and-delivery/
│   ├── event-driven-and-real-time-data/
│   ├── business-architecture/
│   └── data-architecture/
└── <project files>
```

If the target repository already has its own `README.md`, do not overwrite it. Keep this file as `docs/coding-agent-skill-library/README.md` or `AGENT_SKILLS_README.md`.

## User experience skills

This library includes a `skills/user-experience/` category for user-facing design and frontend implementation work.

| Skill | Purpose |
|---|---|
| `ux-design-principles` | User journeys, task flows, forms, navigation and low-cognitive-load workflows. |
| `accessibility-wcag` | WCAG-aligned accessibility checks for all user-facing work. |
| `ui-component-design` | Reusable, accessible and consistent UI components. |
| `frontend-state-and-interaction-design` | Loading, empty, error, disabled, partial-success, long-running and approval states. |
| `data-product-dashboard-design` | Data quality, profiling, validation, quarantine, refined dataset, lineage, audit and operations dashboards. |
| `design-system-practice` | Tokens, variants, typography, spacing, interaction patterns and UI consistency. |
| `user-research-and-usability-testing` | Lightweight validation that users can complete important tasks. |
| `agentic-ux-patterns` | Supervision, approval, evidence, uncertainty and audit interfaces for AI/agent workflows. |

For user-facing work, coding agents should start from the user task, decision, evidence required, risk, states and accessibility requirements. For agentic interfaces, agents must surface plans, tool use, evidence, uncertainty, consequences and approval controls rather than making autonomous actions invisible.

## Reliability and delivery skills

This library includes a `skills/reliability-and-delivery/` category for SRE and DORA Four Keys delivery-performance work.

DORA means **DevOps Research and Assessment** in this library, not financial-services regulation.

| Skill | Purpose |
|---|---|
| `sre-practice` | Production reliability, operability, resilience and service ownership. |
| `slo-error-budget-management` | SLIs, SLOs, error budgets, burn rates and release gating. |
| `incident-response-and-postmortems` | Incident handling, recovery, postmortems and corrective actions. |
| `observability-and-telemetry` | Logs, metrics, traces, dashboards, alerts and telemetry standards. |
| `toil-reduction-and-automation` | Safe reduction of repetitive operational work. |
| `release-engineering-and-progressive-delivery` | Canary releases, rollback, blue/green deployment, feature flags and release safety. |
| `dora-four-keys` | Deployment frequency, lead time for changes, change failure rate and failed deployment recovery time. |

For reliability or delivery work, coding agents should connect changes to user impact, service objectives, telemetry evidence, rollback path, operational ownership and residual risk. Reliability must not be treated as monitoring alone.

## Validation

After installing all categories, validate the library with:

```bash
find skills -name "SKILL.md" | sort
find skills -name "MANIFEST.md" | sort
```

With all eight categories installed, the library should contain **70 skills**.
