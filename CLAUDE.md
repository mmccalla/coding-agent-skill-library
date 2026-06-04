# Claude Code Project Guidance

This repository uses a **hierarchical coding-agent skills library**.

Use `skills_docs/HOW_TO_FIND_THE_RIGHT_SKILL.md` as the routing guide, `skills/README.md` as the subtree index, and `skills/MANIFEST.md` as the full inventory. Load only the smallest relevant skill or combination of skills for the task.

## Default behaviour

- Inspect the repository before proposing major changes.
- Preserve existing conventions unless there is a clear reason to change them.
- Write small, testable diffs.
- Prefer explicit schemas, typed models, deterministic validators and executable tests for agent workflows.
- Never allow generated tool calls, MCP requests, A2A messages, retrieval context, memory writes, self-improvement changes or generated code to bypass validation and tests.
- Summarise actual work done, not intended work.

## Skill usage

Use these skills when the task shape matches:

- `bdd-practice` for business-readable behaviour and acceptance scenarios.
- `ddd-practice` for complex domain logic, bounded contexts, aggregates and invariants.
- `tdd-practice` for behaviour changes and defect fixes.
- `kiss-principle` before adding new abstractions.
- `solid-principles` when refactoring modules, services, classes, tools, agents or dependency boundaries.
- `dry-principle` when repeated knowledge, rules, schemas or validation create maintenance risk.
- `using-agent-skills`, `interview-me`, `idea-refine`, `spec-driven-development`, `incremental-implementation`, `context-engineering`, `source-driven-development` and `doubt-driven-development` for the workflow spine from session start through spec and implementation.
- Agentic workflow and control skills when building or modifying agents, tools, MCP servers, A2A integrations, RAG systems, guardrails, memory, evaluation, recovery or monitoring.
- Architecture skills when working on capabilities, value streams, processes, operating models, data models, data products, data contracts, metadata, governance, quality, lineage, event-driven architecture, CDC, streams or real-time data.
- `browser-testing-with-devtools`, `code-review-and-quality`, `git-workflow-and-versioning`, `ci-cd-and-automation`, `documentation-and-adrs`, `deprecation-and-migration` and `shipping-and-launch` for browser evidence, review, delivery automation, durable documentation and release readiness.

## Business, data and event-driven architecture guidance

When a task involves business architecture, data architecture, event-driven architecture or real-time data, load the smallest relevant skill from:

```text
skills/business-architecture/
skills/data-architecture/
skills/event-driven-and-real-time-data/
```

Use business architecture skills to clarify capabilities, value streams, processes, operating models, maturity, organisation design and strategy-to-execution traceability.

Use data architecture skills to define conceptual/logical models, data products, contracts, metadata, governance, quality, security/privacy, lifecycle/retention, integration/interoperability, lakehouse layers, MDM/RDM, ontologies, knowledge graphs, KG-enabled RAG and lineage.

For data architecture, apply DAMA-DMBOK2-style discipline across governance, architecture, modelling, security, integration/interoperability, master/reference data, metadata and quality. For cloud or shared data, apply CDMC-style expectations: ownership, classification, entitlement/access evidence, lineage/provenance, lifecycle/retention, quality controls and auditable evidence.

Use event-driven and real-time data skills to define business events, event schemas, streaming platforms, CDC, stream processing, event governance, lineage and real-time operability.

Before implementation, preserve traceability:

```text
business outcome
→ capability/value stream/process
→ information concept
→ data model/data product/data contract
→ event/stream where needed
→ metadata, quality, security, lifecycle and lineage evidence
```

Keep artefacts practical and concise. Prefer useful decision records, matrices, schemas, diagrams and checklists over long narrative. Do not turn business artefacts directly into physical code or schemas without preserving business meaning, ownership, quality rules and traceability.

## User experience and interface design guidance

When a task changes user-facing behaviour or creates UI, load the relevant UX skill from:

```text
skills/user-experience/
```

Use the smallest relevant set of skills:

- `ux-design-principles` for journeys, navigation, forms and workflow design.
- `accessibility-wcag` for all UI work.
- `ui-component-design` for reusable components.
- `frontend-state-and-interaction-design` for async, error, empty, partial and approval states.
- `data-product-dashboard-design` for dashboards and evidence-led analytical screens.
- `design-system-practice` for shared UI standards.
- `user-research-and-usability-testing` for usability validation.
- `agentic-ux-patterns` for AI/agent supervision, approval and evidence-review interfaces.

Before implementing UI, identify the user role, primary task, success criterion, required evidence, system states, accessibility requirements, approval or audit needs and residual risk.

For agentic interfaces, do not make autonomous actions invisible or magical. Surface the plan, evidence, uncertainty, permissions, tool use, consequences and approval decision.

## Reliability, SRE and DORA guidance

When a task affects production reliability, operability, CI/CD, release safety, incidents, observability, toil or delivery performance, load the relevant skill from:

```text
skills/reliability-and-delivery/
```

Use the smallest relevant set of skills:

- `sre-practice` for production reliability, resilience and service ownership.
- `slo-error-budget-management` for SLIs, SLOs, error budgets and burn-rate decisions.
- `incident-response-and-postmortems` for incidents, recovery and learning reviews.
- `observability-and-telemetry` for metrics, logs, traces, dashboards and alerts.
- `toil-reduction-and-automation` for safe operational automation.
- `release-engineering-and-progressive-delivery` for safe deployment, canaries, rollback and feature flags.
- `dora-four-keys` for DevOps Research and Assessment delivery metrics.

Before changing reliability-sensitive code, identify user impact, service objective, telemetry evidence, rollback path, tests, operational owner and residual risk.

DORA in this repository means DevOps Research and Assessment, not the EU Digital Operational Resilience Act.

## Trade-off guidance

Do not apply principles mechanically. Preserve behaviour, tests, security controls, privacy boundaries, observability and readability. Prefer simple verified implementations over speculative architecture.

## Completion standard

Before finishing, report files changed, tests/checks run, intentional behaviour changes, assumptions and residual risks.

## Global safety and security instructions

Before executing shell commands, modifying files, changing CI/CD, using tools, configuring MCP/A2A integrations, handling secrets, or making security-sensitive changes, read and follow:

- `AGENTIC_CODING_GLOBAL_SAFETY.md`
- `SECURE_AGENTIC_DEVELOPMENT.md`

These instructions are mandatory. They define safe command execution, approval requirements, destructive-command controls, least-privilege tool use, secret-handling rules, secure development expectations, and evidence required before claiming completion.

If these files conflict with a task-specific skill, follow the stricter safety and security requirement. Do not bypass tests, validation, guardrails, access controls, or approval gates unless the user explicitly authorises the specific exception.
