#!/usr/bin/env bash
# Pre-commit gate: lint, validate, security-scan and test staged changes.
# Install with: ./scripts/dev_workflow/install_git_hooks.sh
# Bypass (emergency only): SKIP_PRECOMMIT=1 git commit ...
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT"

if [[ "${SKIP_PRECOMMIT:-}" == "1" ]]; then
  echo "WARNING: SKIP_PRECOMMIT=1 — pre-commit checks skipped." >&2
  exit 0
fi

export SKILLS_EMBEDDING_PROVIDER="${SKILLS_EMBEDDING_PROVIDER:-deterministic}"
PYTEST_QUALITY_MARKER='not live_neo4j and not slow and not eval_pr'

STAGED=()
while IFS= read -r line; do
  [[ -n "$line" ]] && STAGED+=("$line")
done < <(git diff --cached --name-only --diff-filter=ACMR || true)

if [[ ${#STAGED[@]} -eq 0 ]]; then
  echo "pre-commit: no staged files."
  exit 0
fi

has_prefix() {
  local prefix="$1"
  local f
  for f in "${STAGED[@]}"; do
    case "$f" in
      ${prefix}*) return 0 ;;
    esac
  done
  return 1
}

has_exact() {
  local name="$1"
  local f
  for f in "${STAGED[@]}"; do
    [[ "$f" == "$name" ]] && return 0
  done
  return 1
}

staged_md=()
staged_skills=()
for f in "${STAGED[@]}"; do
  case "$f" in
    *.md) staged_md+=("$f") ;;
  esac
  case "$f" in
    skills/*/SKILL.md) staged_skills+=("$f") ;;
  esac
done

run_python=false
run_skills=false
run_docs=false
run_corpus=false
run_ui=false

if has_prefix "scripts/" || has_prefix "tests/" || has_exact "pyproject.toml"; then
  run_python=true
fi
if has_prefix "skills/"; then
  run_skills=true
fi
if has_prefix "skills_docs/" || has_exact "AGENTS.md" || has_exact "CLAUDE.md" \
  || has_exact "AGENTIC_CODING_GLOBAL_SAFETY.md" || has_exact "SECURE_AGENTIC_DEVELOPMENT.md" \
  || has_exact ".markdownlint-cli2.jsonc"; then
  run_docs=true
fi
if has_prefix "skills/" || has_prefix "tests/fixtures/retrieval_evaluation/" \
  || has_exact "scripts/lib/retrieval/generate_golden_queries.py" || has_exact "scripts/validators/validate_eval_corpus.py"; then
  run_corpus=true
fi
if has_prefix "skills-ui/"; then
  run_ui=true
fi

echo "==> secret scan (staged files)"
python3 - <<'PY'
from __future__ import annotations

import re
import subprocess
import sys

patterns = [
    (re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH |DSA )?PRIVATE KEY-----"), "private-key"),
    (re.compile(r"AKIA[0-9A-Z]{16}"), "aws-access-key-id"),
    (re.compile(r"(?i)api[_-]?key\s*[:=]\s*['\"][A-Za-z0-9_\-]{20,}"), "api-key-assignment"),
    (re.compile(r"(?i)secret\s*[:=]\s*['\"][^'\"]{12,}"), "secret-assignment"),
    (re.compile(r"ghp_[A-Za-z0-9]{36}"), "github-pat"),
    (re.compile(r"xox[baprs]-[A-Za-z0-9-]{10,}"), "slack-token"),
]

allow_prefixes = (
    "tests/fixtures/skill_trust/malicious/",
)

proc = subprocess.run(
    ["git", "diff", "--cached", "--name-only", "--diff-filter=ACMR"],
    check=True,
    capture_output=True,
    text=True,
)
files = [line.strip() for line in proc.stdout.splitlines() if line.strip()]
failures: list[str] = []
for path in files:
    if path.startswith(allow_prefixes):
        continue
    show = subprocess.run(
        ["git", "show", f":{path}"],
        check=False,
        capture_output=True,
        text=True,
    )
    if show.returncode != 0:
        continue
    content = show.stdout
    for pattern, name in patterns:
        if pattern.search(content):
            failures.append(f"{path}: possible {name}")

if failures:
    print("Secret scan failed:", file=sys.stderr)
    for item in failures:
        print(f"  - {item}", file=sys.stderr)
    sys.exit(1)
print("secret scan passed")
PY

if [[ ${#staged_md[@]} -gt 0 ]]; then
  echo "==> markdownlint (staged markdown)"
  if command -v npx >/dev/null 2>&1; then
    npx --yes markdownlint-cli2 "${staged_md[@]}"
  else
    echo "WARNING: npx not found; markdownlint skipped" >&2
  fi
fi

if [[ "$run_docs" == true ]] || [[ "$run_skills" == true ]]; then
  echo "==> validate_docs.py"
  python3 scripts/validators/validate_docs.py
fi

if [[ "$run_skills" == true ]]; then
  echo "==> validate_skills.py"
  python3 scripts/validators/validate_skills.py

  echo "==> validate_skill_practice.py --all"
  python3 scripts/validators/validate_skill_practice.py --all

  echo "==> validate_skills_graph.py"
  python3 scripts/validators/validate_skills_graph.py

  if [[ ${#staged_skills[@]} -gt 0 ]]; then
    echo "==> validate_skill_trust.py --ci-gate (staged skills)"
    python3 scripts/validators/validate_skill_trust.py --ci-gate "${staged_skills[@]}"
  fi
fi

if [[ "$run_corpus" == true ]]; then
  echo "==> validate_eval_corpus.py --check-skill-sync"
  python3 scripts/validators/validate_eval_corpus.py --check-skill-sync
fi

if [[ "$run_python" == true ]]; then
  echo "==> ruff check"
  python3 -m ruff check scripts tests

  echo "==> ruff format --check"
  python3 -m ruff format --check scripts tests

  echo "==> mypy"
  python3 -m mypy

  if python3 -c "import bandit" >/dev/null 2>&1; then
    echo "==> bandit (scripts)"
    python3 -m bandit -q -r scripts -x 'scripts/apply_phase*.py' -ll
  else
    echo "==> bandit skipped (not installed; optional: pip install '.[dev]' with bandit)"
  fi

  echo "==> pytest (quality tier)"
  python3 -m pytest -q --cov=scripts --cov-report=term-missing -m "${PYTEST_QUALITY_MARKER}"
fi

if [[ "$run_ui" == true ]]; then
  echo "==> skills-ui lint/test"
  npm --prefix skills-ui run lint
  npm --prefix skills-ui test -- --no-file-parallelism --maxWorkers=1
fi

echo "pre-commit checks passed."
