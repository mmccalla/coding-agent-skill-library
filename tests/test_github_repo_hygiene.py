"""Guardrails for public-repository hygiene files."""

from __future__ import annotations

import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]

REQUIRED_PATHS = (
    "README.md",
    "LICENSE",
    "NOTICE",
    "CONTRIBUTING.md",
    "CODE_OF_CONDUCT.md",
    "SECURITY.md",
    "CHANGELOG.md",
    ".pre-commit-config.yaml",
    ".github/CODEOWNERS",
    ".github/pull_request_template.md",
    ".github/ISSUE_TEMPLATE/bug_report.yml",
    ".github/ISSUE_TEMPLATE/feature_request.yml",
    ".github/dependabot.yml",
    ".github/workflows/ci.yml",
    ".github/workflows/codeql.yml",
)


class GithubRepoHygieneTests(unittest.TestCase):
    def test_required_public_repo_files_exist(self) -> None:
        missing = [path for path in REQUIRED_PATHS if not (REPO_ROOT / path).is_file()]
        self.assertEqual([], missing, msg=f"Missing hygiene files: {missing}")

    def test_ci_workflow_declares_required_check_jobs(self) -> None:
        ci = (REPO_ROOT / ".github/workflows/ci.yml").read_text(encoding="utf-8")
        for job in ("markdownlint", "ruff", "mypy", "pytest", "pre-commit"):
            self.assertIn(f"name: {job}", ci, msg=f"CI job {job!r} not found")


if __name__ == "__main__":
    unittest.main()
