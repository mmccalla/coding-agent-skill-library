# Coding Agent Skills KG

This repository is a coding-agent skills delivery system. It contains a portable skills library, a Neo4j knowledge graph representation of those skills, a read-only MCP server, a FastAPI GraphRAG API and a React UI for local inspection, API contract review and agent workflow testing.

The intended users are coding delivery systems such as Codex, Claude Code and Cursor agents. The system helps those agents choose the smallest relevant operating procedure for a task, retrieve source-backed guidance, inspect related skills and apply delivery controls such as TDD, safety gates, accessibility checks, reliability checks and evidence reporting.

## Current Purpose

The project now has two linked purposes:

- **Portable skills library:** `skills/` and `skills_docs/` provide reusable coding-agent operating procedures and mandatory startup guidance.
- **Skills KG service:** Neo4j, MCP, FastAPI and the UI expose those skills as a queryable, source-backed knowledge graph for humans and agents.

The long-term goal is for agents to use the Skills KG as a delivery control plane:

```text
user request
→ classify task and risk
→ resolve exact skills or recommend relevant skills
→ retrieve source-backed procedures, rules and verification checklists
→ execute with tests and evidence
→ report files changed, checks run, behaviour changes and residual risk
```

## System Components

- `skills/`: 87 `SKILL.md` files across agentic patterns, control patterns, engineering practices, UX, reliability, event-driven architecture, business architecture and data architecture.
- `skills_docs/`: routing guides, library contract, ontology documents, runbooks and templates.
- `scripts/extract_skills_graph.py`: extracts skill metadata, sections and relationships from the filesystem.
- `scripts/load_skills_neo4j.py` and `scripts/embed_skill_chunks.py`: load the skills graph and deterministic retrieval-unit embeddings into Neo4j.
- `scripts/skills_mcp_server.py`: exposes read-only MCP tools and resources.
- `scripts/skills_api.py`: exposes FastAPI endpoints for health, graph inspection, retrieval, upload preview, Ollama-backed query and MCP HTTP transport.
- `skills-ui/`: React, Tailwind and D3 UI for agent workflow review, OpenAPI/API exploration, graph inspection, model-backed graph questions, upload preview and MCP boundary review.
- `docker-compose.yml`: local full-stack deployment with Neo4j, graph loader, API, UI, Prometheus and Grafana.

## Agent Startup Contract

Every coding-agent session using this library must start with:

1. `AGENTIC_CODING_GLOBAL_SAFETY.md`
2. `SECURE_AGENTIC_DEVELOPMENT.md`
3. `skills/agent-control-patterns/apply-laws-of-ai/SKILL.md`
4. `skills_docs/HOW_TO_FIND_THE_RIGHT_SKILL.md`
5. the smallest relevant `SKILL.md` set for the task

The mandatory baseline is also recorded in `AGENTS.md` and `CLAUDE.md`.

## How Agents Should Use The Skills KG

The current MCP tools are:

- `route_skill_query`: classify a user request as `direct_lookup`, `recommendation`, `context` or `execution_plan`.
- `resolve_skill`: map human names such as `accessibility-wcag` to canonical ids such as `skill:accessibility-wcag`.
- `search_skills`: find likely skills by exact or keyword-oriented lookup.
- `get_skill`: retrieve one skill's bounded metadata and retrieval units.
- `recommend_skills`: recommend connected skills for a task query with evidence.
- `get_skill_context`: retrieve neighbouring skills and graph evidence paths.
- `get_skill_execution_guide`: return when-to-use, objective, procedure, rules, verification checklist and related skills.

The current MCP resources are:

- `skills://ontology`
- `skills://contract`

Recommended agent flow:

```text
1. Use route_skill_query for natural-language requests.
2. Use resolve_skill when a human-readable skill name is present.
3. Use get_skill for direct_lookup.
4. Use recommend_skills for recommendation.
5. Use get_skill_context for context expansion.
6. Use get_skill_execution_guide before acting from a skill.
7. Return route, selected tools, source paths, section ids or evidence paths before planning, editing or claiming completion.
```

`/skills/query` uses this router before generation, so direct skill-description questions use skill-profile evidence and task-oriented questions use recommendation evidence.

Example routes:

| User request | Route | Main tools |
| --- | --- | --- |
| `tell me about accessibility-wcag` | `direct_lookup` | `route_skill_query` → `resolve_skill` → `get_skill` |
| `which skills should I use for a secure MCP server?` | `recommendation` | `route_skill_query` → `recommend_skills` |
| `what is related to kg-enabled-rag?` | `context` | `route_skill_query` → `resolve_skill` → `get_skill_context` |
| `how do I apply tdd-practice?` | `execution_plan` | `route_skill_query` → `resolve_skill` → `get_skill_execution_guide` |

## FastAPI Surface

The API is read-only for graph consumers and does not expose arbitrary Cypher, raw embeddings or write tools.

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
- `/mcp` for the official MCP streamable HTTP app

`POST /skills/upload/preview` validates a candidate `SKILL.md` without persisting it or writing to Neo4j.

`POST /skills/query` sends bounded graph evidence to a user-selected local Ollama model. Ollama endpoint validation is local-only and rejects credential-bearing URLs.

## Run The Full Local Stack

Use Docker Compose for live local testing or redeployment from the repository root:

```bash
cd /Users/mmccalla/Documents/vscode/coding-agent-skill-library
```

Stop the current stack without deleting volumes:

```bash
docker compose down
```

Rebuild and redeploy the full stack:

```bash
docker compose up --build -d
```

Services:

