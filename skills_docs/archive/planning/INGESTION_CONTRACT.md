# KRAG v2 Ingestion Contract

## Objective

Ingest new skills and skill packs into Neo4j as versioned, evidence-backed graph data without manual bridge editing.

## Ingestion stages

### 1. Source registration

For each incoming pack:

- assign `skill_pack_id`
- assign version identifier
- load explicit machine-readable pack metadata
- record source root path or URI
- record checksum
- record timestamps
- record owner and provenance metadata

### 2. Structural parsing

For each skill and referenced document:

- preserve pack, skill, section and checklist structure
- extract frontmatter exactly
- preserve related-skill references
- preserve verification checklist items as distinct structural elements
- preserve references to local overlays or reference docs

### 3. Evidence anchoring

Create stable evidence anchors for every retrieval-relevant fragment:

- frontmatter fields
- summary lines
- section bodies
- checklist items
- related-skill declarations
- reference links

Each evidence anchor must record source path, structural parent, content hash and extractor version.

### 4. Semantic extraction

Promote only the following semantic objects initially:

- canonical skill identity
- explicit skill-pack category membership
- aliases
- capabilities
- task intents
- workflow stages
- constraints
- procedure steps
- verification checks
- related-skill assertions

Everything else remains source structure until a later phase proves it is needed.

### 5. Validation before promotion

Reject or quarantine graph writes when:

- required frontmatter is missing
- aliases collide
- predicates are not allowed
- evidence anchors are missing
- related skills reference unknown targets
- identifiers are unstable
- the skill version duplicates an existing version checksum unexpectedly

### 6. Projection build

After canonical graph load, derive retrieval projections from canonical nodes plus evidence anchors. Do not write projections as if they were canonical source facts.

## Idempotency requirements

- Re-running ingestion for the same pack version must not duplicate skills, aliases, assertions or anchors.
- New skill versions must coexist with old ones until cutover or archival policy says otherwise.
- Canonical identities must remain stable across re-ingestion.

## Failure handling

- Hard fail on schema or provenance violations.
- Quarantine ambiguous semantic extraction.
- Preserve rejected candidate records for audit when useful.
- Never partially promote trusted semantic assertions if evidence anchoring failed.

## First implementation boundary

The first ingestion slice should support:

- one skill pack root
- `SKILL.md`
- local reference documents
- versioned pack load
- canonical nodes
- evidence anchors
- retrieval projections

It should not yet attempt broad ontology inference or speculative concept extraction.
