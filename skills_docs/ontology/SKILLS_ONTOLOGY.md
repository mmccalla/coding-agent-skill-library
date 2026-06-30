# Skills Knowledge Graph Ontology

## Purpose

This ontology defines the canonical semantic contract for representing the repository's `skills/` library as a versioned, provenance-bearing knowledge graph that can support real KRAG.

It separates:

1. canonical skill identity and versioning;
2. source structure and evidence anchors;
3. semantic assertions over controlled vocabularies;
4. retrieval projections used by downstream search systems;
5. runtime skill-selection decisions;
6. answer-time citations;
7. evaluation-time benchmark, regression and governance records.

The ontology is implementation-aware but not runtime-specific. Neo4j labels, indexes, vector settings and MCP tool contracts are downstream projections, not the canonical semantic model.

## Design Principles

- Model only what is needed to answer competency questions and support KRAG safely.
- Keep asserted source structure, promoted semantic assertions, retrieval projections and generated answers distinct.
- Make every promoted semantic fact traceable to evidence anchors, source resources, extraction or mapping provenance, and versioned skill content.
- Use controlled vocabularies for bridge concepts and manage them as governed concept schemes rather than free text.
- Prefer qualified assertions for provenance-bearing semantic claims while allowing simpler direct predicates as convenience projections.

## Competency Questions

- Which skills or skill versions should an agent use for a given task shape?
- Which current skill version belongs to a canonical skill identity?
- Which pack version introduced or changed a skill recommendation?
- Which section, checklist item, alias or reference document supports a retrieved recommendation?
- Which capability, workflow stage, control theme or knowledge domain is evidenced by the current skill version?
- Which citations support an answer returned from the graph?
- Which benchmark task, observed selection and failure mode explain a retrieval regression?
- Which validation rules apply to canonical graph data and which apply only to derived retrieval projections?

## Canonical Layers

### 1. Identity and provenance layer

- `SkillPack`: a governed skill-pack boundary.
- `Skill`: the stable canonical identity of a skill across versions.
- `SkillVersion`: an immutable versioned snapshot of one skill's source-backed content.
- `IngestionRun`: a provenance activity recording how a pack version was parsed and promoted.
- `SourceResource`: a versioned source file or other ingested resource.
- `ReferenceDocument`: a source resource used as supporting local reference material.
- `MappingRule`: a governed rule used to promote semantic assertions from source evidence.
- `ValidationRule`: a structural, semantic or governance constraint.

### 2. Source structure and evidence layer

- `StructuralElement`: a typed structural fragment extracted from a source resource.
- `SkillSection`: a structural element representing a markdown section in `SKILL.md`.
- `EvidenceAnchor`: the smallest stable evidence-bearing fragment promoted for retrieval or citation.
- `Citation`: an answer-time citation pointing to one or more evidence anchors.

Every `EvidenceAnchor` must carry precise source co-ordinates sufficient for developer-facing traceability:

- `sourcePath`
- `headingPath`
- `lineStart`
- `lineEnd`
- optional `charStart`
- optional `charEnd`
- `anchorRole`

### 3. Semantic layer

- `BridgeConcept`: a superclass for governed bridge vocabularies used in routing and KRAG retrieval.
- `SkillCategory`: a governed category concept for human and pack-level organisation.
- `TaskShape`: a governed task-intent concept.
- `WorkflowStage`: a governed lifecycle-stage concept.
- `Capability`: a governed reusable-ability concept.
- `ControlTheme`: a governed safety, policy or governance concept.
- `KnowledgeDomain`: a governed subject-matter concept.
- `SemanticAssertion`: a provenance-bearing promoted semantic statement.
- `BridgeAssertion`: a qualified semantic assertion linking a skill version to a bridge concept with evidence and confidence.
- `SkillDependencyAssertion`: a qualified semantic assertion linking one skill version to another with evidence and dependency type.
- `InvocationCondition`: a governed exclusion or applicability condition used to improve selection precision.
- `Tool`: a governed tool or execution dependency required for a skill to be used safely.
- `AgentRuntime`: a governed runtime profile such as Codex, Claude Code, Cursor, Gemini or MCP-hosted execution.

### 4. Retrieval projection layer

- `RetrievalUnit`: a derived retrieval projection built from one or more evidence anchors.

`RetrievalUnit` is not the source of truth. It exists to support search and retrieval efficiency. Canonical semantics must remain anchored in `SkillVersion`, `StructuralElement`, `EvidenceAnchor` and qualified assertions.

### 5. Runtime selection layer

- `SkillSelectionRun`: one invocation of the selector.
- `SkillSelectionRequest`: a normalised representation of the incoming task.
- `SelectionCandidate`: a skill version considered during retrieval or reranking.
- `SkillSelectionDecision`: the final selected or rejected decision record.

This runtime layer is operational rather than canonical source truth, but it is required for auditable autonomous selection.

