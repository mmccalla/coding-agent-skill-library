---
name: ddd-practice
description: Applies domain-driven design with bounded contexts, aggregates, and ubiquitous language. Use when modelling complex business domains, defining boundaries, or protecting invariants.
---

# Domain-Driven Design (DDD)

## When to use
Use this skill when modelling complex business behaviour, designing service boundaries, refactoring an anemic domain model, defining aggregates, separating subdomains, aligning code with business language, or implementing domain rules that should not leak into infrastructure code.

## Objective

Create a maintainable domain model that reflects the business language, protects invariants, isolates bounded contexts and separates domain logic from technical plumbing.

## Operating procedure

1. Identify the business capability, subdomain and stakeholders.
2. Capture the ubiquitous language: key terms, events, commands, policies, invariants and ambiguous words.
3. Define bounded contexts and context boundaries before designing classes or services.
4. Classify domain concepts as entities, value objects, aggregates, domain services, repositories, domain events or application services.
5. Define aggregate boundaries around consistency rules, not database tables.
6. Keep domain logic in the domain layer; keep persistence, messaging, UI and external integrations in adapters or infrastructure.
7. Use domain events for important state changes that other components need to react to.
8. Validate the model with examples, tests and, where useful, BDD scenarios.

## Tactical modelling guidance

- Entity: has identity and lifecycle.
- Value object: immutable description with equality by value.
- Aggregate: consistency boundary with a root that protects invariants.
- Repository: persistence abstraction for aggregate roots.
- Domain service: domain operation that does not naturally belong to one entity or value object.
- Application service: orchestration layer; it coordinates use cases but should not contain core domain rules.
- Domain event: fact that something meaningful happened in the domain.

## Rules

- Do not create elaborate DDD structure for CRUD-only or simple scripting problems.
- Do not let database schemas dictate aggregate boundaries by default.
- Do not allow controllers, API handlers, ORM models or LLM prompts to become the only place where business rules live.
- Prefer explicit domain terms over generic technical names such as `Manager`, `Processor`, `Handler` or `Data`.
- Keep bounded contexts independent; integration between contexts should use explicit contracts, events or anti-corruption layers.

## Related skills

- `bdd-practice` — scenarios using ubiquitous language
- `spec-driven-development` — bounded context in specs
- `conceptual-data-modelling` — link domain concepts to data models
## Verification

- [ ] Bounded context and key domain terms stated.
- [ ] Aggregate or boundary decisions documented.
- [ ] Invariants protected identified.
- [ ] Modelling assumptions requiring business validation noted.

