# STORY-004: Map Skills to Semantic Bridge Concepts

**Title**: Map Skills to Semantic Bridge Concepts

**User Story**:  
As a skills ontology curator,  
I want a semantic mapper that assigns task shapes, workflow stages, capabilities, control themes and domain links,  
so that the graph becomes a navigable skills operating model instead of a set of file-derived records.

**Persona/Context**:  
Some relationships can be extracted from headings and `Related skills`, but holistic connectedness requires curated mapping rules grounded in manifests, descriptions, categories and the startup/routing spine.

**Acceptance Criteria**:  
- **Given** skill records have been extracted, **When** the semantic mapper runs, **Then** each skill receives at least one task shape or capability and at least one semantic bridge relationship.  
  **Example**: `bdd-practice` maps to acceptance criteria, verification workflow and `tdd-practice`.
- **Given** a category contains skills with few explicit related links, **When** the mapper applies curated category rules, **Then** skills are connected to relevant knowledge domains and workflow stages.  
  **Example**: Business architecture skills connect to strategy, capability, value stream and data traceability domains.
- **Given** a mapping rule is curated rather than directly extracted, **When** the graph export records provenance, **Then** the bridge edge states the mapping source or rule ID.  
  **Example**: `GOVERNS` edge from `guardrails-safety-patterns` records `control-theme-rule` as evidence.

**Non-Functional Requirements (NFRs)**:  
- Mappings must be explainable and traceable to file evidence or curated rule IDs.
- Rules must be stored in configuration or documented mapping files, not hidden in ad hoc code.
- Mapper output must be stable across runs.

**Success Metric**:  
- Every skill satisfies mandatory semantic bridge coverage with traceable mapping evidence.

**Delivery slices** *(optional — use when story spans multiple waves)*:  

| Slice | Wave | Delivers |
| --- | --- | --- |
| **004a** | 2 | Curated bridge taxonomy and mapping config |
| **004b** | 2 | Mapper implementation and tests |

**Dependencies (hard)**:  
- STORY-002, STORY-003

**Dependencies (soft)**:  
- STORY-006 can load initial bridge relationships before full mapper sophistication

**Visual Reference**:  
- Bridge taxonomy table in ontology docs

**Business Value/Priority**:  
- Critical priority because this is the main mechanism preventing graph fragments.
