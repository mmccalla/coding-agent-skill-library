# Skills Manifest

This manifest indexes the coding-agent skill library. Skills are stored in a flat one-level layout under `skills/`, while categories remain semantic inventory groupings.

Use this command to list installed skills:

```bash
find skills -name "SKILL.md" | sort
```

After the agentic, control, engineering, user-experience, reliability-and-delivery, event-driven, enterprise-integration-patterns, business-architecture, solution-and-platform-architecture, data-architecture and KRAG systems skills are installed, the library should contain 113 skills (including mandatory `apply-laws-of-ai`).

## Workflow spine skills

Session and delivery skills added for discovery-through-ship flow:

- `skill-discovery-and-selection`, `requirements-elicitation`, `idea-refinement`
- `spec-driven-development`, `incremental-implementation`, `context-engineering`
- `source-driven-development`, `uncertainty-driven-development`
- `browser-testing-with-devtools`, `code-review-and-quality`, `git-workflow-and-versioning`
- `ci-cd-and-automation`, `deprecation-and-migration`, `documentation-and-adrs`, `shipping-and-launch`
- `knowledge-graph-rag` (graph-native RAG specialist)

Adjacent needs remain covered by existing agentic, control, engineering and architecture skills in the inventory below.

## Category model

| Category grouping | Contents | Status |
|---|---|---|
| `agentic-patterns` | Core agent workflow and session/spec/implementation spine. | Fully populated. |
| `agent-control-patterns` | Safety, guardrails, recovery, RAG, evaluation and prioritisation. | Fully populated. |
| `engineering-practices` | KISS, SOLID, DRY, TDD, BDD, DDD, test strategy and technical debt skills. | Fully populated. |
| `user-experience` | UX, accessibility, UI component, frontend-state, dashboard, design-system, usability-testing and agentic-UX skills. | Fully populated. |
| `reliability-and-delivery` | SRE, SLO/error-budget, incident, observability, browser verification, CI/CD, secure SDLC, FinOps, performance, IaC, deprecation, documentation, launch, toil-reduction, progressive-delivery and DORA delivery-metrics skills. | Fully populated. |
| `event-driven-and-real-time-data` | Event-driven architecture, event modelling, streaming platform, schema contract, CDC, stream processing, event governance and real-time operability skills. | Fully populated. |
| `enterprise-integration-patterns` | Message-based integration design, channels, construction, routing, transformation, endpoints, system management, EIP validation and API lifecycle skills. | Fully populated. |
| `business-architecture` | Capability, value-stream, process, operating-model, strategy traceability, maturity, business concept and organisation design skills. | Fully populated. |
| `solution-and-platform-architecture` | Solution options/NFRs and cloud platform/landing-zone architecture skills. | Fully populated. |
| `data-architecture` | DAMA-DMBOK2-aligned and CDMC-aware data modelling, products, contracts, metadata, governance, quality, security, lifecycle, integration, lakehouse, MDM/RDM, ontology and lineage skills. | Fully populated. |
| `krag-systems` | KRAG system design, ingestion/graph construction, retrieval/answering and evaluation/governance skills. | Fully populated. |

## Agentic patterns

These skills belong to the semantic `agentic-patterns` grouping in the flat `skills/` directory.

