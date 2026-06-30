---
name: spec-driven-development
description: Use when a feature or significant change needs a decision-complete specification before implementation begins.
---

# Spec-Driven Development

## When to use
Use this skill when starting a new feature, changing externally visible behaviour, or making a non-trivial change that needs a clear specification before code or skill edits are made.

## Objective

Write a small, decision-complete spec that makes the implementation path obvious and testable.

## Procedure

1. Define the problem and desired outcome.
2. Name the user, operator or maintainer affected.
3. State the in-scope and out-of-scope behaviour.
4. Capture interfaces, inputs, outputs, states and failure modes.
5. Identify acceptance criteria and verification steps.
6. Note rollout, compatibility or migration concerns if they apply.
7. Break the spec into implementable slices only after the spec is clear.

Optional templates: `skills_docs/templates/agile-epic-template.md` and `skills_docs/templates/agile-user-story-template.md`.

## Rules

- Do not start coding before the spec is complete enough to test against.
- Do not bury key behaviour in prose when a checklist or table is clearer.
- Do not mix requirements, implementation notes and acceptance criteria without distinction.
- Prefer the smallest spec that removes ambiguity.

## Related skills

- `bdd-practice` — business-readable acceptance scenarios
- `incremental-implementation` — implement spec in verifiable slices
- `planning-and-task-decomposition` — break large specs into ordered work

## Verification

- [ ] Final behaviour and acceptance criteria captured.
- [ ] Edge cases and constraints documented.
- [ ] Out-of-scope behaviour stated.
- [ ] Compatibility or rollout concerns noted where relevant.
