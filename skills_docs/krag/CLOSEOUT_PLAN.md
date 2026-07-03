# Closeout plan — golden corpus realism and STATUS.md completion

**Branch:** `plan/golden-corpus-status-closeout`  
**Last updated:** 2026-07-03  
**Owner:** Skills KG / KRAG delivery  
**Living status:** [`STATUS.md`](STATUS.md)  
**Evaluation detail:** [`EVALUATION.md`](EVALUATION.md)

This plan closes every item still open in `STATUS.md` (in progress, to do, known gaps) and replaces the templated 1,194-case golden corpus with a smaller, realistic, tiered evaluation programme.

---

## Executive summary

| Theme | Today | Target |
| --- | --- | --- |
| Golden corpus | 1,194 cases (~85% templated) | ~365 active cases across three tiers (Option B) |
| Release quality gate | Blended 84.6% full-corpus pass | Tiered gates: realistic precision@1, coverage map, abstention probes |
| Phase 10 | Backend shipped; UI preview-only | Admin ingest in UI with trust confirmation |
| Agent journeys | JRN-01–07 | JRN-01–11 (+ catalogue harvest) |
| Exclusion / confusers | 2 failures at ranks 2–3 | Curated confuser set + measured soft gate |
| Docs / STATUS | Stale “in progress” rows | `STATUS.md` reflects shipped state; gaps tracked with owners |
| CI hygiene | `rdflib` transitive only; mypy fails | Explicit `rdflib` dep; mypy debt bounded or staged |

Delivery is **six waves** on this programme branch (stacked PRs or sequential commits), ending with an empty **To do** / **Known gaps** section in `STATUS.md` except for explicitly deferred post-closeout items (none planned).

---

## STATUS.md closeout map

### In progress → close

