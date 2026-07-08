#!/usr/bin/env bash
# Pre-push gate: library validators (pre-push hook stage) + Python quality when needed.
# Install with: ./scripts/dev_workflow/install_git_hooks.sh
# Bypass (emergency only): SKIP_PREPUSH=1 git push ...
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT"

if [[ "${SKIP_PREPUSH:-}" == "1" ]]; then
  echo "WARNING: SKIP_PREPUSH=1 — pre-push checks skipped." >&2
  exit 0
fi

export SKILLS_EMBEDDING_PROVIDER="${SKILLS_EMBEDDING_PROVIDER:-deterministic}"
PYTEST_QUALITY_MARKER='not live_neo4j and not slow and not eval_pr'

remote_name="${1:-}"
range=""
if [[ -n "$remote_name" ]]; then
  branch="$(git rev-parse --abbrev-ref HEAD)"
  if git rev-parse --verify "${remote_name}/${branch}" >/dev/null 2>&1; then
    range="${remote_name}/${branch}..HEAD"
  fi
fi

changed_paths=()
if [[ -n "$range" ]]; then
  while IFS= read -r path; do
    [[ -n "$path" ]] && changed_paths+=("$path")
  done < <(git diff --name-only "$range" || true)
else
  while IFS= read -r path; do
    [[ -n "$path" ]] && changed_paths+=("$path")
  done < <(git diff --name-only HEAD~1..HEAD 2>/dev/null || true)
fi

needs_python=false
for path in "${changed_paths[@]}"; do
  case "$path" in
    scripts/* | tests/* | pyproject.toml) needs_python=true; break ;;
  esac
done

pre_push_args=(--hook-stage pre-push)
if [[ -n "$range" ]]; then
  from_ref="${range%..HEAD}"
  pre_push_args+=(--from-ref "$from_ref" --to-ref HEAD)
fi

echo "==> pre-push hook stage (library validators, skills-ui)"
python3 -m pre_commit run "${pre_push_args[@]}"

if [[ "$needs_python" != true ]]; then
  echo "pre-push: no scripts/tests/pyproject.toml changes; skipping mypy/pytest."
  exit 0
fi

echo "==> mypy (pre-push)"
python3 -m mypy

echo "==> pytest (pre-push quality tier, parallel, no coverage)"
python3 -m pytest -q -n auto -m "${PYTEST_QUALITY_MARKER}" --no-cov

echo "pre-push checks passed."
