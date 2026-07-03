# STORY-010: Document and Validate the Skills KG MCP Workflow

**Title**: Document and Validate the Skills KG MCP Workflow

**User Story**:  
As a repository maintainer,  
I want documentation, runbooks and CI checks for the skills KG and MCP workflow,  
so that future maintainers can rebuild, validate and operate the graph-backed skills server safely.

**Persona/Context**:  
The library is intended to be portable. Documentation must explain local development, Neo4j setup, embeddings, connectivity validation, MCP usage, security boundaries and fallback behaviour.

**Acceptance Criteria**:  
- **Given** the KG/MCP feature is implemented, **When** a maintainer reads the documentation, **Then** they can run extraction, schema setup, load, validation and MCP server commands locally.  
  **Example**: README links to a dedicated KG/MCP guide.
- **Given** CI runs without Neo4j available, **When** tests execute, **Then** unit tests and deterministic validations pass while integration tests are skipped or clearly marked.  
  **Example**: CI does not require a live Neo4j instance unless explicitly configured.
- **Given** a connectedness failure occurs, **When** the runbook is followed, **Then** the maintainer can identify the outlier skill and mapping rule to fix.  
  **Example**: The report explains which bridge relationship is missing.

**Non-Functional Requirements (NFRs)**:  
- Docs must avoid real secrets and use placeholders.
- Integration test requirements must be explicit.
- Operational commands must distinguish local test mode from production-like mode.

**Success Metric**:  
- A new maintainer can rebuild the local graph and run MCP retrieval using documented steps.

**Delivery slices** *(optional — use when story spans multiple waves)*:  

| Slice | Wave | Delivers |
| --- | --- | --- |
| **010a** | 7 | Documentation and runbook |
| **010b** | 7 | CI integration and final validation evidence |

**Dependencies (hard)**:  
- STORY-001 through STORY-009

**Dependencies (soft)**:  
- Future story for hosted deployment, authentication and monitoring

**Visual Reference**:  
- End-to-end workflow diagram

**Business Value/Priority**:  
- High priority because the capability must be maintainable after initial implementation.
