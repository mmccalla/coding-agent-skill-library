# Skills Manifest

This manifest indexes the categorised coding-agent skill library. Skills are stored recursively under `skills/`.

Use this command to list installed skills:

```bash
find skills -name "SKILL.md" | sort
```

After the existing agentic, control, engineering and user-experience skills are installed, the library should contain 41 skills.

## Directory model

| Directory | Contents | Status in this package |
|---|---|---|
| `skills/agentic-patterns/` | Core agent workflow patterns from Chapters 1-10. | Directory provided; drop existing skills here. |
| `skills/agent-control-patterns/` | Advanced agent control patterns from Chapters 11-20. | Directory provided; drop existing skills here. |
| `skills/engineering-practices/` | KISS, SOLID, DRY, TDD, BDD and DDD. | Fully populated. |
| `skills/user-experience/` | UX, accessibility, UI component, frontend-state, dashboard, design-system, usability-testing and agentic-UX skills. | Fully populated. |
| `skills/reliability-and-delivery/` | SRE, SLO/error-budget, incident, observability, toil-reduction, progressive-delivery and DORA Four Keys skills. | Fully populated. |

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

## Governance rule

Prefer the smallest useful skill set. Do not load or apply skills mechanically. When skills conflict, prioritise correctness, safety, accessibility, user impact, reliability, externally visible business behaviour, testability, maintainability and reuse in that order.
