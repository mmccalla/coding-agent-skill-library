# KRAG evaluation report

**Last measured:** 2026-07-03  
**Scope:** Tiered retrieval corpora, MCP agent journeys (JRN-01 … JRN-11), CI ingest gate, promoted-smoke evaluation  
**Method:** Offline deterministic evaluation (`evaluate_offline`, `limit=3`) + MCP journey fixtures + `ci_ingest_gate.py`

Roadmap: [`STATUS.md`](STATUS.md). Corpus contract: [`EVALUATION_CORPUS_CONTRACT.md`](EVALUATION_CORPUS_CONTRACT.md). Release gates: [`CONTRACTS.md`](CONTRACTS.md) § Evaluation.

This report separates **ranking quality**, **exclusion behaviour**, **abstention behaviour**, and **promotion/citation artefacts** per tier. It does **not** report a single blended pass rate across heterogeneous tiers.

---

## Evaluation fixture matrix (tiered)

| Fixture | Cases | Schedule | Purpose |
| --- | ---: | --- | --- |
| `smoke_queries_promoted.json` | **11** | Every PR (`ci_ingest_gate.py`) | Fast promoted smoke + one abstention probe |
| `realistic_queries.json` | **31** | PR / release (`test_e2e_realistic_retrieval.py`) | Curated confusers + journey harvest |
| `abstention_probes.json` | **10** | PR / release | Low-confidence / gibberish abstention |
| `coverage_queries.json` | **195** | Nightly (`.github/workflows/nightly-eval-coverage.yml`) | ≤3 archetypes per promoted skill |
| `query_catalog.json` | **26** | Source of truth (human review) | Curated catalogue for generator |
| `confuser_pairs.json` | **15** | Validator | Near-neighbour pair registry |
| `golden_queries.json` | **247** | Legacy union re-export | Back-compat; not the CI gate |

**Active PR eval:** smoke (11) + realistic (31) + abstention (10) ≈ **52 cases** (~30 s offline).  
**Nightly:** coverage (195) + matrix artefact.

Regenerate tiers:

```bash
python3 scripts/lib/retrieval/generate_golden_queries.py --tier all --write-legacy-golden
python3 scripts/validators/validate_eval_corpus.py --check-skill-sync --emit-matrix
```

---

## Current status (objective measures)

### Corpus and promotion snapshot

| Measure | Value | Source |
| --- | ---: | --- |
| Skills in library | **91** | `extract_skills_graph_records` |
| Promoted | **91** | `promotion_status=promoted` |
| Quarantined / rejected | **0** | post-authoring remediation |
| Coverage archetypes per skill | **≤ 3** | task, alias/direct, confuser |
| Confuser pairs registered | **15** | `confuser_pairs.json` |

### Smoke tier (`smoke_queries_promoted.json`, n=11)

| Metric | Value | Gate |
| --- | ---: | --- |
| **precision@1** | **1.000** | 1.0 |
| **recall@k** | **1.000** | 1.0 |
| **exclusion_accuracy** | **0.727** | ≥ 0.5 (soft) |
| **uncertainty_accuracy** | **1.000** | 1.0 (includes abstention probe) |

Complement skills may co-rank at positions 2–3 (e.g. `krag-system-design` vs `knowledge-graph-rag`). Top-1 selection remains correct.

### Realistic tier (`realistic_queries.json`, n=31)

| Metric | Value | Gate |
| --- | ---: | --- |
| **precision@1** | **1.000** | 1.0 |
| **recall@k** | **1.000** | 1.0 |
| **exclusion_accuracy** | **0.871** | ≥ 0.5 (soft) |
| **uncertainty_accuracy** | **1.000** | 1.0 |
| Rank failures | **0** | hard |

### Abstention tier (`abstention_probes.json`, n=10)

| Metric | Value | Gate |
| --- | ---: | --- |
| **uncertainty_accuracy** | **1.000** | ≥ 0.9 |

