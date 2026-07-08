#!/usr/bin/env bash
# Pre-commit gate: fast commit-stage hooks only (.pre-commit-config.yaml).
# Heavier library validators and pytest run on pre-push; full suite in CI.
# Install with: ./scripts/dev_workflow/install_git_hooks.sh
# Bypass (emergency only): SKIP_PRECOMMIT=1 git commit ...
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT"

if [[ "${SKIP_PRECOMMIT:-}" == "1" ]]; then
  echo "WARNING: SKIP_PRECOMMIT=1 — pre-commit checks skipped." >&2
  exit 0
fi

exec python3 -m pre_commit run "$@"
