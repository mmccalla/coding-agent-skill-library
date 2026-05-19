# Skills Manifest

This manifest indexes the categorised coding-agent skill library. Skills are stored recursively under `skills/`.

Use this command to list installed skills:

```bash
find skills -name "SKILL.md" | sort
```

After the existing agentic, control, engineering, user-experience, reliability-and-delivery, event-driven, business-architecture and data-architecture skills are installed, the library should contain 70 skills.

## Directory model

| Directory | Contents | Status in this package |
|---|---|---|
| `skills/agentic-patterns/` | Core agent workflow patterns from Chapters 1-10. | Directory provided; drop existing skills here. |
| `skills/agent-control-patterns/` | Advanced agent control patterns from Chapters 11-20. | Directory provided; drop existing skills here. |
| `skills/engineering-practices/` | KISS, SOLID, DRY, TDD, BDD and DDD. | Fully populated. |
| `skills/user-experience/` | UX, accessibility, UI component, frontend-state, dashboard, design-system, usability-testing and agentic-UX skills. | Fully populated. |
| `skills/reliability-and-delivery/` | SRE, SLO/error-budget, incident, observability, toil-reduction, progressive-delivery and DORA Four Keys skills. | Fully populated. |
| `skills/event-driven-and-real-time-data/` | Event-driven architecture, event modelling, streaming platform, schema contract, CDC, stream processing, event governance and real-time operability skills. | Fully populated. |
| `skills/business-architecture/` | Capability, value-stream, process, operating-model, strategy traceability, maturity, business concept and organisation design skills. | Fully populated. |
| `skills/data-architecture/` | DAMA-DMBOK2-aligned and CDMC-aware data modelling, products, contracts, metadata, governance, quality, security, lifecycle, integration, lakehouse, MDM/RDM, ontology and lineage skills. | Fully populated. |

## Agentic patterns

Place these existing skill folders under `skills/agentic-patterns/`.

| Skill | Use when | Avoid when |
|---|---|---|
| `prompt-chaining` | A task needs a deterministic sequence of smaller LLM or tool steps. | A single direct implementation is clearer. |
| `routing` | Inputs need conditional dispatch to different tools, models, workflows or agents. | The path is fixed and does not need conditional logic. |
| `parallelisation` | Independent branches can run concurrently to reduce latency. | Steps depend on each other or shared mutable state makes concurrency unsafe. |
| `reflection-and-verification` | Output needs critique, repair, tests or quality gates. | The task is trivial and already covered by deterministic validation. |
| `tool-use-function-calling` | An agent needs to call external tools, APIs, commands, databases or services. | The answer can be produced safely without external execution. |
| `planning-and-task-decomposition` | A complex goal needs an ordered executable plan. | The implementation path is obvious and small. |
| `multi-agent-collaboration` | Specialist roles and hand-offs materially improve the result. | A single module or agent can do the work more simply. |
| `memory-management` | State, session history or long-term retrievable knowledge must be managed. | The task is stateless. |
| `learning-and-adaptation` | Improvements are measured, bounded, reversible and validated. | Changes cannot be evaluated or safely rolled back. |
| `mcp-server-design` | Capabilities need to be exposed as MCP tools, resources or prompts. | A local function or direct API call is sufficient. |

## Agent control patterns

Place these existing skill folders under `skills/agent-control-patterns/`.

