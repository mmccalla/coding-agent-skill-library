# Skills KG — status and roadmap

**Last updated:** 2026-07-07  
**Branch context:** `main`  
**Closeout programme:** [`CLOSEOUT_PLAN.md`](CLOSEOUT_PLAN.md) — **waves 0–5 complete** (optional P2/P3 expansions remain advisory)

This is the **single live roadmap** for the Knowledge Graph service.

For measured retrieval quality, see [`EVALUATION.md`](EVALUATION.md).  
For the evaluation corpus redesign, see [`EVALUATION_CORPUS_CONTRACT.md`](EVALUATION_CORPUS_CONTRACT.md).

---

## Done

| Area | Evidence |
| --- | --- |
| Portable skills library (**113** skills) | `scripts/validators/validate_skills.py`, `skills/MANIFEST.md` |
| KRAG v2 ontology + SHACL profiles | `scripts/validators/validate_skills_ontology.py`, `skills_docs/ontology/*.ttl` |
| Skill extract → graph → hybrid retrieval | `scripts/graph/build/extract_skills_graph.py`, `scripts/lib/retrieval/retrieve_skills_hybrid.py` |
| Read-only MCP + FastAPI | `scripts/runtime/mcp/skills_mcp_server.py`, `scripts/runtime/api/skills_api.py` |
| MCP legacy entrypoint shim | `scripts/skills_mcp_server.py` (forwards to `scripts.runtime.mcp`) |
| Scripts package layout (`scripts/<domain>/`) | PR #34 reorganisation; `scripts/validators/validate_docs.py` stale-path guard |
| Trust gates L1–L4 | `scripts/validators/validate_skill_trust.py` |
| CI ingest gate (Phase 9 + corpus + delta eval) | `scripts/utils/ci/ci_ingest_gate.py`, `scripts/validators/validate_eval_corpus.py` in `ci_local.sh` |
| Full promotion (**113/113** promoted, **0** quarantined) | 2026-07-03 authoring remediation + 2026-07-06 bias/fallacy skills |
| Tiered evaluation corpus (Option B) | smoke **13**, realistic **62**, coverage **256**, abstention **10**; `golden_queries.json` union regenerated |
| Coverage matrix + confuser registry | `coverage_matrix.json`, `confuser_pairs.json` (**38** pairs), `validate_eval_corpus.py` |
| Realistic confuser tier | precision@1 **1.0**; soft exclusion **≥ 0.5** |
| Coverage tier (nightly) | precision@1 **1.0** on promoted-eligible cases |
| Change-scoped delta eval | `scripts/utils/ci/ci_ingest_gate.py` + `DELTA_EVAL_BASE_REF` |
| Usage metrics + Grafana dashboard | `skills-kg-usage.json`, `GET /metrics` |
| MCP agent journeys **JRN-01 … JRN-13** | `tests/fixtures/agent_journeys.json` (incl. bias/fallacy review) |
| Docker Neo4j loader | 113 Skills, **1045** RetrievalUnits (deterministic embed plan) |
| Documentation consolidation (Waves A–D + closeout docs) | `GETTING_STARTED.md`, `krag/*` |
| Phase 10 admin ingest (backend + UI) | `scripts/runtime/mcp/admin_skill_ingest.py`, Skills UI ingest modal, tests |
| Nightly coverage workflow | `.github/workflows/nightly-eval-coverage.yml` |
| `cognitive-bias-review` + `logical-fallacy-review` skills | `skills/cognitive-bias-review/`, `skills/logical-fallacy-review/`; JRN-12, JRN-13 |

### KRAG v2 phases (complete)

Phases 1–7: ontology, ingestion, retrieval projections, runtime, text-to-Cypher, evaluation, cutover — complete (see Done table).

### Semantic selection phases (complete)

Phases 1–9: vocabulary, authoring, trust, ingest, projections, MCP usage, eval cutover, IDP CI + dashboard — complete.

### Closeout programme waves

| Wave | Status | Evidence |
| --- | --- | --- |
| 0 | Done | `CLOSEOUT_PLAN.md`, `EVALUATION_CORPUS_CONTRACT.md`, `rdflib` in `pyproject.toml` |
| 1 | Done | `query_catalog.json`, `abstention_probes.json`, `confuser_pairs.json`, `validate_eval_corpus.py` |
| 2 | Done | Tiered `generate_golden_queries.py`, shrunk corpora, shadow baseline, delta eval |
| 3 | Done | Skills UI admin ingest after trust preview |
| 4 | Done | JRN-08 … JRN-11, confuser catalogue, journey tests |
| 5 | Done | Nightly workflow, docs aligned, **mypy** green |

---

## To do (post-closeout / optional)

| Item | Priority | Acceptance |
| --- | --- | --- |
| Expand realistic tier toward ~100 curated/journey cases | P2 | Category balance per `EVALUATION_CORPUS_CONTRACT.md` (62 today) |
| Expand query catalogue toward ≥100 curated entries | P2 | Source of truth for smoke/realistic generation (40 today) |
| Natural-language OOD abstention probes | P3 | Gate weather/stock-style queries when retrieval abstains reliably |

---

## Known gaps

| Gap | Impact | Notes |
| --- | --- | --- |
| Realistic tier below target size (62 vs ~100) | Less journey/category diversity in PR eval | Expand catalogue over time |
| Query catalogue below target (40 vs ≥100) | Slower realistic-tier growth | Harvest from journeys and confuser reviews |
| OOD abstention uses gibberish probes only | Natural-language off-domain not CI-gated | Documented in `EVALUATION.md` |

---

## Quick commands

```bash
./scripts/dev_workflow/ci_local.sh
python3 scripts/utils/ci/ci_ingest_gate.py
DELTA_EVAL_BASE_REF=origin/main python3 scripts/utils/ci/ci_ingest_gate.py
python3 scripts/validators/validate_eval_corpus.py --check-skill-sync --emit-matrix
python3 scripts/lib/retrieval/generate_golden_queries.py --tier all --write-legacy-golden
python3 scripts/lib/retrieval/run_e2e_retrieval_eval.py --json
python3 scripts/lib/retrieval/evaluate_skill_retrieval.py --dataset tests/fixtures/retrieval_evaluation/smoke_queries_promoted.json --limit 3
```