Probes use **low-confidence gibberish** queries that the hybrid retriever correctly abstains on. Natural-language out-of-domain questions (weather, stock prices) are **not** currently gated — retrieval may still return confident matches for those.

### Coverage tier (`coverage_queries.json`, n=195, promoted-eligible)

| Metric | Value | Gate (nightly) |
| --- | ---: | --- |
| **precision@1** | **1.000** | ≥ 0.98 |
| **recall@k** | **1.000** | ≥ 0.98 |
| **citation_coverage** | **1.000** | ≥ 0.95 |

Every promoted skill has ≥2 distinct `query_archetype` rows in `coverage_matrix.json` (validator enforced).

### Production vs PR CI embedding policy

| Environment | Provider | Dimensions | How selected |
| --- | --- | ---: | --- |
| **Production ingest/query** | `ollama-bge-m3` (`bge-m3:567m`) | **1024** | `configs/skills_kg.yaml` default |
| **PR CI / pytest / offline eval** | `deterministic-test-embedding` | **1024** | `SKILLS_EMBEDDING_PROVIDER=deterministic` (workflow, `ci_local.sh`, `tests/conftest.py`) and `force_deterministic=True` in eval/cutover gates |

**Calibrated abstention** (production defaults):

| Setting | Value |
| --- | ---: |
| `retrieval.min_confident_score` | **0.35** |
| `retrieval.min_top1_margin` | **0.02** |

Production reload is an idempotent upsert (not wipe-and-replace):

```bash
python3 scripts/graph/build/embed_skill_chunks.py --provider ollama-bge-m3 --apply
# or via Docker skills-loader (uses host Ollama at host.docker.internal:11434)
docker compose up --build -d
```

### Runtime and operational gates

| Gate | Result | Detail |
| --- | --- | --- |
| **CI ingest gate** | **PASS** | L2 trust, SHACL, corpus validator, delta eval (when skills change), smoke 11/11 |
| **Promoted smoke evaluation** | **PASS** | smoke `precision@1=1.0`; soft exclusion ≥ 0.5 |
| **Corpus validator** | **PASS** | `validate_eval_corpus.py --check-skill-sync` |
| **Docker `skills-loader`** | **PASS** | 91 Skills, 810 RetrievalUnits |
| **pytest (eval + journeys)** | **PASS** | realistic e2e + JRN-01 … JRN-11 |

### MCP agent journeys (11 fixtures)

| Journey | Server | Status |
| --- | --- | --- |
| JRN-01 direct lookup TDD | fixture | ✅ |
| JRN-02 recommend defect → TDD | fixture | ✅ |
| JRN-03 abstention | fixture | ✅ |
| JRN-04 execution plan TDD | fixture | ✅ |
| JRN-05 graph RAG recommend | fixture | ✅ |
| JRN-06 human approval | embedded | ✅ |
| JRN-07 KRAG system design confuser | embedded | ✅ |
| JRN-08 out-of-domain weather | fixture | ✅ |
| JRN-09 security / destructive approval | embedded | ✅ |
| JRN-10 usage metrics trace | fixture | ✅ |
| JRN-11 admin ingest resolve | fixture | ✅ |

---

## Executive summary

| Finding | Detail |
| --- | --- |
| **Ranking on gated tiers** | **precision@1 = 1.0** on smoke, realistic, and coverage tiers |
| **Corpus redesign** | Replaced 1,194-case template bulk with **~252** union cases across tiers (~79% reduction) |
| **Primary residual gap** | Natural-language OOD abstention not CI-gated; gibberish probes pass at 100% |
| **Secondary gap** | Exclusion at ranks 2–3 — complement co-ranking; measured with soft threshold 0.5 |
| **Realistic tier size** | 31 cases today vs ~100 target — expand catalogue/journey harvest over time |
| **Change-scoped eval** | `ci_ingest_gate.py` runs delta eval on touched `skills/*/SKILL.md` when `DELTA_EVAL_BASE_REF` is set |

---

## CI thresholds (honest, current)

