# STORY-007: Create Skill Chunk Embeddings and Vector Index

**Title**: Create Skill Chunk Embeddings and Vector Index

**User Story**:  
As a skills retrieval engineer,  
I want skill chunks embedded and stored in Neo4j vector indexes,  
so that downstream retrieval can use semantic similarity without relying only on exact keywords.

**Persona/Context**:  
The graph should support KG and vector retrieval. Tests need a deterministic fake embedder, while runtime can use a configurable embedding provider.

**Acceptance Criteria**:  
- **Given** skill chunks exist, **When** the embedding pipeline runs with the test embedder, **Then** each chunk receives a deterministic embedding with the configured dimension.  
  **Example**: The same chunk text produces the same vector in tests.
- **Given** a vector index exists, **When** a vector query is executed in a focused test, **Then** matching chunk IDs, scores, source paths and section provenance are returned for retrieval-layer consumption.  
  **Example**: A query vector for `approval before destructive command` returns candidate chunk IDs that STORY-008 can rank with graph evidence.
- **Given** an embedding provider is unavailable, **When** the pipeline runs in test mode, **Then** it uses the deterministic embedder and records provider metadata.  
  **Example**: No external network call is required in CI.

**Non-Functional Requirements (NFRs)**:  
- Embedding provider must be configurable.
- Raw vectors must not be returned through MCP tools.
- Chunk provenance must be preserved with every retrieval result.

**Success Metric**:  
- Vector index queries return source-backed candidate chunks for representative task embeddings.

**Delivery slices** *(optional — use when story spans multiple waves)*:  

| Slice | Wave | Delivers |
| --- | --- | --- |
| **007a** | 4 | Chunking and deterministic test embeddings |
| **007b** | 4 | Neo4j vector index population and candidate-query tests |

**Dependencies (hard)**:  
- STORY-005, STORY-006

**Dependencies (soft)**:  
- STORY-008 consumes vector candidates and combines them with full-text and graph ranking

**Visual Reference**:  
- Vector retrieval test fixtures

**Business Value/Priority**:  
- High priority because vector search is central to agent skill discovery.