| Skill | Use when | Avoid when |
|---|---|---|
| `goal-setting-and-monitoring` | Objectives, success criteria, stop conditions or progress tracking are needed. | The task has a simple one-shot outcome. |
| `exception-handling-and-recovery` | Workflows need retries, fallbacks, rollback, graceful degradation or escalation. | Failure has no material impact and normal exceptions are enough. |
| `human-in-the-loop` | Human judgement, approval, review or escalation is required. | Fully automated execution is safe, tested and reversible. |
| `knowledge-retrieval-rag` | Answers or actions must be grounded in repository, document or knowledge-base content. | The task does not need external grounding. |
| `inter-agent-communication-a2a` | Agents need task exchange, agent cards, messages or artefacts. | Direct function calls or simple orchestration are enough. |
| `resource-aware-optimisation` | Cost, latency, context, model, compute or token budgets matter. | There is no meaningful resource constraint. |
| `reasoning-techniques` | Complex analysis, debugging, ReAct, code-aided reasoning or alternatives are needed. | Deterministic implementation or tests are enough. |
| `guardrails-safety-patterns` | Inputs, outputs, tools, policies or security controls need safeguards. | The work is low-risk and already validated. |
| `evaluation-and-monitoring` | Metrics, baselines, regression checks, observability or drift detection are needed. | The code is not operationally monitored and has no ongoing behaviour. |
| `prioritisation` | Tasks, risks, bugs, alerts or actions need ranking. | There is only one viable next action. |

## Engineering practices

These skills are fully included in this package under `skills/engineering-practices/`.

| Skill | Use when | Avoid when |
|---|---|---|
| `kiss-principle` | The implementation is more complex than the requirement demands. | Complexity is required for correctness, security, resilience or observability. |
| `solid-principles` | Classes, modules, services or agent components need clearer boundaries and testability. | A small script or simple function would be clearer than formal abstractions. |
| `dry-principle` | Repeated knowledge, rules, schemas or validation create maintenance risk. | Similar-looking code represents different concepts or may evolve separately. |
| `tdd-practice` | Behaviour can be specified with executable tests before implementation. | The test harness is absent and creating one is disproportionate to the change; create a minimal check instead. |
| `bdd-practice` | Business-readable acceptance criteria or user-facing behaviour need clarification. | The change is purely internal and has no observable business behaviour. |
| `ddd-practice` | The domain is complex enough to require explicit language, boundaries and invariants. | CRUD or simple scripting is sufficient. |

## User experience and interface design

These skills are fully included under `skills/user-experience/`.

| Skill | Use when | Avoid when |
|---|---|---|
| `ux-design-principles` | Designing user journeys, workflows, forms, navigation, information architecture or low-cognitive-load screens. | The task is purely backend, infrastructure-only or has no user-facing effect. |
| `accessibility-wcag` | Building or reviewing any user-facing interface, component, form, dashboard, content or interaction. | Do not avoid for user-facing work; apply at least a basic accessibility check. |
| `ui-component-design` | Creating reusable frontend components, layouts, forms, tables, cards, modals, navigation or interaction patterns. | A disposable prototype with no reuse, production path or accessibility expectation. |
| `frontend-state-and-interaction-design` | Handling loading, empty, error, disabled, partial-success, optimistic, long-running, retry or approval states. | Static documentation-only pages. |
| `data-product-dashboard-design` | Building dashboards for data quality, profiling, validation, cleansing, quarantine, refined datasets, lineage, audit or operations. | Non-analytical UI work with no metric, evidence or decision-support need. |
| `design-system-practice` | Standardising design tokens, component variants, spacing, typography, interaction patterns and UI consistency. | Very small one-off prototypes where a design system would add more overhead than value. |
| `user-research-and-usability-testing` | Validating whether target users can complete important tasks safely, accurately and efficiently. | Purely technical refactors with no user-facing behaviour change. |
| `agentic-ux-patterns` | Designing interfaces where users supervise, approve, steer, constrain or audit AI/agent actions. | Interfaces with no AI-mediated, agentic, approval or evidence-review behaviour. |

### UX rules

- Start from the user role, task, decision, required evidence and risk.
- Do not build UI as a decorative wrapper around backend endpoints.
- Make system state visible: loading, success, warning, partial success, error, denied, blocked, awaiting approval and completed.
- Preserve accessibility, keyboard use, semantic markup and screen-reader compatibility.
- For agentic workflows, show what the agent plans to do, what it has done, why it recommends an action, what evidence supports it, what uncertainty remains and what the user can approve, reject, edit or escalate.

## Reliability and Delivery

These skills are fully included under `skills/reliability-and-delivery/`.

DORA means **DevOps Research and Assessment** in this library, not financial-services regulation.

