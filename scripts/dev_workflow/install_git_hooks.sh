#!/usr/bin/env bash
# Install repository git hooks (pre-commit, commit-msg, pre-push).
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT"

chmod +x \
  scripts/dev_workflow/pre_commit_check.sh \
  scripts/dev_workflow/pre_push_check.sh \
  scripts/dev_workflow/run_library_validators.sh \
  scripts/dev_workflow/check_commit_dco.py \
  .githooks/pre-commit \
  .githooks/commit-msg \
  .githooks/pre-push

git config core.hooksPath .githooks

echo "Installing pre-commit hook environments..."
python3 -m pre_commit install-hooks

echo "Installed git hooks from .githooks/ (core.hooksPath)."
echo "Pre-commit: fast staged checks (hygiene, gitleaks, ruff, markdownlint, staged skill trust)."
echo "Commit-msg: DCO Signed-off-by (git commit -s)."
echo "Pre-push: library validators, skills-ui, mypy + parallel pytest when Python paths changed."
echo "Emergency bypass: SKIP_PRECOMMIT=1 git commit ... | SKIP_PREPUSH=1 git push ..."
