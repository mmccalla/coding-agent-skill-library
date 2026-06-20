# Skills Knowledge Graph Ontology

## Purpose

This ontology defines the semantic contract for representing the repository's `skills/` folder as a connected knowledge graph. It describes skill meaning, validation obligations, provenance, bridge concepts and the mapping required for later Neo4j storage and MCP retrieval.

The ontology is deliberately implementation-aware but not storage-specific. Physical Neo4j constraints, full-text indexes and vector indexes belong to the later Neo4j schema slice.

## Competency Questions

- Which skills should an agent use for a given task shape?
- Which skills normally precede, complement, govern or validate another skill?
- Which category, workflow stage, capability, control theme and knowledge domain does a skill support?
- Which source file, section or reference document supports a retrieved skill recommendation?
- Which validation rules apply to each skill and graph artefact?
- Are all skills connected to the startup/root spine with no unexplained fragments or outliers?

## Core Classes

- `Skill`: one operational skill defined by a `SKILL.md` file.
- `SkillCategory`: the category folder containing a skill.
- `SkillSection`: a canonical or optional markdown section within a skill.
- `SkillChunk`: a retrieval unit derived from a skill section or reference.
- `ReferenceDocument`: a linked local reference file used by a skill.
- `ValidationRule`: a structural, semantic or graph-connectivity rule.
- `Source`: an external or local evidence source cited by a skill.
- `TaskShape`: a task-intent bridge such as planning, implementation, verification or security.
- `WorkflowStage`: a lifecycle bridge such as startup, routing, planning, execution, validation or release.
- `Capability`: a reusable ability enabled by one or more skills.
- `ControlTheme`: a governance or safety theme such as provenance, least privilege or human approval.
- `KnowledgeDomain`: a domain bridge such as data architecture, agentic patterns or reliability.
- `BridgeAssertion`: a provenance-bearing assertion that a skill supports a task shape, workflow stage, capability, control theme or knowledge domain.

## Core Relationships

- `belongsToCategory`: connects a skill to exactly one category.
- `hasSection`: connects a skill to its extracted sections.
- `hasChunk`: connects a skill to retrieval chunks.
- `hasReference`: connects a skill to local reference documents.
- `validatedBy`: connects a skill or artefact to validation rules.
- `citesSource`: connects a skill to supporting evidence sources.
- `supportsTaskShape`: connects a skill to a task-intent bridge.
- `operatesInStage`: connects a skill to a workflow stage.
- `enablesCapability`: connects a skill to a capability.
- `governedBy`: connects a skill to a control theme.
- `partOfDomain`: connects a skill to a knowledge domain.
- `assertsBridge`: connects a skill to each bridge assertion used to justify bridge coverage and connectivity.

Semantic skill-to-skill relationships use explicit predicates such as `precedes`, `requires`, `complements`, `refines`, `governsSkill` and `validatesSkill`. Avoid vague relationships such as `relatedTo` unless the source relationship is literal and later mapper slices refine it.

Bridge assertions must include source evidence and confidence. Generic graph-wide bridge values are invalid because they can hide outliers and make fragmented graphs appear connected.

## Property Graph Mapping

| Ontology class | Neo4j label | Identifier policy |
| --- | --- | --- |
| `Skill` | `Skill` | deterministic `skill:{name}` id where `name` matches the skill folder path; unique `name` |
| `SkillCategory` | `SkillCategory` | category folder name |
| `SkillSection` | `SkillSection` | skill id plus heading plus ordinal |
| `SkillChunk` | `SkillChunk` | section id plus chunk ordinal plus content hash |
| `ReferenceDocument` | `ReferenceDocument` | repository-relative path |
| `ValidationRule` | `ValidationRule` | stable rule id |
| `Source` | `Source` | URL or repository-relative path |
| `TaskShape` | `TaskShape` | curated slug |
| `WorkflowStage` | `WorkflowStage` | curated lifecycle slug |
| `Capability` | `Capability` | curated capability slug |
| `ControlTheme` | `ControlTheme` | curated control-theme slug |
| `KnowledgeDomain` | `KnowledgeDomain` | curated domain slug |
| `BridgeAssertion` | `BridgeAssertion` | skill id plus bridge kind plus bridge value |

Required skill properties include `id`, `name`, `title`, `description`, `path`, `contentHash`, `wordCount`, `lineCount` and `isBaselineSkill`. Later slices may add embeddings to `SkillChunk` and optionally coarse embeddings to `Skill`.

## Open Decisions

- Embedding dimensions remain configurable in `configs/skills_kg.yaml`.
- Neo4j physical index names and exact vector similarity settings are deferred to the schema slice.
- The first MCP server release should expose curated read-only tools rather than arbitrary Cypher.
- Connectivity validation must fail unexplained skill fragments, while allowing intentionally external `Source`, `ReferenceDocument` and `ValidationRule` leaves.
