# STORY-003: Extract Skills into Deterministic Graph Records

**Title**: Extract Skills into Deterministic Graph Records

**User Story**:  
As a skills ingestion developer,  
I want a tested extractor that converts `SKILL.md` files and references into graph-ready records,  
so that Neo4j loading and connectivity validation can use stable, repeatable source data.

**Persona/Context**:  
The repository already validates 87 skills. The extractor must preserve source paths, content hashes, frontmatter, canonical sections, related skills, references and provenance without changing the skill files.

**Acceptance Criteria**:  
- **Given** the `skills/` tree exists, **When** the extractor runs, **Then** it emits one deterministic `Skill` record per `SKILL.md`.  
  **Example**: The output contains 87 skill records including `apply-laws-of-ai`.
- **Given** a skill has `## Related skills` entries, **When** the extractor parses the file, **Then** related-skill relationships are emitted with source evidence.  
  **Example**: `mcp-server-design` emits relationships to `tool-use-and-function-calling`, `guardrails-safety-patterns` and `knowledge-retrieval-rag`.
- **Given** the extractor is run twice without file changes, **When** outputs are compared, **Then** record IDs and content hashes are identical.  
  **Example**: The same `SkillSection.id` values are produced on both runs.

**Non-Functional Requirements (NFRs)**:  
- No network access is required.
- Extractor must use deterministic IDs and stable ordering.
- Parsing failures must be explicit and include the source path.

**Success Metric**:  
- 100% of skills are exported with stable IDs, sections and source hashes.

**Delivery slices** *(optional — use when story spans multiple waves)*:  

| Slice | Wave | Delivers |
| --- | --- | --- |
| **003a** | 1 | Skill and section extraction |
| **003b** | 2 | Reference, source and relationship extraction |

**Dependencies (hard)**:  
- STORY-001

**Dependencies (soft)**:  
- STORY-002 can initially validate exported records before Neo4j exists

**Visual Reference**:  
- Extractor output schema example in story test fixtures

**Business Value/Priority**:  
- High priority because all loading and retrieval work depends on deterministic graph records.
