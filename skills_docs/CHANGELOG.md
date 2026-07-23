# Changelog

Release-level changes to the portable skills library and Skills KG service.

## 2026-07-23 (v0.1.11 — L3 discovery proxy promote)

### Skills / retrieval discovery

- Alias and description discovery packs for natural hold-out soft misses (delivery, security, UX, ontology, event-driven, and related skills).
- Vague-filler abstention: hybrid returns empty when the query has only filler tokens (keeps OOD empty=1.0 on fixture 0.2.0).
- Paired trunk vs experiment (same fixture, live Neo4j wipe+reload): B1 soft 0.875 → 1.000; soft Δ vs B2-lex +0.083 → +0.167; OOD intact. Live Cursor Arm B soft remained 1.000 on both arms — **not** a Cursor-superiority claim.
- Hybrid score weights unchanged.

## 2026-07-22 (v0.1.10 — P1-RAG discovery metadata)

### Skills / retrieval discovery

- Enriched `knowledge-retrieval-rag` and `evaluation-and-monitoring` frontmatter for RAG feature / evaluation-gates queries.
- Narrowed `krag-evaluation-governance` metadata to KRAG/GraphRAG-scoped language (removed unconstrained gates/release phrasing).
- Experiment evidence: hold-out BGE soft_hit 0.875 (was 0.833); `multi_rag_eval` soft-hits an acceptable skill; OOD empty 1.0; clean Neo4j live probes agree. Hybrid weights/gates unchanged.

## 2026-07-22 (v0.1.9 — OOD-safe hybrid retrieval defaults)

### Skills KG / retrieval

- Removed the lexical body-text hybrid channel after ranking diagnostics showed text overlap driving wrong tops.
- Promoted evidence-backed defaults: `HybridScoreWeights(metadata=0.70, vector=0.25, graph=0.15, bridge=0.60)` and `min_top1_margin=0.01` (score floor `0.35` unchanged).
- Hold-out BGE evidence for this promote set: soft_hit ≈ 0.833, empty ≈ 0.125, ood_empty = 1.0, ood_false_hit = 0.0 (margin 0.0 discarded for product because of OOD false hits).

## 2026-07-15 (v0.1.8 — lean MCP wire payloads)

### Skills KG / MCP

- Agent-facing MCP/API responses omit fat `selection_trace` for `recommend_skills` and `route_skill_query`; full Phase-7 traces remain in `skills_usage` selection-run logs via `usage.selection_run_id`.
- Recommendation wire keeps anchors/snippets/source paths; duplicate `section_ids` and graph `evidence_paths` are audit-only.
- Execution guides omit graph `evidence_paths` on the wire; non-empty evidence anchors and `related_skill_ids` remain.
- Live Cursor MCP and e2e A/B vs `main` confirmed ranking/route accuracy unchanged.

## 2026-07-08 (bias/fallacy skill rename + routing)

### Skills library

- Canonical IDs: **`cognitive-bias-review`**, **`logical-fallacy-review`** (replace `avoid-cognitive-biases`, `avoid-fallacies`).
- **Alias deprecation:** `avoid-*` names remain in frontmatter aliases until **v0.2.0**; MCP and filesystem routing should prefer canonical IDs in new work.
- Sharper skill boundaries: judgement distortion vs argument validity; sunk-cost on fallacy checklist.
- Neighbour links: `reflection-and-verification`, `reasoning-techniques`, `threat-modeling`, `code-review-and-quality`, `risk-management`.

### Evaluation

- Confuser pairs: bias↔fallacy, bias↔reflection, fallacy↔reflection, fallacy↔code-review, fallacy↔reasoning, bias↔prioritisation.
- Realistic tier **62** cases; confuser registry **38** pairs.

## 2026-07-07 (documentation sync + library growth)

### Skills library

- **113-skill** flat library (`avoid-cognitive-biases`, `avoid-fallacies` added to `agent-control-patterns`).
- Eval corpora refreshed: smoke **13**, realistic **55**, coverage **254**, confuser pairs **31**, legacy golden union **332**.
- Agent journeys **JRN-12** (cognitive-bias review) and **JRN-13** (fallacy review).

### Skills KG / tooling

- `scripts/` reorganised into domain packages (`graph/`, `runtime/`, `lib/`, `validators/`, etc.) — PR #34.
- MCP legacy shim at `scripts/skills_mcp_server.py` for configs still pointing at the pre-reorg path — PR #36.
- `validate_docs.py` stale flat-script-path guard.

### Documentation

- `krag/STATUS.md`, `krag/EVALUATION.md`, `LIBRARY_CONTRACT.md`, runbooks aligned to current counts and layout.

## 2026-07-03 (closeout programme)

### Skills KG

- **Tiered evaluation corpus (Option B):** smoke 11, realistic 31, coverage 195, abstention 10; `golden_queries.json` union ~247 (down from 1,194 templates).
- `validate_eval_corpus.py` — corpus schema, coverage matrix, confuser pairs, duplicate-query guard.
- `generate_golden_queries.py` rewritten for tiered generation; shadow baseline recorded for shrink comparison.
- CI ingest gate: corpus validator + change-scoped **delta eval** on touched `SKILL.md` paths.
- Soft exclusion threshold (0.5) for complement co-ranking at ranks 2–3.
- Skills UI **admin ingest** after trust preview; Phase 10 complete (backend + UI).
- Agent journeys **JRN-08 … JRN-11** (out-of-domain, security, usage trace, admin ingest).
- Nightly workflow: `.github/workflows/nightly-eval-coverage.yml`.

### Documentation

- `krag/EVALUATION.md` rewritten for tiered metrics.
- `krag/STATUS.md`, `EVALUATION_CORPUS_CONTRACT.md`, `CLOSEOUT_PLAN.md` updated.
- `SKILLS_KG_MCP_RUNBOOK.md` — tiered eval, UI ingest, delta eval.

### Residual (Wave 5)

- Resolved: `python3 -m mypy` passes on `scripts/`.

## 2026-07-03 (earlier)

### Skills KG

- Full-library promotion: **91/91** skills promoted; quarantine cleared via Procedure sections and intent registry.
- Golden evaluation corpus regenerated: **1,194** cases with `promotion_tier=release`.
- CI ingest gate (`ci_ingest_gate.py`) wired into `ci_local.sh`.
- Usage and trust metrics on `GET /metrics`; Grafana `Skills KG Usage` dashboard.
- E2E evaluation report consolidated to `krag/EVALUATION.md`.
- Docker loader fix: nested Neo4j property sanitisation.

### Documentation

- Documentation consolidation started: `GETTING_STARTED.md`, `krag/STATUS.md`, updated doc hubs (Waves A–D).
- Waves A–D: consolidated `krag/` docs and added `validate_docs.py` CI gate.
- Phase 10 admin ingest: `POST /skills/admin/ingest`, pack-metadata registration, MCP reload, abstention tuning for synthetic negative probes.
- Closeout programme: tiered realistic golden corpus plan (`krag/CLOSEOUT_PLAN.md`); STATUS.md tracks waves 0–5.

## Earlier

- KRAG v2 cutover: ontology-backed hybrid retrieval, read-only MCP, FastAPI + UI stack.
- Mandatory `apply-laws-of-ai` baseline; flat **91-skill** library with nine semantic categories.
