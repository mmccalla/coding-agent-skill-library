# STORY-009: Expose Skills Graph through Read-Only MCP Tools

**Title**: Expose Skills Graph through Read-Only MCP Tools

**User Story**:  
As a coding agent,  
I want a Skills MCP server with curated read-only search and context tools,  
so that agents can query grounded skill guidance from Neo4j instead of loading raw files manually.

**Persona/Context**:  
The MCP server must expose agent-friendly tools and resources, not unrestricted database access. It should return bounded structured results with evidence and connectivity context.

**Acceptance Criteria**:  
- **Given** the MCP server starts, **When** a client lists capabilities, **Then** tools and resources are discoverable with clear schemas.  
  **Example**: `search_skills`, `get_skill`, `recommend_skills` and `get_skill_context` are listed.
- **Given** an agent asks for skill recommendations, **When** it calls `recommend_skills`, **Then** the response includes skills, rationale, evidence snippets and related connected skills.  
  **Example**: A request for Neo4j GraphRAG recommends KG, ontology and guardrail skills.
- **Given** a request attempts arbitrary Cypher or write access, **When** the MCP server handles it, **Then** no write tool is available and the response denies unsupported access.  
  **Example**: `DELETE` or unrestricted `CALL` cannot be executed through MCP.

**Non-Functional Requirements (NFRs)**:  
- MCP operations must be read-only in the first release.
- Responses must be bounded by result count, chunk count and token budget.
- STDIO logging must not write diagnostics to stdout.

**Success Metric**:  
- MCP client tests can discover tools and retrieve grounded connected skill context.

**Delivery slices** *(optional — use when story spans multiple waves)*:  

| Slice | Wave | Delivers |
| --- | --- | --- |
| **009a** | 6 | MCP schemas and in-process retrieval tools |
| **009b** | 6 | Client tests and bounded response validation |

**Dependencies (hard)**:  
- STORY-008

**Dependencies (soft)**:  
- STORY-010 documents operational setup and examples

**Visual Reference**:  
- MCP tool schema examples

**Business Value/Priority**:  
- Critical priority because it delivers the agent-facing capability.
