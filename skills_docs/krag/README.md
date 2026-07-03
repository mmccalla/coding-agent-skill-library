# Skills KG — KRAG overview

Knowledge Graph-Augmented Retrieval for the skills library: versioned ingest, evidence-backed graph, hybrid retrieval, read-only MCP.

## Read next

| Document | Purpose |
| --- | --- |
| [`STATUS.md`](STATUS.md) | Done, closeout programme, to-do |
| [`CLOSEOUT_PLAN.md`](CLOSEOUT_PLAN.md) | Golden corpus realism + STATUS closeout waves |
| [`EVALUATION_CORPUS_CONTRACT.md`](EVALUATION_CORPUS_CONTRACT.md) | Tiered eval corpus schema and gates |
| [`CONTRACTS.md`](CONTRACTS.md) | Ingest, runtime, trust, projections, vocabulary, eval gates |
| [`ONTOLOGY.md`](ONTOLOGY.md) | Semantic model narrative |
| [`EVALUATION.md`](EVALUATION.md) | Measured retrieval quality (living report) |
| [`../SKILLS_KG_MCP_RUNBOOK.md`](../SKILLS_KG_MCP_RUNBOOK.md) | Operator runbook |
| [`../ontology/skills.ttl`](../ontology/skills.ttl) | Canonical ontology source |

## End-to-end flow

```text
SKILL.md change or pack add
  → trust gates (L1–L4)
  → extract + SHACL validate
  → Neo4j load (promoted retrieval projections only)
  → hybrid retrieve / MCP tools
  → evidence-backed selection + citations
```

## Design position

The graph is the primary retrieval substrate for graph-relevant questions. Vector search supports recall; the system fails its purpose if the graph cannot improve precision, provenance and safe answer generation.

Historical phase plans are in `../archive/planning/`.

## Quick validation

```bash
python3 scripts/validate_skills_ontology.py
python3 scripts/ci_ingest_gate.py
python3 scripts/krag_cutover_acceptance.py --dataset tests/fixtures/retrieval_evaluation/smoke_queries_promoted.json --limit 3
```
