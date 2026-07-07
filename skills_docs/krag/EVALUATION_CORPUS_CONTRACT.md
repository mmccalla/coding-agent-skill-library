# Evaluation corpus contract

**Programme:** [`CLOSEOUT_PLAN.md`](CLOSEOUT_PLAN.md)  
**Last updated:** 2026-07-07

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

### Measured sizes (2026-07-07)

| Tier / artefact | Cases |
| --- | ---: |
| Smoke | 13 |
| Realistic | 55 |
| Coverage | 254 |
| Abstention | 10 |
| Catalogue | 33 |
| Confuser pairs | 31 |
| Legacy `golden_queries.json` union | 332 |

`golden_queries.json` is **deprecated** after Wave 2; do not regenerate template bulk × per-skill archetypes (legacy was 11 × 91).

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
4. Every **promoted** skill must appear in **≥2** coverage-tier cases with **different** `query_archetype` values.
5. Confuser cases must name `excluded_skill_ids` for known near-neighbours.
6. Every entry in `confuser_pairs.json` must have **≥1** realistic-tier case.
7. Regenerate with `python3 scripts/lib/retrieval/generate_golden_queries.py --tier <name>`.

---

## Blind-spot controls

Structural guarantees so corpus shrink does not hide regressions:

| Control | Enforcement |
| --- | --- |
| Coverage matrix | `coverage_matrix.json` — skill × archetype; validator hard gate |
| Category balance | ≥5 realistic cases per pack category (9 categories) |
| Alias coverage | `alias_query` required when skill has frontmatter aliases |
| Confuser registry | `confuser_pairs.json` synced with realistic catalogue |
| Delta eval | `ci_ingest_gate.py` runs cases for each changed `skills/*/SKILL.md` |
| Query diversity | Reject duplicate coverage queries (token Jaccard > 0.85) |
| Shadow arm | Legacy template sample; ≤ 0.02 precision@1 drop vs baseline |
| New skill stubs | `--emit-stubs` adds TODO catalogue rows before merge |

See [`CLOSEOUT_PLAN.md`](CLOSEOUT_PLAN.md) § Blind-spot mitigation programme for full detail.

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

`scripts/validators/validate_eval_corpus.py` (Wave 1) checks:

- JSON schema and unique ids
- Tier size bounds
- Promoted skill coverage matrix (≥2 archetypes per skill)
- Category and confuser-pair coverage
- Template explosion guard (no `_generated_08` style ids in release tiers)
- Query similarity guard within skill coverage rows
- `--check-skill-sync` against `PACK_METADATA.json`

---

## Living corpus

Add or update cases when:

1. A new promoted skill is added (`--emit-stubs` + human review).
2. A realistic-tier confuser case fails precision@1.
3. Usage rollup reports zero hits for 30 days (advisory).
4. Graph extract adds a new `COMPLEMENTS` edge between promoted skills (validator warning until cased).
5. A new agent journey fixture is added (harvest query into catalogue).

Quarterly human review of `query_catalog.json` and `confuser_pairs.json`.

---

## Review

Curated catalogue changes require human review. Journey harvest and archetype generation may be machine-assisted but must pass validator before merge.