- Neo4j browser: `http://localhost:7474`
- Neo4j Bolt: `bolt://localhost:7687`
- FastAPI: `http://localhost:8000`
- OpenAPI docs: `http://localhost:8000/docs`
- OpenAPI spec: `http://localhost:8000/openapi.json`
- Prometheus: `http://localhost:9090`
- Grafana: `http://localhost:3000`
- UI: `http://localhost:5173`

Verify the redeploy:

```bash
docker compose ps
curl -fsS http://localhost:8000/health/live
curl -fsS http://localhost:8000/health/ready
curl -fsS http://localhost:8000/metrics
curl -fsS http://localhost:8000/openapi.json
curl -fsS http://localhost:5173
```

`docker compose down` stops containers and preserves the Neo4j volume. Do not add `-v` unless you intentionally want to delete local graph data.

When the API runs in Docker and Ollama runs on the host, use:

```text
http://host.docker.internal:11434
```

The Docker-served UI defaults to that endpoint. A non-Docker local UI run can use `http://127.0.0.1:11434`.

## Observability

The API now emits bounded local observability signals for root-cause analysis:

- every API response includes an `x-request-id` header;
- `/skills/query` and `/ollama/models` return structured safe error details with `error_type`, `operation`, `request_id` and a remediation hint;
- `GET /metrics` exposes Prometheus metrics for request counts, request duration, Neo4j readiness, graph node/relationship counts, retrieval route outcomes, recommendation counts, top-score distribution and Ollama failures;
- structured API logs include `api_request_completed`, `skill_query_route_selected`, `skill_query_evidence_selected`, `skill_retrieval_completed` and safe failure events keyed by `request_id`;
- Docker Compose starts Prometheus and Grafana with a provisioned `Skills KG API Observability` dashboard.

Prometheus scrapes `skills-api:8000/metrics`. Grafana uses the provisioned Prometheus datasource and dashboard under `configs/grafana/`, including panels for API latency, 5xx ratio, Ollama failures, Neo4j readiness, graph counts and retrieval outcomes.

## UI Navigation And Capabilities

The UI at `http://localhost:5173` is organised around five task-centred workspace sections:

- **Ask:** graph querying through local Ollama. The UI calls `GET /ollama/models` so the user chooses the model explicitly before sending `POST /skills/query`. Query failures show HTTP status, error type, operation, request id and next diagnostic check when the API provides them.
- **Agent Workflow:** the explicit agent contract: route request, resolve skill, retrieve instructions, expand context only when needed, produce the execution checklist, then implement and validate.
- **API Contract:** OpenAPI Standards & API Explorer sourced from `GET /openapi.json`, plus query rules for the agent-critical endpoints.
- **Upload:** upload preview for candidate `SKILL.md` files through `POST /skills/upload/preview`; this validates shape and metadata without persisting or writing to Neo4j.
- **Graph:** D3 graph inspection with pan, zoom, node dragging, node type filters, skill category filtering, selected node details and an accessible graph summary.

The header status cards show API readiness, MCP boundary status and graph counts. The MCP technical information panel reads `GET /mcp/technical-info` and shows exposed tools, resources, endpoints and limits.

The API also exposes FastAPI's native OpenAPI docs at `http://localhost:8000/docs` and the raw OpenAPI document at `http://localhost:8000/openapi.json`.

## Run Backend And UI Without Docker

Install Python dependencies:

```bash
python3 -m pip install -e ".[dev]"
```

Start the API:

```bash
python3 -m uvicorn scripts.skills_api:create_app --factory --host 127.0.0.1 --port 8000 --reload
```

Start the UI:

```bash
cd skills-ui
npm install
VITE_API_BASE_URL=http://localhost:8000 npm run dev
```

## Neo4j Graph Loading

For a local Neo4j instance:

```bash
export NEO4J_URI="bolt://localhost:7687"
export NEO4J_USER="neo4j"
export NEO4J_PASSWORD="testpassword"
export NEO4J_DATABASE="neo4j"

python3 scripts/embed_skill_chunks.py --apply --batch-size 500
python3 scripts/check_neo4j_readiness.py --json
```

`neo4j/skills_schema.cypher` defines constraints, lookup indexes, full-text indexes and the vector index. The readiness report must show `ready: true` before relying on live retrieval.

## Validation

Run the local quality gate:

```bash
./scripts/ci_local.sh
```

The gate includes skill validation, Ruff, mypy, pytest with coverage, offline MCP smoke checks and retrieval evaluation.

For targeted checks:

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

## Portable Library Usage

The skills library can still be copied into another repository as a drop-in agent guidance layer. For a new project, copy:

```text
AGENTS.md
CLAUDE.md
AGENTIC_CODING_GLOBAL_SAFETY.md
SECURE_AGENTIC_DEVELOPMENT.md
skills/
skills_docs/
```

If the target repository already has its own `README.md`, keep this file as `docs/coding-agent-skill-library/README.md` or `AGENT_SKILLS_README.md`.

For portable setup, start with:

- `skills_docs/DROP_IN_BOOTSTRAP.md`
- `skills_docs/HOW_TO_FIND_THE_RIGHT_SKILL.md`
- `skills_docs/LIBRARY_CONTRACT.md`

## Runbook

The detailed graph-backed workflow is documented in `skills_docs/SKILLS_KG_MCP_RUNBOOK.md`. It covers extraction, bridge mapping, Neo4j schema setup, idempotent loading, index readiness, deterministic embeddings, hybrid retrieval, official MCP SDK usage, FastAPI endpoints, retrieval evaluation gates, connectedness troubleshooting and CI expectations.
