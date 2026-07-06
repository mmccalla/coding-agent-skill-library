#!/usr/bin/env bash
# Install repository git hooks (pre-commit lint/test/security gate).
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT"

chmod +x scripts/dev_workflow/pre_commit_check.sh .githooks/pre-commit
git config core.hooksPath .githooks

echo "Installed git hooks from .githooks/ (core.hooksPath)."
echo "Pre-commit runs: secret scan, markdownlint, validators, ruff, mypy, pytest (as needed)."
echo "Optional framework hook: pre-commit install  # uses .pre-commit-config.yaml"
echo "Emergency bypass: SKIP_PRECOMMIT=1 git commit ..."