### 6. Evaluation and governance layer

- `EvaluationDataset`: a versioned benchmark task set.
- `EvaluationTask`: a representative benchmark task.
- `ExpectedSkillVersion`: a ground-truth expected skill version for a benchmark task.
- `ObservedSelection`: the skill version actually returned by the selector.
- `EvaluationRun`: a reproducible execution of a benchmark task or dataset.
- `FailureMode`: a governed failure category such as missed skill, wrong skill, stale skill or over-selection.

This layer links ontology quality, retrieval quality and release governance to explicit benchmark evidence rather than anecdotal examples.

## Controlled Vocabulary Pattern

`SkillCategory`, `TaskShape`, `WorkflowStage`, `Capability`, `ControlTheme`, `KnowledgeDomain` and `FailureMode` are not free-text tags. Their instances are governed concepts and should be managed as `skos:Concept` members of explicit concept schemes.

This supports:

- canonical labels and aliases;
- controlled hidden labels for common abbreviations or typo-tolerant variants where justified;
- narrower or broader relationships where justified;
- mapping and deprecation governance;
- cleaner retrieval and explainable routing.

Each governed concept subtype must validate against its correct concept scheme:

- `SkillCategory` -> `SkillCategoryScheme`
- `TaskShape` -> `TaskShapeScheme`
- `WorkflowStage` -> `WorkflowStageScheme`
- `Capability` -> `CapabilityScheme`
- `ControlTheme` -> `ControlThemeScheme`
- `KnowledgeDomain` -> `KnowledgeDomainScheme`
- `FailureMode` -> `FailureModeScheme`

## Core Relationships

### Canonical identity and provenance

- `containsSkill`: connects a skill pack to its canonical skills.
- `hasVersion`: connects a canonical skill to one or more skill versions.
- `currentVersion`: identifies the current active version used for routing or retrieval.
- `versionOf`: connects a skill version back to its canonical skill.
- `belongsToCategory`: connects a canonical skill to exactly one governed category concept.
- `hasSourceResource`: connects a skill version to the source resources from which it was parsed.
- `validatedBy`: connects canonical entities or projections to validation rules.

### Source structure and evidence

- `hasSection`: connects a skill version to its extracted markdown sections.
- `hasStructuralElement`: connects a skill version to non-section structural fragments when needed.
- `hasEvidenceAnchor`: connects a structural element to stable evidence anchors.
- `derivedFromElement`: connects an evidence anchor to its structural parent.
- `projectsFrom`: connects a retrieval unit to the evidence anchors from which it was derived.
- `citesEvidence`: connects a citation to one or more evidence anchors.

### Qualified semantic assertions

- `assertionFor`: connects a semantic assertion to the skill version it describes.
- `bridgeTarget`: connects a bridge assertion to the governed bridge concept it asserts.
- `supportedBy`: connects a semantic assertion to one or more evidence anchors.
- `usesMappingRule`: connects a semantic assertion to the mapping rule that promoted it when applicable.
- `dependencySourceVersion`: connects a version-aware dependency assertion to the source skill version.
- `dependencyTargetVersion`: connects a version-aware dependency assertion to the target skill version.

### Convenience semantic predicates

For efficient traversal and retrieval, direct predicates may be materialised from qualified assertions:

- `supportsTaskShape`
- `operatesInStage`
- `enablesCapability`
- `governedBy`
- `partOfDomain`

These direct predicates are convenience projections. The qualified assertion remains authoritative because it carries provenance, evidence and confidence. Every direct routing edge must be provably derived from a matching `BridgeAssertion`.

### Exclusion and compatibility semantics

To reduce false positives, the ontology also supports negative or narrowing semantics on `SkillVersion`:

- `notForTaskShape`
- `excludedWhen`
- `requiresTool`
- `incompatibleWithTool`
- `compatibleWithRuntime`
- `incompatibleWithRuntime`
- `requiresHumanApproval`
- `supersededBy`

### Skill-to-skill semantics

Use explicit predicates such as:

- `precedes`
- `requires`
- `complements`
- `refines`
- `governsSkill`
- `validatesSkill`

Avoid vague predicates such as `relatedTo`, `has`, `linksTo` or `associatedWith`.

### Evaluation and governance semantics

- `hasEvaluationTask`: connects an evaluation dataset to its benchmark tasks.
- `evaluatedDataset`: connects an evaluation run to the dataset it executed.
- `expectsSkillVersion`: connects an evaluation task to a ground-truth expectation record.
- `expectedSkillVersion`: connects an expectation record to the expected skill version.
- `observedSkillVersion`: connects an observed selection record to the retrieved skill version.
- `evaluatedTask`: connects an evaluation run to the evaluated task.
- `recordedSelection`: connects an evaluation run to its observed selection record.
- `hasFailureMode`: connects an observed selection to an optional governed failure mode.

