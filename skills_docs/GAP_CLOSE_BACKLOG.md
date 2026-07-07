# Domain Gap-Close Backlog (Living)

Living backlog for closing architecture, compliance, governance, engineering and FinOps gaps in the coding-agent skill library.

**Status:** Complete (merged to `main`, 2026-07-06)  
**Baseline count:** 99 skills  
**Target count:** 111 skills (12 new) + extensions — **exceeded:** **113** skills after bias/fallacy additions  
**Owner:** repository-maintained

Update this file when a PR lands, a skill is deferred, or acceptance criteria change.

## Principles

| Principle | Rule |
|---|---|
| Agent impact first | Prefer gaps agents hit when designing or changing systems |
| Extend before invent | New skill only when a dedicated trigger and confuser pair are required |
| One skill, one PR (preferred) | Programme may batch on a feature branch; DoD still applies per skill |
| DoD is continuous | Inventory, grounding, intents, confusers, coverage and reciprocal links in the same change as the skill |
| Thin MVP | Procedure, checklist, references; no essay packs |
| US skill ids, UK prose | Kebab-case US ids; British English in skill bodies |

## Extend vs create

### Extend (no new folder)

| Gap | Target skill | Status |
|---|---|---|
| Privacy ops (DPIA, data-subject rights) | `data-security-and-privacy-architecture` | Done |
| Physical data design | `logical-data-modeling` | Done |
| FinOps boundary | `resource-aware-optimization` Related skills | Done |

### Create (new skills)

| Skill id | Category | Phase | Status |
|---|---|---|---|
| `threat-modeling` | agent-control-patterns | A | Done |
| `secure-sdlc-and-supply-chain` | reliability-and-delivery | A | Done |
| `api-design-and-lifecycle` | enterprise-integration-patterns | B | Done |
| `ai-model-governance` | agent-control-patterns | B | Done |
| `solution-architecture` | solution-and-platform-architecture (new) | B | Done |
| `test-strategy` | engineering-practices | B | Done |
| `risk-management` | agent-control-patterns | C | Done |
| `finops-practice` | reliability-and-delivery | C | Done |
| `cloud-platform-architecture` | solution-and-platform-architecture | C | Done |
| `performance-engineering` | reliability-and-delivery | C | Done |
| `infrastructure-as-code` | reliability-and-delivery | C | Done |
| `technical-debt-management` | engineering-practices | C | Done |

## Definition of Done (every skill)

- [ ] `SKILL.md` MVP: When to use, When not to use, Objective, Procedure, Rules, Related skills, References, Verification
- [ ] `PACK_METADATA.json` membership
- [ ] `MANIFEST.md` use/avoid row
- [ ] `AGENTS.md` and `CLAUDE.md` routing bullet
- [ ] `STANDARDS_GROUNDING` markers + practice tests green
- [ ] `SKILL_PRIMARY_INTENTS` entry
- [ ] Confuser pair(s) for top neighbour(s)
- [ ] Reciprocal Related skills on neighbours
- [ ] Coverage corpus skill-sync green
- [ ] Skill count updated in `MANIFEST.md` and `LIBRARY_CONTRACT.md`

## Phase A — Security and supply chain

| Order | Change | Type | Status |
|---|---|---|---|
| A1 | `threat-modeling` | New | Done |
| A2 | `secure-sdlc-and-supply-chain` | New | Done |
| A3 | Privacy compliance subsection on `data-security-and-privacy-architecture` | Extend | Done |

**Exit:** 101 skills (intermediate; programme delivered as one branch).

## Phase B — Contracts, models, solution shape

| Order | Change | Type | Status |
|---|---|---|---|
| B1 | `api-design-and-lifecycle` | New | Done |
| B2 | `ai-model-governance` | New | Done |
| B3 | Category `solution-and-platform-architecture` + `solution-architecture` | New | Done |
| B4 | `test-strategy` | New | Done |

**Exit:** 105 skills (intermediate).

## Phase C — Risk, platform, cost, engineering depth

| Order | Change | Type | Status |
|---|---|---|---|
| C1 | `risk-management` | New | Done |
| C2 | `finops-practice` + reciprocal links on `resource-aware-optimization` | New + extend | Done |
| C3 | `cloud-platform-architecture` | New | Done |
| C4 | Physical design section on `logical-data-modeling` | Extend | Done |
| C5 | `performance-engineering` | New | Done |
| C6 | `infrastructure-as-code` | New | Done |
| C7 | `technical-debt-management` | New | Done |

**Exit:** 113 skills (gap-close programme complete; bias/fallacy skills added post-target).

## Phase D — Hardening

| Work | Status |
|---|---|
| Coverage regen and skill-sync | Done |
| Confuser pairs for all new neighbours | Done |
| HOW_TO_FIND_THE_RIGHT_SKILL routing rows | Done |
| Full quality gate (`validate_skills`, practice `--all`, graph, ontology, corpus, pytest) | Done |

## Explicit defer list

- Sector packs (PCI, HIPAA, banking conduct)
- Full COBIT / ITIL / CAB process skills
- EU AI Act legal interpretation (operational AI governance only)
- Mobile/native, i18n-only, vendor-specific IaC modules as skills
- Merging FinOps into `resource-aware-optimization`

## Standards grounding markers

| Skill | Required markers (regex, case-insensitive) |
|---|---|
| `threat-modeling` | `STRIDE\|threat model`, `trust boundary`, `OWASP`, `https?://` |
| `secure-sdlc-and-supply-chain` | `SSDF\|800-218`, `SBOM`, `https?://` |
| `data-security-and-privacy-architecture` | `DPIA`, `data subject\|DSAR\|erasure`, `https?://` |
| `api-design-and-lifecycle` | `OpenAPI`, `https?://` |
| `ai-model-governance` | `AI RMF\|NIST`, `inventory\|risk tier`, `https?://` |
| `solution-architecture` | `NFR\|non-functional`, `option`, `https?://` |
| `test-strategy` | `test pyramid\|risk-based`, `https?://` |
| `risk-management` | `risk register\|treatment`, `https?://` |
| `finops-practice` | `FinOps`, `Inform`, `Optimise\|Optimize`, `unit economics\|allocation\|showback\|chargeback`, `https?://www\.finops\.org\|https?://` |
| `cloud-platform-architecture` | `landing zone\|tenancy`, `https?://` |
| `logical-data-modeling` | `physical`, `index\|partition`, `https?://` |
| `performance-engineering` | `latency\|throughput`, `profil`, `https?://` |
| `infrastructure-as-code` | `declarative\|plan/apply\|IaC`, `https?://` |
| `technical-debt-management` | `debt`, `paydown\|pay-down\|interest`, `https?://` |

## Gate commands

```bash
python3 scripts/validators/validate_skills.py
python3 scripts/validators/validate_skill_practice.py --all
python3 scripts/validators/validate_skills_graph.py
python3 scripts/validators/validate_skills_ontology.py
python3 scripts/validators/validate_eval_corpus.py --check-skill-sync
python3 scripts/validators/validate_docs.py
PYTHONPATH=. python3 -m pytest -m "not live_neo4j and not slow and not eval_pr" -q
```

## Progress log

| Date | Event |
|---|---|
| 2026-07-04 | Backlog created from improved gap-close plan; implementation branch `feat/gap-close-all-phases` |
| 2026-07-04 | All phases implemented: 12 new skills, 3 extensions, category `solution-and-platform-architecture`, inventory and L3 grounding wired |
