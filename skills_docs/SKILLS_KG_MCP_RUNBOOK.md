# Skills KG MCP Runbook

This runbook explains how to rebuild, validate and operate the graph-backed skills workflow locally. Commands use placeholder values only; do not commit real connection strings, usernames, passwords or tokens.

## Offline Local Workflow

No live Neo4j instance is required for offline CI. These commands validate extraction, mapping, embeddings, retrieval and MCP discovery using deterministic local code:

```bash
python3 scripts/extract_skills_graph.py > /tmp/skills-graph.json
python3 scripts/map_skills_bridges.py > /tmp/skills-graph-mapped.json
python3 scripts/validate_skills_graph.py
python3 scripts/load_skills_neo4j.py
python3 scripts/embed_skill_chunks.py --query "approval before destructive command" --limit 3
python3 scripts/retrieve_skills_hybrid.py "graph rag ontology retrieval" --limit 3
python3 scripts/skills_mcp_server.py --list-tools
./scripts/ci_local.sh
```

The dry-run loader reports planned nodes and relationships without contacting Neo4j. The deterministic embedder is used in local test mode and makes no external network call.

## Production-Like Neo4j Workflow

Apply `neo4j/skills_schema.cypher` before loading. The loader can also apply schema during `--apply`, then preflights the required constraints before writing.

Use placeholders for local setup:

```bash
export NEO4J_URI="bolt://localhost:7687"
export NEO4J_USER="neo4j"
export NEO4J_PASSWORD="<placeholder-password>"

python3 scripts/embed_skill_chunks.py --apply --batch-size 500
```

Do not print or store secrets in run logs. The first release is read-only from the MCP surface; graph loading remains an operator action, not an agent tool.

## MCP Usage

The MCP server exposes only read-only capabilities:

- `search_skills`
- `get_skill`
- `recommend_skills`
- `get_skill_context`

STDIO mode is the default:

```bash
python3 scripts/skills_mcp_server.py
```

Discovery smoke checks:

```bash
python3 scripts/skills_mcp_server.py --list-tools
python3 scripts/skills_mcp_server.py --list-resources
```

The server denies unsupported write or arbitrary Cypher tools. Agent-facing resources are curated and do not expose raw vectors, executable Cypher or internal graph schema metadata.

## Integration Tests

Unit tests and deterministic validations run without Neo4j. Live integration tests require explicit local configuration:

- `NEO4J_URI`
- `NEO4J_USER`
- `NEO4J_PASSWORD`

Do not enable live integration tests in shared CI unless credentials are provided through a secure secret store and the target database is disposable.

## Connectedness Failure Runbook

If `python3 scripts/validate_skills_graph.py` reports a connectedness failure:

1. Read the failing skill name and message, for example `missing bridge provenance`, `missing semantic bridge` or `unreachable from root`.
2. Inspect `skills_docs/ontology/bridge_mapping_rules.json` for a missing or incorrect `mapping_rule_id`.
3. Check the owning `SKILL.md` for source evidence, related skills and bridge values.
4. Add or correct the smallest mapping rule that explains the relationship.
5. Re-run:

```bash
python3 scripts/map_skills_bridges.py > /tmp/skills-graph-mapped.json
python3 scripts/validate_skills_graph.py
./scripts/ci_local.sh
```

Do not add universal bridge values to hide outliers. Every connective bridge must have source evidence and provenance.
