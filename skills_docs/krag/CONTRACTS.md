# KRAG operating contracts

Normative rules for ingest, runtime, trust, retrieval projections, vocabulary and evaluation gates.

**Status:** KRAG v2 is the live runtime (cutover complete). Roadmap: `STATUS.md`. Measured quality: `EVALUATION.md`.

Schema source: `../ontology/skills.ttl` and SHACL profiles.

---

## 1. Ingestion

### Objective

Ingest skills and skill packs into Neo4j as versioned, evidence-backed graph data without manual bridge editing.

### Ingestion stages

#### 1. Source registration

For each incoming pack: assign `skill_pack_id`, version, pack metadata, source root, checksum, timestamps, owner and provenance.

#### 2. Structural parsing

Preserve pack, skill, section and checklist structure; extract frontmatter; preserve related-skill references, verification items and reference docs.

#### 3. Evidence anchoring

Create stable evidence anchors for retrieval-relevant fragments (frontmatter, sections, checklist items, related-skill declarations, reference links). Each anchor records source path, structural parent, content hash and extractor version.

#### 4. Semantic extraction

Promote: canonical skill identity, category membership, aliases, capabilities, task intents, workflow stages, constraints, procedure steps, verification checks, related-skill assertions.

#### 5. Validation before promotion

Reject or quarantine when required frontmatter is missing, aliases collide, predicates are disallowed, evidence anchors are missing, related skills are unknown, identifiers are unstable, or checksum duplicates are unexpected.

#### 6. Projection build

Derive retrieval projections from canonical nodes plus evidence anchors. Projections are not canonical source facts.

### Idempotency

Re-running ingestion for the same pack version must not duplicate skills, aliases, assertions or anchors. Canonical identities remain stable.

### Failure handling

Hard fail on schema or provenance violations; quarantine ambiguous semantic extraction; never partially promote assertions if anchoring failed.

---

## 2. Runtime

### Objective

Answer questions from graph structure plus source-backed evidence using bounded, validated retrieval plans.

### Query classification

Minimum intents: `skill_lookup`, `skill_pack_discovery`, `alias_resolution`, `relationship_traversal`, `execution_context`, `governance_validation_lookup`, `multi_skill_synthesis`, `missing_evidence_abstention`.

### Entity resolution

Resolve canonical skill ids, pack ids, aliases and governed concepts against first-class ontology nodes.

### Retrieval strategy

1. graph-first for entities, traversals, constraints, procedures and verification  
2. keyword-first for exact ids or names  
3. vector-first for vague exploratory questions  
4. hybrid when recall matters  

### Safe text-to-Cypher

Bounded by approved labels, relationship types, query families, read-only execution, depth and cardinality limits. Validate before execution; abstain or fall back on failure.

### Evidence packaging

Return bounded evidence: canonical nodes, path summaries, anchor ids, source paths, cited fragments, ranking rationale.

### Answer synthesis

Cite evidence for material claims; state uncertainty; abstain when evidence is missing, weak or contradictory.

### Anti-patterns

- No raw LLM-generated Cypher execution  
- No answers without citations  
- No category-level bridge scores as primary ranking signal  

---

## 3. Skill trust and promotion

Skills are **untrusted content** until validators pass.

### Validation layers

| Layer | Script | Blocks ingest? | Scope |
| --- | --- | --- | --- |
| L1 Structural | `validate_skills.py` | Yes | Template, frontmatter, sections |
| L2 Security | `validate_skill_security.py` | Yes | Injection, override, secrets |
| L3 Best practice | `validate_skill_practice.py` | Yes (new); warn (legacy) | Procedure, verification |
| L4 Semantic readiness | `validate_skill_mapping.py` | Quarantine | TaskIntent mapping |
| Orchestrator | `validate_skill_trust.py` | Aggregates L1–L4 | CI, upload preview |

L2 categories map to `skills_docs/security/OWASP_ASI_CROSSWALK.md` (ASI01, ASI04, ASI05).

### Promotion states

| Status | MCP / graph |
| --- | --- |
| `rejected` | Excluded |
| `quarantined` | Excluded from retrieval projections |
| `promoted` | Full MCP + graph |

**Current state (2026-07-07):** 113/113 promoted. See `STATUS.md`.

Admin ingest must record trust report hash, actor and outcome (Phase 10).

---

## 4. Retrieval projections

Promoted-only slice for hybrid retrieval, vector indexing and MCP selection.

| `promotion_status` | RetrievalUnit | Hybrid retrieval |
| --- | --- | --- |
| `promoted` | Yes | Yes |
| `quarantined` / `rejected` | No | No |

Builder: `scripts/graph/build/build_retrieval_projections.py`. Loader creates `RetrievalUnit` nodes only for promoted skills. `retrieve_skills_hybrid` rejects non-promoted candidates.

SHACL: `../ontology/retrieval-projection.shacl.ttl`.

---

## 5. Governed vocabulary

TaskIntent (contract language) maps to ontology `TaskShape` instances.

| Term | TTL class | Instance id |
| --- | --- | --- |
| TaskIntent | `skills:TaskShape` | `skills:task-intent-{slug}` |
| WorkflowStage | `skills:WorkflowStage` | `skills:workflow-stage-{slug}` |

Mapping slug in `scripts/lib/routing/skill_section_mapping.py` must match the TTL instance suffix after `task-intent-`.

Instance graphs: `../ontology/instances/task-intents.ttl`, `workflow-stages.ttl`.

New slugs require TTL instance, mapping rule (if prose-mapped) and golden eval case.

---

## 6. Evaluation gates

### Operating objective

The graph must materially improve retrieval precision, provenance and answer quality versus vector-only retrieval for graph-relevant questions. **Cutover is complete**; ongoing evaluation tracks regression and known gaps.

### Layers

Source/ingestion, ontology, retrieval, runtime planning, answer quality, operational quality (latency, token cost, observability).

### Required test sets

Canonical-name lookups, alias lookups, vague semantic questions, near-neighbour pairs, relationship traversals, abstention cases, contradictory evidence, pack-version regression, malicious text-to-Cypher prompts.

### Release gates (ongoing)

- Graph-relevant queries outperform vector-only baseline (graph lift ≥ 0)  
- Citation-backed material claims  
- Forbidden Cypher rejected  
- Idempotent ingestion  
- Near-neighbour disambiguation on `realistic_queries.json` (precision@1 = 1.0; exclusion ≥ 0.5)  
- Tiered corpus contract (`EVALUATION_CORPUS_CONTRACT.md`) passes `validate_eval_corpus.py`  
- Change-scoped delta eval passes for touched `skills/*/SKILL.md` when `DELTA_EVAL_BASE_REF` is set  

### Known gaps (not CI-gated)

- Natural-language **OOD abstention** — only gibberish/low-confidence probes are gated in `abstention_probes.json`. See `EVALUATION.md`.
- **mypy** — `python3 -m mypy` passes on `scripts/`; enforced in `ci_local.sh`.

### Observability per query

Query id, intent, resolved entities, strategy, query family, Cypher, validation outcome, node ids, anchor ids, citation ids, latency, cost, abstention reason.
