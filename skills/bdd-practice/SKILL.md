---
name: bdd-practice
description: Applies behaviour-driven development with business-readable scenarios linked to executable acceptance tests. Use when defining externally visible behaviour, acceptance criteria, or user-facing workflows before implementation.
aliases:
  - behavior-driven-development
  - bdd
---

# Behaviour-Driven Development (BDD)

## When to use

Use this skill when the task involves user journeys, acceptance criteria, cross-role collaboration, product behaviour, APIs, workflows, domain rules, or tests that must be understandable by business and technical stakeholders.

## Objective

Translate requirements into clear, testable behaviour using examples. Ensure implementation satisfies externally visible outcomes rather than internal design assumptions.

## Procedure

1. Identify the actor, goal, business rule, preconditions and expected outcome.
2. Express behaviour as concrete examples, preferably in Given/When/Then form.
3. Separate acceptance scenarios from implementation details.
4. Cover the main success path, meaningful alternatives, boundary cases and failure paths.
5. Automate scenarios where practical using the repository's acceptance-test framework.
6. Implement only the behaviour required to satisfy the scenarios.
7. Keep scenario language aligned with the domain vocabulary and DDD ubiquitous language where applicable.
8. Run acceptance tests and report evidence.

## Scenario format

```gherkin
Feature: <capability>

  Scenario: <specific behaviour>
    Given <initial context>
    And <relevant precondition>
    When <action or event>
    Then <observable outcome>
    And <important postcondition>
```

## Rules

- Do not use BDD scenarios as vague documentation; they must be specific enough to verify.
- Do not expose internal implementation details in scenario steps.
- Avoid combinatorial explosion; use representative examples and supplement with lower-level tests.
- Keep business terminology consistent across scenarios, code and documentation.
- When scenarios reveal ambiguity, stop and ask for clarification or encode the assumption explicitly.

## Related skills

- `spec-driven-development` — spec before scenarios
- `tdd-practice` — executable tests from scenarios
- `ddd-practice` — domain language in scenarios

## References

- [Cucumber — Behaviour-Driven Development](https://cucumber.io/docs/bdd/)
- [Gherkin reference](https://cucumber.io/docs/gherkin/reference/)

## Verification

- [ ] Scenarios added or updated in business-readable form.
- [ ] Acceptance tests run with results stated.
- [ ] Implemented behaviour matches scenarios.
- [ ] Stakeholder confirmation gaps noted.
