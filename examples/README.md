# Examples

## Use the skills library in an agent

1. Read [`skills/apply-laws-of-ai/SKILL.md`](../skills/apply-laws-of-ai/SKILL.md).
2. Route with [`skills_docs/HOW_TO_FIND_THE_RIGHT_SKILL.md`](../skills_docs/HOW_TO_FIND_THE_RIGHT_SKILL.md).
3. Copy the portable set from [`skills_docs/DROP_IN_BOOTSTRAP.md`](../skills_docs/DROP_IN_BOOTSTRAP.md).

## Run the Skills KG stack locally

```bash
cp .env.example .env
docker compose up --build -d
```

See [`skills_docs/GETTING_STARTED.md`](../skills_docs/GETTING_STARTED.md) and [`skills_docs/CURSOR_IDE_SETUP.md`](../skills_docs/CURSOR_IDE_SETUP.md).

## Retrieval and MCP fixtures

| Example | Path |
| --- | --- |
| Agent journey fixtures | [`tests/fixtures/agent_journeys.json`](../tests/fixtures/agent_journeys.json) |
| Smoke / realistic eval queries | [`tests/fixtures/retrieval_evaluation/`](../tests/fixtures/retrieval_evaluation/) |
| MCP server smoke | `python3 scripts/runtime/mcp/skills_mcp_server.py --list-tools` |
