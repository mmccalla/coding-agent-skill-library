# Repository Instructions for Coding Agents

This repository uses a **flat `skills/` directory**. Each skill lives directly under `skills/` and remains a reusable operating procedure for a specific type of coding-agent task.

## Startup order

Before planning, routing, tool use, or edits, execute in this order:

1. Read `skills_docs/HOW_TO_FIND_THE_RIGHT_SKILL.md`, then `skills/README.md`.
2. Load only the smallest relevant `SKILL.md` file or skill combination needed for the task.

See `skills_docs/LIBRARY_CONTRACT.md` for portable consistency rules.

## Discovery-first metadata policy

Agents should treat skill frontmatter as the primary discovery surface. Match against, in order:

1. `name`
2. `aliases`
3. `description`
4. explicit pack metadata and manifest context

Folder structure helps human navigation, but frontmatter is authoritative for real-world agent discoverability.

When authoring or changing skills:

- Prefer canonical US-English spellings in skill IDs.
- Prefer clear noun-phrase or gerund names over conversational or imperative labels.
- Prefer industry-standard terms over repository-local shorthand.
- Add aliases for acronyms, alternate spellings, synonymous phrasings and superseded names.

## Skill directory structure

Search recursively for skills under:

```text
skills/
├── README.md
├── MANIFEST.md
├── bdd-practice/
├── knowledge-graph-rag/
├── krag-system-design/
└── ...
```

The physical layout is one level deep: one folder per skill directly under `skills/`. Category remains important, but as explicit pack metadata and human inventory context rather than as a nested filesystem path.

Do not assume a skill from its name alone. Use `skills/README.md` for routing conventions, `skills/PACK_METADATA.json` for machine-readable category membership, `skills/MANIFEST.md` for human inventory, and the relevant `SKILL.md` for execution guidance.

## Core operating principles

1. Prefer the simplest architecture that satisfies the requirement.
2. Use deterministic code, typed interfaces, schemas, tests, explicit errors and policy checks before adding LLM autonomy.
3. Treat LLM calls, tool calls, MCP requests, A2A messages, retrieval context, memory writes, generated code and self-improvement changes as untrusted until validated.
4. Decompose complex work into small, testable steps.
5. Use structured outputs for plans, routes, tool calls, task states, errors, evaluations and hand-offs wherever feasible.
6. Keep changes small, reversible and aligned with existing repository conventions.
7. Preserve existing public behaviour, security posture and data boundaries unless explicitly asked to change them.
8. Run the narrowest useful validation after each material change.
9. For behaviour changes, prefer TDD: first prove the behaviour with a failing test, then implement the smallest passing change.
10. For business-facing requirements, prefer BDD scenarios to clarify externally visible behaviour before implementation.
11. For complex business domains, use DDD to protect language, boundaries, invariants and domain rules.
12. Do not run destructive commands, expose secrets, weaken security controls or bypass tests without explicit approval.
13. Do not claim completion from intention. Provide evidence.

## Skill selection guide

### Core workflow and orchestration

- Use `prompt-chaining` for multi-stage sequential workflows where each step produces a hand-off for the next step.
- Use `routing` for conditional path, model, tool, workflow or sub-agent selection.
- Use `parallelization` for independent concurrent operations where concurrency improves latency without reducing determinism or safety.
- Use `reflection-and-verification` for critique, repair, tests, review loops and quality gates.
- Use `planning-and-task-decomposition` when a complex objective must become an executable, ordered plan.
- Use `multi-agent-collaboration` only when specialised roles and explicit hand-offs materially improve the outcome.
- Use `skill-discovery-and-selection`, `requirements-elicitation`, `idea-refinement`, `spec-driven-development`, `incremental-implementation`, `context-engineering`, `source-driven-development` and `uncertainty-driven-development` when the work needs the local discovery/spec/implementation spine.

### Tooling, integration and knowledge access

- Use `tool-use-and-function-calling` for safe external tool, API, database, command or service execution.
- Use `mcp-server-design` when exposing agent-friendly tools, resources or prompts through MCP.
- Use `knowledge-retrieval-rag` when repository, document or knowledge-base grounding is required.
- Use `inter-agent-communication-a2a` for cross-agent delegation, agent cards, task exchange, artefact exchange or A2A-style interoperability.
- Use `memory-management` for short-term state, long-term memory, retrieval, summarisation or persistence across sessions.

### KRAG systems

For KRAG architecture, ingestion, retrieval or evaluation work, load the smallest relevant KRAG skill from the flat `skills/` directory using pack-metadata/frontmatter category context.

