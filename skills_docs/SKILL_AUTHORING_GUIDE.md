# Skill Authoring Guide

Use this guide when creating or revising skills in this library. It complements `LIBRARY_CONTRACT.md`, which remains the mandatory portable contract.

## Authoring Principles

- Start from a concrete agent task, not a technology label.
- Write the `description` as routing metadata: include `Use when`, trigger terms, and the boundary where the skill applies.
- Treat `name`, `aliases` and `description` as the main runtime discovery surface; weak metadata causes missed or noisy matches.
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
aliases:
  - old-or-alternate-name
---

# Human Title

## When to use

## Objective

## Procedure

## Verification

- [ ] ...
```

`name` must match the parent folder. Supported frontmatter keys are defined in `skills_docs/LIBRARY_CONTRACT.md`; `aliases` are strongly recommended when a skill has an acronym, alternate spelling, superseded name or commonly used synonym.

## Naming And Alias Rules

- Prefer canonical US-English kebab-case for `name`.
- Prefer stable industry terms over repository-local shorthand.
- Use `aliases` for old names, alternate spellings, acronym expansions and likely user prompt phrasing.
- Keep renamed canonical IDs as aliases for at least one release cycle.
- Avoid aliases that could plausibly refer to a different existing skill.

## Selection Boundaries

Strong skills are easy to select and easy to reject. Include:

- a precise `description` with a clear `Use when` trigger;
- a focused `## When to use` section;
- a short `## When not to use` section whenever neighbouring skills are easy to confuse.

## Progressive Disclosure

Follow Anthropic's Agent Skills guidance: the agent sees skill names and descriptions first, then loads `SKILL.md`, then follows linked reference files only when needed. Split a skill when:

- the main file approaches the validator warning threshold;
- detailed examples are useful only for a subset of tasks;
- schemas, code patterns or testing contracts would distract from the core operating procedure.

Keep references one level deep under the skill folder, for example `reference/testing-contract.md`.

## Standards Grounding

When a skill encodes open standards, industry standards or authoritative best practice:

- name the standard explicitly (for example WCAG 2.2, ODCS, CloudEvents, AsyncAPI, BIZBOK, DORA, EIP, MCP, A2A, Google SRE Workbook);
- include a `## References` section with primary-source `http(s)` URLs;
- keep guidance current (for example DORA throughput/instability metrics including rework rate; multi-window multi-burn-rate SLO alerts; architectural HITL gates outside the model);
- do not duplicate identical numbered steps under both `## Procedure` and `## Core pattern`.

L3 practice validation enforces these rules for standards-sensitive skills:

```bash
python3 scripts/validate_skill_practice.py --all
```

## Quality Bar

Before proposing a skill change:

- run `python3 scripts/validate_skills.py`;
- run `python3 scripts/validate_skill_practice.py --all`;
- run `./scripts/ci_local.sh` for material changes;
- check that descriptions remain discoverable;
- verify related skill links use installed folder names;
- record source links when vendor or standards guidance is embedded.

## Sources

- Anthropic: [Equipping agents for the real world with Agent Skills](https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills)
- Library contract: `skills_docs/LIBRARY_CONTRACT.md`
