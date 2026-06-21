#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

echo "==> validate_skills.py"
python3 scripts/validate_skills.py

echo "==> validate_skills_graph.py"
python3 scripts/validate_skills_graph.py

echo "==> ruff check"
python3 -m ruff check scripts tests

echo "==> ruff format"
python3 -m ruff format --check scripts tests

echo "==> mypy"
python3 -m mypy

echo "==> pytest"
python3 -m pytest --cov=scripts --cov-report=term-missing

echo "==> offline KG/MCP smoke"
python3 scripts/embed_skill_chunks.py --query "approval before destructive command" --limit 1 >/dev/null
python3 scripts/retrieve_skills_hybrid.py "graph rag ontology retrieval" --limit 1 >/dev/null
python3 scripts/skills_mcp_server.py --list-tools >/dev/null

echo "==> retrieval evaluation"
python3 scripts/evaluate_skill_retrieval.py --limit 3 >/dev/null

echo "==> skills-ui checks"
npm --prefix skills-ui ci
npm --prefix skills-ui test
npm --prefix skills-ui run lint
npm --prefix skills-ui run build

echo "==> skill count"
count="$(find skills -name 'SKILL.md' | wc -l | tr -d ' ')"
if [ "$count" != "87" ]; then
  echo "expected 87 SKILL.md files, found $count" >&2
  exit 1
fi

echo "CI local checks passed."
