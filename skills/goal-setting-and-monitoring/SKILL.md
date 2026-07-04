---
name: goal-setting-and-monitoring
description: Use when implementing agents that need explicit objectives, measurable success criteria, progress tracking, stop conditions, or iterative improvement against goals.
---

# Goal Setting and Monitoring

## When to use

Use this skill when an agent must work towards a defined outcome rather than simply respond once. Apply it for coding tasks that need acceptance criteria, progress tracking, quality gates, iteration limits, or measurable completion.

## Objective

Define observable goals, measurable success criteria, stop conditions, and progress evidence for agent workflows.

## Procedure

1. Define the goal state in observable terms.
2. Capture the initial state: repository structure, failing tests, requirements, constraints and available tools.
3. Decompose the goal into sub-goals that can be checked independently.
4. Define measurable indicators for each sub-goal.
5. Execute work in small increments.
6. Monitor evidence after each increment: tests, linting, type checks, logs, benchmark results or user-visible artefacts.
7. Stop when success criteria are met, the iteration budget is exhausted, or risk requires escalation.

## Implementation guidance

Represent goals as structured data, not vague prose:

```json
{
  "goal": "Implement feature X",
  "success_criteria": ["tests pass", "public API documented", "no regression in existing behaviour"],
  "constraints": ["do not change database schema", "keep backwards compatibility"],
  "max_iterations": 5,
  "evidence": []
}
```

For coding agents, update the goal record after each tool action. Store what changed, what was verified, what failed, and what remains open.

## Guardrails

- Do not continue iterating without new evidence.
- Do not declare completion without checking the defined success criteria.
- Prefer deterministic checks over LLM judgement where tests, schemas, compilers or linters exist.
- Escalate when the goal is under-specified, safety-critical, or conflicts with repository constraints.

## References

- [Google SRE Book — Service Level Objectives](https://sre.google/sre-book/service-level-objectives/)

## Verification

- [ ] Goal and non-goals are explicit.
- [ ] Success criteria are measurable.
- [ ] Progress evidence is captured.
- [ ] Stop condition is explicit.
- [ ] Final answer reports completed, skipped and unresolved items.
