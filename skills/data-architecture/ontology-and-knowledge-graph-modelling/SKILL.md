---
name: ontology-driven-knowledge-graph-and-krag
description: Design, build, validate and use ontology-driven knowledge graphs, including Knowledge-Graph Retrieval-Augmented Generation (KG-RAG / KRAG / GraphRAG) patterns.
---

# Ontology-Driven Knowledge Graph and KRAG

## When to use

Use this skill when the task involves any of the following:

- Designing an ontology, taxonomy, vocabulary, semantic model or conceptual knowledge model.
- Creating or reviewing RDF/OWL ontologies, SHACL shapes, SKOS vocabularies, property graphs or graph schemas.
- Building, enriching, integrating, validating or querying a knowledge graph.
- Converting source artefacts, documents, databases, APIs or data products into graph-ready semantic structures.
- Designing Knowledge-Graph Retrieval-Augmented Generation, also called KG-RAG, KRAG or GraphRAG.
- Improving LLM grounding, explainability, provenance, semantic search, entity linking, reasoning, validation or graph-based retrieval.

Do not use this skill for a simple graph visualisation, basic entity extraction, or generic vector-only RAG unless the user asks to introduce semantic structure, graph retrieval, ontology governance or explainable grounding.

## Core objective

Create a practical, traceable and implementation-ready semantic design that supports:

1. Clear business purpose and competency questions.
2. Stable ontology-driven modelling.
3. Standards-aligned graph representation.
4. Validated and governed graph data.
5. Hybrid retrieval for LLM grounding.
6. Explainable answers with provenance, confidence and source evidence.
7. Maintainable evolution across domains, systems and use cases.

The output must be useful to both human reviewers and coding agents.

## Key definitions

- **Ontology**: A formal domain model that defines classes, relationships, properties, constraints and, where appropriate, reasoning semantics.
- **Knowledge graph**: A graph of entities, concepts, documents, events and relationships, linked to source evidence and governed identifiers.
- **Ontology-driven knowledge graph**: A knowledge graph whose structure, semantics, constraints and allowed relationship types are controlled by an ontology or semantic schema.
- **KRAG / KG-RAG / GraphRAG**: Retrieval-Augmented Generation that uses a knowledge graph, graph traversal, entity linking, semantic relationships, communities, paths or ontology constraints to retrieve and explain grounding context for an LLM.
- **Competency question**: A question the ontology or knowledge graph must be able to answer.
- **Shape / constraint**: A validation rule, commonly expressed in SHACL for RDF graphs or equivalent schema/rule logic for property graphs.
- **Provenance**: Traceability from graph facts back to source artefacts, extraction method, timestamp, version and confidence.

## Guiding principles

1. **Purpose before modelling**  
   Start with use cases, decisions, competency questions and retrieval behaviours. Do not model everything.

2. **Ontology first, extraction second**  
   Define the target semantic structure before large-scale extraction. Allow controlled extension only when evidence justifies it.

3. **Reuse where definitions align**  
   Reuse standards and external vocabularies only when their definitions genuinely match the intended meaning. Do not force-fit.

4. **Separate semantics from validation**  
   Use ontology semantics for meaning and reasoning. Use constraints for data quality, required properties, cardinality, controlled values and operational checks.

5. **Prefer explicit relationships**  
   Relationship labels must carry business meaning. Avoid generic edges such as `relatedTo`, `has`, `linksTo` or `associatedWith` unless they are intentionally defined and constrained.

6. **Keep identifiers stable**  
   Define URI, IRI, CURIE or graph-key policies early. Stable identifiers are required for merge, lineage, retrieval and trust.

7. **Preserve evidence**  
   Every asserted graph fact should be traceable to source evidence, extraction method and confidence. Separate asserted, inferred and generated facts.

8. **Design for retrieval, not only storage**  
   For KRAG, model the graph so it can retrieve useful context through entity lookup, path expansion, community summaries, semantic filters and hybrid vector+graph search.

9. **Validate continuously**  
   Validate ontology consistency, graph shape conformance, extraction quality, duplicate entities, dangling references, contradictory facts and retrieval outcomes.

10. **Keep the first version small**  
   Start with the minimum useful ontology and expand through competency-question failure, not speculative modelling.

## Recommended modelling standards and patterns

Use these where appropriate:

- **RDF / RDFS** for graph data and basic class/property semantics.
- **OWL** for formal ontology semantics, class axioms, property characteristics and inference.
- **SHACL** for data validation rules, cardinality, required properties, datatype checks and controlled patterns.
- **SKOS** for taxonomies, concept schemes, labels, broader/narrower relationships and controlled vocabularies.
- **SPARQL** for RDF graph querying.
- **JSON-LD** for web/API-friendly RDF serialisation.
- **PROV-O or equivalent provenance model** for source traceability.
- **DCAT / Data Catalog Vocabulary** where modelling datasets, data products or catalogues.
- **FIBO, FOAF, schema.org, Dublin Core, Time Ontology or domain ontologies** only where definitions align.
- **Property graph schema** for Neo4j, Memgraph or similar graph databases when the implementation needs Cypher, low-friction application integration or hybrid graph+vector retrieval.

