# KRAG v2 Phased Implementation Plan

## Purpose

This plan ensures every recommendation in [../ontology_update_recommendations.md](../ontology_update_recommendations.md) is either:

1. already implemented in the ontology baseline; or
2. explicitly assigned to a phase with a completion criterion and validation gate.

No recommendation is left implicit.

## Current implementation status

Implemented now in the ontology baseline:

- explicit runtime selection layer classes:
  - `SkillSelectionRun`
  - `SkillSelectionRequest`
  - `SelectionCandidate`
  - `SkillSelectionDecision`
- evidence-anchor source co-ordinates:
  - `sourcePath`
  - `headingPath`
  - `lineStart`
  - `lineEnd`
  - `charStart`
  - `charEnd`
  - `anchorRole`
- direct-routing derivation constraints in SHACL for:
  - `supportsTaskShape`
  - `enablesCapability`
  - `operatesInStage`
  - `governedBy`
  - `partOfDomain`
- exclusion and compatibility semantics:
  - `notForTaskShape`
  - `excludedWhen`
  - `requiresTool`
  - `incompatibleWithTool`
  - `compatibleWithRuntime`
  - `incompatibleWithRuntime`
  - `requiresHumanApproval`
  - `supersededBy`
- scheme-specific SHACL validation for:
  - `SkillCategory`
  - `TaskShape`
  - `WorkflowStage`
  - `Capability`
  - `ControlTheme`
  - `KnowledgeDomain`
- vocabulary lifecycle governance for governed concepts:
  - `skos:altLabel`
  - `skos:hiddenLabel`
  - `owl:deprecated`
  - `dcterms:isReplacedBy`
  - bounded `skos:broader` and `skos:narrower`
- unique `skos:prefLabel` within scheme
- version-aware dependency semantics:
  - `SkillDependencyAssertion`
  - `dependencySourceVersion`
  - `dependencyTargetVersion`
  - `dependencyType`
- evaluation ontology artefacts:
  - `EvaluationDataset`
  - `EvaluationTask`
  - `ExpectedSkillVersion`
  - `ObservedSelection`
  - `EvaluationRun`
  - `FailureMode`
- evaluation metric properties:
  - `precisionAt1`
  - `recallAtK`
  - `meanReciprocalRank`
  - `ndcgAtK`
  - `graphLiftRecallAtK`
  - `p95LatencyMs`
  - `citationCoverage`
  - `exclusionAccuracy`
  - `tokenCostPerSelection`

Implemented now does not mean runtime-complete. It means the ontology contract now includes those semantics and validates them structurally.

## Recommendation coverage matrix

| Recommendation | Status | Target phase | Completion criterion |
| --- | --- | --- | --- |
| Issue 1: explicit selection-decision model | Implemented in ontology and runtime | Phase 4 complete | Runtime produces inspectable selection runs, candidates, decisions, scores, rationales and supporting evidence. |
| Issue 2: precise EvidenceAnchor source locations | Implemented in ontology | Phase 2 completion gate | Ingestion emits anchors with path, heading path and line range for all retrieval-relevant fragments. |
| Issue 3: direct semantic routing edges must be provably derived | Implemented in SHACL and split profiles | Phase 3 complete | Retrieval projections or loaded graph data pass derivation-backed SHACL validation. |
| Issue 4: stricter scheme validation | Implemented in ontology and SHACL | Closed before Phase 7 | Governed concepts support `skos:altLabel`, `skos:hiddenLabel`, deprecation or replacement policy, and controlled broader or narrower usage. |
| Issue 5: negative selection semantics | Implemented in ontology and runtime filters | Phase 4 complete | Runtime filters actively use exclusion, compatibility, approval, deprecation and supersession semantics. |
| Issue 6: RetrievalUnit ranking metadata | Implemented in ontology and retrieval-profile SHACL | Phase 3 complete | Retrieval projection model includes ranking metadata and reranking inputs. |
| Issue 7: version-aware dependencies | Implemented in ontology and SHACL | Closed before Phase 7 | Evidence-backed version-aware dependency assertions, supporting evidence links, and dependency validation rules are present. |
| Issue 8: split SHACL profiles | Implemented | Phase 2 complete | Canonical-core, retrieval-projection and runtime-selection SHACL profiles exist and are runnable separately. |
| Issue 9: evaluation artefacts | Implemented in ontology, SHACL and evaluation runtime | Phase 6 complete | Evaluation ontology slice, benchmark artefacts and metrics tracking are present and exercised. |
| Minimal target architecture | Implemented and acceptance-tested | Phase 7 complete | End-to-end slice exists from skill-pack ingestion through evidence-backed selection and evaluation logging. |
| Acceptance criteria set | Implemented and acceptance-tested | Phase 7 complete | All acceptance criteria are measured explicitly and reported at cutover. |

## Phase plan

### Phase 1 — Ontology completion and vocabulary governance

Branch:

- `krag-v2/phase-1-ontology-v2`

Scope:

- finalize the ontology baseline already in progress
- add version-aware dependency semantics:
  - `SkillDependencyAssertion`
  - `dependencySourceVersion`
  - `dependencyTargetVersion`
  - `dependencyType`
  - evidence-backed dependency support via `supportedBy`