- Use `krag-system-design` for end-to-end KRAG architecture, graph role definition, retrieval role design and implementation slicing.
- Use `krag-ingestion-graph-construction` for evidence anchoring, extraction, entity resolution, graph construction and validation.
- Use `krag-retrieval-answering` for retrieval planning, graph traversal, hybrid ranking, grounded answer synthesis and abstention.
- Use `krag-evaluation-governance` for retrieval, graph, answer and operational evaluation, governance and release gates.

For KRAG work, do not treat a manually curated routing overlay as sufficient evidence that the graph materially improves retrieval.

### Reliability, control and governance

- Use `apply-laws-of-ai` when the task involves material AI/agent harm risk, unlawful or unauthorised instructions, or explicit safety-law trade-offs — not as a mandatory session preamble.
- Use `goal-setting-and-monitoring` for measurable objectives, success criteria, stop conditions and progress tracking.
- Use `exception-handling-and-recovery` for error detection, retries, fallbacks, rollback, graceful degradation and escalation.
- Use `human-in-the-loop` for human approval, review, judgement or escalation.
- Use `guardrails-safety-patterns` for input validation, output checks, tool restrictions, safety policies and secure defaults.
- Use `threat-modeling` for assets, trust boundaries, threats and mitigations before security-sensitive design.
- Use `ai-model-governance` for model inventory, risk tier, approval, monitoring, drift and retirement.
- Use `risk-management` for risk registers, treatments, owners and residual risk tracking.
- Use `evaluation-and-monitoring` for metrics, baselines, regression tests, observability, drift detection and operational monitoring.
- Use `browser-testing-with-devtools`, `ci-cd-and-automation`, `deprecation-and-migration`, `documentation-and-adrs`, `shipping-and-launch`, `code-review-and-quality` and `git-workflow-and-versioning` when browser evidence, release discipline, durable documentation or source-control hygiene are part of the task.

### Optimisation and advanced intelligence

- Use `resource-aware-optimization` for cost, latency, context-window, token, compute, model-selection and budget trade-offs.
- Use `reasoning-techniques` for complex debugging, design reasoning, code-aided reasoning, ReAct-style tool loops and alternative-path exploration.
- Use `prioritization` for ranking tasks, bugs, risks, requirements, alerts or next actions.
- Use `learning-and-adaptation` only when improvement is measured, bounded, reversible and validated.

### Engineering design and delivery practices

- Use `kiss-principle` to simplify over-engineered code, workflows, architectures or agent designs.
- Use `solid-principles` to improve modularity, dependency boundaries, substitutability, extensibility and testability.
- Use `dry-principle` to remove harmful duplication while avoiding premature or misleading abstraction.
- Use `tdd-practice` to add or change behaviour through a failing test, smallest passing implementation and refactor loop.
- Use `bdd-practice` to express business-readable behaviour, acceptance criteria and user-facing scenarios.
- Use `ddd-practice` to model complex domains using bounded contexts, ubiquitous language, aggregates, value objects, domain events and protected invariants.
- Use `test-strategy` for risk-based test levels, pyramid mix and exit criteria.
- Use `technical-debt-management` for debt inventory, interest and paydown plans.

### Business, data and event-driven architecture

For architecture work, load the smallest relevant skill from the flat `skills/` directory using the `business-architecture`, `data-architecture`, `event-driven-and-real-time-data` and `enterprise-integration-patterns` groupings in `skills/PACK_METADATA.json` and `skills/MANIFEST.md`.

Use business architecture skills to clarify capabilities, value streams, processes, operating models, maturity, organisation design and strategy-to-execution traceability:

- Use `solution-architecture` for end-to-end options, NFRs, views and architecture fitness functions or exceptions.
- Use `cloud-platform-architecture` for landing zones, tenancy, shared services and platform guardrails.
- Use `business-capability-modeling` for stable business abilities, capability maps, decomposition, ownership and heatmaps.
- Use `value-stream-modeling` for trigger-to-outcome value flow across stakeholders, capabilities, data and systems.
- Use `process-modeling` for operational steps, decisions, hand-offs, controls, exceptions and automation opportunities.
- Use `operating-model-design` for people, process, technology, data, governance, funding and delivery alignment.
- Use `strategy-to-execution-traceability` for linking objectives, outcomes, capabilities, initiatives, metrics and evidence.
- Use `capability-maturity-assessment` for current/target maturity, gaps, risks and roadmap priorities.
- Use `business-information-concept-modeling` for deriving business concepts and relationships from business architecture artefacts.
- Use `organization-and-role-design` for roles, decision rights, accountabilities and team boundaries.

