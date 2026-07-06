# Getting Started

Choose the path that matches your goal. You do not need to read KRAG design docs to use this repository.

## Use skills in an agent

This repository defaults to **skills-kg MCP** in Cursor. Full setup for MCP-only or filesystem-only modes: [`CURSOR_IDE_SETUP.md`](CURSOR_IDE_SETUP.md). For portable filesystem routing in other tools or repositories, use:

1. Read `AGENTS.md` (or `CLAUDE.md` for the short mirror).
2. Read `AGENTIC_CODING_GLOBAL_SAFETY.md` and `SECURE_AGENTIC_DEVELOPMENT.md`.
3. Execute `skills/apply-laws-of-ai/SKILL.md` in full.
4. Route with `skills_docs/HOW_TO_FIND_THE_RIGHT_SKILL.md`.
5. Load the smallest matching `skills/<name>/SKILL.md`.

To copy only the portable library into another repository, see `DROP_IN_BOOTSTRAP.md`.

## Run the Skills KG service locally

### Quick start (Docker)

```bash
cp .env.example .env   # set local passwords — do not commit .env
docker compose up --build -d
```

Service URLs:

| Service | URL |
| --- | --- |
| UI | <http://localhost:5173> |
| API + OpenAPI | <http://localhost:8000/docs> |
| Neo4j Browser | <http://localhost:7474> |
| Grafana | <http://localhost:3000> |

Health checks:

```bash
curl -fsS http://localhost:8000/health/ready
curl -fsS http://localhost:8000/metrics
```

See `SECURITY_HARDENING.md` for Docker credential and network guidance.

### Connect Cursor (MCP)

Read-only stdio server:

```bash
uv run --no-project \
  --directory /path/to/coding-agent-skill-library \
  --with-editable /path/to/coding-agent-skill-library \
  python scripts/skills_mcp_server.py --sdk-stdio
```

List tools:

```bash
python3 scripts/skills_mcp_server.py --list-tools
```

Cursor `mcpServers` entry (replace paths):

```json
{
  "mcpServers": {
    "skills-kg": {
      "command": "/path/to/uv",
      "args": [
        "run", "--no-project",
        "--directory", "/path/to/coding-agent-skill-library",
        "--with-editable", "/path/to/coding-agent-skill-library",
        "python", "scripts/skills_mcp_server.py", "--sdk-stdio"
      ]
    }
  }
}
```

MCP exposes **read-only** skill tools. Agents cannot ingest or write skills through MCP.

Cursor IDE configuration (MCP-only vs filesystem-only): [`CURSOR_IDE_SETUP.md`](CURSOR_IDE_SETUP.md).

### Validate your setup

```bash
python3 -m pip install -e ".[dev]"
./scripts/ci_local.sh
```

Targeted smoke:

```bash
python3 scripts/skills_mcp_server.py --list-tools
python3 scripts/evaluate_skill_retrieval.py --limit 3
```

Full operator workflow: `SKILLS_KG_MCP_RUNBOOK.md`.

## Write or change a skill

1. Read `SKILL_AUTHORING_GUIDE.md` and `LIBRARY_CONTRACT.md`.
2. Install git hooks once: `./scripts/install_git_hooks.sh`.
3. Edit `skills/<skill-name>/SKILL.md` (and inventory/docs as needed).
4. Commit — pre-commit runs secret scan, markdownlint, skill validators, ruff, mypy and quality pytest for relevant staged paths.
5. For a full local CI mirror, run `./scripts/ci_local.sh`.

Pre-commit entrypoint: `scripts/pre_commit_check.sh` (via `.githooks/pre-commit`). Bypass only in emergencies with `SKIP_PRECOMMIT=1`.

Skill changes also pass the ingest gate (`scripts/ci_ingest_gate.py`) inside `ci_local.sh`: L2 security, graph connectivity, SHACL, promoted smoke retrieval and dry-run Neo4j load.

## Maintain KRAG (ontology, eval, roadmap)

| Document | Purpose |
| --- | --- |
| `krag/STATUS.md` | Done, in progress, and to-do (single roadmap) |
| `krag/README.md` | Short KRAG overview |
| `krag/CONTRACTS.md` | Ingest, runtime, trust, eval gates |
| `krag/ONTOLOGY.md` | Semantic model narrative |
| `krag/EVALUATION.md` | Measured retrieval quality |
| `ontology/skills.ttl` | Canonical ontology source |
| `SKILLS_KG_MCP_RUNBOOK.md` | Rebuild, load, troubleshoot |
