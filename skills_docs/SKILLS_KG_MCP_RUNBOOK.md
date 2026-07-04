# Skills KG MCP Runbook

This runbook explains how to rebuild, validate and operate the graph-backed skills workflow locally. Commands use placeholder values only; do not commit real connection strings, usernames, passwords or tokens.

## Offline Local Workflow

Install the project and run the deterministic offline gate first:

```bash
python3 -m pip install -e ".[dev]"
python3 scripts/extract_skills_graph.py > /tmp/skills-graph.json
python3 scripts/validate_skills_graph.py
python3 scripts/load_skills_neo4j.py
python3 scripts/embed_skill_chunks.py --query "approval before destructive command" --limit 3
python3 scripts/retrieve_skills_hybrid.py "graph rag ontology retrieval" --limit 3
python3 scripts/skills_mcp_server.py --list-tools
python3 scripts/evaluate_skill_retrieval.py --limit 3
./scripts/ci_local.sh
```

The dry-run loader reports planned nodes and relationships without contacting Neo4j. The deterministic retrieval-unit embedder is used in local test mode and makes no external network call. `./scripts/ci_local.sh` runs skill validators, Ruff, mypy, pytest with coverage, offline smoke checks and the retrieval evaluation gate.

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

`neo4j/skills_schema.cypher` defines required constraints, lookup indexes, full-text indexes and the `RetrievalUnit` vector index. The live readiness report must show `ready: true`, all required constraints/indexes online and `vector_query_ok: true`.

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

Before acting, agents must return or retain the selected route, resolved skill id where applicable, source paths, heading paths, line ranges, `source_section_id` or other evidence paths, and the verification checklist for execution-plan routes. The contract examples cover direct lookup, recommendation, context expansion and execution-plan requests.

### Agent workflow and selection trace fields

Follow this tool sequence for natural-language skill questions:

1. `route_skill_query` — classify the request and read `selection_trace.query_intent`, `suggested_tool` and `evidence_required`.
2. `resolve_skill` — when the user names a skill in prose, resolve the canonical `skill_id` before lookup, context or execution-guide calls.
3. Route-specific follow-up:
   - `direct_lookup` → `get_skill` (optionally `get_skill_context`)
   - `recommendation` → `recommend_skills`
   - `context` → `get_skill_context`
   - `execution_plan` → `get_skill_execution_guide`

`route_skill_query` and `recommend_skills` both return a `selection_trace` object for audit. Existing keys (`request`, `selected`, `rejected`) are preserved; Phase 7 adds:

| Field | Tool(s) | Purpose |
| --- | --- | --- |
| `tool` | route, recommend | MCP tool that produced the trace |
| `query_intent` | route, recommend | Route or recommendation intent (`direct_lookup`, `recommendation`, etc.) |
| `usage_event_id` | route, recommend | Deterministic id (`sel-…`) for correlating logs and metrics |
| `filter` | route, recommend | Resolution or promotion filters applied (`promotion_status`, `rejected_count`, `evidence_required`) |
| `rank` | recommend | Ordered candidates with `skill_id`, `rank` and `score` |
| `evidence` | route | Resolved skill `source_paths` and `evidence_anchors` when available |
| `evidence_anchor_ids` | route, recommend | Section or retrieval-unit ids cited in the trace |
| `abstention_reason` | recommend | Present when `uncertain=true` and no confident match was promoted |

Retain `selection_trace` alongside tool results before acting. Do not expose raw user query text in metrics labels; use `query_intent`, `tool`, `skill_id`, `rank` and `outcome` only.

## Cursor IDE setup

Cursor configuration for **MCP-only** and **filesystem-only** modes: [`CURSOR_IDE_SETUP.md`](CURSOR_IDE_SETUP.md). This repository defaults to MCP-only (`.vscode/settings.json`, `.cursor/rules/skills-kg-mcp-only.mdc`).

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
- **admin ingest** after a trust-passing preview when an admin key is configured (`POST /skills/admin/ingest` via the Ingest skill modal);
- D3 graph inspection through `GET /skills/graph`;
- local Ollama-backed graph questions through `POST /skills/query`;
- API readiness and MCP boundary checks through `GET /health/ready` and `GET /mcp/technical-info`.

Upload preview is intentionally non-persistent. It validates the file shape, frontmatter and trust layers but does not write to the repository or Neo4j. Use **Ingest skill** (admin key required) to persist a trust-passing upload through the same gate as `POST /skills/admin/ingest`.

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

## Observability Checks

Use the API request id to connect UI/API failures to structured logs and Prometheus metrics. The API emits safe JSON log events for completed requests, selected skill-query routes, selected query evidence, retrieval results and Ollama failures. These logs intentionally omit raw prompts, embeddings, credentials and `.env` values.

Prometheus scrapes `GET /metrics` and includes:

- `skills_api_requests_total` and `skills_api_request_duration_seconds` for route-level traffic and latency;
- `skills_api_readiness_state` for Neo4j dependency readiness;
- `skills_api_graph_nodes` and `skills_api_graph_relationships` for loaded graph shape after reloads;
- `skills_api_retrieval_requests_total`, `skills_api_retrieval_recommendation_count` and `skills_api_retrieval_top_score` for retrieval outcome tracking;
- `skills_api_ollama_failures_total` for model discovery and query failures.
- `skills_usage_hits_total`, `skills_usage_abstention_total`, `skills_usage_execution_guide_total` and `skills_usage_recommend_rank_total` for MCP/API skill selection usage;
- `skills_trust_rejected_total`, `skills_quarantined_total` and `skills_admin_ingest_total` for pre-ingest trust, promotion gates and admin writes.