Do not mix RDF and property graph patterns casually. If both are used, explicitly define the canonical model and mapping rules.

## Procedure

### 1. Establish purpose and scope

Define:

- Business objective.
- Users and consuming systems.
- Decisions or workflows the graph will support.
- In-scope and out-of-scope domains.
- Data sources and source artefacts.
- Required retrieval or reasoning behaviours.
- Non-functional constraints: privacy, latency, scale, cost, explainability, auditability and security.

Write 5-15 competency questions. Include both direct factual questions and multi-hop questions.

Examples:

- Which source artefacts support this answer?
- Which entities are equivalent or duplicates?
- Which policies govern this data product?
- Which risks are linked to this process through controls and evidence?
- Which document sections justify this relationship?
- What related entities should be retrieved to answer this user question?

### 2. Choose the graph representation

Select one primary representation:

- **RDF/OWL/SHACL** when interoperability, standards, reasoning, semantic precision or ontology governance is important.
- **Property graph** when implementation speed, graph traversal, developer accessibility, graph algorithms or Cypher-based applications are the priority.
- **Hybrid RDF + property graph** only when there is a clear reason, such as RDF as canonical semantics and Neo4j as retrieval/runtime projection.

Record the choice, trade-offs and mapping rules.

### 3. Build the ontology or semantic schema

Define:

- Core classes or node labels.
- Object properties or relationship types.
- Datatype properties or node/edge attributes.
- Controlled vocabularies and enumerations.
- Class hierarchy, only where definitions genuinely support subclassing.
- Domain and range expectations.
- Cardinality and mandatory/optional properties.
- Inverse relationships where helpful.
- Naming conventions for classes, predicates, properties and labels.
- Human-readable labels, descriptions and examples.
- Deprecated, experimental and stable model elements.

Prefer shallow, meaningful hierarchies over deep speculative taxonomies.

### 4. Define entity identity and resolution rules

Specify:

- Natural keys and surrogate identifiers.
- URI/IRI/CURIE patterns or property graph key patterns.
- Normalisation rules.
- Equivalence rules, such as `owl:sameAs`, `skos:exactMatch`, `same_as`, or domain-specific match relationships.
- Duplicate detection approach.
- Confidence scoring for entity resolution.
- Human review thresholds.
- Merge, split and rollback approach.
- Handling of aliases, synonyms, abbreviations and acronyms.

Do not assert equivalence unless the identity semantics are strong. Prefer weaker match predicates when certainty is incomplete.

### 5. Define provenance, lineage and evidence

For each graph assertion, define how to capture:

- Source document, dataset, table, API, file, URL or message.
- Source section, page, paragraph, row, field, timestamp or byte/character offset where possible.
- Extraction method: manual, deterministic parser, LLM, rule, ontology mapping or inference.
- Model/tool version where LLM or automated extraction is used.
- Confidence score and validation status.
- Assertion type: asserted, inferred, generated, curated, rejected or deprecated.
- Load batch, pipeline run ID and change history.
- Data owner, steward and accountable domain.

For KRAG, source provenance must be available at answer time so generated answers can cite source evidence.

### 6. Define constraints and validation

Create validation rules for:

- Required properties.
- Cardinality.
- Datatypes.
- controlled vocabularies.
- Valid class/property combinations.
- Allowed relationship directions.
- Required provenance.
- Required confidence thresholds.
- Identifier uniqueness.
- Source-to-graph completeness.
- No orphan entities unless explicitly allowed.
- No unsupported relationship types.
- No circular structures where invalid for the domain.
- No unapproved external vocabulary reuse.

For RDF, use SHACL where practical. For property graphs, use schema constraints, validation queries, tests or application-level validation.

### 7. Define inference and reasoning boundaries

Specify:

- Which facts may be inferred.
- Which rules, axioms or graph algorithms are allowed.
- Whether reasoning is materialised at ingestion time, query time or both.
- How inferred facts are labelled and traced.
- How contradictions are detected.
- Whether the graph uses open-world or closed-world assumptions.
- Which reasoning profiles are supported by the target tooling.
- How inference affects KRAG retrieval and answer generation.

Keep reasoning explainable. Do not allow inferred facts to appear as direct source facts.

### 8. Design KRAG retrieval

Select one or more retrieval strategies:

