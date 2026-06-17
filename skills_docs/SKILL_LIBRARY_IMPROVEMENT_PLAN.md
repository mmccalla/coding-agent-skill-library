# Skill Library Improvement Plan

Phased improvement programme for the 87-skill coding-agent library. Each phase runs on its own branch, completes with passing CI, and **waits for your approval and merge** before the next phase begins.

## Workflow

```text
main
 └── improve/skills-phase-N-<slug>   # one branch per phase
       ├── implement phase scope
       ├── python3 scripts/ci_local.sh  (must PASS)
       └── PR → your review → merge → next phase branches from updated main
```

**Rules**

- Do not start phase *N+1* until phase *N* is merged to `main`.
- Do not combine phases on one branch.
- Run `python3 scripts/ci_local.sh` before requesting review.
- Update this document's progress table when a phase completes.

## Progress

| Phase | Branch | Status | Merged |
|-------|--------|--------|--------|
| 1 | `improve/skills-phase-1-descriptions-validator` | Ready for review | — |
| 2 | `improve/skills-phase-2-verification-related` | Pending | — |
| 3 | `improve/skills-phase-3-boilerplate-normalise` | Pending | — |
| 4 | `improve/skills-phase-4-dataops-overlay` | Pending | — |
| 5 | `improve/skills-phase-5-kg-enabled-rag-split` | Pending | — |
| 6 | `improve/skills-phase-6-owasp-asi-mapping` | Pending | — |
| 7 | `improve/skills-phase-7-thin-skill-enrichment` | Pending | — |
| 8 | `improve/skills-phase-8-vendor-depth-authoring` | Pending | — |

---

## Phase 1 — Descriptions and validator

**Branch:** `improve/skills-phase-1-descriptions-validator`

**Goal:** Improve skill discoverability and enforce description quality in CI.

**Scope**

1. Rewrite descriptions for all skills missing explicit `Use when` triggers (52 skills).
2. Expand descriptions under 80 characters to meet minimum length.
3. Extend `scripts/validate_skills.py`:
   - Description length 80–1024 characters
   - Description must contain `Use when` (case-insensitive)
   - Folder name must match frontmatter `name:`
4. Add unit tests for new validator rules.

**Out of scope:** Body content changes, section renames, overlays, `kg-enabled-rag` split.

**Acceptance criteria**

- [ ] `python3 scripts/ci_local.sh` passes
- [ ] All 87 descriptions include `Use when` and are 80–1024 characters
- [ ] Validator tests cover description and folder-name rules

**Sources:** [Anthropic Agent Skills](https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills), [LIBRARY_CONTRACT.md](LIBRARY_CONTRACT.md)

---

## Phase 2 — Verification and related skills

**Branch:** `improve/skills-phase-2-verification-related`

**Goal:** Standardise completion evidence and improve routing between skills.

**Scope**

1. Standardise `## Verification` sections to checklist format across all 87 skills.
2. Add `## Related skills` to high-traffic skills (minimum 15): `apply-laws-of-ai`, `using-agent-skills`, `guardrails-safety-patterns`, `spec-driven-development`, `tdd-practice`, `planning-and-task-decomposition`, `incremental-implementation`, `reflection-and-verification`, `mcp-server-design`, `knowledge-retrieval-rag`, `human-in-the-loop`, `code-review-and-quality`, `bdd-practice`, `ddd-practice`, `accessibility-wcag`.
3. Extend validator to require at least one checklist item in `## Verification`.
4. Update `LIBRARY_CONTRACT.md` with optional `## Related skills` convention.

**Acceptance criteria**

- [ ] Every skill has a checklist-style `## Verification` section
- [ ] Related skills links use valid `skills/<category>/<name>` paths
- [ ] CI passes

---

## Phase 3 — Boilerplate removal and section normalisation

**Branch:** `improve/skills-phase-3-boilerplate-normalise`

**Goal:** Reduce token noise and unify procedure structure.

**Scope**

1. Remove generic `## Additional guidance` / `## Additional guidelines` blocks from 11 skills (replace with actionable items only where needed).
2. Rename procedure headings to canonical `## Procedure`:
   - `## Operating procedure` → `## Procedure`
   - `## Implementation pattern` → `## Procedure` (where it is the main workflow)
3. Add `## Objective` to skills that lack it (23 skills).
4. Update validator for canonical `## Procedure` on skills above minimum complexity threshold.

**Affected skills (Additional guidance removal):** `spec-driven-development`, `tdd-practice`, `parallelisation`, `reflection-and-verification`, `code-review-and-quality`, `git-workflow-and-versioning`, `idea-refine`, `planning-and-task-decomposition`, `incremental-implementation`, `multi-agent-collaboration`, `using-agent-skills`.

**Acceptance criteria**

- [ ] No generic boilerplate Additional guidance sections remain
- [ ] Procedure heading variance reduced to one canonical name
- [ ] CI passes

---

## Phase 4 — MAS DataOps overlay extraction

**Branch:** `improve/skills-phase-4-dataops-overlay`

**Goal:** Decouple portable skills from product-specific MAS DataOps MCP content.

**Scope**

1. Create `skills_docs/overlays/mas-dataops-mcp-overlay.md` with extracted content.
2. Replace inline `## MAS DataOps MCP …` and `## DataOps-specific …` sections in 12 skills with a short pointer to the overlay.
3. Add validator rule: core `SKILL.md` files must not contain `MAS DataOps MCP` (overlay exempt).

