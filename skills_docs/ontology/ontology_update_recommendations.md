Main issues and recommendations

Current alignment note

This document predates the latest ontology baseline update.

Current repository state:

Implemented now in the ontology baseline

* Issue 1 is partially implemented at the ontology level:
  * `SkillSelectionRun`
  * `SkillSelectionRequest`
  * `SelectionCandidate`
  * `SkillSelectionDecision`
  * `selectedSkillVersion`
  * `rejectedSkillVersion`
  * `selectionScore`
  * `selectionReason`
  * `rejectionReason`
  * `selectionSupportedBy`
* Issue 2 is implemented at the ontology and SHACL level:
  * `sourcePath`
  * `headingPath`
  * `lineStart`
  * `lineEnd`
  * optional `charStart`
  * optional `charEnd`
  * `anchorRole`
* Issue 3 is implemented at the SHACL level:
  * direct routing edges must be backed by matching `BridgeAssertion` provenance
* Issue 4 is partially implemented:
  * subtype-specific concept-scheme shapes are present
  * unique `skos:prefLabel` within scheme is enforced
  * `skos:altLabel`, `skos:hiddenLabel`, deprecation, replacement, and controlled hierarchy policy remain planned
* Issue 5 is implemented at the ontology level:
  * `notForTaskShape`
  * `excludedWhen`
  * `requiresTool`
  * `incompatibleWithTool`
  * `compatibleWithRuntime`
  * `incompatibleWithRuntime`
  * `requiresHumanApproval`
  * `supersededBy`

Not yet implemented

* Issue 6 retrieval ranking metadata
* Issue 7 version-aware dependency assertions
* Issue 8 split SHACL profiles
* Issue 9 evaluation artefacts and metric model

Authoritative implementation sequencing now lives in:

* `skills_docs/ontology/krag_v2/PHASED_IMPLEMENTATION_PLAN.md`

Use that file as the source of truth for phase assignment and completion criteria.

Issue 1 — The ontology lacks an explicit selection-decision model

Problem

The KG can represent skills, concepts and evidence, but it does not explicitly represent:

* the incoming task;
* candidate skills considered;
* selected skill versions;
* rejected near-matches;
* ranking scores;
* rationale;
* evidence used in the final selection.

For a KRAG skill selector, this is a material gap. Agentic routing and tool-routing patterns require traceable decisions, especially where the system is selecting skills autonomously.

Recommendation

Add a lightweight runtime selection layer:

Add	Purpose
SkillSelectionRun	One invocation of the selector
SkillSelectionRequest	Normalised representation of the user/agent task
SelectionCandidate	Skill version considered during retrieval
SkillSelectionDecision	Final selected/rejected decision
selectedSkillVersion	Chosen skill version
rejectedSkillVersion	Near-match rejected
selectionScore	Combined retrieval/ranking score
selectionReason	Human-readable explanation
rejectionReason	Why a skill was not selected
selectionSupportedBy	Evidence anchors supporting the decision

Keep this as an operational/runtime layer, not the canonical source model.

⸻

Issue 2 — Evidence anchors need precise source locations

Problem

The ontology has EvidenceAnchor, which is right. But EvidenceAnchor needs precise source co-ordinates to support explainable selection and citations.

The current ontology identifies EvidenceAnchor as the smallest stable evidence-bearing fragment and maps its ID to the structural parent plus a content-hash prefix.   That is useful for integrity, but insufficient for developer-facing traceability.

Recommendation

Add source-location fields:

Property	Purpose
sourcePath	Repository-relative file path
headingPath	Markdown heading hierarchy
lineStart	Start line
lineEnd	End line
charStart	Optional precise offset
charEnd	Optional precise offset
anchorRole	Trigger, constraint, procedure, exclusion, example, reference
contentHash	Integrity and deduplication

This lets the selector return:

Selected neo4j_cypher/SKILL.md because Usage > When to use, lines 14–24, match the task shape and required capability.

Without this, citations remain too opaque.

⸻

Issue 3 — Direct semantic routing edges must be provably derived

Problem

The ontology allows direct predicates:

* supportsTaskShape
* operatesInStage
* enablesCapability
* governedBy
* partOfDomain

These are acceptable as performance projections. The ontology explicitly says they are convenience projections and that qualified assertions remain authoritative.  

The risk is that direct edges may be loaded or modified without a corresponding BridgeAssertion.

Recommendation

Add SHACL constraints that enforce this rule:

Every direct semantic routing edge must be backed by a valid BridgeAssertion with assertionFor, bridgeTarget, supportedBy, confidence and provenance.

Practical rule:

If this edge exists	Then this must also exist
SkillVersion supportsTaskShape TaskShape	Matching BridgeAssertion
SkillVersion enablesCapability Capability	Matching BridgeAssertion
SkillVersion operatesInStage WorkflowStage	Matching BridgeAssertion
SkillVersion governedBy ControlTheme	Matching BridgeAssertion
SkillVersion partOfDomain KnowledgeDomain	Matching BridgeAssertion

This is the most important SHACL improvement.

⸻

Issue 4 — Controlled vocabularies need stricter scheme validation

Problem

The ontology correctly says bridge concepts should be governed SKOS-style concepts, not free-text tags.  

However, the validation should also ensure that each concept is in the right scheme.

Recommendation

Add subtype-specific shapes:

Class	Must be in
TaskShape	TaskShapeScheme
Capability	CapabilityScheme
WorkflowStage	WorkflowStageScheme
ControlTheme	ControlThemeScheme
KnowledgeDomain	KnowledgeDomainScheme
SkillCategory	SkillCategoryScheme

Also add:

Constraint	Reason
Unique skos:prefLabel within scheme	Prevents routing ambiguity
Controlled skos:altLabel	Improves recall safely
skos:hiddenLabel for common variants	Handles typos and abbreviations
deprecated / replacedBy	Supports vocabulary evolution
Selective skos:broader / skos:narrower	Enables graph expansion without uncontrolled fan-out

⸻

Issue 5 — The model needs negative selection semantics

Problem

The ontology is good at modelling positive relevance:

* this skill supports this task shape;
* this skill enables this capability;
* this skill operates in this workflow stage.

But precise selection also requires exclusion logic:

* do not use this skill for this artefact type;
* do not use when no web access is allowed;
* do not use with this agent runtime;
* do not use deprecated skills;
* do not use when a safer/newer skill supersedes it.

This is essential because vector and graph retrieval both over-retrieve. Precision comes from filtering as much as from matching.

Recommendation

Add minimal exclusion and compatibility semantics:

Add	Example
notForTaskShape	Not for slide generation
excludedWhen	Exclude when user forbids web access
requiresTool	Requires shell, Python, Neo4j, RDF parser
incompatibleWithTool	Not compatible with Codex/Cursor/Claude Code
requiresHumanApproval	Do not invoke autonomously
supersededBy	Prefer the replacement skill

This directly supports the project goal: fast, precise skill selection rather than broad retrieval.

⸻

Issue 6 — Retrieval units need ranking metadata

Problem

RetrievalUnit exists, but it needs operational metadata for hybrid retrieval and reranking.

GraphRAG/KRAG practice is not “graph only” or “vector only”. The useful pattern is:

1. exact lexical match;
2. embedding similarity;
3. graph traversal over governed concepts;
4. deterministic filters;
5. reranking;
6. evidence-backed response.

The current model supports part of this, but not enough ranking metadata.

Recommendation

Add projection-only retrieval fields:

