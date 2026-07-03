# STORY-001: Define Skills Ontology Contract

**Title**: Define Skills Ontology Contract

**User Story**:  
As a skills platform architect,  
I want a formal ontology and SHACL shapes for the skills library,  
so that the skills graph has explicit semantics and validation rules before storage or ingestion begins.

**Persona/Context**:  
Architecture and data-modelling stakeholders need a standards-friendly semantic model that reflects the shipped `skills/` library and the validation rules already enforced in CI. Neo4j physical constraints and indexes are handled separately by STORY-005.

**Acceptance Criteria**:  
- **Given** the current `skills/` folder and validator rules are available, **When** the ontology artefacts are generated or authored, **Then** classes, properties, relationships and SHACL shapes describe skills, sections, chunks, references, sources and validation rules.  
  **Example**: The ontology defines `Skill`, `SkillCategory`, `SkillSection`, `SkillChunk`, `ReferenceDocument`, `ValidationRule` and `Source`.
- **Given** the ontology must support later Neo4j storage, **When** ontology-to-property-graph mappings are documented, **Then** each core class has a proposed Neo4j label and identifier policy without defining physical indexes.  
  **Example**: `Skill` maps to label `Skill` with deterministic `id` and unique `name` requirements deferred to STORY-005.
- **Given** a modelling decision cannot be inferred from files, **When** the ontology document is written, **Then** the assumption is recorded as an explicit open decision rather than hidden in code.  
  **Example**: Embedding dimensions are documented in `configs/skills_kg.yaml`.

**Non-Functional Requirements (NFRs)**:  
- Ontology artefacts must be deterministic, reviewable text files.
- Ontology mappings must leave room for Neo4j 5.x native graph, full-text and vector indexes without defining them in this story.
- No generated schema may expose secrets or local environment values.

**Success Metric**:  
- Ontology and SHACL files pass review and are referenced by downstream extraction, schema and loading stories.

**Delivery slices** *(optional — use when story spans multiple waves)*:  

| Slice | Wave | Delivers |
| --- | --- | --- |
| **001a** | 1 | Ontology markdown plus competency questions |
| **001b** | 1 | Turtle and SHACL validation shapes |

**Dependencies (hard)**:  
- None

**Dependencies (soft)**:  
- STORY-002 for holistic connectivity validation

**Visual Reference**:  
- `skills_docs/ontology/SKILLS_ONTOLOGY.md` model diagram

**Business Value/Priority**:  
- High priority because all graph ingestion, schema, retrieval and MCP work depends on a valid semantic contract.