Use data architecture skills to define conceptual/logical models, data products, contracts, metadata, governance, quality, security/privacy, lifecycle/retention, integration/interoperability, lakehouse layers, MDM/RDM, ontologies, knowledge graphs and lineage. For data architecture, apply DAMA-DMBOK2-style separation of data management concerns across governance, architecture, modelling, security, integration/interoperability, master/reference data, metadata and quality. For cloud or shared data, apply CDMC-style control expectations: ownership, classification, entitlement/access evidence, lineage/provenance, lifecycle/retention, quality controls and auditable evidence.

- Use `conceptual-data-modeling` for implementation-independent business concepts and relationships.
- Use `logical-data-modeling` for logical entities, attributes, identifiers, keys, relationships and constraints.
- Use `data-product-design` for domain-owned, governed, discoverable and reusable data products.
- Use `data-contract-design` for producer-consumer schema, semantics, quality, compatibility and operational obligations.
- Use `metadata-management` for business, technical, operational, governance, quality and lineage metadata.
- Use `data-governance-and-quality` for ownership, policy, quality rules, controls, monitoring and remediation.
- Use `data-security-and-privacy-architecture` for classification, access, masking, privacy and entitlement controls.
- Use `data-lifecycle-and-retention-management` for retention, archival, deletion, legal hold and lifecycle controls.
- Use `data-integration-and-interoperability` for batch, API, event, CDC and semantic interoperability patterns.
- Use `lakehouse-and-medallion-architecture` for raw, quarantine, cleansed, refined and serving-layer design.
- Use `master-and-reference-data-management` for golden records, controlled values, identifiers, hierarchies and survivorship.
- Use `ontology-and-knowledge-graph-modeling` for semantic models, ontologies, knowledge graphs and inference-ready structures.
- Use `knowledge-graph-rag` for Neo4j-native GraphRAG, KG-backed retrieval, text-to-Cypher, graph provenance and graph-grounded answer generation.
- Use `data-lineage-and-provenance` for source-to-target lineage, transformation evidence and provenance.

Use event-driven and real-time data skills to define business events, event schemas, streaming platforms, CDC, stream processing, event governance, lineage and real-time operability:

- Use `event-driven-architecture` for asynchronous event-first system design.
- Use `event-modeling` for business events, commands, decisions and event timelines.
- Use `event-streaming-platform-design` for Kafka/Pulsar/Event Hubs-style shared streaming platforms.
- Use `schema-registry-and-contracts` for event schemas, compatibility, versioning and contracts.
- Use `cdc-and-source-to-stream-ingestion` for change-data-capture and streaming ingestion.
- Use `stream-processing-patterns` for enrichment, joins, windows, stateful processing and event-time logic.
- Use `event-governance-and-lineage` for event ownership, metadata, classification, lineage and discoverability.
- Use `streaming-operations-and-slos` for lag, freshness, replay, back-pressure, SLOs and streaming operations.

Use enterprise-integration-patterns skills for message-based integration design and review:

- Use `message-based-integration-design` for integration style and topology selection.
- Use `message-channel-design` for queues, topics, delivery guarantees and dead-letter channels.
- Use `integration-message-construction` for command, event, document and request-reply contracts.
- Use `message-routing-design` for routers, splitters, aggregators and process managers.
- Use `message-transformation-design` for translators, enrichers, filters and canonical models.
- Use `message-endpoint-design` for producers, consumers, gateways and idempotent receivers.
- Use `messaging-system-management` for observability, replay, control and operational safety.
- Use `eip-integration-validation` after design or implementation to review against EIP criteria.
- Use `api-design-and-lifecycle` for HTTP/RPC OpenAPI contracts, versioning and API deprecation.

For architecture work, preserve traceability:

```text
strategy/outcome
→ capability
→ value stream/process
→ business information concept
→ conceptual/logical data model
→ data product/data contract
→ event/schema/stream where relevant
→ metadata, quality, security, lifecycle and lineage controls
```

Do not collapse business architecture, data architecture, event-driven architecture and enterprise integration patterns into one undifferentiated design. Keep capability, value stream, process, conceptual data, logical data, data product, contract, event, stream-processing and messaging-pattern concerns distinct, then link them explicitly.

### User experience and interface design

