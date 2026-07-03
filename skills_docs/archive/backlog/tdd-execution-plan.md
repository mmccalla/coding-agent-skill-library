# Skills KG MCP TDD Execution Plan

This execution plan groups the Skills KG MCP backlog into small, dependency-aware delivery slices. Each slice starts with failing tests, implements the smallest passing change, then runs targeted validation before moving on.

## Story Atomicity Reflection

The backlog has been reviewed for atomicity and discreteness:

- `STORY-001` now owns only the ontology contract and SHACL shapes. Neo4j physical constraints and indexes belong to `STORY-005`.
- `STORY-007` now owns embedding generation, vector index population and candidate vector queries. Hybrid ranking belongs to `STORY-008`.
- `STORY-002`, `STORY-003`, `STORY-004`, `STORY-005`, `STORY-006`, `STORY-008`, `STORY-009` and `STORY-010` each own a distinct capability boundary.
- `STORY-010` is intentionally an enablement story covering documentation, CI and runbooks after implementation slices exist.

## TDD Rules

For every slice:

1. Write the smallest failing test for the observable behaviour.
2. Run the targeted test and confirm it fails for the expected reason.
3. Implement the smallest passing change.
4. Run the targeted test again.
5. Run broader validation only after the slice passes.
6. Record residual risk before starting the next slice.

Use deterministic fake services for tests unless the slice explicitly requires Neo4j integration. Live Neo4j tests should be optional and clearly marked.

## Deliverable Slices

| Slice | Stories | Outcome | TDD Gate | Depends On |
| --- | --- | --- | --- | --- |
| 1 | `STORY-001` | Ontology contract, competency questions, Turtle and SHACL shape files | Tests parse ontology artefacts and verify required classes/properties/shapes exist | None |
| 2 | `STORY-002` | Connectivity contract and no-fragment validation rules over exported records | Tests fail on isolated skill fixtures and pass on one connected fixture | Slice 1 |
| 3 | `STORY-003` | Deterministic skill extractor for `SKILL.md` files, sections, references and related skills | Tests prove stable IDs, 91 skill records and repeatable hashes | Slice 1 |
| 4 | `STORY-004` | Semantic bridge mapper for task shapes, workflow stages, capabilities, control themes and domains | Tests prove every fixture skill gets bridge coverage with mapping provenance | Slices 2, 3 |
| 5 | `STORY-005` | Neo4j schema script with uniqueness constraints, lookup indexes, full-text indexes and vector index definitions | Tests inspect generated Cypher for required constraints and indexes | Slice 1 |
| 6 | `STORY-006` | Idempotent Neo4j loader and schema preflight checks | Tests prove duplicate loads preserve logical counts using a fake repository or test Neo4j | Slices 3, 4, 5 |
| 7 | `STORY-002`, `STORY-006` | End-to-end connectivity report after load/export | Tests fail missing bridge edges and pass when all skills are reachable from the root spine | Slices 4, 6 |
| 8 | `STORY-007` | Deterministic embedding provider, chunk embeddings and vector candidate queries | Tests prove same text gives same embedding and vector candidates preserve provenance | Slices 5, 6 |
| 9 | `STORY-008` | Hybrid retrieval using full-text, vector candidates and graph connectivity | Tests prove connected evidence outranks isolated similarity and uncertainty is reported | Slices 7, 8 |
| 10 | `STORY-009` | Read-only Skills MCP server tools and resources | Tests prove tool discovery, bounded responses and no arbitrary Cypher/write tools | Slice 9 |
| 11 | `STORY-010` | Documentation, runbooks and CI integration | Tests/CI prove deterministic validations run without live Neo4j and integration tests are optional | Slices 1-10 |

## Suggested Branching Order

Use one branch per deliverable slice or small group of adjacent slices:

1. `feature/skills-kg-ontology-contract` for Slices 1-2.
2. `feature/skills-kg-extractor-mapper` for Slices 3-4.
3. `feature/skills-kg-neo4j-load` for Slices 5-7.
4. `feature/skills-kg-vector-retrieval` for Slices 8-9.
5. `feature/skills-kg-mcp-server` for Slice 10.
6. `feature/skills-kg-docs-ci` for Slice 11.

## Validation Ladder

Run the narrowest useful check first:

| Level | Command or Check | When |
| --- | --- | --- |
| Unit | `python3 -m unittest <target>` | Every slice |
| Structural | `python3 scripts/validate_skills.py` | Any skill/doc rule change |
| Backlog lint | `ReadLints` on changed markdown | Any story or docs change |
| Local CI | `./scripts/ci_local.sh` | Before review hand-off |
| Neo4j integration | Optional test profile with Neo4j connection | Loader, schema and vector slices |
| MCP contract | MCP tool discovery and response schema tests | MCP server slice |

## Definition of Done

A slice is complete only when:

- failing tests were observed before implementation;
- targeted tests pass;
- relevant docs or story references are updated;
- graph connectedness assumptions are recorded;
- local CI passes where applicable;
- residual risks are stated in the hand-off notes.

## Residual Planning Notes

- `STORY-010` may become two stories later if CI integration and documentation grow independently, but it is acceptable as a final enablement slice for now.
- Neo4j integration tests should not be mandatory in default CI unless the project adds a managed test database or container workflow.
- The first MCP release should stay read-only and avoid arbitrary Cypher exposure.