| Skill | Use when | Avoid when |
|---|---|---|
| `prompt-chaining` | A task needs a deterministic sequence of smaller LLM or tool steps. | A single direct implementation is clearer. |
| `routing` | Inputs need conditional dispatch to different tools, models, workflows or agents. | The path is fixed and does not need conditional logic. |
| `parallelization` | Independent branches can run concurrently to reduce latency. | Steps depend on each other or shared mutable state makes concurrency unsafe. |
| `reflection-and-verification` | Output needs critique, repair, tests or quality gates. | The task is trivial and already covered by deterministic validation. |
| `tool-use-and-function-calling` | An agent needs to call external tools, APIs, commands, databases or services. | The answer can be produced safely without external execution. |
| `planning-and-task-decomposition` | A complex goal needs an ordered executable plan. | The implementation path is obvious and small. |
| `multi-agent-collaboration` | Specialist roles and hand-offs materially improve the result. | A single module or agent can do the work more simply. |
| `skill-discovery-and-selection` | The agent must search a local skill library, compare candidates and choose the smallest valid skill set for the task. | The correct skill is already explicit and no discovery or routing work is needed. |
| `requirements-elicitation` | The task is underspecified and requirements, constraints or acceptance criteria must be clarified before implementation. | The requirements are already explicit, stable and testable. |
| `idea-refinement` | A rough concept needs shaping into a clearer problem statement, option set or implementation direction. | The problem and chosen direction are already concrete. |
| `spec-driven-development` | Work should be anchored in an explicit specification, contract or executable design artifact before code changes start. | A tiny local fix is faster and safer without creating a full spec. |
| `incremental-implementation` | A larger change needs to be broken into safe, reversible delivery slices. | The work is already minimal and can be completed in one verified step. |
| `context-engineering` | Relevant context must be selected, framed and bounded so the agent loads the right evidence without excess noise. | The task is self-contained and does not depend on broader context selection. |
| `source-driven-development` | Primary source material such as code, contracts, schemas or standards should drive the design and implementation. | There is no meaningful source corpus beyond the local change itself. |
| `uncertainty-driven-development` | The work has meaningful unknowns that need explicit assumptions, probes, validation steps or staged risk reduction. | The path is already well understood and low uncertainty. |
| `memory-management` | State, session history or long-term retrievable knowledge must be managed. | The task is stateless. |
| `learning-and-adaptation` | Improvements are measured, bounded, reversible and validated. | Changes cannot be evaluated or safely rolled back. |
| `mcp-server-design` | Capabilities need to be exposed as MCP tools, resources or prompts. | A local function or direct API call is sufficient. |

## Agent control patterns

These skills belong to the semantic `agent-control-patterns` grouping in the flat `skills/` directory.

| Skill | Use when | Avoid when |
|---|---|---|
| `apply-laws-of-ai` | **Mandatory first at every session.** Immutable baseline for all reasoning before any other skill, plan, or edit. | Never skip; no substitute or summary is acceptable. |
| `avoid-cognitive-biases` | Reviewing plans, recommendations, prioritisation or retrospectives for systematic cognitive bias before accepting conclusions. | Purely mechanical execution with no judgement or ranking left. |
| `avoid-fallacies` | Evaluating ADRs, reviews, security justifications or recommendations for logical fallacies in the reasoning chain. | Conclusions already fixed by executable checks alone. |
| `goal-setting-and-monitoring` | Objectives, success criteria, stop conditions or progress tracking are needed. | The task has a simple one-shot outcome. |
| `exception-handling-and-recovery` | Workflows need retries, fallbacks, rollback, graceful degradation or escalation. | Failure has no material impact and normal exceptions are enough. |
| `human-in-the-loop` | Human judgement, approval, review or escalation is required. | Fully automated execution is safe, tested and reversible. |
| `knowledge-retrieval-rag` | Answers or actions must be grounded in repository, document or knowledge-base content. Use `knowledge-graph-rag` when retrieval must be graph-native, Neo4j-backed or provenance-first. | The task does not need external grounding. |
| `inter-agent-communication-a2a` | Agents need task exchange, agent cards, messages or artefacts. | Direct function calls or simple orchestration are enough. |
| `resource-aware-optimization` | Cost, latency, context, model, compute or token budgets matter. | There is no meaningful resource constraint. |
| `reasoning-techniques` | Complex analysis, debugging, ReAct, code-aided reasoning or alternatives are needed. | Deterministic implementation or tests are enough. |
| `guardrails-safety-patterns` | Inputs, outputs, tools, policies or security controls need safeguards. | The work is low-risk and already validated. |
| `evaluation-and-monitoring` | Metrics, baselines, regression checks, observability or drift detection are needed. | The code is not operationally monitored and has no ongoing behaviour. |
| `prioritization` | Tasks, risks, bugs, alerts or actions need ranking. | There is only one viable next action. |
| `threat-modeling` | Security-sensitive design needs assets, trust boundaries, threats and mitigations. | Only runtime guardrails are required. |
| `ai-model-governance` | Models need inventory, risk tier, approval, monitoring or retirement. | Session safety laws or one-off metrics suffice. |
| `risk-management` | Material risks need a register, treatment and owners. | Only backlog ordering is required. |

## Engineering practices

These skills are fully included in this package and grouped under `engineering-practices`.

