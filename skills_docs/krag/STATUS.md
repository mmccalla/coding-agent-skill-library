# Skills KG — status and roadmap

**Last updated:** 2026-07-03  
**Branch context:** `plan/golden-corpus-status-closeout` (ready to merge)  
**Closeout programme:** [`CLOSEOUT_PLAN.md`](CLOSEOUT_PLAN.md) — **waves 0–5 complete** (optional P2/P3 expansions remain advisory)

This is the **single live roadmap** for the Knowledge Graph service. Completed phase plans are archived under `skills_docs/archive/planning/`.

For measured retrieval quality, see [`EVALUATION.md`](EVALUATION.md).  
For the evaluation corpus redesign, see [`EVALUATION_CORPUS_CONTRACT.md`](EVALUATION_CORPUS_CONTRACT.md).

---

## Done

| Area | Evidence |
| --- | --- |
| Portable skills library (**91** skills) | `scripts/validate_skills.py`, `skills/MANIFEST.md` |
| KRAG v2 ontology + SHACL profiles | `scripts/validate_skills_ontology.py`, `skills_docs/ontology/*.ttl` |
| Skill extract → graph → hybrid retrieval | `extract_skills_graph.py`, `retrieve_skills_hybrid.py` |
| Read-only MCP + FastAPI | `skills_mcp_server.py`, `skills_api.py` |
| Trust gates L1–L4 | `validate_skill_trust.py` |
| CI ingest gate (Phase 9 + corpus + delta eval) | `ci_ingest_gate.py`, `validate_eval_corpus.py` in `ci_local.sh` |
| Full promotion (**91/91** promoted, **0** quarantined) | 2026-07-03 authoring remediation |
| Tiered evaluation corpus (Option B) | smoke **11**, realistic **31**, coverage **195**, abstention **10**; `golden_queries.json` union **~247** |
| Coverage matrix + confuser registry | `coverage_matrix.json`, `confuser_pairs.json`, `validate_eval_corpus.py` |
| Realistic confuser tier | precision@1 **1.0**; soft exclusion **≥ 0.5** |
| Coverage tier (nightly) | precision@1 **1.0** on promoted-eligible cases |
| Change-scoped delta eval | `ci_ingest_gate.py` + `DELTA_EVAL_BASE_REF` |
| Usage metrics + Grafana dashboard | `skills-kg-usage.json`, `GET /metrics` |
| MCP agent journeys **JRN-01 … JRN-11** | `tests/fixtures/agent_journeys.json` |
| Docker Neo4j loader | 91 Skills, 810 RetrievalUnits |
| Documentation consolidation (Waves A–D + closeout docs) | `GETTING_STARTED.md`, `krag/*`, `archive/planning/` |
| Phase 10 admin ingest (backend + UI) | `admin_skill_ingest.py`, Skills UI ingest modal, tests |
| Nightly coverage workflow | `.github/workflows/nightly-eval-coverage.yml` |

### KRAG v2 phases (complete)

Phases 1–7: ontology, ingestion, retrieval projections, runtime, text-to-Cypher, evaluation, cutover — see archived `PHASED_IMPLEMENTATION_PLAN.md`.

### Semantic selection phases (complete)

Phases 1–9: vocabulary, authoring, trust, ingest, projections, MCP usage, eval cutover, IDP CI + dashboard — see archived `SEMANTIC_SELECTION_PHASED_PLAN.md`.

### Closeout programme waves

| Wave | Status | Evidence |
| --- | --- | --- |
| 0 | Done | `CLOSEOUT_PLAN.md`, `EVALUATION_CORPUS_CONTRACT.md`, `rdflib` in `pyproject.toml` |
| 1 | Done | `query_catalog.json`, `abstention_probes.json`, `confuser_pairs.json`, `validate_eval_corpus.py` |
| 2 | Done | Tiered `generate_golden_queries.py`, shrunk corpora, shadow baseline, delta eval |
| 3 | Done | Skills UI admin ingest after trust preview |
| 4 | Done | JRN-08 … JRN-11, confuser catalogue, journey tests |
| 5 | Partial | Done — nightly workflow, docs aligned, **mypy** green |

---

## To do (post-closeout / optional)

| Item | Priority | Acceptance |
| --- | --- | --- |
| Expand realistic tier toward ~100 curated/journey cases | P2 | Category balance per `EVALUATION_CORPUS_CONTRACT.md` |
| Natural-language OOD abstention probes | P3 | Gate weather/stock-style queries when retrieval abstains reliably |

---

## Known gaps

| Gap | Impact | Notes |
| --- | --- | --- |
| Realistic tier below target size (31 vs ~100) | Less journey/category diversity in PR eval | Expand catalogue over time |
| OOD abstention uses gibberish probes only | Natural-language off-domain not CI-gated | Documented in `EVALUATION.md` |

---

## Quick commands

```bash
./scripts/ci_local.sh
python3 scripts/ci_ingest_gate.py
DELTA_EVAL_BASE_REF=origin/main python3 scripts/ci_ingest_gate.py
python3 scripts/validate_eval_corpus.py --check-skill-sync --emit-matrix
python3 scripts/generate_golden_queries.py --tier all --write-legacy-golden
python3 scripts/run_e2e_retrieval_eval.py --json
python3 scripts/krag_cutover_acceptance.py --limit 3
```
