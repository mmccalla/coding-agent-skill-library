# Drop-In Bootstrap

Use this library as a portable default reference set for any repository that supports repository-local agent guidance.

## Goal

Drop the library into a repo with one clear startup path for agents:

1. read repository `AGENTS.md`
2. read safety files and **execute `skills/agent-control-patterns/apply-laws-of-ai/SKILL.md`**
3. route through `skills_docs/HOW_TO_FIND_THE_RIGHT_SKILL.md`
4. open the relevant category `README.md`
5. load the smallest matching `SKILL.md`

## Minimum files to copy

Copy these into the target repository root:

- `AGENTS.md`
- `CLAUDE.md`
- `AGENTIC_CODING_GLOBAL_SAFETY.md`
- `SECURE_AGENTIC_DEVELOPMENT.md`
- `skills/`
- `skills_docs/`

## Recommended startup path for agents

- `AGENTS.md` is the mandatory repository entrypoint.
- `skills/agent-control-patterns/apply-laws-of-ai/SKILL.md` is the mandatory immutable baseline — first operational skill every session.
- `skills_docs/LIBRARY_CONTRACT.md` defines portable consistency rules.
- `skills_docs/HOW_TO_FIND_THE_RIGHT_SKILL.md` is the canonical routing guide.
- `skills/README.md` explains how the `skills/` subtree is structured.
- `skills/MANIFEST.md` is the canonical inventory.

## Portable-default rules

- Keep the library IDE-agnostic; do not require tool-specific rules or hooks.
- Keep `AGENTS.md` routing-oriented with explicit startup order.
- Keep `README.md` focused on install, structure and bootstrap.
- Keep `skills_docs/README.md` as the docs hub, not a second root README.
- Keep category `README.md` files lightweight and consistent.
- Keep category `MANIFEST.md` files as the fuller inventory for that category.
- Keep `SKILL.md` files as the executable guidance.

## Target repo structure

```text
target-repo/
├── AGENTS.md
├── CLAUDE.md
├── AGENTIC_CODING_GLOBAL_SAFETY.md
├── SECURE_AGENTIC_DEVELOPMENT.md
├── skills/
│   ├── README.md
│   ├── MANIFEST.md
│   ├── agentic-patterns/
│   ├── agent-control-patterns/
│   │   └── apply-laws-of-ai/   # mandatory first skill
│   ├── engineering-practices/
│   ├── user-experience/
│   ├── reliability-and-delivery/
│   ├── event-driven-and-real-time-data/
│   ├── business-architecture/
│   └── data-architecture/
└── skills_docs/
    ├── README.md
    ├── LIBRARY_CONTRACT.md
    ├── HOW_TO_FIND_THE_RIGHT_SKILL.md
    └── DROP_IN_BOOTSTRAP.md
```
