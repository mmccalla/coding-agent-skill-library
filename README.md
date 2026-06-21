# Coding Agent Skills KG

Portable coding-agent skills library plus a local Neo4j-backed GraphRAG service.

Core surfaces:

- `skills/`: reusable `SKILL.md` operating procedures.
- `skills_docs/`: routing, contracts, ontology, runbooks and templates.
- `scripts/skills_mcp_server.py`: read-only MCP server.
- `scripts/skills_api.py`: FastAPI GraphRAG API, OpenAPI, metrics and MCP HTTP transport.
- `skills-ui/`: React/Tailwind/D3 inspection UI.
- `docker-compose.yml`: Neo4j, loader, API, UI, Prometheus and Grafana.

Primary consumers: Cursor, Claude Code, Codex and other coding-agent runtimes that need deterministic task routing, source-backed skill retrieval and delivery controls.

## Agent Contract

Mandatory session startup order:

1. `AGENTIC_CODING_GLOBAL_SAFETY.md`
2. `SECURE_AGENTIC_DEVELOPMENT.md`
3. `skills/agent-control-patterns/apply-laws-of-ai/SKILL.md`
4. `skills_docs/HOW_TO_FIND_THE_RIGHT_SKILL.md`
5. smallest relevant `SKILL.md` set for the task

Minimum agent loop:

```text
classify task and risk
→ resolve or recommend skills
→ retrieve source-backed guidance
→ execute with tests and evidence
→ report changed files, checks, behaviour changes, assumptions and residual risk
```

## MCP Server

Read-only stdio server:

```bash
uv run --no-project \
  --directory /path/to/coding-agent-skill-library \
  --with-editable /path/to/coding-agent-skill-library \
  python scripts/skills_mcp_server.py --sdk-stdio
```

Discovery checks:

```bash
python3 scripts/skills_mcp_server.py --list-tools
python3 scripts/skills_mcp_server.py --list-resources
```

Tools:

- `route_skill_query`
- `resolve_skill`
- `search_skills`
- `get_skill`
- `recommend_skills`
- `get_skill_context`
- `get_skill_execution_guide`

Resources:

- `skills://ontology`
- `skills://contract`

Global Cursor MCP config shape:

```json
{
  "mcpServers": {
    "skills-kg": {
      "command": "/path/to/uv",
      "args": [
        "run",
        "--no-project",
        "--directory",
        "/path/to/coding-agent-skill-library",
        "--with-editable",
        "/path/to/coding-agent-skill-library",
        "python",
        "scripts/skills_mcp_server.py",
        "--sdk-stdio"
      ]
    }
  }
}
```

## API

Graph consumers are read-only. No arbitrary Cypher, raw embeddings or write tools are exposed.

Endpoints:

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
- `GET /metrics`
- `GET /docs`
- `GET /openapi.json`
- `/mcp`

Notes:

- `POST /skills/upload/preview` validates a candidate `SKILL.md`; it does not persist or write to Neo4j.
- `POST /skills/query` sends bounded graph evidence to a user-selected local Ollama model.
- Ollama URL validation is local-only and rejects credential-bearing URLs.

## Local Stack

Start from the repository root:

```bash
docker compose up --build -d
```

Stop without deleting Neo4j data:

```bash
docker compose down
```

Service URLs:

- UI: `http://localhost:5173`
- FastAPI: `http://localhost:8000`
- OpenAPI: `http://localhost:8000/docs`
- OpenAPI JSON: `http://localhost:8000/openapi.json`
- Neo4j browser: `http://localhost:7474`
- Neo4j Bolt: `bolt://localhost:7687`
- Prometheus: `http://localhost:9090`
- Grafana: `http://localhost:3000`

Health checks:

```bash
docker compose ps
curl -fsS http://localhost:8000/health/live
curl -fsS http://localhost:8000/health/ready
curl -fsS http://localhost:8000/metrics
curl -fsS http://localhost:5173
```

