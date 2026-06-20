# STORY-002: Validate Holistic Graph Connectivity

**Title**: Validate Holistic Graph Connectivity

**User Story**:  
As a skills knowledge graph steward,  
I want mandatory bridge concepts and connectivity checks for every skill,  
so that the Neo4j skills graph has no unexplained fragments, category islands or outlier skills.

**Persona/Context**:  
Agents must rely on the skills graph as a connected operating model. Category membership alone is insufficient; every skill must connect through task shapes, workflow stages, capabilities, control themes, domains or semantic skill relationships.

**Acceptance Criteria**:  
- **Given** all 87 skills have been exported as graph records, **When** connectivity validation runs, **Then** no `Skill` node is isolated and all skills are reachable from the startup/root spine.  
  **Example**: `apply-laws-of-ai` can reach `kg-enabled-rag` through startup, routing, data-architecture and graph-retrieval bridge paths.
- **Given** a skill lacks task/capability or semantic bridge coverage, **When** validation runs, **Then** the validation report fails and names the affected skill.  
  **Example**: `shipping-and-launch` missing a workflow-stage edge is reported as an outlier.
- **Given** reference documents or external sources are not directly connected to all bridge nodes, **When** connectivity validation runs, **Then** they are exempt only when marked intentionally external and not counted as skill fragments.  
  **Example**: A `Source` URL cited by one skill is allowed as a leaf node.

**Non-Functional Requirements (NFRs)**:  
- Connectivity checks must be deterministic and runnable without Neo4j GDS.
- If Neo4j GDS is available, weakly connected component analysis should be supported as an optional check.
- Reports must be human-readable and suitable for CI output.

**Success Metric**:  
- Connectivity report shows one non-exempt skills component and zero unexplained outliers.

**Delivery slices** *(optional — use when story spans multiple waves)*:  

| Slice | Wave | Delivers |
| --- | --- | --- |
| **002a** | 1 | Bridge node taxonomy and mandatory relationship rules |
| **002b** | 2 | Cypher and Python no-fragment validation checks |

**Dependencies (hard)**:  
- STORY-001

**Dependencies (soft)**:  
- STORY-004 semantic mapper can add richer bridge edges later

**Visual Reference**:  
- Connectivity diagram in `SKILLS_ONTOLOGY.md`

**Business Value/Priority**:  
- Critical priority because the user explicitly requires a holistic connected graph.
