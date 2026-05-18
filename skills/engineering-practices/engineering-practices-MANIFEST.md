# Engineering Practices Skills Manifest

This manifest indexes the engineering-practice skills in this category. These skills guide coding agents when the task is primarily about software design quality, implementation discipline, testing practice, behaviour specification, or domain modelling.

## Directory

Place this file at:

```text
skills/engineering-practices/MANIFEST.md
```

Expected category structure:

```text
skills/engineering-practices/
├── MANIFEST.md
├── README.md
├── kiss-principle/
│   └── SKILL.md
├── solid-principles/
│   └── SKILL.md
├── dry-principle/
│   └── SKILL.md
├── tdd-practice/
│   └── SKILL.md
├── bdd-practice/
│   └── SKILL.md
└── ddd-practice/
    └── SKILL.md
```

## Skill selection guide

| Skill | Use when | Avoid when |
|---|---|---|
| `kiss-principle` | The code, workflow, architecture, or agent design is more complex than the requirement demands. | Complexity is required for correctness, security, resilience, observability, compatibility, or performance. |
| `solid-principles` | Classes, modules, services, tools, agents, or boundaries need clearer responsibilities, contracts, substitution, extensibility, or testability. | A simple function, script, or module is clearer than formal abstraction. |
| `dry-principle` | Repeated knowledge, business rules, schemas, validation, prompts, configuration, or integration logic create maintenance risk. | Similar-looking code represents different concepts, has different reasons to change, or may evolve separately. |
| `tdd-practice` | Implementing a feature, fixing a defect, or refactoring behaviour where tests can define or protect the expected outcome. | The work is exploratory, the requirement is not yet understood, or no useful assertion can be written yet. Clarify or spike first. |
| `bdd-practice` | Business-facing behaviour, acceptance criteria, scenarios, workflow rules, or cross-role alignment need to be expressed clearly. | The change is purely internal and has no meaningful externally observable behaviour. |
| `ddd-practice` | The problem contains meaningful domain complexity, business rules, bounded contexts, aggregates, invariants, or language ambiguity. | The task is CRUD-only, technically simple, or the domain language is not yet stable enough to model deeply. |

## Recommended combinations

### New business-facing feature

Use:

```text
bdd-practice → ddd-practice where domain complexity warrants it → tdd-practice → reflection-and-verification
```

Rationale:

1. BDD clarifies externally observable behaviour.
2. DDD clarifies domain language, boundaries, invariants, and model ownership.
3. TDD drives implementation safely from executable expectations.
4. Reflection and verification checks that the implementation still meets the intended behaviour.

### Defect fix

Use:

```text
tdd-practice → kiss-principle → reflection-and-verification
```

Rationale:

1. First reproduce the defect with a failing test.
2. Apply the smallest simple fix.
3. Verify the defect is fixed and no relevant behaviour regressed.

### Refactoring

Use:

```text
tdd-practice → kiss-principle → solid-principles where boundaries are weak → dry-principle where duplication is harmful
```

Rationale:

1. Tests provide a safety net.
2. KISS removes accidental complexity before introducing new structure.
3. SOLID is useful when responsibilities, interfaces, or dependencies need clearer boundaries.
4. DRY is applied last to avoid premature or misleading abstraction.

### Domain-heavy feature

Use:

```text
bdd-practice → ddd-practice → tdd-practice
```

Rationale:

1. BDD captures stakeholder-visible behaviour.
2. DDD turns domain language and invariants into a coherent model.
3. TDD implements the model with executable tests.

### Simplification or maintainability review

Use:

```text
kiss-principle → solid-principles if structure remains unclear → dry-principle if duplicated knowledge remains
```

Rationale:

1. Prefer simplification before abstraction.
2. Introduce boundaries only when they improve maintainability or testability.
3. Remove duplication only when it represents the same knowledge or behaviour.

## Conflict rules

Engineering principles can conflict. Resolve conflicts in this order:

1. Correctness and safety.
2. Security and privacy.
3. Required external behaviour.
4. Clarity and local reasoning.
5. Testability.
6. Maintainability.
7. Reuse.
8. Extensibility for plausible, evidenced change.

Apply these specific rules:

- KISS may justify retaining small explicit duplication instead of creating a premature abstraction.
- DRY should consolidate repeated knowledge, not merely similar-looking syntax.
- SOLID should improve real boundaries, not introduce interfaces for their own sake.
- TDD should not force brittle tests against implementation details.
- BDD should describe business behaviour, not technical implementation steps.
- DDD should be used where the domain complexity justifies modelling effort.

## Default operating standard

When using any engineering-practice skill, the coding agent should:

1. Inspect the existing code and conventions before changing anything.
2. State the intended change briefly.
3. Preserve public behaviour unless explicitly asked to change it.
4. Make the smallest useful change.
5. Add or update tests when behaviour is affected.
6. Avoid weakening validation, security, observability, or error handling.
7. Report actual evidence: files changed, tests run, checks performed, residual risks, and assumptions.

## Validation commands

From the repository root, check the category contains all six skills:

```bash
find skills/engineering-practices -name "SKILL.md" | sort
find skills/engineering-practices -maxdepth 2 -name "MANIFEST.md" -o -name "README.md" | sort
```

Expected `SKILL.md` count:

```text
6
```

You can verify with:

```bash
find skills/engineering-practices -name "SKILL.md" | wc -l
```
