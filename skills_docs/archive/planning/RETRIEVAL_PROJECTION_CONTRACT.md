# Retrieval projection contract (KRAG v2 Phase 6)

Retrieval projections are the **promoted-only** slice of the skills graph used for hybrid retrieval, vector indexing and MCP skill selection.

## Promotion gate

| `promotion_status` | In admin graph | RetrievalUnit nodes | Hybrid retrieval |
| --- | --- | --- | --- |
| `promoted` | Yes | Yes | Yes |
| `quarantined` | Yes | No | No |
| `rejected` | Yes | No | No |
| missing / other | Yes | No | No |

Only skills with `promotion_status = promoted` receive `RetrievalUnit` projections.

## Builder API

`scripts/build_retrieval_projections.py`:

- `PROMOTED_STATUS` — canonical promoted value (`"promoted"`)
- `filter_promoted_records(records)` — promoted skills plus dependent sections, bridges, references and inter-promoted relationships
- `build_retrieval_projection_records(records)` — `RetrievalUnit` property dicts aligned with `load_skills_neo4j._retrieval_unit_from_section`
- `build_retrieval_projections(records)` — `{ skills, retrieval_units, promotion_summary }`

## Load and retrieval wiring

- `load_skills_neo4j.build_load_plan` loads the full graph for admin visibility but creates `RetrievalUnit` nodes only via `build_retrieval_projection_records`.
- `retrieve_skills_hybrid.retrieve_hybrid_skills` rejects candidates where `Skill.promotion_status != promoted`.

## SHACL alignment

Retrieval unit fields must satisfy `skills_docs/ontology/retrieval-projection.shacl.ttl` (`RetrievalUnitShape`).
