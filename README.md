# Coding Agent Skill Library

A portable default reference library for repository-aware coding agents.

This repository is designed to be dropped into another repo and provide one coherent startup path, one skills inventory, and one layered documentation model:

- repository entrypoint: `AGENTS.md`
- immutable baseline: `skills/agent-control-patterns/apply-laws-of-ai/SKILL.md`
- portable contract: `skills_docs/LIBRARY_CONTRACT.md`
- routing guide: `skills_docs/HOW_TO_FIND_THE_RIGHT_SKILL.md`
- skills subtree index: `skills/README.md`
- full inventory: `skills/MANIFEST.md`
- execution guidance: the smallest relevant `SKILL.md`

## Mandatory startup order

Every agent session:

1. `AGENTIC_CODING_GLOBAL_SAFETY.md`
2. `SECURE_AGENTIC_DEVELOPMENT.md`
3. **`skills/agent-control-patterns/apply-laws-of-ai/SKILL.md`** (immutable baseline)
4. `skills_docs/HOW_TO_FIND_THE_RIGHT_SKILL.md` → smallest relevant `SKILL.md`

## Portable bootstrap

For a drop-in install, start with:

- `skills_docs/DROP_IN_BOOTSTRAP.md`
- `skills_docs/HOW_TO_FIND_THE_RIGHT_SKILL.md`

The library currently contains 87 `SKILL.md` files across eight categories (including mandatory `apply-laws-of-ai`).

## Recommended directory structure

```text
coding-agent-skill-library/
├── AGENTS.md
├── CLAUDE.md
├── README.md
├── AGENTIC_CODING_GLOBAL_SAFETY.md
├── SECURE_AGENTIC_DEVELOPMENT.md
├── skills/
│   ├── README.md
│   ├── MANIFEST.md
│   ├── agentic-patterns/
│   │   └── ...
│   ├── agent-control-patterns/
│   │   ├── apply-laws-of-ai/   # mandatory first skill
│   │   └── ...
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
    ├── DROP_IN_BOOTSTRAP.md
    └── templates/
```

## Installation into a project

For a new project, copy the contents of this directory into the root of the target repository:

```text
my-project/
├── AGENTS.md
├── CLAUDE.md
├── AGENTIC_CODING_GLOBAL_SAFETY.md
├── SECURE_AGENTIC_DEVELOPMENT.md
├── skills/
│   ├── README.md
│   ├── MANIFEST.md
│   ├── agentic-patterns/
│   ├── agent-control-patterns/
│   ├── engineering-practices/
│   ├── user-experience/
│   ├── reliability-and-delivery/
│   ├── event-driven-and-real-time-data/
│   ├── business-architecture/
│   └── data-architecture/
├── skills_docs/
│   ├── README.md
│   ├── LIBRARY_CONTRACT.md
│   ├── HOW_TO_FIND_THE_RIGHT_SKILL.md
│   └── DROP_IN_BOOTSTRAP.md
└── <project files>
```

If the target repository already has its own `README.md`, do not overwrite it. Keep this file as `docs/coding-agent-skill-library/README.md` or `AGENT_SKILLS_README.md`.

## Documentation model

- `AGENTS.md` is the required repository entrypoint with mandatory startup order.
- `skills/agent-control-patterns/apply-laws-of-ai/SKILL.md` is the immutable baseline skill.
- `skills_docs/LIBRARY_CONTRACT.md` defines portable consistency rules.
- `skills_docs/HOW_TO_FIND_THE_RIGHT_SKILL.md` is the canonical routing guide.
- `skills/README.md` explains how to traverse the portable `skills/` subtree.
- Category `README.md` files are quick routing pages.
- Category `MANIFEST.md` files are fuller inventories.
- `SKILL.md` files are the actual operating procedures.

## Validation

After installing all categories, validate the library with:

```bash
python3 scripts/validate_skills.py
./scripts/ci_local.sh
find skills -maxdepth 2 -name "README.md" | sort
find skills -name "SKILL.md" | sort
find skills -name "MANIFEST.md" | sort
```

With all eight categories installed, the library should contain **87 skills** (including mandatory `apply-laws-of-ai`).