Grafana's `Skills KG API Observability` dashboard shows API request rate, 5xx ratio, p95 latency, Ollama failures, Neo4j readiness, graph node counts and retrieval requests by route. The `Skills KG Usage` dashboard (`configs/grafana/dashboards/skills-kg-usage.json`) shows top skills, hits by tool, abstention rate, execution-guide conversion and zero-hit snapshots.

MCP stdio parity: `python3 scripts/skills_mcp_server.py --metrics` prints the same combined usage and trust counters for operator scraping when HTTP is unavailable.

## Admin skill ingest

Trusted skill uploads use admin auth and the same L1–L4 trust gates as CI preview:

```bash
export SKILLS_ADMIN_API_KEY='replace-me'
export SKILLS_ADMIN_WRITE_MODE=direct   # or staging
curl -sS -X POST http://127.0.0.1:8000/skills/admin/ingest \
  -H "X-Skills-Admin-Key: $SKILLS_ADMIN_API_KEY" \
  -F "file=@skills/tdd-practice/SKILL.md;type=text/markdown"
```

`GET /skills/admin/ingests` returns the in-memory audit trail. Successful ingest registers the skill in `PACK_METADATA.json`, re-extracts the graph, and reloads the MCP server plan in-process.

## CI Ingest Gate

Skill changes run the Phase 9 ingest gate from `./scripts/ci_local.sh`:

```bash
python3 scripts/ci_ingest_gate.py
```

The gate runs, in order: L2 trust validation (`validate_skill_trust.py --ci-gate` semantics), graph connectivity, SHACL with governed instances, tiered corpus validation (`validate_eval_corpus.py`), change-scoped delta retrieval eval when `DELTA_EVAL_BASE_REF` is set (or `--delta-base-ref` / `--changed-skill`), promoted-release retrieval smoke (`tests/fixtures/retrieval_evaluation/smoke_queries_promoted.json`) and a Neo4j dry-run load plan. Merge is blocked on L2 security failure, corpus contract failure, delta regression on changed skills, or promoted retrieval regression.

Weekly zero-hit promoted skills rollup:

```bash
python3 scripts/rollup_skill_usage.py --period-days 7
python3 scripts/report_skill_usage.py --json
```

## Integration Tests

Unit tests and deterministic validations run without Neo4j. Live integration tests require explicit local configuration or the GitHub Actions Neo4j service:

- `NEO4J_URI`
- `NEO4J_USER`
- `NEO4J_PASSWORD`
- `NEO4J_DATABASE`

GitHub Actions uses a disposable `neo4j:5.26-community` service with placeholder credentials, runs `./scripts/ci_local.sh`, then emits `python scripts/check_neo4j_readiness.py --json`. Do not point the live test profile at a shared or production database.

## Retrieval Evaluation

Evaluation uses a **tiered corpus** (see `skills_docs/krag/EVALUATION_CORPUS_CONTRACT.md`):

| Tier | Fixture | PR gate |
| --- | --- | --- |
| Smoke | `smoke_queries_promoted.json` | Yes (`ci_ingest_gate.py`) |
| Realistic | `realistic_queries.json` | Yes (`test_e2e_realistic_retrieval.py`) |
| Abstention | `abstention_probes.json` | Yes (`test_e2e_realistic_retrieval.py`) |
| Coverage | `coverage_queries.json` | Nightly workflow |

Validate and regenerate:

```bash
python3 scripts/validate_eval_corpus.py --check-skill-sync
python3 scripts/generate_golden_queries.py --tier all --write-legacy-golden
python3 scripts/evaluate_skill_retrieval.py \
  --dataset tests/fixtures/retrieval_evaluation/smoke_queries_promoted.json \
  --limit 3
```

Release gates (see `krag/EVALUATION.md`):

- smoke / realistic: **precision@1 = 1.0**; exclusion_accuracy **≥ 0.5**
- abstention: **uncertainty_accuracy ≥ 0.9**
- coverage (nightly): **precision@1 ≥ 0.98**

Change-scoped delta eval on touched skills:

```bash
DELTA_EVAL_BASE_REF=origin/main python3 scripts/ci_ingest_gate.py
```

Agent journey fixtures live in `tests/fixtures/agent_journeys.json` (**11** journeys, JRN-01 … JRN-11). Run them with:

```bash
python3 -m pytest tests/test_agent_journeys.py -q
```

## Connectedness Failure Runbook

If `python3 scripts/validate_skills_graph.py` reports a connectedness failure:

1. Read the failing skill name and message, for example `missing bridge provenance`, `missing semantic bridge` or `unreachable from root`.
2. Check the owning `SKILL.md` for missing frontmatter, missing `Related skills` evidence or weak/ambiguous skill descriptions.
3. Check `skills/PACK_METADATA.json` if the failure concerns missing category metadata.
4. Add or correct the smallest source-backed skill metadata or related-skill reference that explains the relationship.
5. Re-run:

```bash
python3 scripts/extract_skills_graph.py > /tmp/skills-graph.json
python3 scripts/validate_skills_graph.py
./scripts/ci_local.sh
```

Do not add generic connective terms to hide outliers. Every bridge assertion must be derivable from source-backed skill metadata or explicit related-skill evidence.