- Use `ux-design-principles` for user journeys, workflows, forms, navigation, information architecture and low-cognitive-load interfaces.
- Use `accessibility-wcag` for any user-facing interface, component, form, dashboard, content or interaction.
- Use `ui-component-design` for reusable frontend components, tables, cards, modals, forms and layout patterns.
- Use `frontend-state-and-interaction-design` for loading, empty, error, disabled, partial-success, optimistic, long-running and approval states.
- Use `data-product-dashboard-design` for dashboards covering data quality, profiling, validation, quarantine, refined datasets, lineage, audit and operations.
- Use `design-system-practice` for tokens, component variants, typography, spacing, patterns and UI consistency.
- Use `user-research-and-usability-testing` for validating whether users can complete important tasks.
- Use `agentic-ux-patterns` for interfaces where users supervise, approve, steer, constrain or audit AI/agent actions.

For user-facing work, do not build UI as a decorative wrapper around backend endpoints. Start from the user role, task, decision, required evidence, failure states, accessibility requirements and audit or approval needs.

For AI or agent-mediated workflows, always show what the agent plans to do, what it has done, why it recommends an action, what evidence supports it, what uncertainty remains, and what the user can approve, reject, edit or escalate.

### Reliability, SRE and DORA

- Use `sre-practice` for production reliability, operability, resilience and service ownership.
- Use `slo-error-budget-management` for SLIs, SLOs, error budgets, burn rates and release gating.
- Use `incident-response-and-postmortems` for incident handling, recovery, postmortems and corrective actions.
- Use `observability-and-telemetry` for logs, metrics, traces, dashboards, alerts and telemetry standards.
- Use `toil-reduction-and-automation` for safe reduction of repetitive operational work.
- Use `release-engineering-and-progressive-delivery` for canary releases, rollback, blue/green deployment, feature flags and release safety.
- Use `dora-four-keys` for DevOps Research and Assessment metrics: deployment frequency, lead time for changes, change failure rate, failed deployment recovery time and deployment rework rate (throughput and instability factors).
- Use `secure-sdlc-and-supply-chain` for SSDF-aligned delivery, SBOM and dependency/agent supply-chain controls.
- Use `finops-practice` for platform cloud spend, allocation, unit economics and cost anomalies (not agent-run token budgets).
- Use `performance-engineering` for latency, throughput, profiling and capacity evidence.
- Use `infrastructure-as-code` for declarative plan/apply infrastructure change.

For production, platform, CI/CD, operational resilience or service reliability work, load the relevant reliability skill from the flat `skills/` directory using the `reliability-and-delivery` grouping in `skills/PACK_METADATA.json` and `skills/MANIFEST.md`.

Do not treat reliability as only monitoring. Reliability work must connect user impact, service objectives, telemetry, incident response, release safety, operational evidence and continuous improvement.

In this repository, DORA means DevOps Research and Assessment delivery-performance metrics, not financial-services regulation.

## Trade-off rule

When KISS, SOLID, DRY, TDD, BDD, DDD, UX, SRE/DORA and architecture practices conflict, prefer correctness, safety, accessibility, user impact, regulatory/control evidence and externally visible business behaviour first, then reliability, data/architecture traceability, testability, maintainability and reuse. A small amount of explicit duplication is acceptable when it avoids premature or misleading abstraction. Do not add domain layers, interfaces, frameworks, agents, memory or learning mechanisms where a simpler verified implementation is sufficient.

## Safety and approval rules

Escalate for human approval before:

- destructive filesystem, database or infrastructure actions;
- changing authentication, authorisation, cryptography, secrets or security policy;
- weakening tests, validation, guardrails or audit logging;
- exposing sensitive data to external tools, LLMs or logs;
- making externally visible behaviour changes without tests or acceptance criteria;
- implementing autonomous actions with financial, legal, safety or compliance impact.

## Verification standard

Before finishing, provide:

1. Files changed.
2. Tests, checks or commands run and their result.
3. Behaviour intentionally changed.
4. Assumptions made.
5. Residual risks.
6. Next recommended action, if any.

## Global safety and security instructions

Before executing shell commands, modifying files, changing CI/CD, using tools, configuring MCP/A2A integrations, handling secrets, or making security-sensitive changes, read and follow:

- `AGENTIC_CODING_GLOBAL_SAFETY.md`
- `SECURE_AGENTIC_DEVELOPMENT.md`

These instructions are mandatory. They define safe command execution, approval requirements, destructive-command controls, least-privilege tool use, secret-handling rules, secure development expectations, and evidence required before claiming completion.

If these files conflict with a task-specific skill, follow the stricter safety and security requirement. Do not bypass tests, validation, guardrails, access controls, or approval gates unless the user explicitly authorises the specific exception.