Field	Purpose
retrievalText	Text optimised for lexical/vector retrieval
retrievalUnitType	Trigger, constraint, procedure, example, reference
lexicalBoostTerms	Exact-match keywords
semanticAliases	Controlled synonyms
priorityWeight	Prefer high-signal sections such as “When to use”
embeddingModel	Reproducibility
embeddingVersion	Reindex control
vectorDimension	Index compatibility
retrievalProfile	claude-code, codex, cursor, gemini, mcp

Keep these out of the canonical semantic layer. They belong to the retrieval projection layer.

⸻

Issue 7 — Skill dependencies should be version-aware

Problem

The ontology models skill-to-skill relationships using explicit predicates such as requires, precedes, complements, refines, governsSkill and validatesSkill.  

That is useful, but some dependencies are version-specific. For example, skill A v1.2 may require skill B v2.0, while skill A v1.0 did not.

Recommendation

Support both:

Level	Use
Skill → Skill	Stable conceptual relationship
SkillVersion → SkillVersion	Operational dependency for exact routing

Add a qualified dependency assertion where needed:

Add	Purpose
SkillDependencyAssertion	Evidence-backed dependency
dependencySourceVersion	Source skill version
dependencyTargetVersion	Target skill version
dependencyType	requires, precedes, validates, complements
supportedBy	Evidence anchor

This avoids stale dependency traversal.

⸻

Issue 8 — The SHACL profile should be split

Problem

The ontology itself distinguishes canonical graph data, derived retrieval projections and answer-time citations.   The SHACL should mirror that separation.

A single validation profile becomes hard to reason about because canonical facts and derived search projections have different quality rules.

Recommendation

Split SHACL into three profiles:

SHACL profile	Purpose
canonical-core.shacl.ttl	Skills, versions, source resources, evidence anchors, bridge assertions
retrieval-projection.shacl.ttl	Retrieval units, direct predicates, embeddings, ranking metadata
runtime-selection.shacl.ttl	Selection runs, candidates, decisions, citations and rejection reasons

This keeps canonical validation strict while allowing projection-specific rules.

⸻

Issue 9 — The system needs evaluation artefacts

Problem

The project objective is not just to build a graph. It is to prove that the graph enables better skill selection: faster, more precise, more framework-agnostic and lower-token than manual or vendor-specific approaches.

The ontology does not yet model evaluation.

Recommendation

Add a minimal evaluation layer:

Add	Purpose
EvaluationDataset	Versioned benchmark task set
EvaluationTask	Representative coding-agent task
ExpectedSkillVersion	Ground truth
ObservedSelection	What the selector returned
EvaluationRun	Reproducible test run
FailureMode	Missed skill, wrong skill, stale skill, over-selection

Track these metrics:

Metric	Why
Precision@1	Did it choose the right first skill?
Recall@k	Did it include all needed skills?
MRR	How highly was the correct skill ranked?
nDCG@k	Did ranking reflect graded relevance?
p95 latency	Proves “fast”
citation coverage	Proves evidence-backed selection
exclusion accuracy	Proves false-positive control
token cost per selection	Proves MCP/KG efficiency benefit

⸻

Minimal target architecture

skills.md files
  → structured markdown parser
  → Skill / SkillVersion / SourceResource / SkillSection
  → EvidenceAnchor with line/heading co-ordinates
  → BridgeAssertion to governed concepts
  → materialised routing edges
  → RetrievalUnit projection
  → hybrid retrieval: lexical + vector + graph traversal
  → deterministic filters: current, compatible, not excluded, not deprecated
  → reranker
  → SkillSelectionDecision with evidence and rejection reasons
  → evaluation logging

This architecture preserves the ontology’s core design while adding the missing operational layer.

⸻

Prioritised change list

P0 — Required before relying on the selector

Priority	Change	Why
P0.1	Add lineStart, lineEnd, headingPath, anchorRole to EvidenceAnchor	Makes citations and debugging usable
P0.2	Enforce direct routing edges derive from BridgeAssertion	Prevents ungrounded semantic tags
P0.3	Add exclusion and compatibility semantics	Reduces false positives
P0.4	Add concept-scheme-specific SHACL shapes	Prevents vocabulary pollution
P0.5	Add SkillSelectionRun and SelectionCandidate	Makes selection auditable

