# Repository Instructions for Coding Agents

This repository uses a **hierarchical `skills/` directory**. Each skill is a reusable operating procedure for a specific type of coding-agent task.

Read `skills/MANIFEST.md` first, then search recursively under `skills/` and load only the smallest relevant `SKILL.md` file or skill combination needed for the task.

## Skill directory structure

Search recursively for skills under:

```text
skills/
├── agentic-patterns/
├── agent-control-patterns/
├── engineering-practices/
├── user-experience/
└── reliability-and-delivery/
```

Do not assume a skill from its name alone. Open and read the relevant `SKILL.md` before applying it.

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
- Use `parallelisation` for independent concurrent operations where concurrency improves latency without reducing determinism or safety.
- Use `reflection-and-verification` for critique, repair, tests, review loops and quality gates.
- Use `planning-and-task-decomposition` when a complex objective must become an executable, ordered plan.
- Use `multi-agent-collaboration` only when specialised roles and explicit hand-offs materially improve the outcome.

### Tooling, integration and knowledge access

- Use `tool-use-function-calling` for safe external tool, API, database, command or service execution.
- Use `mcp-server-design` when exposing agent-friendly tools, resources or prompts through MCP.
- Use `knowledge-retrieval-rag` when repository, document or knowledge-base grounding is required.
- Use `inter-agent-communication-a2a` for cross-agent delegation, agent cards, task exchange, artefact exchange or A2A-style interoperability.
- Use `memory-management` for short-term state, long-term memory, retrieval, summarisation or persistence across sessions.

### Reliability, control and governance

- Use `goal-setting-and-monitoring` for measurable objectives, success criteria, stop conditions and progress tracking.
- Use `exception-handling-and-recovery` for error detection, retries, fallbacks, rollback, graceful degradation and escalation.
- Use `human-in-the-loop` for human approval, review, judgement or escalation.
- Use `guardrails-safety-patterns` for input validation, output checks, tool restrictions, safety policies and secure defaults.
- Use `evaluation-and-monitoring` for metrics, baselines, regression tests, observability, drift detection and operational monitoring.

### Optimisation and advanced intelligence

- Use `resource-aware-optimisation` for cost, latency, context-window, token, compute, model-selection and budget trade-offs.
- Use `reasoning-techniques` for complex debugging, design reasoning, code-aided reasoning, ReAct-style tool loops and alternative-path exploration.
- Use `prioritisation` for ranking tasks, bugs, risks, requirements, alerts or next actions.
- Use `learning-and-adaptation` only when improvement is measured, bounded, reversible and validated.

### Engineering design and delivery practices

- Use `kiss-principle` to simplify over-engineered code, workflows, architectures or agent designs.
- Use `solid-principles` to improve modularity, dependency boundaries, substitutability, extensibility and testability.
- Use `dry-principle` to remove harmful duplication while avoiding premature or misleading abstraction.
- Use `tdd-practice` to add or change behaviour through a failing test, smallest passing implementation and refactor loop.
- Use `bdd-practice` to express business-readable behaviour, acceptance criteria and user-facing scenarios.
- Use `ddd-practice` to model complex domains using bounded contexts, ubiquitous language, aggregates, value objects, domain events and protected invariants.

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
- Use `dora-four-keys` for DevOps Research and Assessment metrics: deployment frequency, lead time for changes, change failure rate and failed deployment recovery time.

For production, platform, CI/CD, operational resilience or service reliability work, load the relevant reliability skill from `skills/reliability-and-delivery/`.

Do not treat reliability as only monitoring. Reliability work must connect user impact, service objectives, telemetry, incident response, release safety, operational evidence and continuous improvement.

In this repository, DORA means DevOps Research and Assessment delivery-performance metrics, not financial-services regulation.

## Trade-off rule

When KISS, SOLID, DRY, TDD, BDD, DDD, UX and SRE/DORA practices conflict, prefer correctness, safety, accessibility, user impact and externally visible business behaviour first, then reliability, testability, maintainability and reuse. A small amount of explicit duplication is acceptable when it avoids premature or misleading abstraction. Do not add domain layers, interfaces, frameworks, agents, memory or learning mechanisms where a simpler verified implementation is sufficient.

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