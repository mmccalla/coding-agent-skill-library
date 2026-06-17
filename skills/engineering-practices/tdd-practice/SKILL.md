---
name: tdd-practice
description: Applies TDD: failing test first, smallest passing change, refactor under test protection. Use when adding behaviour, fixing defects, or refactoring with executable expectations.
---

# Test-Driven Development (TDD)

## When to use

Use this skill when adding behaviour, fixing a defect, refactoring risky code, creating library functions, implementing business rules, or improving code where expected behaviour can be specified with executable tests.

## Objective

Drive implementation from executable expectations. Produce code that is correct, minimal, refactorable and protected by targeted tests.

## Procedure

1. Identify the behaviour, edge cases and observable outcome.
2. Write the smallest failing test that proves the behaviour is missing or broken.
3. Run the test and confirm it fails for the expected reason.
4. Implement the smallest production change that makes the test pass.
5. Run the targeted test again and confirm it passes.
6. Refactor for clarity, KISS, SOLID or DRY only while tests remain green.
7. Add additional tests for meaningful edge cases, error paths, invariants and regression risks.
8. Run the narrowest relevant test suite before finishing.

## Pytest source-aligned guidance

For Python projects, pytest recommends isolated development environments, package installation in editable mode for development, and conventional discovery using `test_*.py` or `*_test.py`. New projects should prefer a `src/` layout with `--import-mode=importlib` to avoid surprising import-path behaviour. When a repository uses `pyproject.toml`, keep pytest configuration there or in a dedicated pytest config file and prefer strict options such as `strict_config` and `strict_markers` where compatible with the pinned pytest version.

Do not use `python setup.py test` or `pytest-runner`; pytest documents that setuptools test integration is deprecated and can bypass modern packaging/security mechanisms.

Source: [pytest — Good Integration Practices](https://docs.pytest.org/en/latest/explanation/goodpractices.html).

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