| Skill | Use when | Avoid when |
|---|---|---|
| `kiss-principle` | The implementation is more complex than the requirement demands. | Complexity is required for correctness, security, resilience or observability. |
| `solid-principles` | Classes, modules, services or agent components need clearer boundaries and testability. | A small script or simple function would be clearer than formal abstractions. |
| `dry-principle` | Repeated knowledge, rules, schemas or validation create maintenance risk. | Similar-looking code represents different concepts or may evolve separately. |
| `tdd-practice` | Behaviour can be specified with executable tests before implementation. | The test harness is absent and creating one is disproportionate to the change; create a minimal check instead. |
| `bdd-practice` | Business-readable acceptance criteria or user-facing behaviour need clarification. | The change is purely internal and has no observable business behaviour. |
| `ddd-practice` | The domain is complex enough to require explicit language, boundaries and invariants. | CRUD or simple scripting is sufficient. |
| `test-strategy` | Risk-based test levels, pyramid mix and exit criteria must be planned. | Only a single TDD or BDD loop is needed. |
| `technical-debt-management` | Debt needs inventory, interest and paydown tracking. | Only ranking today's tasks is required. |

## User experience and interface design

These skills are fully included in the flat library and grouped under `user-experience`.

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

These skills are fully included in the flat library and grouped under `reliability-and-delivery`.

DORA means **DevOps Research and Assessment** in this library, not financial-services regulation.

| Skill | Use when | Avoid when |
|---|---|---|
| `sre-practice` | Designing, operating or reviewing production services for reliability, operability, resilience and service ownership. | The work is a local-only prototype with no operational expectation. |
| `slo-error-budget-management` | Defining SLIs, SLOs, error budgets, burn rates, reliability targets or release gates. | There is no user-visible service or measurable reliability objective. |
| `incident-response-and-postmortems` | Handling incidents, operational failures, recovery, postmortems, learning reviews or corrective actions. | The issue is a simple local development error with no service impact. |
| `observability-and-telemetry` | Adding or reviewing logs, metrics, traces, dashboards, alerts or telemetry standards. | The task has no runtime behaviour or operational monitoring need. |
| `browser-testing-with-devtools` | Verifying browser-rendered behaviour with DOM, console, network and performance evidence from DevTools. | Static code inspection alone is sufficient and no runtime browser evidence is needed. |
| `ci-cd-and-automation` | Designing or improving CI pipelines, build automation, validation gates or delivery workflow automation. | The task does not affect build, test, release or automation workflows. |
| `deprecation-and-migration` | Replacing legacy paths, retiring obsolete interfaces or planning safe migrations with compatibility controls. | No deprecation, cutover or compatibility concern exists. |
| `documentation-and-adrs` | Durable technical documentation, ADRs or decision records are needed alongside implementation changes. | The task is a tiny local edit with no lasting decision or operational value. |
| `shipping-and-launch` | The work needs release readiness, launch checks, rollout coordination or post-launch follow-through. | There is no user-visible release or launch event. |
| `code-review-and-quality` | Changes need structured review for defects, regressions, risk and maintainability before acceptance. | The task is purely exploratory and not yet at a reviewable change point. |
| `git-workflow-and-versioning` | Source-control hygiene, branching, commits, tags or release/version workflow decisions matter. | No repository history or version-control action is involved. |
| `toil-reduction-and-automation` | Reducing repetitive manual operational work through safe, tested and auditable automation. | Automation would increase risk, hide judgement or remove necessary human approval. |
| `release-engineering-and-progressive-delivery` | Improving deployment safety through rollback, canary, blue/green, feature flags, release gates or staged rollout. | The task has no deployment or release impact. |
| `dora-four-keys` | Improving deployment frequency, lead time for changes, change failure rate, failed deployment recovery time or deployment rework rate. | The task is unrelated to software delivery performance. |
| `secure-sdlc-and-supply-chain` | Pipelines, dependencies, SBOM or agent supply chain need secure delivery controls. | Only runtime guardrails are required. |
| `finops-practice` | Platform cloud spend, allocation, unit economics or cost anomalies need FinOps practice. | Only an agent-run token/model budget is in scope. |
| `performance-engineering` | Latency, throughput or capacity must be measured and improved. | Only SLO policy or agent session budgets apply. |
| `infrastructure-as-code` | Infrastructure must change through declarative plan/apply workflows. | Only application CI is changing. |

### Reliability and delivery rules

- Connect reliability work to user impact, not only infrastructure health.
- Prefer measurable service objectives over vague “make it reliable” goals.
- Define operational evidence before claiming improvement.
- Alerts must be actionable and tied to symptoms users or services experience.
- Automate toil only when the automation is safer, tested, observable and reversible.
- Progressive delivery should reduce blast radius and improve rollback speed.
- DORA metrics should drive learning and improvement, not individual performance management.

