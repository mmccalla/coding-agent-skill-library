# Skills KG MCP Runbook

This runbook explains how to rebuild, validate and operate the graph-backed skills workflow locally. Commands use placeholder values only; do not commit real connection strings, usernames, passwords or tokens.

## Offline Local Workflow

Install the project and run the deterministic offline gate first:

```bash
python3 -m pip install -e ".[dev]"
python3 scripts/extract_skills_graph.py > /tmp/skills-graph.json
python3 scripts/map_skills_bridges.py > /tmp/skills-graph-mapped.json
python3 scripts/validate_skills_graph.py
python3 scripts/load_skills_neo4j.py
python3 scripts/embed_skill_chunks.py --query "approval before destructive command" --limit 3
python3 scripts/retrieve_skills_hybrid.py "graph rag ontology retrieval" --limit 3
python3 scripts/skills_mcp_server.py --list-tools
python3 scripts/evaluate_skill_retrieval.py --limit 3
./scripts/ci_local.sh
```

The dry-run loader reports planned nodes and relationships without contacting Neo4j. The deterministic embedder is used in local test mode and makes no external network call. `./scripts/ci_local.sh` runs skill validators, Ruff, mypy, pytest with coverage, offline smoke checks and the retrieval evaluation gate.

## Production-Like Neo4j Workflow

Use Docker Compose for a disposable local Neo4j instance:

```bash
docker compose up -d neo4j
```

Then set placeholder local credentials and load the embedded graph:

```bash
export NEO4J_URI="bolt://localhost:7687"
export NEO4J_USER="neo4j"
export NEO4J_PASSWORD="testpassword"
export NEO4J_DATABASE="neo4j"

python3 scripts/embed_skill_chunks.py --apply --batch-size 500
python3 scripts/check_neo4j_readiness.py --json
python3 -m pytest -m live_neo4j tests/test_live_neo4j_integration.py -q
```

`neo4j/skills_schema.cypher` defines required constraints, lookup indexes, full-text indexes and the vector index. The live readiness report must show `ready: true`, all required constraints/indexes online and `vector_query_ok: true`.

Do not print or store real secrets in run logs. The MCP and API surfaces are read-only; graph loading remains an operator action, not an agent tool.

## MCP Usage

The MCP server exposes only read-only capabilities:

- `route_skill_query`
- `resolve_skill`
- `search_skills`
- `get_skill`
- `recommend_skills`
- `get_skill_context`
- `get_skill_execution_guide`

The legacy JSON-RPC stdio compatibility mode remains the default:

```bash
python3 scripts/skills_mcp_server.py
```

Use the official MCP SDK stdio server for protocol-compatible clients:

```bash
python3 scripts/skills_mcp_server.py --sdk-stdio
```

Discovery smoke checks:

```bash
python3 scripts/skills_mcp_server.py --list-tools
python3 scripts/skills_mcp_server.py --list-resources
```

The server denies unsupported write or arbitrary Cypher tools. Agent-facing resources are curated and do not expose raw vectors, executable Cypher or internal graph schema metadata. Tests include a real official MCP client discovery and tool-call check.

`skills://contract` defines the agent workflow explicitly:

- call `route_skill_query` before answering ambiguous natural-language skill questions;
- use `resolve_skill` when the user provides a human-readable skill name such as `accessibility-wcag`;
- use `get_skill` for `direct_lookup` requests;
- use `recommend_skills` only for task-oriented recommendation prompts;
- use `get_skill_context` for related, prerequisite, complementary or neighbouring skills;
- use `get_skill_execution_guide` before acting from a skill so the agent has when-to-use, objective, procedure, rules, verification checklist and related-skill evidence.

Before acting, agents must return or retain the selected route, resolved skill id where applicable, source paths, section ids or evidence paths, and the verification checklist for execution-plan routes. The contract examples cover direct lookup, recommendation, context expansion and execution-plan requests.

## FastAPI Usage

The FastAPI app factory lives in `scripts/skills_api.py`. It exposes read-only endpoints:

- `GET /health/live`
- `GET /health/ready`
- `GET /skills/graph`
- `GET /skills/search`
- `GET /skills/{skill_id}`
- `GET /skills/{skill_id}/context`
- `GET /ollama/models`
- `POST /skills/route`
- `GET /skills/resolve`
- `GET /skills/{skill_id}/execution-guide`
- `POST /skills/recommend`
- `POST /skills/query`
- `POST /skills/upload/preview`
- `GET /mcp/technical-info`

For local serving:

```bash
python3 -m uvicorn scripts.skills_api:create_app --factory --host 127.0.0.1 --port 8000
```

The app also mounts the official MCP streamable HTTP app at `/mcp`.

## UI Usage

The separate React deployable lives in `skills-ui/`. It uses Tailwind for styling, D3 for graph rendering and the existing FastAPI surface for all backend calls.

Run it locally after starting the FastAPI app:

```bash
cd skills-ui
npm install
VITE_API_BASE_URL=http://localhost:8000 npm run dev
```

The UI supports:

- upload preview for candidate `SKILL.md` files through `POST /skills/upload/preview`;
- D3 graph inspection through `GET /skills/graph`;
- local Ollama-backed graph questions through `POST /skills/query`;
- API readiness and MCP boundary checks through `GET /health/ready` and `GET /mcp/technical-info`.

Upload preview is intentionally non-persistent. It validates the file shape and frontmatter but does not write to the repository or Neo4j.

The Ollama query flow defaults to `http://127.0.0.1:11434` and lets the user edit the endpoint. Server-side guardrails allow only local endpoints such as `127.0.0.1`, `localhost`, `::1` and `host.docker.internal`, reject URLs containing credentials, and send only bounded graph evidence to the selected model. Keep `.env` files out of source control. The UI calls `GET /ollama/models` so users can choose from running and installed local Ollama models before submitting a graph query.

## Full Local Docker Stack

For live testing with Neo4j, the FastAPI service and the UI together:

```bash
docker compose up --build
```

Compose starts:

- `neo4j` on `http://localhost:7474` and `bolt://localhost:7687`;
- `skills-loader`, which applies the graph load once Neo4j is healthy;
- `skills-api` on `http://localhost:8000`;
- `skills-ui` on `http://localhost:5173`.

Use `http://localhost:5173` for UI testing and `http://localhost:8000/health/ready` to inspect live Neo4j readiness evidence.

If the FastAPI service is running in Docker and Ollama is running on the host, use `http://host.docker.internal:11434` in the UI endpoint field. Load the model list in the UI, then choose the model explicitly before querying. The API does not auto-rank or auto-select models.

## Integration Tests

Unit tests and deterministic validations run without Neo4j. Live integration tests require explicit local configuration or the GitHub Actions Neo4j service:

- `NEO4J_URI`
- `NEO4J_USER`
- `NEO4J_PASSWORD`
- `NEO4J_DATABASE`

GitHub Actions uses a disposable `neo4j:5.26-community` service with placeholder credentials, runs `./scripts/ci_local.sh`, then emits `python scripts/check_neo4j_readiness.py --json`. Do not point the live test profile at a shared or production database.

## Retrieval Evaluation

Golden cases are stored in `tests/fixtures/retrieval_evaluation/golden_queries.json`. The gate runs:

```bash
python3 scripts/evaluate_skill_retrieval.py --limit 3
```

The report must pass these metrics:

- recall@k
- mean reciprocal rank
- source and section coverage
- uncertainty accuracy for absent answers

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
