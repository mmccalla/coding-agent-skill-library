# Ontology v2 Contract

## Design objective

Define a compact ontology that distinguishes source structure, semantic meaning, retrieval projections and answer citations cleanly enough to support real KRAG.

## Core modelling principles

1. Keep source structure separate from semantic meaning.
2. Keep asserted facts separate from inferred facts.
3. Keep evidence anchors separate from retrieval projections.
4. Keep ontology classes separate from instance entities.
5. Keep runtime query intent separate from stored skill semantics.
6. Do not use category membership as a substitute for ontology meaning.

## Canonical classes

### Source and versioning

- `SkillPack`
- `Skill`
- `SkillVersion`
- `SourceResource`
- `StructuralElement`
- `EvidenceAnchor`

### Semantic knowledge

- `Alias`
- `Capability`
- `TaskIntent`
- `WorkflowStage`
- `Constraint`
- `ProcedureStep`
- `VerificationCheck`
- `RelatedSkillAssertion`
- `OntologyMappingAssertion`
- `SkillDependencyAssertion`

### Runtime and answering

- `QueryIntent`
- `QueryTemplate`
- `RetrievalProjection`
- `Citation`
- `EvaluationDataset`
- `EvaluationTask`
- `ExpectedSkillVersion`
- `ObservedSelection`
- `EvaluationRun`
- `FailureMode`

## Required semantics

### SkillPack

Represents a coherent installable pack or library segment. Must carry stable identity, version, checksum and source ownership.

### Skill

Represents the canonical operational unit. Must carry stable id, canonical name, title, summary and links to current and historical versions.

### SkillVersion

Represents a specific versioned representation of a skill. This is the node that binds a skill to its source resource, extracted structure and promoted assertions.

### SourceResource

Represents the physical source file or referenced artefact. Every promoted fact must trace back to one or more source resources.

### StructuralElement

Represents section, paragraph, list item, checklist item, heading or referenced document fragment. It preserves layout and source hierarchy without pretending those elements are semantic concepts.

### EvidenceAnchor

Represents the exact source-grounded span or fragment used to justify a semantic assertion or answer citation.

### Alias

Represents a discoverable lexical surface. Aliases are first-class retrieval assets, not incidental frontmatter strings.

Governed aliases should distinguish:

- canonical labels
- controlled alternative labels
- hidden labels for common abbreviations or typo-tolerant variants
- deprecated concepts with explicit replacements
- bounded broader or narrower hierarchy links within the same scheme

### Capability, TaskIntent, WorkflowStage

Represent curated semantic concepts used for retrieval and reasoning. They must be explicitly defined and governed, not inferred from category names by default.

### Constraint, ProcedureStep, VerificationCheck

Represent the operational content of a skill in normalized, queryable form. These are more retrieval-relevant than raw markdown sections alone.

### SkillDependencyAssertion

Represents a version-aware dependency between skill versions. It must identify source skill version, target skill version, dependency type, provenance and evidence support.

### EvaluationDataset, EvaluationTask, ExpectedSkillVersion, ObservedSelection, EvaluationRun, FailureMode

Represent the benchmark and governance layer needed to prove KRAG quality. The ontology must capture:

- versioned benchmark datasets
- ground-truth expected skill versions
- observed selections returned by the runtime
- governed failure modes
- reproducible evaluation runs with metrics

## Required relationship families

- `HAS_VERSION`
- `DERIVED_FROM_SOURCE`
- `HAS_STRUCTURE`
- `HAS_EVIDENCE`
- `HAS_ALIAS`
- `ENABLES_CAPABILITY`
- `SUPPORTS_TASK_INTENT`
- `OPERATES_IN_STAGE`
- `HAS_CONSTRAINT`
- `HAS_PROCEDURE_STEP`
- `HAS_VERIFICATION_CHECK`
- `ASSERTS_RELATED_SKILL`
- `JUSTIFIED_BY`
- `PROJECTED_AS`
- `USED_IN_QUERY_TEMPLATE`
- `SUPPORTED_BY_CITATION`
- `HAS_EVALUATION_TASK`
- `EVALUATED_DATASET`
- `EXPECTS_SKILL_VERSION`
- `EXPECTED_SKILL_VERSION`
- `OBSERVED_SKILL_VERSION`
- `EVALUATED_TASK`
- `RECORDED_SELECTION`
- `HAS_FAILURE_MODE`

## Prohibited shortcuts

- Do not create `ControlTheme` and `KnowledgeDomain` by copying the category folder name into every skill.
- Do not use `RELATED_TO` where a real operational predicate exists.
- Do not let retrieval depend on broad synthetic bridge labels instead of skill-specific facts.
- Do not rely on section text alone as the only retrieval surface.

## Retrieval projection requirements

The canonical graph must remain semantically clean. Retrieval-friendly projections may denormalize for search, but they must be derived from canonical graph data and remain traceable.

Every `RetrievalProjection` must include:

- canonical skill id
- canonical name
- aliases
- summary
- selected capability labels
- selected task intents
- selected constraints or verification cues
- linked evidence anchors

Evaluation runs must include, at minimum:

- precision at 1
- recall at k
- mean reciprocal rank
- nDCG at k
- graph lift over vector-only baseline
- p95 latency
- citation coverage
- exclusion accuracy
- token cost per selection

## Validation requirements

The ontology must be backed by machine validation rules that enforce:

- evidence linkage for promoted assertions
- alias uniqueness within the library
- allowed predicates only
- stable identifier policy
- version integrity
- no orphan promoted assertions
- no retrieval projection without canonical provenance
- no deprecated governed concept without explicit replacement
- no cross-scheme broader or narrower hierarchy edge
- no version-aware dependency without evidence and provenance
- no evaluation run without benchmark task, observed selection and metric fields

## Competency questions

The ontology passes only if it can support these questions directly:

1. Which skill best fits this user task and why?
2. Which aliases resolve to the same skill?
3. Which constraints govern use of this skill?
4. Which related skills complement or refine it?
5. Which source spans justify that recommendation?
6. Which skill pack introduced this skill version?
7. Which answer claims are direct facts versus inferences?
