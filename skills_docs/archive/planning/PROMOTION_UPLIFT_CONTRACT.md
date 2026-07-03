# Promotion uplift contract (Phase 2b)

## Purpose

Raise the promoted skill corpus from phrase-only `## When to use` matching to a
governed, auditable promotion model suitable for Phase 8 evaluation — without
weakening L2/L3 trust gates or promoting on category alone.

## Promotion sources (ordered)

| Source | Confidence | Promotes? | Evidence |
| --- | ---: | --- | --- |
| `when_to_use` | 0.95 | Yes | Section heading + line range |
| `description` | 0.85 | Yes | YAML description + section prose |
| `skill_registry` | 0.80 | Yes | Curated `SKILL_PRIMARY_INTENTS` map |
| `category` | 0.60 | **No** | Reserved for L4 warnings only |

## Status rules

```text
rejected   ← L2 security fail, or L3 practice fail (no grandfather waiver)
quarantined ← trust pass but no promotion-ready task intent
promoted   ← trust pass + ≥1 promotion-ready task intent
```

## Phase 2b exit gates

| Gate | Target |
| --- | --- |
| Promoted skills | ≥ 30 |
| Golden-query cases with ≥1 promoted expected skill | ≥ 150 / 614 |
| L4 mapping validator | `validate_skill_mapping.py` operational |
| Registry skills | Top 35 golden-query targets + baseline `apply-laws-of-ai` |

## Residual risks (deferred)

| Risk | Resolution phase |
| --- | --- |
| Registry maintenance drift | Phase 8 — tag golden cases with `promotion_tier`; CI diff on registry |
| Category-only skills remain quarantined | Phase 9 — authoring programme + L4 in `ci_local.sh` |
| Full 614-case eval on promoted subset only | Phase 8 — split release vs diagnostic eval arms |
| `apply-laws-of-ai` L3 practice waiver | Phase 9 — template `## Procedure` for baseline skill |
| Description inference false positives | Phase 8 — precision audit on promoted-only eval |
