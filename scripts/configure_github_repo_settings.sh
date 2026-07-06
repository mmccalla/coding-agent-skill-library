#!/usr/bin/env bash
# Align GitHub repository settings with docs/PUBLIC_REPO_READINESS.md.
# Usage: ./scripts/configure_github_repo_settings.sh [--check-only]
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

REPO="${GITHUB_REPOSITORY:-mmccalla/coding-agent-skill-library}"
CHECK_ONLY=false
if [[ "${1:-}" == "--check-only" ]]; then
  CHECK_ONLY=true
fi

require_cmd() {
  command -v "$1" >/dev/null 2>&1 || {
    echo "Missing required command: $1" >&2
    exit 1
  }
}

require_cmd gh
require_cmd python3

echo "==> Repository: ${REPO}"

if [[ "$CHECK_ONLY" == true ]]; then
  echo "==> Local hygiene files"
  python3 -m pytest -q tests/test_github_repo_hygiene.py

  echo "==> Secret scan (tracked files)"
  python3 scripts/pre_public_secret_scan.py

  echo "==> GitHub settings snapshot"
  gh api "repos/${REPO}" --jq '{
    visibility,
    is_template,
    has_wiki,
    has_discussions,
    has_projects,
    allow_squash_merge,
    allow_merge_commit,
    allow_rebase_merge,
    delete_branch_on_merge,
    web_commit_signoff_required
  }'
  gh api "repos/${REPO}/actions/permissions/workflow" --jq '.'
  gh api "repos/${REPO}/automated-security-fixes" --jq '.' || true
  echo "check-only complete"
  exit 0
fi

echo "==> Repository feature flags (template, merge, wiki, issues)"
gh repo edit "${REPO}" \
  --template \
  --enable-issues \
  --enable-squash-merge \
  --enable-merge-commit=false \
  --enable-rebase-merge=false \
  --delete-branch-on-merge \
  --enable-wiki=false \
  --enable-discussions=false \
  --enable-projects=false

echo "==> Dependabot vulnerability alerts"
gh api -X PUT "repos/${REPO}/vulnerability-alerts" || true

echo "==> Dependabot security updates"
gh api -X PUT "repos/${REPO}/automated-security-fixes" || true

echo "==> Actions workflow permissions (read-only token; no PR approval from Actions)"
gh api -X PUT "repos/${REPO}/actions/permissions/workflow" \
  --input - <<'EOF'
{
  "default_workflow_permissions": "read",
  "can_approve_pull_request_reviews": false
}
EOF

echo "==> Private vulnerability reporting"
gh api --method PATCH "repos/${REPO}" --input - <<'EOF' || true
{
  "security_and_analysis": {
    "private_vulnerability_reporting": {
      "status": "enabled"
    }
  }
}
EOF

VISIBILITY="$(gh api "repos/${REPO}" --jq '.visibility')"
if [[ "$VISIBILITY" == "public" ]]; then
  echo "==> Public repo: enabling secret scanning and push protection"
  gh repo edit "${REPO}" --enable-secret-scanning --enable-secret-scanning-push-protection || true

  echo "==> Branch protection for main"
  gh api --method PUT "repos/${REPO}/branches/main/protection" --input - <<'EOF'
{
  "required_status_checks": {
    "strict": true,
    "checks": [
      {"context": "markdownlint"},
      {"context": "ruff"},
      {"context": "mypy"},
      {"context": "pytest"},
      {"context": "pre-commit"}
    ]
  },
  "enforce_admins": false,
  "required_pull_request_reviews": {
    "dismiss_stale_reviews": true,
    "require_code_owner_reviews": true,
    "required_approving_review_count": 1
  },
  "restrictions": null,
  "required_linear_history": true,
  "allow_force_pushes": false,
  "allow_deletions": false
}
EOF
else
  echo "NOTE: Repository is ${VISIBILITY}. Secret scanning and branch protection apply when public."
  echo "      After visibility change, re-run this script."
fi

echo "configure_github_repo_settings: done"
