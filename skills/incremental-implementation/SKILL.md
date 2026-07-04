---
name: incremental-implementation
description: Use when a change should land as a sequence of small, verifiable slices instead of a single large edit.
---

# Incremental Implementation

## When to use

Use this skill when a change touches multiple files, has rollback risk, or benefits from being delivered in small vertical slices with validation after each step.

## Objective

Reduce risk by implementing one coherent slice at a time and verifying each slice before moving on.

## Procedure

1. Choose the smallest meaningful slice of the overall change.
2. Make that slice self-contained.
3. Run the narrowest useful validation.
4. Confirm the slice preserves unrelated behaviour.
5. Repeat for the next slice only after the previous one is verified.
6. Keep each slice reversible if the repository supports that.

## Rules

- Do not bundle unrelated refactors into the same slice.
- Do not postpone validation until the end of a large change.
- Do not widen the scope when a smaller slice already satisfies the user request.
- Prefer explicit checkpoints over hidden progress.

## Related skills

- `planning-and-task-decomposition` — ordered plan before slicing
- `tdd-practice` — verify each slice with tests
- `reflection-and-verification` — quality gate per slice

## References

- [Agile Alliance — Incremental development](https://www.agilealliance.org/glossary/incremental-development/)

## Verification

- [ ] Slice scope and acceptance criteria stated.
- [ ] Validation run for the completed slice.
- [ ] Behaviour change and rollback path described.
- [ ] Next slice or residual risks noted.
