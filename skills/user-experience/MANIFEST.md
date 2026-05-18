# User Experience Skills Manifest

Use these skills for user-facing design, frontend implementation, dashboards, accessibility, design systems, usability validation and agent-supervision workflows.

| Skill | Use when | Avoid when |
|---|---|---|
| `ux-design-principles` | Designing journeys, task flows, navigation, forms, IA, workflow screens or low-cognitive-load interfaces. | The task is purely backend or infrastructure-only. |
| `accessibility-wcag` | Building or reviewing any user-facing interface, component, content, form, dashboard or interaction. | Do not avoid for user-facing work. |
| `ui-component-design` | Creating reusable frontend components, layouts, forms, tables, cards, modals, navigation or interaction patterns. | A disposable prototype with no reuse or production path. |
| `frontend-state-and-interaction-design` | Handling loading, empty, error, disabled, partial-success, optimistic, long-running or approval states. | Static documentation-only pages. |
| `data-product-dashboard-design` | Building dashboards for data quality, profiling, validation, quarantine, refined datasets, metadata, audit or operations. | Non-analytical UI work. |
| `design-system-practice` | Standardising tokens, variants, spacing, typography, interaction patterns and UI consistency. | Very small one-off prototypes. |
| `user-research-and-usability-testing` | Validating whether users can complete important tasks. | Purely technical refactors with no UX impact. |
| `agentic-ux-patterns` | Designing interfaces where users supervise, approve, steer, constrain or audit AI/agent actions. | Interfaces with no AI-mediated or agentic behaviour. |

## Recommended combinations

| Task | Recommended skills |
|---|---|
| New user-facing feature | `ux-design-principles`, `accessibility-wcag`, `frontend-state-and-interaction-design`, `ui-component-design` |
| Data quality dashboard | `data-product-dashboard-design`, `accessibility-wcag`, `frontend-state-and-interaction-design` |
| Quarantine triage screen | `data-product-dashboard-design`, `agentic-ux-patterns`, `accessibility-wcag`, `ux-design-principles` |
| Rule approval workflow | `agentic-ux-patterns`, `ux-design-principles`, `frontend-state-and-interaction-design`, `accessibility-wcag` |
| Design-system work | `design-system-practice`, `ui-component-design`, `accessibility-wcag` |
| Usability review | `user-research-and-usability-testing`, `ux-design-principles`, `accessibility-wcag` |

## General rules

- Start from the user task, not the data model or API endpoint.
- Identify the user role, decision, evidence needed, risk and success criterion.
- Make system state visible: loading, success, warning, partial success, error, blocked, awaiting approval and completed.
- For AI/agent workflows, show what the agent intends to do, what it has done, why it recommends an action, and what evidence supports it.
- Preserve accessibility, keyboard use, semantic markup and screen-reader compatibility.