Do not use `docker compose down -v` unless deleting local graph data is intentional.

Ollama endpoint when API runs in Docker and Ollama runs on the host:

```text
http://host.docker.internal:11434
```

Non-Docker local UI endpoint:

```text
http://127.0.0.1:11434
```

## UI

Workspace sections:

- `Ask`: local Ollama-backed graph queries.
- `Agent Workflow`: route, resolve, retrieve, expand context and produce execution guidance.
- `API Contract`: OpenAPI and agent-critical endpoint rules.
- `Upload`: non-persistent `SKILL.md` preview validation.
- `Graph`: D3 graph inspection with filters, labels, selected node detail and accessible summary.

The header shows API readiness, MCP status and graph counts. The MCP panel reads `GET /mcp/technical-info`.

## Neo4j Loading

For a local Neo4j instance:

```bash
export NEO4J_URI="bolt://localhost:7687"
export NEO4J_USER="neo4j"
export NEO4J_PASSWORD="<local-password>"
export NEO4J_DATABASE="neo4j"

python3 scripts/embed_skill_chunks.py --apply --batch-size 500
python3 scripts/check_neo4j_readiness.py --json
```

Schema: `neo4j/skills_schema.cypher`

Readiness requirement:

```json
{"ready": true}
```

## Observability

Signals:

- `x-request-id` on API responses.
- Structured safe errors for `/skills/query` and `/ollama/models`.
- Prometheus metrics at `GET /metrics`.
- Structured logs for request completion, route selection, evidence selection and retrieval completion.
- Provisioned Grafana dashboard: `Skills KG API Observability`.

Key metric groups:

- request count and duration;
- 5xx ratio;
- Neo4j readiness;
- graph node and relationship counts;
- retrieval requests by route and outcome;
- recommendation count and top-score distribution;
- Ollama failures.

Config locations:

- `configs/prometheus/prometheus.yml`
- `configs/grafana/`

## Local Development

Install Python dependencies:

```bash
python3 -m pip install -e ".[dev]"
```

Run API:

```bash
python3 -m uvicorn scripts.skills_api:create_app --factory --host 127.0.0.1 --port 8000 --reload
```

Run UI:

```bash
cd skills-ui
npm install
VITE_API_BASE_URL=http://localhost:8000 npm run dev
```

## Validation

Full local gate:

```bash
./scripts/ci_local.sh
```

Targeted checks:

```bash
python3 scripts/validate_skills.py
python3 scripts/validate_skills_graph.py
python3 scripts/evaluate_skill_retrieval.py --limit 3
python3 scripts/skills_mcp_server.py --list-tools
python3 scripts/skills_mcp_server.py --list-resources
npm --prefix skills-ui test
npm --prefix skills-ui run lint
npm --prefix skills-ui run build
```

Quality baseline:

- Ruff and Ruff format clean.
- mypy clean for `scripts/`.
- pytest coverage threshold: 80%.
- offline MCP smoke checks pass.
- retrieval evaluation gate passes.

## Portable Library

Copy set:

```text
AGENTS.md
CLAUDE.md
AGENTIC_CODING_GLOBAL_SAFETY.md
SECURE_AGENTIC_DEVELOPMENT.md
skills/
skills_docs/
```

Bootstrap docs:

- `skills_docs/DROP_IN_BOOTSTRAP.md`
- `skills_docs/HOW_TO_FIND_THE_RIGHT_SKILL.md`
- `skills_docs/LIBRARY_CONTRACT.md`

## Runbook

Detailed workflow: `skills_docs/SKILLS_KG_MCP_RUNBOOK.md`

Coverage:

- extraction;
- bridge mapping;
- Neo4j schema setup;
- idempotent loading;
- index readiness;
- retrieval-unit embeddings;
- hybrid retrieval;
- MCP SDK usage;
- FastAPI endpoints;
- retrieval evaluation gates;
- connectedness troubleshooting;
- CI expectations.
