---
name: frontend-state-and-interaction-design
description: Designs predictable states for loading, empty, error, partial, long-running and approval workflows. Use when implementing async UI, agent tasks, or multi-step forms.
---

# Frontend State and Interaction Design

## When to use
Use this skill when implementing async flows, long-running jobs, background workflows, forms, dashboards, approval flows, optimistic updates, error recovery, retry actions, partial success states or agent task execution.

## Objective

Make frontend behaviour predictable, recoverable and transparent across all meaningful states.

## Operating procedure

1. Identify all relevant states.
2. Define state transitions explicitly.
3. Make the current state visible.
4. Provide recovery actions for errors where possible.
5. Preserve user input during recoverable failures.
6. Distinguish empty, loading, error, denied, partial and complete states.
7. For long-running jobs, show progress, status, timestamps and next update behaviour.
8. For destructive or high-risk actions, require confirmation.
9. For optimistic updates, provide rollback or reconciliation.
10. Test transitions, not just final rendered output.

## Required states

Consider `idle`, `loading`, `validating`, `submitting`, `running`, `awaiting_approval`, `success`, `partial_success`, `empty`, `warning`, `error`, `denied`, `cancelled`, `retrying` and `stale`.

## Rules

- Do not show a spinner with no context for long-running work.
- Do not collapse policy denial, validation failure and system error into the same message.
- Do not lose user-entered data on validation failure.
- Do not use optimistic updates for irreversible or high-risk operations.
- Do not allow double submission unless the action is idempotent.
- Do not hide partial success where some records, rules or batches failed.

## DataOps-specific guidance

For source-to-refined workflows, show workflow run status, current step, timestamps, records processed, records passed, cleansed and quarantined, rule progress, approval status, retry/cancel options and links to audit, lineage and validation evidence.

## Verification

Report states implemented, transitions handled, recovery options, high-risk controls, tests or manual checks, and residual interaction risks.