- **Entity-centric retrieval**: identify entities in the user query, link them to graph nodes, expand relevant neighbourhoods.
- **Path-based retrieval**: retrieve shortest, weighted or semantically constrained paths between query entities.
- **Subgraph retrieval**: retrieve a bounded k-hop subgraph with filters on type, confidence, source, time or access rights.
- **Community retrieval**: use graph communities or clusters with generated summaries for broad synthesis questions.
- **Ontology-guided retrieval**: use class hierarchy, relationship semantics and constraints to choose relevant graph areas.
- **Hybrid vector + graph retrieval**: combine semantic chunk retrieval with graph traversal and re-ranking.
- **Graph-to-query retrieval**: translate a natural-language question into SPARQL, Cypher or a controlled graph query.
- **Evidence-first retrieval**: retrieve source passages attached to graph facts rather than graph facts alone.

Use vector-only retrieval for lexical/semantic recall, graph retrieval for relationship-aware precision, and ontology constraints for trust and filtering.

### 9. Design KRAG answer grounding

Require generated answers to include:

- Retrieved entities and relationships used.
- Source snippets or references.
- Path or subgraph explanation where useful.
- Distinction between source facts, inferred facts and model-generated synthesis.
- Confidence or evidence strength.
- Missing evidence and uncertainty.
- Access-control enforcement before context reaches the LLM.
- No unsupported claims beyond retrieved context unless explicitly marked as general knowledge.

The LLM must not invent graph facts. New candidate facts must be written to a review queue, not directly asserted as trusted graph data.

### 10. Define ingestion and extraction pipeline

For each source type, specify:

- Parser and chunking approach.
- Metadata extraction.
- Entity and relationship extraction method.
- Deterministic extraction where possible.
- LLM extraction only where rules are insufficient.
- Structured output schema for LLM extraction.
- Ontology/schema validation after extraction.
- Entity resolution and deduplication.
- Provenance attachment.
- Human-in-the-loop review for low-confidence or high-impact facts.
- Incremental loading, reprocessing and deletion handling.
- Versioning of ontology, prompts, extractors and mappings.

Do not let LLM extraction create uncontrolled node labels, relationship types or properties in production.

### 11. Define governance and security controls

Address:

- Ownership and stewardship.
- Classification and sensitivity.
- Access control and entitlement checks.
- Tenant, domain or purpose boundaries.
- Privacy, retention and deletion requirements.
- Prompt injection and malicious source-content handling.
- PII handling and redaction.
- Model/data leakage risks.
- Audit logs for ingestion, query and answer generation.
- Approval workflow for ontology changes.
- Change impact analysis for schema evolution.
- Data quality SLAs and exception handling.

For regulated environments, record auditable evidence for model, data, retrieval and answer decisions.

### 12. Test and evaluate

Test at four levels:

1. **Ontology tests**
   - Consistency.
   - Naming.
   - Definition quality.
   - Reuse justification.
   - Competency-question coverage.

2. **Graph data tests**
   - Constraint conformance.
   - Entity resolution accuracy.
   - Provenance completeness.
   - Duplicate/orphan detection.
   - Relationship validity.

3. **Retrieval tests**
   - Recall and precision for known questions.
   - Correct entity linking.
   - Correct path/subgraph selection.
   - No retrieval of unauthorised data.
   - Latency and cost.

4. **Answer-quality tests**
   - Faithfulness to retrieved context.
   - Citation/source accuracy.
   - Handling of missing evidence.
   - Hallucination rate.
   - Explainability.
   - User usefulness.

Maintain a regression test set of competency questions and expected evidence paths.

## Required outputs

When using this skill, produce the relevant subset of the following outputs.

### Minimum outputs

- Purpose and scope.
- Competency questions.
- Core classes or node labels.
- Core relationships or predicates.
- Key properties.
- Identifier rules.
- Provenance model.
- Constraints and validation rules.
- Retrieval design.
- Risks and assumptions.
- Completion report.

### Ontology outputs

- Ontology/module structure.
- Class hierarchy.
- Property catalogue.
- Domain/range rules.
- SKOS concept schemes, if applicable.
- External vocabulary reuse decisions.
- Reasoning/inference rules.
- SHACL shapes or equivalent constraints.
- Versioning and change-control approach.

### Knowledge graph outputs

- Source-to-graph mapping.
- Entity resolution rules.
- Load and update pattern.
- Graph schema or RDF model.
- Sample triples or Cypher examples where useful.
- Data quality checks.
- Provenance and lineage fields.
- Security and access-control model.

### KRAG outputs

- Retrieval pattern.
- Query understanding and entity-linking approach.
- Graph expansion rules.
- Hybrid vector + graph strategy.
- Context packaging format for the LLM.
- Re-ranking approach.
- Answer citation rules.
- Guardrails for unsupported claims.
- Evaluation questions and metrics.

