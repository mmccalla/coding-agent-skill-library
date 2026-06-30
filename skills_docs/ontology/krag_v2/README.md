# KRAG v2 Design Package

This directory defines the target architecture for refactoring the Skills KG into a real Knowledge Graph-Augmented Retrieval system.

The intent is not to tune the current bridge-heavy recommender. The intent is to replace it with a production-sensible KRAG architecture where:

1. users can add a new skill or skill pack;
2. the pack is ingested as a versioned, validated source;
3. ontology-backed graph data is built from that source with provenance;
4. runtime query planning selects graph, keyword, vector or hybrid retrieval intentionally;
5. approved text-to-Cypher patterns execute bounded read-only graph queries;
6. the answerer returns grounded results with citations, uncertainty and abstention.

## Scope

This package covers phase 0 only:

- target operating model
- ontology v2 contract
- ingestion contract
- runtime KRAG contract
- evaluation and governance contract

It does not yet prescribe code-level implementation details for each script. That work belongs in the later phase branches.

## Branch model

The KRAG refactor is organized under:

- `krag-v2-base`
- `krag-v2/phase-0-design-package`
- `krag-v2/phase-1-ontology-v2`
- `krag-v2/phase-2-ingestion-pipeline`
- `krag-v2/phase-3-retrieval-projections`
- `krag-v2/phase-4-runtime-query-planning`
- `krag-v2/phase-5-safe-text-to-cypher`
- `krag-v2/phase-6-evaluation-governance`
- `krag-v2/phase-7-cutover-migration`

## Documents

- `TARGET_OPERATING_MODEL.md` defines the end-to-end runtime and the minimum viable KRAG slice.
- `ONTOLOGY_V2.md` defines the canonical graph model and non-negotiable semantics.
- `INGESTION_CONTRACT.md` defines how skill packs become trusted graph data.
- `RUNTIME_CONTRACT.md` defines query classification, safe graph retrieval and answer generation.
- `EVALUATION_CONTRACT.md` defines the quality gates required before cutover.
- `PHASED_IMPLEMENTATION_PLAN.md` maps every recommendation from `../ontology_update_recommendations.md` to a specific phase, completion criterion and validation expectation.

## Repo-native cutover command

Use the Phase 7 acceptance harness to prove the minimum viable KRAG slice and release gates:

```bash
.venv/bin/python scripts/krag_cutover_acceptance.py --dataset tests/fixtures/retrieval_evaluation/smoke_queries.json --limit 3 --token-budget 240
```

This command validates:

- ontology and SHACL profiles
- bounded query-family planning and rendered read-only Cypher
- route-specific graph execution
- evidence-backed skill selection
- benchmark retrieval metrics and graph lift
- measured token-cost reduction versus manual skill loading

## Non-negotiable design position

The graph is not decorative metadata around markdown files.

The graph must become the primary retrieval and reasoning substrate for graph-relevant questions. Vector search remains useful for recall, but the system fails its purpose if the graph cannot materially improve retrieval precision, provenance, explainability or safe answer generation.
