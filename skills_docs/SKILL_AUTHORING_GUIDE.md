# Skill Authoring Guide

Use this guide when creating or revising skills in this library. It complements `LIBRARY_CONTRACT.md`, which remains the mandatory portable contract.

## Authoring Principles

- Start from a concrete agent task, not a technology label.
- Write the `description` as routing metadata: include `Use when`, trigger terms, and the boundary where the skill applies.
- Keep `SKILL.md` concise enough for routine context loading; move long examples, schemas and implementation details into one-level reference files.
- Prefer deterministic checklists, templates, schemas and tests over broad advice.
- Keep product-specific or project-specific guidance in `skills_docs/overlays/`, not in portable core skills.
- Treat bundled scripts as executable tools: keep them deterministic, typed, local, dependency-light and covered by tests.

## Required Shape

Every skill must use:

```markdown
---
name: folder-name
description: Use when ...
---

# Human Title

## When to use

## Objective

## Procedure

## Verification

- [ ] ...
```

`name` must match the parent folder. The only supported frontmatter keys are `name` and `description`.

## Progressive Disclosure

Follow Anthropic's Agent Skills guidance: the agent sees skill names and descriptions first, then loads `SKILL.md`, then follows linked reference files only when needed. Split a skill when:

- the main file approaches the validator warning threshold;
- detailed examples are useful only for a subset of tasks;
- schemas, code patterns or testing contracts would distract from the core operating procedure.

Keep references one level deep under the skill folder, for example `reference/testing-contract.md`.

## Quality Bar

Before proposing a skill change:

- run `python3 scripts/validate_skills.py`;
- run `./scripts/ci_local.sh` for material changes;
- check that descriptions remain discoverable;
- verify related skill links use installed folder names;
- record source links when vendor or standards guidance is embedded.

## Sources

- Anthropic: [Equipping agents for the real world with Agent Skills](https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills)
- Library contract: `skills_docs/LIBRARY_CONTRACT.md`
