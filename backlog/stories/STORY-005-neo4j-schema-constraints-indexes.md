# STORY-005: Apply Neo4j Constraints and Indexes

**Title**: Apply Neo4j Constraints and Indexes

**User Story**:  
As a Neo4j graph engineer,  
I want Cypher schema scripts for uniqueness constraints, full-text indexes and vector indexes,  
so that the skills graph supports safe idempotent writes and performant retrieval.

**Persona/Context**:  
The KG-enabled RAG skill requires Neo4j-native graph, full-text and vector indexes. Constraints must be created before ingestion to avoid duplicate logical records.

**Acceptance Criteria**:  
- **Given** Neo4j schema scripts are available, **When** the schema script is inspected or run against a test database, **Then** required uniqueness constraints are present for skills, chunks, sections, bridge nodes and sources.  
  **Example**: `Skill.name`, `SkillChunk.id`, `TaskShape.id` and `Capability.id` are unique.
- **Given** retrieval indexes are required, **When** the schema script is applied, **Then** full-text indexes exist for skill metadata and chunk text.  
  **Example**: A full-text search for `ontology design` can target skill and chunk text.
- **Given** vector retrieval is enabled, **When** the schema script is applied with configured dimensions, **Then** a vector index exists for `SkillChunk.embedding`.  
  **Example**: The index uses the dimension configured in `skills_kg.yaml`.

**Non-Functional Requirements (NFRs)**:  
- Schema scripts must be idempotent where Neo4j syntax allows.
- Index names must be stable and documented.
- Schema setup must not require production credentials.

**Success Metric**:  
- A test Neo4j instance reports all expected constraints and indexes.

**Delivery slices** *(optional — use when story spans multiple waves)*:  

| Slice | Wave | Delivers |
| --- | --- | --- |
| **005a** | 2 | Constraint and lookup index script |
| **005b** | 3 | Full-text and vector index script |

**Dependencies (hard)**:  
- STORY-001

**Dependencies (soft)**:  
- STORY-006 loader validates schema before writes

**Visual Reference**:  
- `neo4j/skills_schema.cypher`

**Business Value/Priority**:  
- High priority because schema guarantees protect idempotent loading and retrieval performance.
