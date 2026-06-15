---
name: prioritisation
description: Use when an agent must rank tasks, goals, files, bugs, actions, alerts, or implementation options under limited time, resources, dependencies or risk.
---

# Prioritisation

## When to use

Use this skill when there are multiple possible actions and not all can or should be done immediately. Apply it to backlog triage, bug fixing, test selection, refactoring, incident response, tool calls, dependency upgrades and implementation sequencing.

## Core pattern

1. List candidate tasks or actions.
2. Define prioritisation criteria before scoring.
3. Score each candidate consistently.
4. Account for dependencies and blockers.
5. Select the next best action or ordered sequence.
6. Re-prioritise when new evidence arrives.

## Criteria

Use a simple weighted model unless the context demands more sophistication:

- urgency: time sensitivity or deadline;
- impact: value or risk reduction;
- confidence: likelihood of success;
- effort: estimated cost or complexity;
- dependency: whether other work depends on it;
- reversibility: cost of being wrong;
- safety/security: potential harm if delayed.

## Coding-agent guidance

During repository work, prioritise in this order unless instructed otherwise:

1. Prevent data loss or security exposure.
2. Restore broken builds or failing critical tests.
3. Fix user-visible defects.
4. Implement required acceptance criteria.
5. Improve maintainability where it reduces near-term risk.
6. Defer speculative refactoring.

## Guardrails

- Do not prioritise attractive low-value work over blocking risks.
- Do not ignore dependencies when selecting the next task.
- Do not let an LLM invent priorities without explicit criteria.
- Escalate conflicts between business value, safety and user instructions.

## Verification
- [ ] Candidate actions are listed.
- [ ] Criteria and weights are explicit.
- [ ] Dependencies are considered.
- [ ] Top priority has a clear rationale.
- [ ] Deferred items are recorded.

