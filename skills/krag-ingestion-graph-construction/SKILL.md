---
name: krag-ingestion-graph-construction
description: Build KRAG ingestion and graph-construction pipelines from documents, records, metadata, ontologies, or enterprise systems. Use when implementing parsing, extraction, entity resolution, provenance, graph schema, constraints, and quality gates.
aliases:
  - krag ingestion graph construction
  - graphrag ingestion
  - graph construction pipeline
---

# KRAG Ingestion and Graph Construction

## When to use

Use when implementing or reviewing the ingestion, extraction, evidence anchoring, entity resolution, graph validation or graph-loading path of a KRAG system.

## Objective

Convert sources into a validated, evidence-backed graph that supports retrieval, reasoning, navigation, and auditability.

## Procedure

1. Register the source resource with stable identifiers and provenance metadata.
2. Parse and preserve document structure down to evidence-bearing elements.
3. Anchor evidence spans with locators, confidence, and parser provenance.
4. Extract candidate entities, concepts, relationships, and claims.
5. Normalise identifiers, resolve entities, and map concepts to governed vocabulary.
6. Validate against schema, cardinality, and mandatory provenance rules.
7. Promote accepted facts while retaining rejected candidates for audit.

## Pipeline

1. **Register resource**: assign stable `resource_id`, source URI/path, owner, licence, classification, version, checksum, timestamps.
2. **Parse structure**: preserve document hierarchy: document, part, section, heading, paragraph, table, row, figure, footnote, appendix.
3. **Anchor evidence**: create stable anchors for spans, cells, pages, offsets, or record fields. Store text, locator, confidence, parser, and source version.
4. **Extract candidates**: entities, concepts, relationships, claims, obligations, controls, outcomes, systems, teams, metrics, events, dates.
5. **Normalise**: canonical names, IDs, aliases, entity resolution, concept mapping, ontology/class assignment.
6. **Validate**: schema constraints, allowed relationship types, cardinality, mandatory provenance, confidence thresholds, duplicate detection.
7. **Promote**: mark accepted facts separately from candidate facts. Preserve rejected candidates for audit where useful.

## Minimal graph pattern

Use distinct node types unless the project schema says otherwise:

- `Resource`: whole source asset.
- `StructuralElement`: section, paragraph, table, row, figure, etc.
- `EvidenceAnchor`: source-grounded span, cell, page, record, or locator.
- `Entity`: real-world thing, organisation, system, person, team, product, regulation, control.
- `Concept`: taxonomy/ontology concept.
- `Claim`: asserted proposition that requires evidence.
- `Relationship`: domain edge represented as a typed graph relationship where possible; reify only when it needs evidence, time, confidence, or qualifiers.

## Edge rules

- Every extracted node/edge must have `derived_from` or equivalent evidence linkage.
- Use domain verbs for relationships, not generic `RELATED_TO`, unless still a candidate.
- Add `confidence`, `extraction_method`, `extractor_version`, `validated_by`, and `valid_time` where decisions depend on reliability or temporality.
- Keep source structure separate from semantic meaning; connect them through evidence anchors.

## Anti-patterns

- Chunk-only ingestion with no structural or semantic model.
- LLM extraction directly persisted as trusted graph facts.
- Overly broad ontologies before observing real query patterns.
- Duplicate entities caused by missing identifier strategy.
- Relationship labels that do not read as real-world predicates.

## Output format

Return ingestion design, graph schema changes, validation rules, idempotency strategy, test cases, and failure handling.

## Related skills

- `knowledge-graph-rag` — graph-native KRAG implementation guidance
- `ontology-and-knowledge-graph-modeling` — semantic model and graph schema design
- `data-lineage-and-provenance` — source-to-target provenance discipline
- `krag-system-design` — end-to-end KRAG system architecture
- `krag-evaluation-governance` — ingestion and graph quality gates

## References

- Neo4j documentation — data import and modeling: https://neo4j.com/docs/
- W3C PROV-O (provenance): https://www.w3.org/TR/prov-o/

## Verification

- [ ] Source structure, evidence anchors and semantic entities remain distinct.
- [ ] Validation and provenance rules are explicit.
- [ ] Failure handling and idempotency approach are defined.