**Affected skills:** `observability-and-telemetry`, `sre-practice`, `slo-error-budget-management`, `dora-four-keys`, `incident-response-and-postmortems`, `release-engineering-and-progressive-delivery`, `toil-reduction-and-automation`, `accessibility-wcag`, `ux-design-principles`, `frontend-state-and-interaction-design`, `agentic-ux-patterns`, `user-research-and-usability-testing`.

**Acceptance criteria**

- [ ] Overlay file contains all extracted guidance
- [ ] No inline MAS DataOps sections in core skills
- [ ] CI passes

---

## Phase 5 — kg-enabled-rag progressive disclosure

**Branch:** `improve/skills-phase-5-kg-enabled-rag-split`

**Goal:** Align the largest skill with Anthropic progressive-disclosure guidance (&lt;500 lines in `SKILL.md`).

**Scope**

1. Split `skills/data-architecture/kg-enabled-rag/SKILL.md` (620 lines) into:
   - `SKILL.md` — contract, lifecycle summary, links (&lt;200 lines)
   - `reference/implementation-lifecycle.md`
   - `reference/code-patterns.md`
   - `reference/testing-contract.md`
2. Move extended YAML frontmatter (`version`, `activation_keywords`, `primary_stack`) to `reference/metadata.yaml`; retain only `name` and `description` in frontmatter per `LIBRARY_CONTRACT.md`.
3. Add validator warning at 500 lines, fail at 600 lines.
4. Update `skills/MANIFEST.md` and any cross-references.

**Acceptance criteria**

- [ ] `SKILL.md` under 200 lines
- [ ] Reference files linked one level deep from `SKILL.md`
- [ ] CI passes

---

## Phase 6 — OWASP Agentic Top 10 mapping

**Branch:** `improve/skills-phase-6-owasp-asi-mapping`

**Goal:** Align control-pattern skills with [OWASP Top 10 for Agentic Applications (2026)](https://genai.owasp.org/2025/12/09/owasp-top-10-for-agentic-applications-the-benchmark-for-agentic-security-in-the-age-of-autonomous-ai/).

**Scope**

1. Add ASI01–ASI10 mapping tables to:
   - `guardrails-safety-patterns`
   - `tool-use-function-calling`
   - `memory-management`
   - `inter-agent-communication-a2a`
   - `mcp-server-design`
2. Cross-link `human-in-the-loop` for ASI09 controls.
3. Add `skills_docs/security/OWASP_ASI_CROSSWALK.md` as shared reference.

**Acceptance criteria**

- [ ] Each control skill maps at least 3 ASI risks to concrete mitigations
- [ ] Crosswalk document links to official OWASP source
- [ ] CI passes

---

## Phase 7 — Thin skill enrichment

**Branch:** `improve/skills-phase-7-thin-skill-enrichment`

**Goal:** Raise business-architecture and event-driven skills from ~150 to 250–350 words with worked examples.

**Scope**

1. Enrich all 8 `business-architecture/` skills with one mini worked example each.
2. Enrich all 8 `event-driven-and-real-time-data/` skills with decision trees or templates.
3. Enrich `doubt-driven-development` with a doubt-log template.
4. Raise `MIN_WORDS` in validator from 140 to 200 for non-baseline skills (baseline exempt).

**Acceptance criteria**

- [ ] No skill under 200 words (except documented exemptions)
- [ ] Each enriched skill has at least one concrete example or template
- [ ] CI passes

---

## Phase 8 — Vendor depth and authoring guide

**Branch:** `improve/skills-phase-8-vendor-depth-authoring`

**Goal:** Embed vendor-aligned depth and publish authoring standards.

**Scope**

1. Create `skills_docs/SKILL_AUTHORING_GUIDE.md`.
2. Deepen vendor-specific guidance:
   - `mcp-server-design` — MCP stdio logging, capability negotiation, JSON Schema ([MCP docs](https://modelcontextprotocol.io/docs/develop/build-server))
   - `tdd-practice` — pytest src layout, `pyproject.toml`, strict markers ([pytest docs](https://docs.pytest.org/en/latest/explanation/goodpractices.html))
   - `accessibility-wcag` — WCAG 2.2 AA success-criteria mapping ([W3C WCAG 2.2](https://www.w3.org/TR/WCAG22/))
3. Add `scripts/suggest_skills.py` keyword matcher (optional helper).
4. Add `skills_docs/CHANGELOG.md` for library version tracking.

**Acceptance criteria**

- [ ] Authoring guide published and linked from `LIBRARY_CONTRACT.md`
- [ ] Three vendor-depth skills updated with cited controls
- [ ] CI passes

---

## After all phases

1. Run full library audit against `SKILL_AUTHORING_GUIDE.md`.
2. Tag release (e.g. `skill-library-v2.0.0`).
3. Update `DROP_IN_BOOTSTRAP.md` upgrade notes if validator rules changed materially.

## References

| Topic | Source |
|-------|--------|
| Skill authoring | [Anthropic — Agent Skills engineering blog](https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills) |
| Agentic security | [OWASP Top 10 for Agentic Applications](https://genai.owasp.org/2025/12/09/owasp-top-10-for-agentic-applications-the-benchmark-for-agentic-security-in-the-age-of-autonomous-ai/) |
| MCP | [Model Context Protocol — Build a server](https://modelcontextprotocol.io/docs/develop/build-server) |
| Testing | [pytest — Good integration practices](https://docs.pytest.org/en/latest/explanation/goodpractices.html) |
| Accessibility | [W3C WCAG 2.2](https://www.w3.org/TR/WCAG22/) |
| AI governance | [NIST AI Agent Standards Initiative](https://www.nist.gov/artificial-intelligence/ai-agent-standards-initiative) |
