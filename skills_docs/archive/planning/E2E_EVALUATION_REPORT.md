# E2E Retrieval Evaluation Report

**Last measured:** 2026-07-03  
**Scope:** Skills KG hybrid retrieval, MCP agent journeys, golden corpus, realistic confuser set, CI ingest gate, Docker Neo4j load  
**Method:** Offline deterministic evaluation (`evaluate_offline`, `limit=3`) + MCP journey fixtures + cutover acceptance + `ci_ingest_gate.py`

This report is intentionally **not** tuned for flattering metrics. It separates **ranking quality**, **exclusion behaviour**, **abstention behaviour**, and **promotion/citation artefacts**.

---

## Current status (objective measures)

### Corpus and promotion snapshot

| Measure | Value | Source |
| --- | ---: | --- |
| Skills in library | **91** | `extract_skills_graph_records` |
| Promoted | **91** | `promotion_status=promoted` |
| Quarantined | **0** | post-authoring remediation |
| Rejected | **0** | L2 security |
| Golden cases (`golden_queries.json`) | **1,194** | regenerated with `promotion_tier` |
| Release-tagged cases | **1,194** (100%) | all cases `promotion_tier=release` |
| Realistic confuser cases | **8** | `realistic_queries.json` |
| Positive retrieval cases | **1,011** | `expected_skill_ids` non-empty |
| Synthetic negative/abstention cases | **183** | 2 per skill (`*_negative_*`) |

### Retrieval quality — positive cases only (n=1,011)

These are the cases that matter for **skill selection accuracy**. Measured 2026-07-03.

| Metric | Value | CI / gate threshold |
| --- | ---: | --- |
| **precision@1** | **1.000** | realistic: 1.0; release: ≥ 0.98 |
| **recall@k** (k=3) | **1.000** | realistic: 1.0; release: ≥ 0.98 |
| **MRR** | **1.000** | — |
| **NDCG@k** | **1.000** | — |
| **source_coverage** | **1.000** | release: ≥ 0.95 |
| **citation_coverage** | **1.000** | release: ≥ 0.95 |
| **graph_lift_recall@k** | **1.000** | must be ≥ 0 |
| **exact_lookup_accuracy** | **1.000** | — |
| **alias_resolution_accuracy** | **1.000** | — |
| **Rank failures** | **0** | hard gate on realistic set |
| **Positive case pass rate** | **99.8%** (1,009 / 1,011) | 2 exclusion-only failures |

**Interpretation:** Ranking and evidence grounding on positive queries are **at ceiling** in the current offline harness. Remaining positive failures are **exclusion violations** (related skills co-rank at positions 2–3), not wrong top-1 selection.

### Exclusion behaviour (full golden corpus, n=1,194)

| Metric | Value |
| --- | ---: |
| **exclusion_accuracy** | **0.993** |
| **Exclusion failures** | **2** |

| Case ID | Expected top-1 | Excluded skill ranked |
| --- | --- | --- |
| `krag_system_design` | `skill:krag-system-design` | `skill:knowledge-graph-rag` (rank 3) |
| `human_approval` | `skill:human-in-the-loop` | `skill:agentic-ux-patterns` (rank 2) |

### Abstention behaviour — synthetic negatives (n=183)

| Metric | Value |
| --- | ---: |
| **uncertainty_accuracy** | **0.005** (1 / 183) |
| **Cases passing** | **1 / 183** |

Synthetic negative probes use deliberately nonsense queries with `expect_uncertain: true`. After full-library promotion, the retriever **still returns confident matches** for almost all of these probes instead of abstaining.

**Interpretation:** This is the **largest honest gap** in the current system. Overall golden case pass rate (1,010 / 1,194 = **84.6%**) is dominated by this abstention weakness, **not** by ranking errors.

### Realistic confuser arm (`realistic_queries.json`, n=8)

Hand-curated near-neighbour and multi-skill scenarios. Measured 2026-07-03.

| Metric | Value |
| --- | ---: |
| Cases | 8 |
| **precision@1** | **1.000** |
| **recall@k** | **1.000** |
| **exclusion_accuracy** | **0.875** |
| **uncertainty_accuracy** | **1.000** |
| Rank failures | 0 |
| Case pass rate | **87.5%** (7 / 8) |
| Eval wall time | ~0.9 s |

