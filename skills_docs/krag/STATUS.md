# Skills KG — status and roadmap

**Last updated:** 2026-07-03  
**Branch context:** `main`  
**Closeout programme:** [`CLOSEOUT_PLAN.md`](CLOSEOUT_PLAN.md) on branch `plan/golden-corpus-status-closeout`

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
| CI ingest gate (Phase 9) | `ci_ingest_gate.py` in `ci_local.sh` |
| Full promotion (**91/91** promoted, **0** quarantined) | 2026-07-03 authoring remediation |
| Release-arm positive retrieval | precision@1 **1.0**, recall@k **1.0** (n=1,011 positives) |
| Realistic confuser set | precision@1 **1.0**; 7/8 cases pass |
| Usage metrics + Grafana dashboard | `skills-kg-usage.json`, `GET /metrics` |
| MCP agent journeys **JRN-01 … JRN-07** | `tests/fixtures/agent_journeys.json` |
| Docker Neo4j loader | 91 Skills, 810 RetrievalUnits |
| Documentation consolidation (Waves A–D) | `GETTING_STARTED.md`, `krag/*`, `archive/planning/` |
| Phase 10 admin ingest (backend) | `admin_skill_ingest.py`, `POST /skills/admin/ingest`, tests |

### KRAG v2 phases (complete)

Phases 1–7: ontology, ingestion, retrieval projections, runtime, text-to-Cypher, evaluation, cutover — see archived `PHASED_IMPLEMENTATION_PLAN.md`.

### Semantic selection phases (complete)

Phases 1–9: vocabulary, authoring, trust, ingest, projections, MCP usage, eval cutover, IDP CI + dashboard — see archived `SEMANTIC_SELECTION_PHASED_PLAN.md`.

---

## Closeout programme (in progress)

All rows below are tracked in [`CLOSEOUT_PLAN.md`](CLOSEOUT_PLAN.md). Target: **empty** in progress / to do / known gaps when programme completes.

| Wave | Scope | Closes |
| --- | --- | --- |
| 0 | Plan, STATUS hygiene, `rdflib` dep, corpus contract | Stale STATUS rows; CI import reliability |
| 1 | `query_catalog.json`, `abstention_probes.json`, `confuser_pairs.json`, `validate_eval_corpus.py`, coverage matrix | Corpus contract; blind-spot structure |
| 2 | Tiered generator; shrink 1,194 → ~365 cases; delta eval; shadow baseline | Abstention corpus; blind-spot on skill diffs |
| 3 | Skills UI admin ingest | Phase 10 UI; preview-only gap |
| 4 | JRN-08 … JRN-11; confuser catalogue | Journey + exclusion gaps |
| 5 | `ci_local.sh` green (mypy); nightly coverage + shadow arm | CI typing debt; ongoing blind-spot monitoring |

---

## To do (programme backlog)

| Item | Priority | Wave | Acceptance |
| --- | --- | --- | --- |
| Realistic golden corpus (Option B) | P0 | 1–2 | Tiered files; <150 CI cases; per-tier metrics |
| Skills UI **Ingest** button after trust report | P1 | 3 | Same gate as CI; confirmation modal |
| Agent journeys **JRN-08 … JRN-11** | P2 | 4 | Out-of-domain, malicious block, usage trace, admin upload |
| Exclusion at ranks 2–3 (near-neighbours) | P2 | 4–5 | Confuser catalogue; realistic tier gates |

---

## Known gaps (until programme complete)

| Gap | Impact | Programme wave |
| --- | --- | --- |
| Template-heavy golden corpus (1,194 cases) | Misleading blended pass **84.6%** | 2 (+ shadow arm) |
| Regression blind spot after shrink | Per-skill/category/confuser gaps | 1–2 (matrix, delta eval, nightly) |
| Abstention on 182 nonce negatives | Dominated by synthetic probes | 2 |
| 2 exclusion failures in full golden set | Co-rank at 2–3 | 4 |
| Upload preview without UI persist path | Operators use API for ingest | 3 |
| `ci_local.sh` mypy failures | Merge CI not fully green | 5 |

---

## Quick commands

```bash
./scripts/ci_local.sh
python3 scripts/ci_ingest_gate.py
python3 scripts/run_e2e_retrieval_eval.py --json
python3 scripts/krag_cutover_acceptance.py --limit 3
```