| STATUS item | Actual state on `main` | Closeout action | Wave |
| --- | --- | --- | --- |
| Documentation consolidation | Waves A–D merged (#2, #6) | Move to **Done**; link `GETTING_STARTED.md`, `krag/*`, archive | 0 |
| Phase 10 admin skill ingest | `admin_skill_ingest.py`, API routes, tests | Move backend to **Done**; ship UI ingest (P1) | 3 |
| Synthetic negative abstention tuning | Vector-aware gate shipped; nonce negatives still weak | Replace 182 nonce cases with ~15 OOD probes; gate abstention separately | 2 |

### To do → close

| STATUS item | Priority | Acceptance | Wave |
| --- | --- | --- | --- |
| Skills UI **Ingest** button | P1 | Trust preview → confirmation modal → `POST /skills/admin/ingest`; reload feedback; tests | 3 |
| Agent journeys **JRN-08 … JRN-11** | P2 | Fixtures pass with selection traces; queries copied into realistic catalogue | 4 |
| Exclusion at ranks 2–3 | P2 | Confuser cases in catalogue; exclusion_accuracy ≥ 0.5 on realistic tier; document complement co-ranking | 4–5 |

### Known gaps → close

| Gap | Closeout action | Wave |
| --- | --- | --- |
| Abstention on nonsense queries (84.6% blended pass) | Stop reporting single blended pass rate; `abstention_probes.json` with uncertainty_accuracy ≥ 0.9 | 2 |
| 2 exclusion failures in full golden set | Remove full-golden exclusion hard gate; add confuser cases; tune only if realistic tier fails | 4 |
| `POST /skills/upload/preview` only | UI uses admin ingest for persist; runbook + UI copy distinguish preview vs ingest | 3 |

### Residual hygiene (not in STATUS but blocks green CI)

| Item | Action | Wave |
| --- | --- | --- |
| `rdflib` not declared in `pyproject.toml` | Add `rdflib>=7,<8` | 0 |
| `mypy` ~66 errors in `scripts/` | Fix high-traffic modules or add staged `mypy` allowlist with expiry; CI must pass | 5 |
| `STATUS.md` branch context | Update to `main` | 0 |

---

## Golden corpus redesign (Option B — balanced)

### Problem

`generate_golden_queries.py` produces **11 templates × 91 skills + 2 nonce negatives × 91 skills + 12 seeds ≈ 1,194 cases**. Queries like `tell me about {name}` and `how to implement {name} based on…` overstate ranking quality and understate disambiguation. **183 synthetic negatives** dominate abstention failure.

### Target tier model

```text
Tier 1 — smoke (CI merge)       25–35 cases   hand-curated + promoted smoke
Tier 2 — realistic (release)      ~100 cases    curated catalogue + journeys
Tier 3 — coverage (nightly)     ~250 cases    ≤3 archetypes per promoted skill
Abstention probes (release)     ~15 cases     varied OOD, not per-skill nonces
```

**Active CI eval:** ~125–135 cases (smoke + realistic + abstention).  
**Nightly:** coverage tier (~250).  
**Reduction:** ~70% fewer cases than today; **>90%** of release-gated queries are curated/journey-sourced.

### Corpus files

| File | Role | Replaces |
| --- | --- | --- |
| `tests/fixtures/retrieval_evaluation/query_catalog.json` | **New** — reviewed catalogue (source of truth) | bulk of `SEED_CASES` |
| `tests/fixtures/retrieval_evaluation/smoke_queries_promoted.json` | CI ingest gate | expand 6 → ~30 |
| `tests/fixtures/retrieval_evaluation/realistic_queries.json` | Release gate | expand 8 → ~100 (subset of catalogue) |
| `tests/fixtures/retrieval_evaluation/coverage_queries.json` | **New** — sparse per-skill archetypes | bulk of `golden_queries.json` |
| `tests/fixtures/retrieval_evaluation/abstention_probes.json` | **New** — OOD / nonsense / off-domain | per-skill `_negative_*` |
| `tests/fixtures/retrieval_evaluation/golden_queries.json` | Deprecated or re-export of coverage + catalogue | 1,194 template corpus |

### Case schema extensions

```json
{
  "id": "confuser_krag_vs_kg_rag",
  "query": "KRAG architecture summary graph schema outline retrieval strategy…",
  "query_source": "curated",
  "query_archetype": "confuser",
  "naturalness": "high",
  "expected_skill_ids": ["skill:krag-system-design"],
  "excluded_skill_ids": ["skill:knowledge-graph-rag"],
  "promotion_tier": "release"
}
```

`query_source`: `curated` | `journey` | `archetype` | `abstention_probe`

### Generator refactor (`generate_golden_queries.py`)

- CLI: `--tier smoke|realistic|coverage|abstention|all`
- Remove `MIN_CASES = 500` and 11-template loop
- **Coverage:** max **3 archetypes** per skill — `task_query`, `alias_query`, optional `confuser_query` when graph lists a confuser
- **Abstention:** single shared probe set, not `NEGATIVE_CASES_PER_SKILL = 2`
- Add `scripts/validate_eval_corpus.py` — schema, tier minimums, skill coverage map, no template explosion

### Evaluation gate changes

| Gate | Dataset | Threshold | Runner |
| --- | --- | --- | --- |
| Ingest / merge | `smoke_queries_promoted.json` | precision@1 ≥ 0.98; 0 rank failures | `ci_ingest_gate.py` |
| Release | `realistic_queries.json` + `abstention_probes.json` | precision@1 = 1.0; exclusion ≥ 0.5; uncertainty ≥ 0.9 | `test_e2e_realistic_retrieval.py` |
| Coverage | `coverage_queries.json` | every promoted skill ≥1 case; precision@1 ≥ 0.95 | nightly / `run_e2e_retrieval_eval.py` |

**Stop** gating release on 1,194-case blended pass rate. Update `EVALUATION.md` to report **per-tier** metrics.

### Query realism sources

1. **Curated catalogue** — migrate `SEED_CASES` + `realistic_queries.json`; grow confuser/multi-skill groups
2. **Agent journeys** — harvest `route_skill_query` / `recommend_skills` arguments from JRN-01–11
3. **Sparse archetypes** — category-aware templates (not literal skill-id repetition)
4. **Later:** usage harvest from `rollup_skill_usage.py` (manual review queue)

### Drop

- 11 templates × every skill
- 2 nonce negatives × every skill
- `test_load_cases_requires_large_golden_query_contract` minimum of 500 cases

---

## Agent journeys JRN-08 … JRN-11

| ID | Intent | Tool steps | Catalogue link |
| --- | --- | --- | --- |
| JRN-08 | Out-of-domain / weather | `route_skill_query` → uncertain; `recommend_skills` abstain | `abstention_probes.json` |
| JRN-09 | Malicious / trust block | trust fixture reject; no persist | `query_catalog` security group |
| JRN-10 | Usage metrics trace | selection trace includes `usage_event_id`; metrics increment | ops validation |
| JRN-11 | Admin ingest + resolve | API ingest (test) or MCP resolve after fixture ingest | Phase 10 UI e2e |

Acceptance: `tests/test_agent_journeys.py` passes 11 journeys; each JRN query appears in catalogue or abstention file.

---

## Skills UI ingest (P1)

### Behaviour

1. User selects `SKILL.md` → **Preview upload** (existing trust report)
2. If trust `passed` and admin enabled → show **Ingest** button + confirmation modal (skill name, trust hash, consequences)
3. On confirm → `POST /skills/admin/ingest` with `X-Skills-Admin-Key` (settings field or env-backed config panel)
4. Success → show written path, promotion status; failure → trust layers in modal
5. Copy: preview is non-persisting; ingest requires admin key

### Files

- `skills-ui/src/types.ts` — `AdminIngestResult`, config
- `skills-ui/src/api.ts` — `ingestSkill`, `listRecentIngests`
- `skills-ui/src/App.tsx` — ingest button, modal, trust panel
- `skills-ui/src/App.test.tsx` — preview + ingest flows (mock API)

### API contract

Already implemented: `POST /skills/admin/ingest`, `GET /skills/admin/ingests` (`skills_api.py`).

---

## Exclusion at ranks 2–3 (P2)

### Approach

1. Add **~25 confuser cases** to catalogue (KRAG vs graph-RAG, guardrails vs HITL, RAG vs KRAG retrieval, etc.)
2. Keep **soft gate** on realistic tier: `exclusion_accuracy ≥ 0.5` (complements may co-rank)
3. **Hard gate:** precision@1 = 1.0 on realistic tier (no wrong top-1)
4. Optional retrieval tweak only if realistic confusers fail after catalogue expansion — avoid tuning to templates

---

## Delivery waves (this programme)

All work lands via stacked commits/PRs from `plan/golden-corpus-status-closeout` → `main`.

### Wave 0 — Plan and STATUS hygiene

- [x] This document
- [ ] Update `STATUS.md` — programme tracker, move shipped items to Done
- [ ] Link from `krag/README.md`
- [ ] Add `rdflib>=7,<8` to `pyproject.toml`
- [ ] Add `EVALUATION_CORPUS_CONTRACT.md` (tier rules, schema, regeneration)

**Exit:** Plan approved; STATUS reflects true shipped state.

### Wave 1 — Corpus contract and catalogue skeleton

- [ ] Add `query_catalog.json` (~40 cases: seeds + realistic + journey harvest)
- [ ] Add `abstention_probes.json` (~15 cases)
- [ ] Add `validate_eval_corpus.py` + tests
- [ ] Update `EVALUATION.md` tier model (no gate changes yet)

**Exit:** Catalogue reviewable; validator passes.

### Wave 2 — Generator rewrite and corpus shrink

- [ ] Refactor `generate_golden_queries.py` (tiers, no 11-template loop)
- [ ] Emit `coverage_queries.json` (~250 cases)
- [ ] Expand `realistic_queries.json` from catalogue (~100)
- [ ] Expand `smoke_queries_promoted.json` (~30)
- [ ] Deprecate or slim `golden_queries.json`
- [ ] Update `test_evaluate_skill_retrieval.py`, `test_e2e_realistic_retrieval.py`

**Exit:** Release gates use new tiers; CI eval < 30s; abstention gated on probes.

**Closes:** synthetic negative abstention tuning (corpus); known gap “abstention blended pass rate”.

### Wave 3 — Skills UI admin ingest (P1)

- [ ] UI types, API client, ingest button + modal
- [ ] Admin key input (local dev settings)
- [ ] Tests + runbook UI section
- [ ] Clarify preview vs ingest in upload panel

**Exit:** Operator can ingest trusted skill from UI; `App.test.tsx` green.

**Closes:** Phase 10 (full); known gap “preview only”; STATUS Phase 10 row.

### Wave 4 — Journeys and confusers (P2)

- [ ] Add JRN-08 … JRN-11 to `agent_journeys.json`
- [ ] Grow confuser catalogue to ~25 cases
- [ ] Copy journey queries into catalogue
- [ ] `test_agent_journeys.py` ≥ 11 journeys

**Exit:** Journeys green; realistic tier precision@1 = 1.0; exclusion ≥ 0.5.

**Closes:** JRN-08–11; exclusion failures (as release gate); doc consolidation final verification.

### Wave 5 — CI green and STATUS final

- [ ] Fix or stage mypy errors until `ci_local.sh` passes
- [ ] Nightly workflow for coverage tier (optional GitHub Actions job)
- [ ] Final `STATUS.md` — empty In progress / To do / Known gaps
- [ ] `CHANGELOG.md` entry

**Exit:** `./scripts/ci_local.sh` passes; STATUS.md closeout complete.

---

## Acceptance criteria (programme complete)

1. `STATUS.md` has **no** in-progress or to-do rows except archived historical notes.
2. Golden active CI corpus **< 150 cases**; coverage tier **< 280 cases**.
3. **≥90%** of release-gated queries are `curated` or `journey` sourced.
4. `test_e2e_realistic_retrieval.py` passes with tier thresholds documented in `EVALUATION.md`.
5. Skills UI admin ingest works end-to-end with tests.
6. JRN-01 … JRN-11 pass in `test_agent_journeys.py`.
7. `rdflib` declared; `ci_ingest_gate.py` runs in clean `pip install -e ".[dev]"` env.
8. `ci_local.sh` exits 0 (including mypy).

---

## PR sequence (recommended)

| PR | Branch slice | Contents |
| --- | --- | --- |
| 1 | `plan/golden-corpus-status-closeout` wave 0–1 | Plan, STATUS, contract, catalogue skeleton |
| 2 | `feat/eval-corpus-tier-2` | Generator + corpus files + tests |
| 3 | `feat/skills-ui-admin-ingest` | UI wave 3 |
| 4 | `feat/journeys-confusers` | JRN-08–11 + catalogue |
| 5 | `chore/ci-mypy-closeout` | mypy + nightly + STATUS final |

---

## Risks

| Risk | Mitigation |
| --- | --- |
| Coverage blind spot after shrink | Coverage tier + per-skill assertion in `validate_eval_corpus.py` |
| UI admin key exposure | Key in local settings only; never commit; document env var |
| Confuser gate too strict | Soft exclusion gate; hard precision@1 only |
| mypy scope creep | Wave 5 time-boxed; fix modules touched in waves 1–4 first |
| Catalogue staleness | Quarterly review checklist in `EVALUATION_CORPUS_CONTRACT.md` |

---

## Quick commands (during programme)

```bash
git checkout plan/golden-corpus-status-closeout
python3 scripts/validate_eval_corpus.py          # after wave 1
python3 scripts/generate_golden_queries.py --tier all
python3 -m pytest tests/test_e2e_realistic_retrieval.py tests/test_agent_journeys.py -q
npm --prefix skills-ui test
./scripts/ci_local.sh
```
