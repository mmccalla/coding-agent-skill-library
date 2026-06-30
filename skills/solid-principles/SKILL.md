---
name: solid-principles
description: Applies SOLID for modularity, dependency boundaries and testability without over-engineering. Use when refactoring modules, services, agents, or dependency boundaries.
aliases:
  - solid-design
  - solid
---

# SOLID Principles

## When to use
Use this skill when designing or refactoring classes, modules, services, interfaces, dependency boundaries, plug-ins, tools, agents, MCP servers or A2A components.

## Objective

Improve maintainability and testability by ensuring code has clear responsibilities, stable boundaries, substitutable components, focused interfaces and explicit dependencies.

## Procedure

1. Identify the unit under change: class, module, service, tool, agent or workflow.
2. Check Single Responsibility: each unit should have one reason to change.
3. Check Open/Closed: extension should not require risky modification of stable code paths.
4. Check Liskov Substitution: implementations must honour the contract expected by callers.
5. Check Interface Segregation: consumers should depend only on methods, fields or capabilities they actually use.
6. Check Dependency Inversion: high-level policy should depend on abstractions or ports, not concrete infrastructure details.
7. Apply the smallest refactor that improves the design.
8. Add or update tests around the changed boundary.

## Rules

- Do not create abstract interfaces unless there is a real boundary, more than one implementation, a test seam, or likely volatility.
- Do not split code so aggressively that behaviour becomes harder to trace.
- Prefer composition over inheritance unless inheritance clearly models a stable substitutable relationship.
- Keep contracts explicit with types, schemas, protocols or tests.
- Preserve public behaviour unless explicitly asked to change it.

## Verification

- [ ] SOLID issue addressed identified.
- [ ] Design boundary change described.
- [ ] Tests or checks run reported.
- [ ] Residual risks or assumptions stated.
