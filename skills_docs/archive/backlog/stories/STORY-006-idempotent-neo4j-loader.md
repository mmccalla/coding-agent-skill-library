# STORY-006: Load Skills into Neo4j Idempotently

**Title**: Load Skills into Neo4j Idempotently

**User Story**:  
As a skills graph ingestion operator,  
I want a loader that applies schema and upserts all skills, chunks, bridge nodes and relationships into Neo4j,  
so that the graph can be rebuilt safely whenever skill files change.

**Persona/Context**:  
Ingestion must use deterministic identifiers, `MERGE` semantics and transaction boundaries. Re-running the load must not duplicate nodes or relationships.

**Acceptance Criteria**:  
- **Given** a valid export exists, **When** the loader runs against an empty Neo4j database, **Then** all skills, sections, chunks, bridge nodes and relationships are created.  
  **Example**: The database contains 87 `Skill` nodes.
- **Given** the same export is loaded twice, **When** node and relationship counts are compared, **Then** logical counts do not increase on the second run.  
  **Example**: `Skill`, `SkillChunk` and bridge-node counts remain stable.
- **Given** a required uniqueness constraint is missing, **When** the loader starts, **Then** it fails before writing records and reports the missing schema item.  
  **Example**: Missing `Skill.name` uniqueness is reported before ingestion.

**Non-Functional Requirements (NFRs)**:  
- Writes must be transactional in batches.
- The loader must not log secrets or connection strings.
- Connection settings must come from environment or local config.

**Success Metric**:  
- Two consecutive loads produce identical logical counts and pass connectivity validation.

**Delivery slices** *(optional — use when story spans multiple waves)*:  

| Slice | Wave | Delivers |
| --- | --- | --- |
| **006a** | 3 | Schema-aware loader with dry-run/test mode |
| **006b** | 3 | Idempotency and duplicate-prevention tests |

**Dependencies (hard)**:  
- STORY-003, STORY-004, STORY-005

**Dependencies (soft)**:  
- STORY-007 can use deterministic fake embeddings until production embedding provider exists

**Visual Reference**:  
- Loader run report

**Business Value/Priority**:  
- High priority because the graph must be rebuildable and trustworthy.
