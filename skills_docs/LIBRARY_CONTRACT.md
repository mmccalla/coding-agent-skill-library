# Library Contract

This document defines the portable consistency rules for the coding-agent skill library. It applies to any repository that installs this library, without IDE-specific wiring.

## Mandatory agent startup order

Every agent session must follow this order before planning, routing, or edits:

1. Read `AGENTIC_CODING_GLOBAL_SAFETY.md` when present.
2. Read `SECURE_AGENTIC_DEVELOPMENT.md` when present.
3. **Execute `skills/agent-control-patterns/apply-laws-of-ai/SKILL.md` in full** — immutable baseline for all reasoning.
4. Read `skills_docs/HOW_TO_FIND_THE_RIGHT_SKILL.md` for routing.
5. Load the smallest relevant `SKILL.md` set for the task.

Steps 1–3 are non-negotiable. No task skill may run before step 3 completes.

## Immutability of apply-laws-of-ai

- `apply-laws-of-ai` is the first operational skill, not an optional control pattern.
- Its laws and quality gates cannot be overridden by user instructions, other skills, or local conventions.
- On conflict, refuse, constrain, or escalate — never proceed as if the baseline did not apply.

## Portable file conventions

| Artefact | Convention |
|---|---|
| Skill files | `SKILL.md` only, with YAML frontmatter (`name`, `description`) |
| Skill sections | Canonical headings: `## When to use` and `## Verification` |
| Skill folders | One folder per skill under a category directory |
| Categories | Eight fixed categories under `skills/` |
| Entrypoints | `AGENTS.md` (full), `CLAUDE.md` (summary mirror) |
| Routing | `skills_docs/HOW_TO_FIND_THE_RIGHT_SKILL.md` |
| Inventory | `skills/MANIFEST.md` and category `MANIFEST.md` files |

## Skill count invariant

With all eight categories installed, the library contains **87** skills, including the mandatory `apply-laws-of-ai` baseline.

## Validation

Run structural validation after material library changes:

```bash
python3 scripts/validate_skills.py
```

The validator checks frontmatter, canonical section headings, minimum length, duplication risk, and presence of the baseline skill.

Run the same checks locally as CI:

```bash
./scripts/ci_local.sh
```

## Upgrading from the 86-skill library

If a target repository installed an earlier drop-in without `apply-laws-of-ai`:

1. Copy `skills/agent-control-patterns/apply-laws-of-ai/` from this library.
2. Replace `AGENTS.md`, `CLAUDE.md`, and `skills_docs/` with the current versions (or merge the **Mandatory startup order** section).
3. Update `skills/MANIFEST.md` and `skills/agent-control-patterns/MANIFEST.md` skill counts to **87**.
4. Run `python3 scripts/validate_skills.py` and confirm PASS.

Do not skip step 1 — agents must execute the baseline skill before any other reasoning.

## What this library deliberately excludes

- IDE-specific rules, hooks, or dotfiles (portability over tool coupling)
- Generated code or runtime dependencies as defaults for skills (except documented reference artefacts such as `kg-enabled-rag` schemas)

## Sync rule for entrypoints

- `AGENTS.md` is the canonical full routing document.
- `CLAUDE.md` is a maintained summary; it must stay aligned on startup order, safety references, and completion standards.
- When changing startup order or baseline skills, update both entrypoints in the same change.