## Event-Driven and Real-Time Data

These skills are fully included in the flat library and grouped under `event-driven-and-real-time-data`.

| Skill | Use when | Avoid when |
|---|---|---|
| `event-driven-architecture` | Designing asynchronous event-first systems, event-driven integration or decoupled producer/consumer flows. | A simple synchronous request/response call is sufficient and safer. |
| `event-modeling` | Discovering business events, commands, decisions, state changes and event timelines. | The task is purely technical plumbing with no business event semantics. |
| `event-streaming-platform-design` | Designing Kafka, Pulsar, Event Hubs or similar shared streaming platforms, topics, partitions, retention and replay. | A simple queue or direct integration is sufficient. |
| `schema-registry-and-contracts` | Defining event schemas, compatibility, versioning and producer/consumer obligations. | Payloads are local, temporary and not consumed by others. |
| `cdc-and-source-to-stream-ingestion` | Designing CDC or source-to-stream ingestion from databases, files, APIs or operational systems. | Batch extraction is sufficient and latency does not matter. |
| `stream-processing-patterns` | Designing filtering, enrichment, joins, windows, aggregation, stateful processing or event-time logic. | The transformation is simple and better handled in batch. |
| `event-governance-and-lineage` | Governing event ownership, classification, metadata, lineage, quality, retention and lifecycle. | Events are local implementation details with no reuse or compliance need. |
| `streaming-operations-and-slos` | Designing lag, freshness, replay, back-pressure, SLOs, alerts and incident response for streaming systems. | The stream is non-critical and not operationally monitored. |

### Event-driven rules

- Treat events as business facts where appropriate, not just messages.
- Define producer, consumer, schema, compatibility, partition key, ordering, idempotency, retention, replay and lineage before implementation.
- Design for duplicates unless the platform and processing model explicitly guarantee otherwise.
- Do not treat raw CDC records as business events without translation.

## Enterprise Integration Patterns

These skills are fully included in the flat library and grouped under `enterprise-integration-patterns`.

