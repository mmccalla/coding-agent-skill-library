#!/usr/bin/env bash
# Local CI orchestrator — mirrors .github/workflows/validate-skills.yml job tiers.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

# PR CI always uses deterministic embeddings; production uses BGE-M3 via Ollama.
export SKILLS_EMBEDDING_PROVIDER="${SKILLS_EMBEDDING_PROVIDER:-deterministic}"

PYTEST_QUALITY_MARKER='not live_neo4j and not slow and not eval_pr'

run_quality() {
  echo "==> validate_docs.py"
  python3 scripts/validate_docs.py

  echo "==> validate_skills.py"
  python3 scripts/validate_skills.py

  echo "==> validate_skills_graph.py"
  python3 scripts/validate_skills_graph.py

  echo "==> validate_eval_corpus.py"
  python3 scripts/validate_eval_corpus.py --check-skill-sync

  echo "==> ruff check"
  python3 -m ruff check scripts tests

  echo "==> ruff format"
  python3 -m ruff format --check scripts tests

  echo "==> mypy"
  python3 -m mypy

  echo "==> pytest (quality tier)"
  python3 -m pytest --cov=scripts --cov-report=term-missing -m "${PYTEST_QUALITY_MARKER}"

  echo "==> offline KG/MCP smoke"
  python3 scripts/embed_skill_chunks.py --query "approval before destructive command" --limit 1 >/dev/null
  python3 scripts/retrieve_skills_hybrid.py "graph rag ontology retrieval" --limit 1 >/dev/null
  python3 scripts/skills_mcp_server.py --list-tools >/dev/null

  echo "==> skill count"
  count="$(find skills -name 'SKILL.md' | wc -l | tr -d ' ')"
  if [ "$count" -lt 1 ]; then
    echo "expected at least one SKILL.md file, found $count" >&2
    exit 1
  fi
  echo "discovered $count SKILL.md files"
}

run_ingest_gate() {
  echo "==> ci_ingest_gate.py"
  python3 scripts/ci_ingest_gate.py
}

run_eval_pr() {
  echo "==> pytest (eval_pr tier)"
  python3 -m pytest -m eval_pr -q
}

run_skills_ui() {
  echo "==> skills-ui checks"
  npm --prefix skills-ui ci
  npm --prefix skills-ui test
  npm --prefix skills-ui run lint
  npm --prefix skills-ui run build
}

run_neo4j_integration() {
  if ! [[ "${NEO4J_URI:-}" && "${NEO4J_USER:-}" && "${NEO4J_PASSWORD:-}" ]]; then
    echo "==> neo4j integration skipped (NEO4J_* not configured)"
    return 0
  fi
  echo "==> pytest (live_neo4j tier)"
  python3 -m pytest tests/test_live_neo4j_integration.py -q
}

run_nightly_eval() {
  echo "==> pytest (slow tier)"
  python3 -m pytest -m slow -q
}

case "${1:-all}" in
  quality)
    run_quality
    ;;
  ingest-gate)
    run_ingest_gate
    ;;
  eval-pr)
    run_eval_pr
    ;;
  skills-ui)
    run_skills_ui
    ;;
  neo4j)
    run_neo4j_integration
    ;;
  nightly)
    run_nightly_eval
    ;;
  all)
    run_quality
    run_ingest_gate
    run_eval_pr
    run_skills_ui
    run_neo4j_integration
    ;;
  *)
    echo "usage: $0 [quality|ingest-gate|eval-pr|skills-ui|neo4j|nightly|all]" >&2
    exit 1
    ;;
esac

echo "CI local checks passed (${1:-all})."
