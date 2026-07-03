# Skills KG and MCP Backlog

Backlog derived from `Skills KG and MCP Plan`. Stories use the enhanced agile user story template and BDD-style acceptance criteria.

| Story | Title | Primary dependency |
| --- | --- | --- |
| STORY-001 | [Define Skills Ontology Contract](STORY-001-ontology-and-neo4j-schema.md) | None |
| STORY-002 | [Validate Holistic Graph Connectivity](STORY-002-holistic-graph-connectivity.md) | STORY-001 |
| STORY-003 | [Extract Skills into Deterministic Graph Records](STORY-003-skill-graph-extractor.md) | STORY-001 |
| STORY-004 | [Map Skills to Semantic Bridge Concepts](STORY-004-semantic-bridge-mapper.md) | STORY-002 |
| STORY-005 | [Apply Neo4j Constraints and Indexes](STORY-005-neo4j-schema-constraints-indexes.md) | STORY-001 |
| STORY-006 | [Load Skills into Neo4j Idempotently](STORY-006-idempotent-neo4j-loader.md) | STORY-003 |
| STORY-007 | [Create Skill Chunk Embeddings and Vector Index](STORY-007-embeddings-and-vector-index.md) | STORY-005 |
| STORY-008 | [Retrieve Skills with Hybrid Graph and Vector Evidence](STORY-008-hybrid-connected-retrieval.md) | STORY-002 |
| STORY-009 | [Expose Skills Graph through Read-Only MCP Tools](STORY-009-read-only-skills-mcp-server.md) | STORY-008 |
| STORY-010 | [Document and Validate the Skills KG MCP Workflow](STORY-010-docs-runbooks-and-ci.md) | STORY-001 through STORY-009 |
