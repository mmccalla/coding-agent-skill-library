---
name: kiss-principle
description: Applies KISS to simplify code, architecture, workflows and agent designs without losing required behaviour. Use when reducing over-engineering, speculative abstractions, or unnecessary agent complexity.
aliases:
  - keep-it-simple
  - kiss
---

# KISS Principle

## When to use
Use this skill when simplifying code, reviewing design complexity, reducing cognitive load, choosing between alternative implementations, or preventing over-engineering.

## Objective

Deliver the simplest maintainable solution that satisfies the current requirement, preserves required behaviour, and remains testable.

## Procedure

1. State the required behaviour and constraints.
2. Identify accidental complexity: unused layers, speculative abstractions, redundant configuration, excessive indirection, unclear control flow, and unnecessary dependencies.
3. Identify essential complexity: domain rules, security controls, validation, observability, error handling, concurrency, persistence and compatibility requirements.
4. Remove or reduce accidental complexity first.
5. Prefer direct code, explicit names, small functions, local reasoning and boring dependencies.
6. Keep abstractions only when they demonstrably reduce change cost, isolate volatility, improve testability, or protect a stable boundary.
7. Validate behaviour with the narrowest useful tests.

## Rules

- Do not simplify by weakening correctness, security, validation, observability, error handling or tests.
- Do not introduce a framework where a function or small module is sufficient.
- Do not introduce generality for hypothetical future requirements.
- Prefer readable duplication over premature abstraction when the duplication is small and likely to evolve differently.
- Preserve existing public behaviour unless the requested change explicitly requires otherwise.

## Verification

- [ ] Simplification described with rationale.
- [ ] Retained complexity justified.
- [ ] Tests or checks run reported.
- [ ] Residual risks or assumptions stated.
