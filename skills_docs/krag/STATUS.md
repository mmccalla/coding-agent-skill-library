# Skills KG — status and roadmap

**Last updated:** 2026-07-03  
**Branch context:** `krag-v2/semantic-selection`

This is the **single live roadmap** for the Knowledge Graph service. Completed phase plans are archived under `skills_docs/archive/planning/` (Wave C).

For measured retrieval quality, see `ontology/krag_v2/E2E_EVALUATION_REPORT.md` (consolidated into `krag/EVALUATION.md` in Wave B).

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

### KRAG v2 phases (complete)

Phases 1–7: ontology, ingestion, retrieval projections, runtime, text-to-Cypher, evaluation, cutover — see archived `PHASED_IMPLEMENTATION_PLAN.md`.

### Semantic selection phases (complete)

Phases 1–9: vocabulary, authoring, trust, ingest, projections, MCP usage, eval cutover, IDP CI + dashboard — see archived `SEMANTIC_SELECTION_PHASED_PLAN.md`.

---

## In progress

| Item | Surface | Notes |
| --- | --- | --- |
| Documentation consolidation | `skills_docs/` | Waves A–D; simpler paths for repo users |
| Phase 10 — admin skill ingest | `skills_api.py`, `skills-ui` Upload tab | Preview exists; persist + graph reload not shipped |

---

## To do

| Item | Priority | Acceptance |
| --- | --- | --- |
| `POST /skills/admin/ingest` with admin auth | P1 | Trusted upload → extract → load → agent `resolve_skill` |
| Skills UI **Ingest** button after trust report | P1 | Same gate as CI; confirmation modal |
| Agent journeys **JRN-08 … JRN-11** | P1 | Out-of-domain, malicious block, usage trace, admin upload |
| Synthetic negative **abstention** improvement | P2 | `uncertainty_accuracy` on 183 negative probes (currently **0.5%**) |
| Exclusion at ranks 2–3 (near-neighbours) | P2 | KRAG vs graph-RAG confuser cases |

---

## Known gaps (not hidden)

| Gap | Impact | CI gated? |
| --- | --- | --- |
| Abstention on nonsense queries | Overall golden pass **84.6%** (1,010/1,194) | No |
| 2 exclusion failures in full golden set | Related skills co-rank at 2–3 | Partial (realistic set) |
| `POST /skills/upload/preview` only | No admin persist path | N/A |

---

## Quick commands

```bash
./scripts/ci_local.sh
python3 scripts/ci_ingest_gate.py
python3 scripts/run_e2e_retrieval_eval.py --json
python3 scripts/krag_cutover_acceptance.py --limit 3
```