| Skill | Use when | Avoid when |
|---|---|---|
| `sre-practice` | Designing, operating or reviewing production services for reliability, operability, resilience and service ownership. | The work is a local-only prototype with no operational expectation. |
| `slo-error-budget-management` | Defining SLIs, SLOs, error budgets, burn rates, reliability targets or release gates. | There is no user-visible service or measurable reliability objective. |
| `incident-response-and-postmortems` | Handling incidents, operational failures, recovery, postmortems, learning reviews or corrective actions. | The issue is a simple local development error with no service impact. |
| `observability-and-telemetry` | Adding or reviewing logs, metrics, traces, dashboards, alerts or telemetry standards. | The task has no runtime behaviour or operational monitoring need. |
| `toil-reduction-and-automation` | Reducing repetitive manual operational work through safe, tested and auditable automation. | Automation would increase risk, hide judgement or remove necessary human approval. |
| `release-engineering-and-progressive-delivery` | Improving deployment safety through rollback, canary, blue/green, feature flags, release gates or staged rollout. | The task has no deployment or release impact. |
| `dora-four-keys` | Improving deployment frequency, lead time for changes, change failure rate or failed deployment recovery time. | The task is unrelated to software delivery performance. |

### Reliability and delivery rules

- Connect reliability work to user impact, not only infrastructure health.
- Prefer measurable service objectives over vague “make it reliable” goals.
- Define operational evidence before claiming improvement.
- Alerts must be actionable and tied to symptoms users or services experience.
- Automate toil only when the automation is safer, tested, observable and reversible.
- Progressive delivery should reduce blast radius and improve rollback speed.
- DORA metrics should drive learning and improvement, not individual performance management.

## Event-Driven and Real-Time Data

These skills are fully included under `skills/event-driven-and-real-time-data/`.

| Skill | Use when | Avoid when |
|---|---|---|
| `event-driven-architecture` | Designing asynchronous event-first systems, event-driven integration or decoupled producer/consumer flows. | A simple synchronous request/response call is sufficient and safer. |
| `event-modelling` | Discovering business events, commands, decisions, state changes and event timelines. | The task is purely technical plumbing with no business event semantics. |
| `event-streaming-platform-design` | Designing Kafka, Pulsar, Event Hubs or similar shared streaming platforms, topics, partitions, retention and replay. | A simple queue or direct integration is sufficient. |
| `schema-registry-and-contracts` | Defining event schemas, compatibility, versioning and producer/consumer obligations. | Payloads are local, temporary and not consumed by others. |
| `cdc-and-source-to-stream-ingestion` | Designing CDC or source-to-stream ingestion from databases, files, APIs or operational systems. | Batch extraction is sufficient and latency does not matter. |
| `stream-processing-patterns` | Designing filtering, enrichment, joins, windows, aggregation, stateful processing or event-time logic. | The transformation is simple and better handled in batch. |
| `event-governance-and-lineage` | Governing event ownership, classification, metadata, lineage, quality, retention and lifecycle. | Events are local implementation details with no reuse or compliance need. |
| `real-time-operability` | Designing lag, freshness, replay, back-pressure, SLOs, alerts and incident response for streaming systems. | The stream is non-critical and not operationally monitored. |

### Event-driven rules

- Treat events as business facts where appropriate, not just messages.
- Define producer, consumer, schema, compatibility, partition key, ordering, idempotency, retention, replay and lineage before implementation.
- Design for duplicates unless the platform and processing model explicitly guarantee otherwise.
- Do not treat raw CDC records as business events without translation.

## Business Architecture

These skills are fully included under `skills/business-architecture/`.

