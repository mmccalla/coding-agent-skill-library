# Evaluation corpus contract

**Programme:** [`CLOSEOUT_PLAN.md`](CLOSEOUT_PLAN.md)  
**Last updated:** 2026-07-03

Defines tiered retrieval evaluation corpora replacing the templated 1,194-case `golden_queries.json` bulk generator.

---

## Tiers

| Tier | File | Target size | CI role |
| --- | --- | --- | --- |
| Smoke | `smoke_queries_promoted.json` | 25–35 | Merge gate (`ci_ingest_gate.py`) |
| Realistic | `realistic_queries.json` | ~100 | Release gate (precision@1, confusers) |
| Coverage | `coverage_queries.json` | ~250 | Nightly; all promoted skills represented |
| Abstention | `abstention_probes.json` | ~15 | Release gate (uncertainty_accuracy) |
| Catalogue | `query_catalog.json` | ≥100 curated | Source of truth for realistic + smoke |

`golden_queries.json` is **deprecated** after Wave 2; do not regenerate 11 templates × 91 skills.

---

## Case schema

Required fields:

- `id` — stable snake_case identifier
- `query` — natural-language user/agent utterance
- `expected_skill_ids` — list of acceptable top matches (may be empty for abstention)
- `expect_uncertain` — boolean
- `promotion_tier` — `release` | `diagnostic`

Optional fields:

- `required_skill_ids` — must appear in top-k
- `excluded_skill_ids` — must not appear in top-k
- `query_source` — `curated` | `journey` | `archetype` | `abstention_probe`
- `query_archetype` — `direct` | `task` | `alias` | `confuser` | `multi_skill` | `abstention`
- `naturalness` — `high` | `medium` (archetype only)

---

## Generation rules

1. **No** per-skill nonce negative probes (`zzqp qxjv…`).
2. **Max 3** positive cases per skill in coverage tier.
3. **≥90%** of smoke + realistic queries must be `curated` or `journey` sourced.
4. Every **promoted** skill must appear in **≥1** coverage-tier case.
5. Confuser cases must name `excluded_skill_ids` for known near-neighbours.
6. Regenerate with `python3 scripts/generate_golden_queries.py --tier <name>`.

---

## Gate thresholds

| Metric | Smoke | Realistic | Coverage | Abstention |
| --- | --- | --- | --- | --- |
| precision@1 | ≥ 0.98 | **1.0** | ≥ 0.95 | n/a |
| recall@k (k=3) | ≥ 0.98 | **1.0** | ≥ 0.95 | n/a |
| exclusion_accuracy | n/a | ≥ 0.5 | measured | n/a |
| uncertainty_accuracy | n/a | n/a | n/a | ≥ 0.9 |
| rank failures | 0 | 0 | report only | n/a |

---

## Validation

`scripts/validate_eval_corpus.py` (Wave 1) checks:

- JSON schema and unique ids
- Tier size bounds
- Promoted skill coverage map
- Template explosion guard (no `_generated_08` style ids in release tiers)

---

## Review

Curated catalogue changes require human review. Journey harvest and archetype generation may be machine-assisted but must pass validator before merge.