Status against current repository state

* P0.1 implemented in ontology and SHACL
* P0.2 implemented in SHACL
* P0.3 implemented in ontology
* P0.4 partially implemented in SHACL and deferred for completion in Phase 1
* P0.5 partially implemented in ontology and deferred for runtime completion in Phase 4

P1 — Required for better precision

Priority	Change	Why
P1.1	Add retrieval metadata to RetrievalUnit	Supports hybrid reranking
P1.2	Add agent/runtime/tool compatibility concepts	Supports Claude, Codex, Gemini, Cursor and MCP
P1.3	Make dependencies version-aware	Prevents stale skill chains
P1.4	Split SHACL profiles	Separates canonical validation from projection validation
P1.5	Add deprecation and replacement rules	Prevents obsolete skills being selected

Status against current repository state

* P1.1 deferred to Phase 3
* P1.2 partially implemented in ontology and deferred for runtime use in Phase 4
* P1.3 deferred to Phase 1
* P1.4 deferred to Phase 2
* P1.5 partially implemented in ontology via `supersededBy`, with fuller governance deferred to Phase 1 and Phase 4

P2 — Required to prove value

Priority	Change	Why
P2.1	Add benchmark task set	Creates ground truth
P2.2	Log selection runs	Enables regression testing
P2.3	Track Precision@1, Recall@k, MRR, nDCG	Measures ranking quality
P2.4	Track p95 latency and token cost	Measures efficiency
P2.5	Track citation and exclusion accuracy	Measures trustworthiness

Status against current repository state

* P2.1 to P2.5 are deferred to Phase 6 and Phase 7

⸻

Acceptance criteria

The ontology and KG are ready for KRAG skill selection when the system can satisfy these checks:

Acceptance criterion	Target
Every selected skill version has at least one supporting evidence anchor	100%
Every direct routing edge is derived from a qualified assertion	100%
Every evidence anchor has source path, heading path and line range	100%
Deprecated or superseded skills are excluded unless explicitly requested	100%
Selection response includes selected skill, rationale and evidence	100%
Top-1 skill accuracy on benchmark tasks	≥85% initially
Recall@3 for required skill sets	≥95% initially
p95 selection latency	Defined by runtime target; measure continuously
Token cost versus manual skill loading	Demonstrably lower on benchmark suite

⸻

Final recommendation

Keep the current ontology. It is a strong foundation and already reflects good knowledge-engineering discipline: stable identity, versioning, evidence anchoring, controlled vocabularies, qualified assertions and retrieval projections.

Do not expand it into a large enterprise ontology. Add only the minimum missing operational elements:

1. precise evidence co-ordinates;
2. derivation-checked semantic routing edges;
3. exclusion and compatibility semantics;
4. selection trace;
5. retrieval/ranking metadata;
6. evaluation metrics.

That moves the design from a good skills knowledge graph to a practical KRAG skill-selection system.

Alignment note

The current repository no longer treats all six items above as entirely future work. Several are already present in the ontology baseline, while the remainder are assigned to explicit phases in `skills_docs/ontology/krag_v2/PHASED_IMPLEMENTATION_PLAN.md`:

* Phase 1: ontology completion and vocabulary governance
* Phase 2: SHACL profile split
* Phase 3: retrieval projection semantics
* Phase 4: runtime selection trace and precision controls
* Phase 5: safe text-to-Cypher and bounded execution
* Phase 6: evaluation ontology and benchmark governance
* Phase 7: cutover and acceptance

For execution sequencing and completion criteria, use `skills_docs/ontology/krag_v2/PHASED_IMPLEMENTATION_PLAN.md` as the authoritative plan.

Confidence: 90%.
