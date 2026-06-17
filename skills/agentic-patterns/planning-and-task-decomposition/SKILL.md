---
name: planning-and-task-decomposition
description: Use when a coding request is too complex for a single edit or command and must be decomposed into ordered, dependency-aware implementation steps.
---

# Planning and Task Decomposition

## When to use

Use this skill for multi-step implementation, refactoring, migration, debugging, architecture or repository-generation tasks. Use planning when the path is not fully known, dependencies must be discovered, or several tools/files must be coordinated.

Do not over-plan routine one-file changes.

## Implementation pattern

1. State the objective and acceptance criteria.
2. Inspect the repository or available artefacts.
3. Identify constraints, dependencies and unknowns.
4. Decompose the goal into small executable steps.
5. Order steps by dependency and risk.
6. Execute incrementally, verifying after each material change.
7. Adapt the plan when evidence invalidates an assumption.

## Coding guidance

- Keep the plan actionable, not aspirational.
- Prefer a shallow plan with clear checkpoints.
- Avoid speculative architecture unless justified by the requirement.
- Use explicit deferred-work notes only for work intentionally postponed and disclosed.

## Related skills

- `incremental-implementation` — execute plan as small slices
- `spec-driven-development` — decision-complete spec before coding
- `using-agent-skills` — select supporting skills per step
## Verification
- [ ] Objective and acceptance criteria are clear.
- [ ] Plan steps are executable and ordered.
- [ ] Unknowns and assumptions are explicit.
- [ ] Verification steps are included.
- [ ] Plan was updated if implementation evidence changed it.

## Additional guidance

Strengthen planning and task decomposition by applying these guidelines:

- **Dependency and unknowns mapping:** Identify and document dependencies and unknowns early to inform the ordering of tasks and reduce surprises.
- **Periodic checkpoints:** Include periodic checkpoints to revisit assumptions and adjust the plan based on evidence gathered during execution.
- **Definition‑of‑Done criteria:** Establish clear exit criteria aligned with the Definition of Done for each plan segment to avoid premature closure.
- **Progress metrics:** Measure plan execution using metrics such as tasks completed and verification steps performed to provide objective feedback.
- **Contingency plans:** Define escalation and contingency paths for tasks that encounter persistent blockers or high uncertainty.
