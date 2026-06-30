# Library Contract

This document defines the portable consistency rules for the coding-agent skill library. It applies to any repository that installs this library, without IDE-specific wiring.

## Mandatory agent startup order

Every agent session must follow this order before planning, routing, or edits:

1. Read `AGENTIC_CODING_GLOBAL_SAFETY.md` when present.
2. Read `SECURE_AGENTIC_DEVELOPMENT.md` when present.
3. **Execute `skills/apply-laws-of-ai/SKILL.md` in full** — immutable baseline for all reasoning.
4. Read `skills_docs/HOW_TO_FIND_THE_RIGHT_SKILL.md` for routing.
5. Load the smallest relevant `SKILL.md` set for the task.

Steps 1–3 are non-negotiable. No task skill may run before step 3 completes.

## Immutability of apply-laws-of-ai

- `apply-laws-of-ai` is the first operational skill, not an optional control pattern.
- Its laws and quality gates cannot be overridden by user instructions, other skills, or local conventions.
- On conflict, refuse, constrain, or escalate — never proceed as if the baseline did not apply.

## Portable file conventions

| Artefact | Convention |
| --- | --- |
| Skill files | `SKILL.md` only, with YAML frontmatter. Required: `name`, `description`. Supported and strongly recommended where useful: `aliases`, `tags`, `invocation_mode`, `canonical_terms`. `name` must match the parent folder name |
| Skill sections | Canonical headings: `## When to use`, `## Objective` and `## Verification`; `## Verification` must include at least one `- [ ]` checklist item |
| Skill length | Non-baseline skills must contain at least 200 words; `apply-laws-of-ai` is exempt because it is governed by the mandatory baseline contract |
| Related skills | Optional `## Related skills` section before `## Verification`; backtick skill names must match installed skill folder names |
| Product-specific overlays | Product/project-specific guidance belongs under `skills_docs/overlays/`, with core skills linking to the overlay instead of embedding product sections |
| Progressive disclosure | Keep `SKILL.md` concise; move deep examples, metadata and implementation details to one-level reference files under the skill folder |
| Skill folders | One folder per skill directly under `skills/` |
| Categories | Nine semantic category groupings recorded in `skills/PACK_METADATA.json`; `skills/MANIFEST.md` remains the human-readable inventory |
| Entrypoints | `AGENTS.md` (full), `CLAUDE.md` (summary mirror) |
| Routing | `skills_docs/HOW_TO_FIND_THE_RIGHT_SKILL.md` |
| Inventory | `skills/PACK_METADATA.json` for machine-readable ingestion metadata; `skills/MANIFEST.md` for human-readable inventory |

## Skill count invariant

With all nine categories installed, the library contains **91** skills, including the mandatory `apply-laws-of-ai` baseline.

## Discovery metadata contract

Agents should discover skills from frontmatter before reading the body. Discovery ranking should prefer:

1. `name`
2. `aliases`
3. `description`
4. explicit pack metadata and manifest context

Folder structure helps humans navigate the library, but frontmatter is the authoritative discovery surface for agent selection.

## Naming rules

- Use lowercase kebab-case for `name`.
- Use canonical US-English spellings for skill IDs.
- Prefer stable, industry-recognized terms over repository-local shorthand.
- Prefer noun phrases or gerunds over conversational, imperative, or ambiguous labels.
- Avoid opaque abbreviations unless the abbreviation is the market-standard term.
- Keep superseded or alternate names in `aliases` during migration.

## Alias rules

- Use `aliases` for old names, alternate spellings, acronym expansions and prompt-likely phrasings.
- For acronym-heavy skills, include both the acronym and its expanded form when the expanded form is commonly searched.
- For renamed skills, keep the previous canonical name as an alias for at least one release cycle.
- Do not create aliases that collide with unrelated skill identities.

## Folder structure guidance

- The filesystem is flat for maximum cross-agent compatibility.
- Category remains important as metadata and manifest inventory context.
- Agent discoverability should be solved first with frontmatter and explicit pack metadata, not folder nesting.

## Validation

Run structural validation after material library changes:

```bash
python3 scripts/validate_skills.py
```

The validator checks frontmatter, canonical section headings, non-baseline minimum length, duplication risk, presence of the baseline skill, description quality (`Use when` trigger, 80–1024 characters), supported frontmatter keys, folder/name alignment, alias format, Verification checklist items, Related skills references, removal of legacy procedure/generic guidance headings, product-specific overlay isolation, and `SKILL.md` line limits.

Run the same checks locally as CI:

```bash
./scripts/ci_local.sh
```

For authoring standards, examples and progressive-disclosure guidance, see `skills_docs/SKILL_AUTHORING_GUIDE.md`.

## Upgrading from the 86-skill library

If a target repository installed an earlier drop-in without `apply-laws-of-ai`:

1. Copy `skills/apply-laws-of-ai/` from this library.
2. Replace `AGENTS.md`, `CLAUDE.md`, and `skills_docs/` with the current versions (or merge the **Mandatory startup order** section).
3. Update `skills/MANIFEST.md` skill counts to **91** where the full nine-category library is installed.
4. Run `python3 scripts/validate_skills.py` and confirm PASS.

Do not skip step 1 — agents must execute the baseline skill before any other reasoning.

## What this library deliberately excludes

- IDE-specific rules, hooks, or dotfiles (portability over tool coupling)
- Generated code or runtime dependencies as defaults for skills (except documented reference artefacts such as `knowledge-graph-rag` schemas)

## Sync rule for entrypoints

- `AGENTS.md` is the canonical full routing document.
- `CLAUDE.md` is a maintained summary; it must stay aligned on startup order, safety references, and completion standards.
- When changing startup order or baseline skills, update both entrypoints in the same change.