| Skill | Use when | Avoid when |
|---|---|---|
| `business-capability-modelling` | Defining stable business abilities, capability maps, capability levels, ownership and heatmaps. | The work is purely technical and has no business capability context. |
| `value-stream-modelling` | Mapping trigger-to-outcome value creation across stakeholders, stages, capabilities, data and systems. | The task only needs a local implementation workflow. |
| `process-modelling` | Modelling operational steps, decisions, hand-offs, controls, exceptions or automation opportunities. | The concern is stable business ability rather than procedural flow. |
| `operating-model-design` | Designing how people, process, technology, data, governance, funding and delivery work together. | The task is a narrow component-level design. |
| `strategy-to-execution-traceability` | Linking objectives, outcomes, capabilities, value streams, initiatives, metrics and evidence. | There is no strategic objective or portfolio context. |
| `capability-maturity-assessment` | Assessing current/target maturity, gaps, risks and roadmap priorities. | The user only needs a descriptive model. |
| `business-information-concept-modelling` | Deriving business concepts, entities and relationships from capabilities, value streams and processes. | The task is physical database design only. |
| `organisation-and-role-design` | Defining roles, decision rights, accountabilities, team boundaries or ownership. | Organisation design is out of scope. |

### Business architecture rules

- Keep capabilities, value streams, processes, organisation, information concepts, initiatives and metrics distinct.
- Capabilities describe what the business must be able to do.
- Value streams describe how value flows from trigger to outcome.
- Processes describe how work is performed.
- Maintain traceability from strategy to capability, value stream, process, data, technology and metrics.

## Data Architecture

These skills are fully included under `skills/data-architecture/`.

The data architecture skills apply DAMA-DMBOK2-style separation of data management concerns and CDMC-style cloud/shared-data control expectations where relevant.

| Skill | Use when | Avoid when |
|---|---|---|
| `conceptual-data-modelling` | Identifying business concepts, entities and relationships independent of implementation. | The task is only physical schema tuning. |
| `logical-data-modelling` | Defining logical entities, attributes, identifiers, keys, relationships, constraints and reference data. | The work only needs a high-level conceptual model. |
| `data-product-design` | Designing domain-owned, governed, discoverable and reusable data products. | The dataset is temporary or single-use. |
| `data-contract-design` | Defining producer-consumer schema, semantics, quality, compatibility and operational obligations. | There is no stable producer-consumer boundary. |
| `metadata-management` | Designing business, technical, operational, governance, quality and lineage metadata. | Metadata is not needed beyond local code comments. |
| `data-governance-and-quality` | Defining ownership, policy, quality rules, controls, monitoring and remediation. | The task has no data risk, reuse or decision impact. |
| `data-security-and-privacy-architecture` | Designing classification, access, masking, privacy, entitlement and sensitive-data controls. | Data is public, local and non-sensitive with no shared access concerns. |
| `data-lifecycle-and-retention-management` | Designing retention, archival, deletion, legal hold and lifecycle controls. | Data is temporary and has no retention or disposal concern. |
| `data-integration-and-interoperability` | Designing batch, API, event, CDC, semantic or file-based integration patterns. | No system, domain, product or platform boundary is crossed. |
| `lakehouse-and-medallion-architecture` | Designing raw, quarantine, cleansed, refined and serving layers. | A simple transactional store is sufficient. |
| `master-and-reference-data-management` | Designing golden records, controlled values, identifiers, hierarchies, survivorship and stewardship. | There is no shared identity or controlled vocabulary problem. |
| `ontology-and-knowledge-graph-modelling` | Designing ontologies, semantic models, knowledge graphs, inference-ready structures or RDF/OWL-style models. | A relational/logical model is sufficient. |
| `data-lineage-and-provenance` | Tracking source-to-target lineage, transformation history, evidence, ownership and provenance. | The data is local, disposable and not reused. |

### Data architecture rules

- Separate conceptual, logical and physical concerns.
- Define ownership, classification, access/entitlement, metadata, quality rules, lineage/provenance, lifecycle/retention, consumer impact and audit evidence for material shared/cloud data.
- Treat data products as governed interfaces, not just datasets.
- Do not generate physical schemas before preserving business meaning and ownership.

## Common combinations

