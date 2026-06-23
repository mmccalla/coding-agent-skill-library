# STORY-008: Retrieve Skills with Hybrid Graph and Vector Evidence

**Title**: Retrieve Skills with Hybrid Graph and Vector Evidence

**User Story**:  
As a agent retrieval designer,  
I want hybrid retrieval that combines full-text, vector similarity and graph connectivity,  
so that agents receive grounded skill recommendations with connected context and evidence paths.

**Persona/Context**:  
Retrieval should prefer connected evidence, not isolated high-similarity chunks. Results must include why a skill was selected and how it connects to adjacent skills and workflow stages.

**Acceptance Criteria**:  
- **Given** a task query is submitted, **When** hybrid retrieval runs, **Then** results include ranked skills, evidence snippets and relationship paths.  
  **Example**: A GraphRAG query returns `knowledge-graph-rag`, `ontology-and-knowledge-graph-modeling` and `knowledge-retrieval-rag` with evidence paths.
- **Given** a vector result is semantically similar but poorly connected, **When** ranking is calculated, **Then** connected skills with stronger graph evidence rank higher.  
  **Example**: A generic documentation chunk does not outrank a domain-specific skill with bridge coverage.
- **Given** no confident skill match exists, **When** retrieval runs, **Then** the response states uncertainty and suggests clarification rather than fabricating a route.  
  **Example**: A nonsense query returns low-confidence evidence and asks for a narrower task description.

**Non-Functional Requirements (NFRs)**:  
- Retrieval must enforce result limits, traversal depth limits and token budgets.
- Returned context must include source paths and section identifiers.
- No raw Cypher, embeddings or internal schema metadata should be exposed to agents.

**Success Metric**:  
- Representative queries return relevant connected skill sets with explainable evidence.

**Delivery slices** *(optional — use when story spans multiple waves)*:  

| Slice | Wave | Delivers |
| --- | --- | --- |
| **008a** | 5 | Full-text plus graph expansion retrieval |
| **008b** | 5 | Vector plus graph hybrid ranking |

**Dependencies (hard)**:  
- STORY-002, STORY-004, STORY-007

**Dependencies (soft)**:  
- STORY-009 can expose only stable retrieval modes at first

**Visual Reference**:  
- Retrieval evidence path examples

**Business Value/Priority**:  
- Critical priority because this is what makes the MCP server useful and grounded.