[Pattern names and taxonomy are derived from Enterprise Integration Patterns by Gregor Hohpe and Bobby Woolf](https://www.enterpriseintegrationpatterns.com/patterns/messaging/)

| Skill | Use when | Avoid when |
|---|---|---|
| `message-based-integration-design` | Choosing messaging, request-reply, file transfer, broker mediation or overall integration style/topology. | The work is a single local API call with no system boundary. |
| `message-channel-design` | Defining queues, topics, streams, dead-letter handling, bridges, adapters or delivery guarantees. | No transport or channel decision is required. |
| `integration-message-construction` | Creating command, event, document or request-reply message contracts and envelopes. | Payloads are ephemeral and not shared across systems. |
| `message-routing-design` | Building routers, filters, split/aggregate, scatter-gather, process managers or routing slips. | Routing is a trivial static destination. |
| `message-transformation-design` | Mapping schemas, enriching payloads, filtering content or defining canonical models. | Source and target already share an identical contract. |
| `message-endpoint-design` | Building producers, consumers, gateways, transactional clients or idempotent receivers. | No messaging endpoint is being implemented. |
| `messaging-system-management` | Adding monitoring, wire taps, message stores, test messages, replay or operational runbooks. | The integration is non-production and disposable. |
| `eip-integration-validation` | Reviewing an integration design or implementation against EIP and operability criteria. | No design artefact exists yet to review. |
| `api-design-and-lifecycle` | HTTP/RPC APIs need OpenAPI contracts, versioning and deprecation. | Dataset or event contracts are the focus. |

### Enterprise integration rules

- Separate channel, message construction, routing, transformation, endpoint and management decisions.
- Prefer asynchronous messaging when decoupling, buffering or independent deployment matters.
- Make message intent explicit: command, event, document or request/reply.
- Design for at-least-once delivery with idempotent receivers unless a stronger guarantee is proven.
- Use `eip-integration-validation` after design or implementation work.

Pack overview: `skills_docs/enterprise-integration-patterns.md`.

## Business Architecture

These skills are fully included in the flat library and grouped under `business-architecture`.

| Skill | Use when | Avoid when |
|---|---|---|
| `business-capability-modeling` | Defining stable business abilities, capability maps, capability levels, ownership and heatmaps. | The work is purely technical and has no business capability context. |
| `value-stream-modeling` | Mapping trigger-to-outcome value creation across stakeholders, stages, capabilities, data and systems. | The task only needs a local implementation workflow. |
| `process-modeling` | Modelling operational steps, decisions, hand-offs, controls, exceptions or automation opportunities. | The concern is stable business ability rather than procedural flow. |
| `operating-model-design` | Designing how people, process, technology, data, governance, funding and delivery work together. | The task is a narrow component-level design. |
| `strategy-to-execution-traceability` | Linking objectives, outcomes, capabilities, value streams, initiatives, metrics and evidence. | There is no strategic objective or portfolio context. |
| `capability-maturity-assessment` | Assessing current/target maturity, gaps, risks and roadmap priorities. | The user only needs a descriptive model. |
| `business-information-concept-modeling` | Deriving business concepts, entities and relationships from capabilities, value streams and processes. | The task is physical database design only. |
| `organization-and-role-design` | Defining roles, decision rights, accountabilities, team boundaries or ownership. | Organisation design is out of scope. |

### Business architecture rules

- Keep capabilities, value streams, processes, organisation, information concepts, initiatives and metrics distinct.
- Capabilities describe what the business must be able to do.
- Value streams describe how value flows from trigger to outcome.
- Processes describe how work is performed.
- Maintain traceability from strategy to capability, value stream, process, data, technology and metrics.

## Solution and Platform Architecture

These skills are fully included in the flat library and grouped under `solution-and-platform-architecture`.

| Skill | Use when | Avoid when |
|---|---|---|
| `solution-architecture` | Choosing system structure with NFRs, options, views and architecture governance. | Only a small change spec or ADR text is needed. |
| `cloud-platform-architecture` | Designing landing zones, tenancy, shared services and platform guardrails. | The work is a single product solution without shared platform scope. |

### Solution and platform architecture rules

- Separate product solution options from shared platform foundations.
- Record NFRs, alternatives and fitness functions or exceptions for material decisions.
- Require ownership, isolation and allocation tags on shared platform services.

## Data Architecture

These skills are fully included in the flat library and grouped under `data-architecture`.

The data architecture skills apply DAMA-DMBOK2-style separation of data management concerns and CDMC-style cloud/shared-data control expectations where relevant.

| Skill | Use when | Avoid when |
|---|---|---|
| `conceptual-data-modeling` | Identifying business concepts, entities and relationships independent of implementation. | The task is only physical schema tuning. |
| `logical-data-modeling` | Defining logical entities, attributes, identifiers, keys, relationships, constraints and reference data. | The work only needs a high-level conceptual model. |
| `data-product-design` | Designing domain-owned, governed, discoverable and reusable data products. | The dataset is temporary or single-use. |
| `data-contract-design` | Defining producer-consumer schema, semantics, quality, compatibility and operational obligations. | There is no stable producer-consumer boundary. |
| `metadata-management` | Designing business, technical, operational, governance, quality and lineage metadata. | Metadata is not needed beyond local code comments. |
| `data-governance-and-quality` | Defining ownership, policy, quality rules, controls, monitoring and remediation. | The task has no data risk, reuse or decision impact. |
| `data-security-and-privacy-architecture` | Designing classification, access, masking, privacy, entitlement and sensitive-data controls. | Data is public, local and non-sensitive with no shared access concerns. |
| `data-lifecycle-and-retention-management` | Designing retention, archival, deletion, legal hold and lifecycle controls. | Data is temporary and has no retention or disposal concern. |
| `data-integration-and-interoperability` | Designing batch, API, event, CDC, semantic or file-based integration patterns. | No system, domain, product or platform boundary is crossed. |
| `lakehouse-and-medallion-architecture` | Designing raw, quarantine, cleansed, refined and serving layers. | A simple transactional store is sufficient. |
| `master-and-reference-data-management` | Designing golden records, controlled values, identifiers, hierarchies, survivorship and stewardship. | There is no shared identity or controlled vocabulary problem. |
| `ontology-and-knowledge-graph-modeling` | Designing ontologies, semantic models, knowledge graphs, inference-ready structures or RDF/OWL-style models. | A relational/logical model is sufficient. |
| `knowledge-graph-rag` | Building Neo4j-native GraphRAG or KG-enabled RAG with text-to-Cypher, provenance, conceptual schema control and hybrid graph/vector retrieval. Load its one-level `reference/` files only when detailed lifecycle, code-pattern or testing guidance is needed. | Generic document RAG or ontology-only work is sufficient. |
| `data-lineage-and-provenance` | Tracking source-to-target lineage, transformation history, evidence, ownership and provenance. | The data is local, disposable and not reused. |

### Data architecture rules

- Separate conceptual, logical and physical concerns.
- Define ownership, classification, access/entitlement, metadata, quality rules, lineage/provenance, lifecycle/retention, consumer impact and audit evidence for material shared/cloud data.
- Treat data products as governed interfaces, not just datasets.
- Do not generate physical schemas before preserving business meaning and ownership.

## KRAG Systems

These skills are fully included in the flat library and grouped under `krag-systems`.

| Skill | Use when | Avoid when |
|---|---|---|
| `krag-system-design` | Designing KRAG architecture, graph role, retrieval strategy, provenance model and implementation slices. | Generic document RAG or ontology-only discussion is sufficient. |
| `krag-ingestion-graph-construction` | Building ingestion, extraction, evidence anchoring, entity resolution, graph construction and validation pipelines. | The work only needs lightweight chunking with no semantic graph. |
| `krag-retrieval-answering` | Implementing graph traversal, hybrid retrieval, ranking, grounded answering and abstention. | The graph is not part of retrieval or answer grounding. |
| `krag-evaluation-governance` | Defining KRAG-specific evaluation, observability, governance and release gates. | There is no KRAG runtime to evaluate or govern. |

### KRAG system rules

- The graph must materially improve retrieval, reasoning, provenance, navigation, governance or explainability.
- Do not treat a manually curated routing overlay as proof of KRAG capability.
- Keep source structure, semantic concepts, graph entities, claims and evidence anchors distinct.
- Require evidence-backed answers and explicit abstention when the graph cannot support the answer.

## Common combinations

| Scenario | Recommended skill sequence |
|---|---|
| New business-facing feature | `bdd-practice` → `ddd-practice` where domain complexity warrants it → `tdd-practice` → `reflection-and-verification` |
| Bug fix | `tdd-practice` → `exception-handling-and-recovery` if failure handling is involved → `reflection-and-verification` |
| Refactor | `tdd-practice` safety net → `kiss-principle` → `solid-principles` where boundaries are weak → `dry-principle` where duplication is harmful |
| Agent tool integration | `tool-use-and-function-calling` → `guardrails-safety-patterns` → `exception-handling-and-recovery` → `evaluation-and-monitoring` |
| RAG feature | `knowledge-retrieval-rag` → `guardrails-safety-patterns` → `evaluation-and-monitoring` → `resource-aware-optimization` |
| GraphRAG feature | `knowledge-graph-rag` → `knowledge-retrieval-rag` → `guardrails-safety-patterns` → `evaluation-and-monitoring` |
| KRAG system feature | `krag-system-design` → `krag-ingestion-graph-construction` → `krag-retrieval-answering` → `krag-evaluation-governance` |
| MCP feature | `mcp-server-design` → `tool-use-and-function-calling` → `guardrails-safety-patterns` → `exception-handling-and-recovery` |
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
| Delivery performance review | `dora-four-keys` → `prioritization` → `toil-reduction-and-automation` |
| Strategy to governed data product | `strategy-to-execution-traceability` → `business-capability-modeling` → `value-stream-modeling` → `data-product-design` → `data-contract-design` |
| BCM to conceptual data model | `business-capability-modeling` → `business-information-concept-modeling` → `conceptual-data-modeling` |
| Value stream to events | `value-stream-modeling` → `event-modeling` → `schema-registry-and-contracts` |
| Source-to-refined data pipeline | `lakehouse-and-medallion-architecture` → `data-contract-design` → `data-governance-and-quality` → `data-lineage-and-provenance` |
| Real-time data product | `event-modeling` → `data-product-design` → `schema-registry-and-contracts` → `event-governance-and-lineage` |
| Knowledge graph | `business-information-concept-modeling` → `conceptual-data-modeling` → `ontology-and-knowledge-graph-modeling` |
| Cloud/shared data control design | `data-security-and-privacy-architecture` → `metadata-management` → `data-lifecycle-and-retention-management` → `data-lineage-and-provenance` |

## Governance rule

Prefer the smallest useful skill set. Do not load or apply skills mechanically. When skills conflict, prioritise correctness, safety, accessibility, user impact, reliability, regulatory/control evidence, architecture traceability, externally visible business behaviour, testability, maintainability and reuse in that order.
