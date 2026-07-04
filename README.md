# Coding Agent Skills KG

Portable **111-skill** library for coding agents, plus an optional local **Neo4j GraphRAG** service (MCP, API, UI).

## Start here

| I want to… | Read |
| --- | --- |
| Use skills in my agent | `AGENTS.md` → `skills/apply-laws-of-ai/SKILL.md` → `skills_docs/HOW_TO_FIND_THE_RIGHT_SKILL.md` |
| Get running locally (Docker, MCP) | [`skills_docs/GETTING_STARTED.md`](skills_docs/GETTING_STARTED.md) |
| Configure Cursor (MCP vs filesystem) | [`skills_docs/CURSOR_IDE_SETUP.md`](skills_docs/CURSOR_IDE_SETUP.md) |
| Copy skills into another repo | `skills_docs/DROP_IN_BOOTSTRAP.md` |
| Operate or troubleshoot the KG | [`skills_docs/SKILLS_KG_MCP_RUNBOOK.md`](skills_docs/SKILLS_KG_MCP_RUNBOOK.md) |
| See KRAG status and roadmap | [`skills_docs/krag/STATUS.md`](skills_docs/krag/STATUS.md) |
| Measured retrieval quality | [`skills_docs/krag/EVALUATION.md`](skills_docs/krag/EVALUATION.md) |

## What is in this repo

```text
skills/           SKILL.md operating procedures (the portable product)
skills_docs/      Routing, runbooks, KRAG contracts and ontology
scripts/          Extract, validate, load, retrieve, MCP, API
skills-ui/        Inspection and agent-workflow UI
docker-compose.yml Neo4j, API, UI, Prometheus, Grafana
```

Agents: mandatory startup order is in `AGENTS.md` (safety files → `apply-laws-of-ai` → route → smallest `SKILL.md` set).

## Quick local stack

```bash
cp .env.example .env
docker compose up --build -d
```

- [UI](http://localhost:5173)
- [API](http://localhost:8000/docs)
- [Neo4j](http://localhost:7474)

## Validation

```bash
python3 -m pip install -e ".[dev]"
./scripts/install_git_hooks.sh   # pre-commit: secrets, markdownlint, validators, ruff, mypy, pytest
./scripts/ci_local.sh
```

Pre-commit runs automatically on `git commit` after hooks are installed. It selects checks from staged paths (skills, Python, docs, UI). Emergency bypass: `SKIP_PRECOMMIT=1 git commit ...` (use only when necessary).

## Portable copy set

For drop-in use without the KG service:

```text
AGENTS.md, CLAUDE.md, AGENTIC_CODING_GLOBAL_SAFETY.md, SECURE_AGENTIC_DEVELOPMENT.md
skills/
skills_docs/   (at minimum: LIBRARY_CONTRACT, HOW_TO_FIND, DROP_IN_BOOTSTRAP)
```

Details: `skills_docs/GETTING_STARTED.md` and `skills_docs/CHANGELOG.md`.
