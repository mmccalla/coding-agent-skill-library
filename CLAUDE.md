# Claude Code Project Guidance

This repository uses a **hierarchical coding-agent skills library**.

Use `skills/MANIFEST.md` as the main index. Search recursively under `skills/` for the relevant `SKILL.md`. Load only the smallest relevant skill or combination of skills for the task.

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
- Agentic workflow and control skills when building or modifying agents, tools, MCP servers, A2A integrations, RAG systems, guardrails, memory, evaluation, recovery or monitoring.

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