## KRAG architecture pattern

Use this reference pattern unless the task requires otherwise:

1. **Source ingestion**
   - Parse documents, datasets or APIs.
   - Preserve source metadata and evidence anchors.

2. **Semantic extraction**
   - Extract candidate entities, concepts, claims and relationships.
   - Use deterministic extraction where practical.
   - Use LLM structured extraction for ambiguous text.
   - Validate against the ontology/schema.

3. **Graph construction**
   - Resolve entities.
   - Attach provenance.
   - Store trusted assertions.
   - Route low-confidence candidates to review.

4. **Indexing**
   - Create graph indexes for identifiers, labels and relationship types.
   - Create vector indexes for text chunks, entity descriptions and summaries.
   - Optionally create community summaries or path summaries.

5. **Retrieval**
   - Analyse the user query.
   - Link query terms to graph entities and concepts.
   - Choose graph, vector or hybrid retrieval.
   - Apply security filters before retrieval results are exposed to the LLM.
   - Retrieve source evidence, not only graph facts.

6. **Reasoning and context assembly**
   - Build concise context from facts, paths, subgraphs, summaries and source snippets.
   - Mark asserted, inferred and generated context separately.
   - Include provenance and confidence.

7. **Generation**
   - Generate an answer grounded in the provided context.
   - Cite evidence.
   - State uncertainty and missing evidence.
   - Avoid claims not supported by retrieved context.

8. **Feedback and improvement**
   - Log query, retrieval set, answer, citations and user feedback.
   - Add failed questions to evaluation.
   - Improve ontology, extraction rules and retrieval routing.

## KRAG retrieval routing guide

Use this routing logic:

- Use **vector retrieval** when the question is about wording, passages, broad semantic similarity or document recall.
- Use **graph retrieval** when the question depends on relationships, hierarchy, dependencies, ownership, lineage, policy, causality, provenance or multi-hop reasoning.
- Use **community/summary retrieval** when the question asks for themes, trends or corpus-level synthesis.
- Use **structured graph queries** when the question has clear filters, counts, paths, entity types, dates or relationship constraints.
- Use **hybrid retrieval** when either graph or vector retrieval alone would be incomplete.
- Refuse or narrow the answer when evidence is missing, access is denied or entity linking is ambiguous.

## Quality checklist

Before finishing, check that:

- Competency questions are explicit and testable.
- Classes and relationships are defined in business language.
- Subclass relationships are justified by definition, not convenience.
- Relationship names are meaningful and directional.
- The model separates concepts, entities, documents, events and evidence.
- External vocabulary reuse is documented and semantically justified.
- Identifiers are stable and merge-safe.
- Provenance is attached to graph assertions.
- Constraints are executable where possible.
- Inference rules are bounded and explainable.
- KRAG retrieval returns source evidence, not just graph nodes.
- The LLM cannot write trusted graph facts without validation.
- Security filters are applied before LLM context assembly.
- Evaluation includes retrieval quality and answer faithfulness.
- The design can evolve without breaking existing graph consumers.

## Anti-patterns to avoid

- Building a graph from LLM outputs without a schema.
- Treating vector embeddings as a substitute for semantic modelling.
- Using `sameAs` for weak similarity.
- Adding deep class hierarchies before competency questions prove the need.
- Creating generic relationships with no domain meaning.
- Losing source provenance during extraction.
- Mixing asserted, inferred and generated facts.
- Allowing unrestricted ontology evolution at runtime.
- Sending sensitive or unauthorised graph context to an LLM.
- Using GraphRAG/KRAG when simple vector RAG or database querying is sufficient.
- Optimising for impressive demos rather than measurable retrieval and answer quality.
- Failing to test against known questions and expected evidence.

## Best-practice alignment

Align work with:

- **DAMA-DMBOK2**: governance, architecture, modelling, metadata, integration/interoperability, master/reference data, security and quality.
- **EDM Council CDMC-style controls**: ownership, classification, entitlement evidence, lineage, lifecycle, quality controls and auditability.
- **W3C semantic web standards**: RDF, RDFS, OWL, SHACL, SKOS, SPARQL and JSON-LD where appropriate.
- **Responsible AI / LLM grounding practices**: context minimisation, source citation, confidence handling, access-control enforcement, prompt-injection resistance, evaluation and human review for high-impact assertions.
- **Continuous delivery for data/AI systems**: version ontology, prompts, mappings, test data, retrieval configuration and evaluation sets together.

## Completion report

At the end of the task, state:

- Artefacts produced.
- Main modelling decisions.
- External vocabularies reused or rejected.
- Assumptions.
- Risks and mitigations.
- Validation performed.
- Retrieval and KRAG design decisions.
- Files changed.
- Open questions or follow-up actions.