| Case | Top-1 correct | Pass | Notes |
| --- | --- | --- | --- |
| KRAG system design vs graph RAG | ✅ | ❌ | `knowledge-graph-rag` at rank 3 (exclusion) |
| Human approval (HITL) | ✅ | ✅ | — |
| Guardrails vs HITL | ✅ | ✅ | — |
| TDD vs reflection | ✅ | ✅ | complement may co-rank |
| KG-RAG vs generic RAG | ✅ | ✅ | — |
| Event streaming pipeline | ✅ | ✅ | multi-skill recall in top-3 |
| Session baseline (`apply-laws-of-ai`) | ✅ | ✅ | — |
| Abstention (nonsense query) | ✅ | ✅ | — |

### Runtime and operational gates

| Gate | Result | Detail |
| --- | --- | --- |
| **CI ingest gate** (`ci_ingest_gate.py`) | **PASS** | 91 skills L2; SHACL; smoke 6/6; dry-run load |
| **KRAG cutover acceptance** | **PASS** | smoke `precision@1=1.0`, `recall@k=1.0`, 6 cases |
| **Promoted smoke eval** | **PASS** | `smoke_queries_promoted.json` |
| **Docker `skills-loader`** | **PASS** | Neo4j load after property sanitisation fix |
| **Neo4j load counts** | — | 91 Skills, 810 RetrievalUnits, 22 batches |
| **pytest realistic + journeys** | **PASS** | 3 tests (realistic confuser + 2 journey tests) |
| **Full golden eval wall time** | **~92 s** | 1,194 cases, single-threaded offline |

### MCP agent journeys (7 fixtures)

| Journey | Server | Status (2026-07-03) |
| --- | --- | --- |
| JRN-01 direct lookup TDD | fixture | ✅ |
| JRN-02 recommend defect → TDD | fixture | ✅ |
| JRN-03 abstention | fixture | ✅ |
| JRN-04 execution plan TDD | fixture | ✅ |
| JRN-05 graph RAG recommend | fixture | ✅ |
| JRN-06 human approval | embedded | ✅ |
| JRN-07 KRAG system design confuser | embedded | ✅ |

Embedded journeys run against the **live repository extract**, not the small test fixture graph.

---

## Executive summary

| Finding | Detail |
| --- | --- |
| **Ranking on positive queries** | **precision@1 = 1.0** across 1,011 positive golden cases and 8 realistic confusers |
| **Primary quality gap** | **Abstention on synthetic negatives: 0.5%** (1/183) — promoted corpus increases false-confidence on nonsense probes |
| **Secondary quality gap** | **Exclusion at ranks 2–3: 99.3%** — complement skills legitimately co-rank |
| **Prior quarantine artefact (resolved)** | Pre-fix 43% case-pass rate was dominated by quarantined skills missing retrieval units, not rank errors |
| **Promotion state** | **91/91 promoted** after `## Procedure` + registry remediation |
| **Template corpus caveat** | ~85% of golden cases are auto-generated self-retrieval templates — strong regression smoke, weak disambiguation signal |

---

## Historical baseline — pre-fix (614 cases, 47 promoted)

Measured before skill authoring remediation (2026-07-02):

| Arm | Cases | Failed | precision@1 | recall@k | citation |
| --- | ---: | ---: | ---: | ---: | ---: |
| Full corpus | 614 | 265 | 0.991 | 0.991 | 0.522 |
| Promoted-eligible filter | 285 | 0 | 1.000 | 1.000 | 1.000 |

### Failure decomposition (pre-fix full corpus)

| Category | Count | Interpretation |
| --- | ---: | --- |
| Evidence/citation only (rank correct) | 260 | Quarantined skills ranked #1 but had no retrieval units |
| Wrong rank | 5 | Quarantined KRAG + HITL skills not in projection |
| Other | 0 | — |

**Conclusion:** The promoted-eligible arm passing at 100% was **not** evidence of retrieval excellence — it excluded quarantined expectations.

---

## Remediation applied (2026-07-02 → 2026-07-03)

### Skill authoring

