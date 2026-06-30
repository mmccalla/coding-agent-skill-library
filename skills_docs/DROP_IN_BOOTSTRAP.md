# Drop-In Bootstrap

Use this library as a portable default reference set for any repository that supports repository-local agent guidance.

## Goal

Drop the library into a repo with one clear startup path for agents:

1. read repository `AGENTS.md`
2. read safety files and **execute `skills/apply-laws-of-ai/SKILL.md`**
3. route through `skills_docs/HOW_TO_FIND_THE_RIGHT_SKILL.md`
4. inspect `skills/MANIFEST.md` when category grouping context is needed
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
- `skills/apply-laws-of-ai/SKILL.md` is the mandatory immutable baseline — first operational skill every session.
- `skills_docs/LIBRARY_CONTRACT.md` defines portable consistency rules.
- `skills_docs/HOW_TO_FIND_THE_RIGHT_SKILL.md` is the canonical routing guide.
- `skills/README.md` explains how the `skills/` subtree is structured.
- `skills/MANIFEST.md` is the canonical inventory.

## Portable-default rules

- Keep the library IDE-agnostic; do not require tool-specific rules or hooks.
- Keep `AGENTS.md` routing-oriented with explicit startup order.
- Keep `README.md` focused on install, structure and bootstrap.
- Keep `skills_docs/README.md` as the docs hub, not a second root README.
- Keep semantic category grouping in `skills/PACK_METADATA.json`; treat `skills/MANIFEST.md` as the human-readable mirror.
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
│   ├── apply-laws-of-ai/       # mandatory first skill
│   ├── bdd-practice/
│   ├── knowledge-graph-rag/
│   ├── krag-system-design/
│   └── ...
└── skills_docs/
    ├── README.md
    ├── LIBRARY_CONTRACT.md
    ├── HOW_TO_FIND_THE_RIGHT_SKILL.md
    └── DROP_IN_BOOTSTRAP.md
```