## Canonical Property Policy

- Use stable IRIs and identifiers.
- Use explicit version identifiers for skill packs and skill versions.
- Use `skos:prefLabel`, `skos:altLabel` and selectively `skos:hiddenLabel` for governed concept labels and aliases.
- Use `owl:deprecated` together with `dcterms:isReplacedBy` when evolving governed concepts.
- Use `skos:broader` and `skos:narrower` only where same-scheme expansion is intentional and bounded.
- Use `prov:wasDerivedFrom`, `prov:wasGeneratedBy`, `prov:startedAtTime`, `prov:endedAtTime` and version identifiers for provenance instead of relying on string-only source notes.
- Use typed properties for structural and evidence identities rather than overloading one generic property across unrelated classes.
- Keep runtime selection traces separate from canonical source semantics, but link them back to `SkillVersion` and `EvidenceAnchor`.

Legacy string fields such as `source`, `rule_id`, `source_scope` and `source_ref` may still appear in downstream operational projections during migration, but they are not the canonical semantic representation.

## Property Graph Mapping

| Canonical class | Recommended Neo4j label | Identifier policy |
| --- | --- | --- |
| `SkillPack` | `SkillPack` | stable pack id |
| `Skill` | `Skill` | deterministic `skill:{name}` id |
| `SkillVersion` | `SkillVersion` | `skill-version:{skill-name}:{version}` |
| `SourceResource` | `SourceResource` | repository-relative path or governed URI |
| `ReferenceDocument` | `ReferenceDocument` | repository-relative path |
| `StructuralElement` | `StructuralElement` | source id plus structural type plus ordinal |
| `SkillSection` | `SkillSection` | skill-version id plus heading plus ordinal |
| `EvidenceAnchor` | `EvidenceAnchor` | structural parent id plus content-hash prefix |
| `RetrievalUnit` | `RetrievalUnit` | `retrieval:{skill-version-id}:{anchor-hash-prefix}` |
| `SkillSelectionRun` | `SkillSelectionRun` | stable runtime selection id |
| `SkillSelectionRequest` | `SkillSelectionRequest` | selection-run id plus request hash |
| `SelectionCandidate` | `SelectionCandidate` | selection-run id plus skill-version id |
| `SkillSelectionDecision` | `SkillSelectionDecision` | selection-run id plus ordinal |
| `EvaluationDataset` | `EvaluationDataset` | benchmark dataset id plus version |
| `EvaluationTask` | `EvaluationTask` | dataset id plus task ordinal or stable task id |
| `ExpectedSkillVersion` | `ExpectedSkillVersion` | task id plus expected skill-version id |
| `ObservedSelection` | `ObservedSelection` | evaluation-run id plus ordinal |
| `EvaluationRun` | `EvaluationRun` | stable evaluation run id |
| `Citation` | `Citation` | answer id plus ordinal |
| `MappingRule` | `MappingRule` | stable rule id |
| `ValidationRule` | `ValidationRule` | stable rule id |
| `SkillCategory` | `SkillCategory` | governed concept slug |
| `TaskShape` | `TaskShape` | governed concept slug |
| `WorkflowStage` | `WorkflowStage` | governed concept slug |
| `Capability` | `Capability` | governed concept slug |
| `ControlTheme` | `ControlTheme` | governed concept slug |
| `KnowledgeDomain` | `KnowledgeDomain` | governed concept slug |
| `FailureMode` | `FailureMode` | governed concept slug |
| `BridgeAssertion` | `BridgeAssertion` | skill-version id plus target concept plus evidence hash |
| `SkillDependencyAssertion` | `SkillDependencyAssertion` | source skill-version id plus target skill-version id plus dependency type |

## KRAG-Specific Rules

- Canonical graph retrieval should start from governed concepts, skill identity, aliases, versioned content or evidence anchors, not from synthetic category bridges.
- Graph answers must cite `EvidenceAnchor` or `Citation` nodes, not opaque skill-level summaries alone.
- Generated Cypher and retrieval projections must be validated against the canonical ontology and SHACL constraints.
- A graph answer without evidence anchors is incomplete.
- Pack versioning and skill versioning must be first-class so ingestion, rollback and evaluation remain auditable.
- Selection traces must record the chosen skill version, rejected near-matches, ranking score, rationale and supporting evidence.
- Evaluation runs must record the benchmark task, expected skill version, observed selection, failure mode where applicable, and measured quality metrics.

## Open Decisions

- Whether `SkillCategory` should remain mandatory one-to-one for every canonical skill or become pack-scoped classification with optional multi-taxonomy support.
- Whether answer-time `Citation` should be persisted or generated ephemerally from evidence anchors.
- Whether confidence should remain a simple decimal or become a structured provenance bundle by extraction method and validation state.
- Which additional bridge concepts, if any, merit governed schemes beyond the current set.