- complete controlled vocabulary governance:
  - `skos:altLabel`
  - `skos:hiddenLabel`
  - deprecation policy
  - replacement policy
  - selective `skos:broader` or `skos:narrower` usage guidance
- ensure all ontology tests and `pyshacl` validation pass

Validation:

- `.venv/bin/python scripts/validate_skills_ontology.py`
- ontology contract tests

### Phase 2 — SHACL profile split and validation tooling

Branch:

- `krag-v2/phase-2-ingestion-pipeline`

Scope:

- split validation into:
  - `canonical-core.shacl.ttl`
  - `retrieval-projection.shacl.ttl`
  - `runtime-selection.shacl.ttl`
- extend `scripts/validate_skills_ontology.py` to run one profile or all profiles
- preserve a default all-up validation path

Validation:

- each SHACL profile runs independently
- combined validation still passes

### Phase 3 — Retrieval projection semantics

Branch:

- `krag-v2/phase-3-retrieval-projections`

Scope:

- add retrieval projection metadata:
  - `retrievalText`
  - `retrievalUnitType`
  - `lexicalBoostTerms`
  - `semanticAliases`
  - `priorityWeight`
  - `embeddingModel`
  - `embeddingVersion`
  - `vectorDimension`
  - `retrievalProfile`
- ensure direct routing edges in projection data are derivation-backed by qualified assertions
- align projection validation with SHACL profile split

Validation:

- retrieval-projection SHACL passes
- projection tests prove presence of ranking metadata

### Phase 4 — Runtime selection trace and precision controls

Branch:

- `krag-v2/phase-4-runtime-query-planning`

Scope:

- use the runtime selection layer operationally:
  - `SkillSelectionRun`
  - `SkillSelectionRequest`
  - `SelectionCandidate`
  - `SkillSelectionDecision`
- emit:
  - selected skill version
  - rejected near-matches
  - ranking score
  - selection reason
  - rejection reason
  - evidence anchors used
- enforce:
  - `excludedWhen`
  - `notForTaskShape`
  - runtime compatibility
  - tool compatibility
  - `requiresHumanApproval`
  - `supersededBy`
  - deprecated-skill filtering unless explicitly requested

Validation:

- runtime-selection SHACL passes on produced selection traces
- retrieval tests inspect selected and rejected decision artefacts

### Phase 5 — Safe text-to-Cypher and bounded graph execution

Branch:

- `krag-v2/phase-5-safe-text-to-cypher`

Scope:

- implement bounded query-family planning against the ontology-backed graph
- preserve evidence-anchor citations and selection-trace context through query execution

Validation:

- query-family validation
- citation and abstention tests

### Phase 6 — Evaluation ontology and benchmark governance

Branch:

- `krag-v2/phase-6-evaluation-governance`

Scope:

- add evaluation artefacts:
  - `EvaluationDataset`
  - `EvaluationTask`
  - `ExpectedSkillVersion`
  - `ObservedSelection`
  - `EvaluationRun`
  - `FailureMode`
- track metrics:
  - `Precision@1`
  - `Recall@k`
  - `MRR`
  - `nDCG@k`
  - `p95 latency`
  - citation coverage
  - exclusion accuracy
  - token cost per selection

Validation:

- benchmark corpus exists
- evaluation runs produce reproducible metrics

### Phase 7 — Cutover and acceptance

Branch:

- `krag-v2/phase-7-cutover-migration`

Scope:

- prove the minimal target architecture end to end:
  - skill pack ingestion
  - canonical graph load
  - retrieval projection build
  - hybrid retrieval
  - deterministic filters
  - reranking
  - evidence-backed selection decision
  - evaluation logging
- measure and report all acceptance criteria from `ontology_update_recommendations.md`

Required acceptance evidence:

- every selected skill version has at least one supporting evidence anchor
- every direct routing edge is derived from a qualified assertion
- every evidence anchor has source path, heading path and line range
- deprecated or superseded skills are excluded unless explicitly requested
- selection responses include selected skill, rationale and evidence
- top-1 skill accuracy target is measured
- Recall@3 target is measured
- p95 latency is measured
- token cost versus manual loading is measured
- citation coverage is measured on the benchmark suite
- exclusion accuracy is measured on the benchmark suite

Validation:

- `.venv/bin/python scripts/krag_cutover_acceptance.py --dataset tests/fixtures/retrieval_evaluation/smoke_queries.json --limit 3 --token-budget 240`
- targeted cutover acceptance tests

## Validation policy

Any ontology or SHACL change in any phase must be validated with:

```bash
.venv/bin/python scripts/validate_skills_ontology.py
```

If the SHACL profile split is introduced, the validator must support:

1. default all-up validation
2. per-profile validation
3. failure output that clearly identifies the failing profile

## Non-negotiable rule

The implementation is not complete until every recommendation in `ontology_update_recommendations.md` is either:

1. implemented in code or ontology artifacts; and
2. validated by the phase-specific checks above.

No recommendation may be silently dropped because it is inconvenient for the current runtime.
