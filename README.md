# Coding Agent Skill Library

A portable default reference library for repository-aware coding agents.

This repository is designed to be dropped into another repo and provide one coherent startup path, one skills inventory, and one layered documentation model:

- repository entrypoint: `AGENTS.md`
- routing guide: `skills_docs/HOW_TO_FIND_THE_RIGHT_SKILL.md`
- skills subtree index: `skills/README.md`
- full inventory: `skills/MANIFEST.md`
- execution guidance: the smallest relevant `SKILL.md`

## Portable bootstrap

For a drop-in install, start with:

- `skills_docs/DROP_IN_BOOTSTRAP.md`
- `skills_docs/HOW_TO_FIND_THE_RIGHT_SKILL.md`

The library currently contains 86 `SKILL.md` files across eight categories.

## Recommended directory structure

```text
coding-agent-skill-library/
├── AGENTS.md
├── CLAUDE.md
├── README.md
├── AGENTIC_CODING_GLOBAL_SAFETY.md
├── SECURE_AGENTIC_DEVELOPMENT.md
├── skills/
│   ├── README.md
│   └── MANIFEST.md
├── skills_docs/
│   ├── README.md
│   ├── HOW_TO_FIND_THE_RIGHT_SKILL.md
│   └── DROP_IN_BOOTSTRAP.md
└── skills/
    ├── agentic-patterns/
    │   ├── MANIFEST.md
    │   ├── using-agent-skills/
    │   ├── interview-me/
    │   ├── idea-refine/
    │   ├── prompt-chaining/
    │   ├── routing/
    │   ├── parallelisation/
    │   ├── reflection-and-verification/
    │   ├── planning-and-task-decomposition/
    │   ├── spec-driven-development/
    │   ├── incremental-implementation/
    │   ├── context-engineering/
    │   ├── source-driven-development/
    │   ├── doubt-driven-development/
    │   ├── tool-use-function-calling/
    │   ├── multi-agent-collaboration/
    │   ├── memory-management/
    │   ├── learning-and-adaptation/
    │   └── mcp-server-design/
    ├── agent-control-patterns/
    │   ├── MANIFEST.md
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
    │   ├── ddd-practice/
    │   ├── code-review-and-quality/
    │   └── git-workflow-and-versioning/
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
    │   ├── browser-testing-with-devtools/
    │   ├── toil-reduction-and-automation/
    │   ├── release-engineering-and-progressive-delivery/
    │   ├── dora-four-keys/
    │   ├── ci-cd-and-automation/
    │   ├── deprecation-and-migration/
    │   ├── documentation-and-adrs/
    │   └── shipping-and-launch/
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
        ├── kg-enabled-rag/
        └── data-lineage-and-provenance/
```

## Installation into a project

For a new project, copy the contents of this directory into the root of the target repository:

```text
my-project/
├── AGENTS.md
├── CLAUDE.md
├── AGENTIC_CODING_GLOBAL_SAFETY.md
├── SECURE_AGENTIC_DEVELOPMENT.md
├── skills/
│   ├── README.md
│   ├── MANIFEST.md
│   ├── agentic-patterns/
│   ├── agent-control-patterns/
│   ├── engineering-practices/
│   ├── user-experience/
│   ├── reliability-and-delivery/
│   ├── event-driven-and-real-time-data/
│   ├── business-architecture/
│   └── data-architecture/
├── skills_docs/
│   ├── README.md
│   ├── HOW_TO_FIND_THE_RIGHT_SKILL.md
│   └── DROP_IN_BOOTSTRAP.md
└── <project files>
```

If the target repository already has its own `README.md`, do not overwrite it. Keep this file as `docs/coding-agent-skill-library/README.md` or `AGENT_SKILLS_README.md`.

## Documentation model

- `AGENTS.md` is the required repository entrypoint.
- `skills_docs/HOW_TO_FIND_THE_RIGHT_SKILL.md` is the canonical routing guide.
- `skills/README.md` explains how to traverse the portable `skills/` subtree.
- Category `README.md` files are quick routing pages.
- Category `MANIFEST.md` files are fuller inventories.
- `SKILL.md` files are the actual operating procedures.

## Validation

After installing all categories, validate the library with:

```bash
find skills -maxdepth 2 -name "README.md" | sort
find skills -name "SKILL.md" | sort
find skills -name "MANIFEST.md" | sort
```

With all eight categories installed, the library should contain **86 skills**.
