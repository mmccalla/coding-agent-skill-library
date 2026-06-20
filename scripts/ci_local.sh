#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

echo "==> validate_skills.py"
python3 scripts/validate_skills.py

echo "==> validate_skills_graph.py"
python3 scripts/validate_skills_graph.py

echo "==> unittest"
python3 -m unittest discover -s tests -p 'test_*.py' -q

echo "==> offline KG/MCP smoke"
python3 scripts/embed_skill_chunks.py --query "approval before destructive command" --limit 1 >/dev/null
python3 scripts/retrieve_skills_hybrid.py "graph rag ontology retrieval" --limit 1 >/dev/null
python3 scripts/skills_mcp_server.py --list-tools >/dev/null

echo "==> skill count"
count="$(find skills -name 'SKILL.md' | wc -l | tr -d ' ')"
if [ "$count" != "87" ]; then
  echo "expected 87 SKILL.md files, found $count" >&2
  exit 1
fi

echo "CI local checks passed."