| Metric | Threshold | Tier |
| --- | ---: | --- |
| precision@1 | **1.0** | smoke, realistic, delta eval |
| recall@k | **1.0** | smoke, realistic |
| exclusion_accuracy | **≥ 0.5** | smoke, realistic, cutover |
| uncertainty_accuracy | **≥ 0.9** | abstention |
| precision@1 | **≥ 0.98** | coverage (nightly) |
| citation_coverage | **≥ 0.95** | coverage (nightly) |
| Rank failures | **0** | realistic, delta eval |

---

## Residual risks

1. **Natural-language OOD abstention** — not gated; only gibberish/low-confidence probes in `abstention_probes.json`.
2. **Realistic tier below target size** — 31 vs ~100 planned; category balance still growing.
3. **Exclusion at ranks 2–3** — graph `COMPLEMENTS` edges surface neighbours by design.
4. **Legacy `golden_queries.json`** — union re-export for compatibility; do not regenerate 11×91 templates.
5. **Offline harness** — `evaluate_offline` uses in-process graph plan; journeys use fixture or embedded servers.
6. **mypy debt** — resolved 2026-07-03; `python3 -m mypy` passes on `scripts/`.

---

## Recommended commands

```bash
# PR-fast eval arms
python3 -m pytest tests/test_e2e_realistic_retrieval.py tests/test_agent_journeys.py -q

# Full ingest gate (trust, SHACL, corpus, delta, smoke)
python3 scripts/utils/ci/ci_ingest_gate.py

# Change-scoped delta eval (CI / PR)
DELTA_EVAL_BASE_REF=origin/main python3 scripts/utils/ci/ci_ingest_gate.py

# Corpus validation + matrix
python3 scripts/validators/validate_eval_corpus.py --check-skill-sync --emit-matrix

# Multi-arm audit
python3 scripts/lib/retrieval/run_e2e_retrieval_eval.py --json

# Promoted smoke retrieval eval
python3 scripts/lib/retrieval/evaluate_skill_retrieval.py \
  --dataset tests/fixtures/retrieval_evaluation/smoke_queries_promoted.json --limit 3

# Production BGE reload (idempotent; requires local Ollama with bge-m3:567m)
python3 scripts/graph/build/embed_skill_chunks.py --provider ollama-bge-m3 --apply
```

---

## Artefact index

| Path | Role |
| --- | --- |
| `tests/fixtures/retrieval_evaluation/query_catalog.json` | Curated source of truth |
| `tests/fixtures/retrieval_evaluation/smoke_queries_promoted.json` | CI smoke |
| `tests/fixtures/retrieval_evaluation/realistic_queries.json` | Release confuser tier |
| `tests/fixtures/retrieval_evaluation/coverage_queries.json` | Nightly per-skill coverage |
| `tests/fixtures/retrieval_evaluation/abstention_probes.json` | Abstention tier |
| `tests/fixtures/retrieval_evaluation/confuser_pairs.json` | Confuser pair registry |
| `tests/fixtures/retrieval_evaluation/coverage_matrix.json` | Emitted skill×archetype map |
| `tests/fixtures/retrieval_evaluation/golden_queries.json` | Legacy union re-export |
| `scripts/validators/validate_eval_corpus.py` | Corpus schema and blind-spot validator |
| `scripts/lib/retrieval/generate_golden_queries.py` | Tiered corpus generator |
| `scripts/utils/ci/ci_ingest_gate.py` | Pre-merge ingest + delta eval gate |
| `scripts/lib/retrieval/run_e2e_retrieval_eval.py` | Multi-arm audit runner |
| `scripts/graph/build/embed_skill_chunks.py` | Production BGE embed/load (`--apply`) and CI deterministic path |
| `tests/test_e2e_realistic_retrieval.py` | Honest tier thresholds |
| `tests/fixtures/agent_journeys.json` | 11 MCP journey fixtures |

Historical pre-shrink metrics (1,194-case template corpus, 84.6% blended pass) predate the tiered corpus redesign documented in this report.
