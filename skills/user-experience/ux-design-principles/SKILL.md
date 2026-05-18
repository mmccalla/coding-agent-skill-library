---
name: ux-design-principles
description: Apply practical UX design principles to create clear, task-centred, low-cognitive-load user journeys, navigation, forms and workflows.
---

# UX Design Principles

## When to use this skill

Use this skill when designing or changing user journeys, task flows, forms, navigation, information architecture, workflow screens, review and approval flows, onboarding screens, or data-quality user journeys.

## Objective

Create user-facing workflows that help users complete meaningful tasks with minimal cognitive load, clear feedback, visible system status, and explicit evidence for decisions.

## Operating procedure

1. Identify the primary user role.
2. State the task the user is trying to complete.
3. Identify the user's decision point and required evidence.
4. Map the smallest useful flow from entry point to completion.
5. Identify states: default, loading, empty, success, warning, error, partial success, blocked and awaiting approval.
6. Remove unnecessary choices, fields, screens and jargon.
7. Group information by user decision, not backend structure.
8. Apply progressive disclosure for advanced or high-risk details.
9. Make next actions explicit.
10. Validate the flow against accessibility, error recovery and evidence needs.

## Rules

- Do not start by mirroring database tables, API endpoints or internal architecture.
- Do not make users infer system status from missing information.
- Do not hide failures, warnings, partial results or uncertainty.
- Do not overload a single screen with all available data.
- Do not ask for information the system already knows.
- Prefer clear task language over implementation terms.

## DataOps-specific guidance

For source-to-refined and quarantine workflows, users must be able to understand which source is being processed, what metadata was generated, which rules were applied, which records passed, which records failed, why records were quarantined, what cleansing was applied, what approvals are required, and what evidence supports the result.

## Verification

Report the user role, primary task, key screens or flow steps changed, states handled, accessibility considerations, assumptions, residual UX risks, and tests or manual checks performed.