| Scenario | Recommended skill sequence |
|---|---|
| New business-facing feature | `bdd-practice` → `ddd-practice` where domain complexity warrants it → `tdd-practice` → `reflection-and-verification` |
| Bug fix | `tdd-practice` → `exception-handling-and-recovery` if failure handling is involved → `reflection-and-verification` |
| Refactor | `tdd-practice` safety net → `kiss-principle` → `solid-principles` where boundaries are weak → `dry-principle` where duplication is harmful |
| Agent tool integration | `tool-use-function-calling` → `guardrails-safety-patterns` → `exception-handling-and-recovery` → `evaluation-and-monitoring` |
| RAG feature | `knowledge-retrieval-rag` → `guardrails-safety-patterns` → `evaluation-and-monitoring` → `resource-aware-optimisation` |
| MCP feature | `mcp-server-design` → `tool-use-function-calling` → `guardrails-safety-patterns` → `exception-handling-and-recovery` |
| Multi-agent workflow | `planning-and-task-decomposition` → `routing` → `multi-agent-collaboration` → `inter-agent-communication-a2a` where interoperability is needed |
| User-facing feature | `ux-design-principles` → `accessibility-wcag` → `frontend-state-and-interaction-design` → `ui-component-design` → `tdd-practice` |
| Data quality dashboard | `data-product-dashboard-design` → `accessibility-wcag` → `frontend-state-and-interaction-design` → `ui-component-design` |
| Quarantine triage screen | `data-product-dashboard-design` → `agentic-ux-patterns` → `ux-design-principles` → `accessibility-wcag` |
| Rule approval workflow | `agentic-ux-patterns` → `ux-design-principles` → `frontend-state-and-interaction-design` → `accessibility-wcag` |
| Agent supervision interface | `agentic-ux-patterns` → `frontend-state-and-interaction-design` → `accessibility-wcag` → `evaluation-and-monitoring` |
| Design-system change | `design-system-practice` → `ui-component-design` → `accessibility-wcag` |
| Usability validation | `user-research-and-usability-testing` → `ux-design-principles` → `accessibility-wcag` |
| Production service design | `sre-practice` → `slo-error-budget-management` → `observability-and-telemetry` |
| New operational dashboard | `observability-and-telemetry` → `slo-error-budget-management` → `data-product-dashboard-design` where UI is involved |
| Incident fix | `incident-response-and-postmortems` → `exception-handling-and-recovery` → `tdd-practice` → `observability-and-telemetry` |
| Release pipeline improvement | `release-engineering-and-progressive-delivery` → `dora-four-keys` → `evaluation-and-monitoring` |
| Toil reduction | `toil-reduction-and-automation` → `sre-practice` → `guardrails-safety-patterns` → `tdd-practice` |
| Reliability regression | `slo-error-budget-management` → `observability-and-telemetry` → `incident-response-and-postmortems` |
| Delivery performance review | `dora-four-keys` → `prioritisation` → `toil-reduction-and-automation` |
| Strategy to governed data product | `strategy-to-execution-traceability` → `business-capability-modelling` → `value-stream-modelling` → `data-product-design` → `data-contract-design` |
| BCM to conceptual data model | `business-capability-modelling` → `business-information-concept-modelling` → `conceptual-data-modelling` |
| Value stream to events | `value-stream-modelling` → `event-modelling` → `schema-registry-and-contracts` |
| Source-to-refined data pipeline | `lakehouse-and-medallion-architecture` → `data-contract-design` → `data-governance-and-quality` → `data-lineage-and-provenance` |
| Real-time data product | `event-modelling` → `data-product-design` → `schema-registry-and-contracts` → `event-governance-and-lineage` |
| Knowledge graph | `business-information-concept-modelling` → `conceptual-data-modelling` → `ontology-and-knowledge-graph-modelling` |
| Cloud/shared data control design | `data-security-and-privacy-architecture` → `metadata-management` → `data-lifecycle-and-retention-management` → `data-lineage-and-provenance` |

## Governance rule

Prefer the smallest useful skill set. Do not load or apply skills mechanically. When skills conflict, prioritise correctness, safety, accessibility, user impact, reliability, regulatory/control evidence, architecture traceability, externally visible business behaviour, testability, maintainability and reuse in that order.
