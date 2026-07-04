---
name: dry-principle
description: Applies DRY to remove harmful duplication while avoiding misleading abstraction. Use when refactoring repeated knowledge, schemas, validation rules, or agent instructions.
aliases:
  - dont-repeat-yourself
  - dry
---

# DRY Principle

## When to use

Use this skill when reviewing repeated code, configuration, schemas, prompts, tests, error handling, validation or business rules.

## Objective

Remove duplication of knowledge and behaviour where it creates maintenance risk, while preserving clarity and avoiding premature abstraction.

## Procedure

1. Identify the duplicated elements.
2. Classify the duplication as harmless coincidence, repeated syntax, repeated business rule, repeated validation, repeated integration logic, repeated configuration, repeated prompt or repeated agent instruction.
3. Consolidate only when the duplication represents the same knowledge or is likely to change together.
4. Choose the least complex consolidation mechanism: helper function, constant, schema, shared module, template, configuration, policy or test fixture.
5. Keep intentionally separate code paths where similar-looking logic serves different business meanings.
6. Add tests to prove the consolidated behaviour remains correct.

## Rules

- Do not abstract merely because two blocks look similar.
- Do not create a shared abstraction that hides meaningful differences.
- Do not centralise volatile code too early.
- Prefer explicit duplication over a misleading abstraction.
- Centralise business rules, validation rules, schemas and security policies when they must remain consistent.

## References

- [C2 Wiki — Don't Repeat Yourself](https://wiki.c2.com/?DontRepeatYourself)

## Verification

- [ ] Duplication removed or deliberately retained with reason.
- [ ] Any new abstraction justified as safe.
- [ ] Tests or checks run reported.
- [ ] Residual risks or assumptions stated.