| Action | Count | Effect |
| --- | ---: | --- |
| Added `## Procedure` (L3 practice gate) | 16 skills | KRAG pack, HITL, baseline, agent-control |
| Extended `SKILL_PRIMARY_INTENTS` registry | 28 skills | BDD/DDD/data-architecture mapping |
| Security phrase rules | 3 phrases | human-approval queries |

**Promotion result:** 47 → **91 promoted**; quarantined **0**.

### Corpus and harness

| Action | Detail |
| --- | --- |
| Regenerated `golden_queries.json` | 614 → **1,194** cases; all `promotion_tier=release` |
| Added `realistic_queries.json` | 8 hand-curated confuser cases |
| Added `run_e2e_retrieval_eval.py` | Multi-arm audit runner |
| Added `test_e2e_realistic_retrieval.py` | Honest thresholds (precision hard, exclusion soft) |
| Embedded MCP journeys | JRN-06 (HITL), JRN-07 (KRAG confuser) |

### Operational fix (Docker)

| Issue | Fix |
| --- | --- |
| `skills-loader` exit 1 | Neo4j `CypherTypeError` on nested map properties (`supported_task_intents`) |
| Resolution | `_sanitize_neo4j_properties()` in `load_skills_neo4j.py` — JSON-serialise nested structures |

---

## CI thresholds (honest, current)

| Metric | Threshold | Rationale |
| --- | ---: | --- |
| precision@1 (realistic) | **1.0** | Primary user-facing quality gate |
| recall@k (realistic) | **1.0** | Required skills in top-3 |
| exclusion_accuracy (realistic) | **≥ 0.5** | Complement co-ranking at 2–3 is expected |
| precision@1 (release arm) | **≥ 0.98** | Template corpus regression guard |
| citation_coverage (release) | **≥ 0.95** | Evidence grounding |
| Rank failures (realistic) | **0** | Hard gate — no wrong top-1 on confusers |

**Not currently gated in CI:** synthetic negative abstention accuracy (0.5%). This should be tracked and improved before claiming production-safe out-of-domain behaviour.

---

## Residual risks (not hidden)

1. **Abstention weakness** — 182/183 synthetic negative probes return confident (non-uncertain) results after full promotion.
2. **Template-heavy golden corpus** — inflates full-corpus ranking scores; use `realistic_queries.json` for disambiguation signal.
3. **Exclusion at ranks 2–3** — graph `COMPLEMENTS` edges intentionally surface neighbours; 2 seed cases fail strict exclusion.
4. **Registry maintenance** — `SKILL_PRIMARY_INTENTS` is curated, not fully phrase-derived.
5. **Eval runtime** — full golden eval ~92 s for 1,194 cases; CI uses subsets.
6. **Offline harness** — no live Neo4j in `evaluate_offline`; journeys use embedded in-process graph plan.

---

## Recommended commands

```bash
# Fast realistic e2e (hand-curated confusers + MCP journeys)
python3 -m pytest tests/test_e2e_realistic_retrieval.py tests/test_agent_journeys.py -q

# CI ingest gate (trust, SHACL, smoke, dry-run)
python3 scripts/ci_ingest_gate.py

# Full multi-arm audit (slow, ~3 min)
python3 scripts/run_e2e_retrieval_eval.py --json

# KRAG cutover smoke
python3 scripts/krag_cutover_acceptance.py --limit 3
```

---

## What we did **not** do

- Did not lower expected skills to match wrong rankings.
- Did not remove confuser cases that fail exclusion-only checks.
- Did not claim overall golden pass rate without decomposing abstention vs ranking failures.
- Did not add Python intent boosts or confuser registry overrides.
- Did not hide the promoted-eligible filter artefact from the historical record.

---

## Artefact index

| Path | Role |
| --- | --- |
| `tests/fixtures/retrieval_evaluation/golden_queries.json` | 1,194-case regression corpus |
| `tests/fixtures/retrieval_evaluation/realistic_queries.json` | 8-case confuser corpus |
| `tests/fixtures/retrieval_evaluation/smoke_queries_promoted.json` | 6-case CI smoke |
| `tests/fixtures/agent_journeys.json` | 7 MCP journey fixtures |
| `scripts/run_e2e_retrieval_eval.py` | Multi-arm audit runner |
| `scripts/ci_ingest_gate.py` | Pre-merge ingest gate |
| `tests/test_e2e_realistic_retrieval.py` | Honest CI thresholds |
