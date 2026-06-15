---
name: tdd-practice
description: Apply test-driven development by writing a failing test first, implementing the smallest passing change, and refactoring under test protection.
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

## Verification

Report the failing test added, the production change made, the final test result, any refactor performed, and remaining untested risks.
