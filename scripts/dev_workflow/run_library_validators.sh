#!/usr/bin/env bash
# Run skills/docs library validators (pre-push tier and CI library-validators job).
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT"

run_docs=false
run_skills=false
run_graph=false
run_corpus=false
run_ontology=false
run_practice=false
run_trust=false

if [[ $# -eq 0 ]]; then
  run_docs=true
  run_skills=true
  run_graph=true
  run_corpus=true
  run_ontology=true
  run_practice=true
  run_trust=true
else
  for arg in "$@"; do
    case "$arg" in
      --docs-only) run_docs=true ;;
      --skills-only) run_skills=true; run_practice=true ;;
      --graph-only) run_graph=true ;;
      --corpus-only) run_corpus=true ;;
      --ontology-only) run_ontology=true ;;
      --practice-only) run_practice=true ;;
      --trust-only) run_trust=true ;;
      --all)
        run_docs=true
        run_skills=true
        run_graph=true
        run_corpus=true
        run_ontology=true
        run_practice=true
        run_trust=true
        ;;
      *)
        echo "usage: $0 [--all|--docs-only|--skills-only|--graph-only|--corpus-only|--ontology-only|--practice-only|--trust-only]" >&2
        exit 1
        ;;
    esac
  done
fi

if [[ "$run_docs" == true ]]; then
  echo "==> validate_docs.py"
  python3 scripts/validators/validate_docs.py
fi

if [[ "$run_skills" == true ]]; then
  echo "==> validate_skills.py"
  python3 scripts/validators/validate_skills.py
fi

if [[ "$run_practice" == true ]]; then
  echo "==> validate_skill_practice.py --all"
  python3 scripts/validators/validate_skill_practice.py --all
fi

if [[ "$run_graph" == true ]]; then
  echo "==> validate_skills_graph.py"
  python3 scripts/validators/validate_skills_graph.py
fi

if [[ "$run_corpus" == true ]]; then
  echo "==> validate_eval_corpus.py --check-skill-sync"
  python3 scripts/validators/validate_eval_corpus.py --check-skill-sync
fi

if [[ "$run_ontology" == true ]]; then
  echo "==> validate_skills_ontology.py"
  python3 scripts/validators/validate_skills_ontology.py
fi

if [[ "$run_trust" == true ]]; then
  echo "==> validate_skill_trust.py --ci-gate --skills-root skills"
  python3 scripts/validators/validate_skill_trust.py --ci-gate --skills-root skills
fi

echo "library validators passed."
