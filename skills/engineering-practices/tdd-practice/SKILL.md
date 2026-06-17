---
name: tdd-practice
description: Applies TDD: failing test first, smallest passing change, refactor under test protection. Use when adding behaviour, fixing defects, or refactoring with executable expectations.
---

# Test-Driven Development (TDD)

## When to use
Use this skill when adding behaviour, fixing a defect, refactoring risky code, creating library functions, implementing business rules, or improving code where expected behaviour can be specified with executable tests.

## Objective

Drive implementation from executable expectations. Produce code that is correct, minimal, refactorable and protected by targeted tests.

## Operating procedure

1. Identify the behaviour, edge cases and observable outcome.
2. Write the smallest failing test that proves the behaviour is missing or broken.
3. Run the test and confirm it fails for the expected reason.
4. Implement the smallest production change that makes the test pass.
5. Run the targeted test again and confirm it passes.
6. Refactor for clarity, KISS, SOLID or DRY only while tests remain green.
7. Add additional tests for meaningful edge cases, error paths, invariants and regression risks.
8. Run the narrowest relevant test suite before finishing.

## Rules

- Do not write broad implementation before the first failing test unless the repository has no viable test harness; if so, create a minimal harness first.
- Do not overfit tests to implementation details.
- Test public behaviour, contracts, boundaries and externally visible outcomes.
- Prefer deterministic tests over sleeps, live network calls, real secrets or brittle environment assumptions.
- Keep tests fast enough to support iterative development.
- Use mocks, fakes or fixtures for unstable external dependencies, but do not mock the unit under test so heavily that the test proves nothing.

## Related skills

- `code-review-and-quality` — review after tests pass
- `reflection-and-verification` — repair loop when checks fail
- `bdd-practice` — acceptance scenarios for external behaviour

## Verification

- [ ] Failing test added before production change.
- [ ] Production change made and targeted tests pass.
- [ ] Refactor performed only with tests green.
- [ ] Remaining untested risks stated.

## Additional guidelines

Apply these guidelines to maximise the benefits of TDD:

- **Team standards:** Establish team standards for test naming, structure and coverage so that tests remain consistent and maintainable.
- **Fast feedback loops:** Keep tests focused and run them frequently to maintain fast feedback loops and support iterative development.
- **Risk‑based coverage:** Allocate testing effort based on risk, focusing on high‑impact code paths rather than exhaustive coverage.
- **Continuous refactoring:** After tests pass, refactor code incrementally to remove duplication and improve design while keeping tests green.
- **CI and review integration:** Integrate tests into continuous integration pipelines and require tests to run during code review to enforce discipline and catch regressions early.
