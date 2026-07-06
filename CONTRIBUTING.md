# Contributing

Thank you for improving the coding-agent skills library and Skills KG service.

## Before you start

1. Read [`AGENTS.md`](AGENTS.md) and [`skills/apply-laws-of-ai/SKILL.md`](skills/apply-laws-of-ai/SKILL.md).
2. For skills changes, read [`skills_docs/SKILL_AUTHORING_GUIDE.md`](skills_docs/SKILL_AUTHORING_GUIDE.md).
3. For KG/MCP changes, read [`skills_docs/SKILLS_KG_MCP_RUNBOOK.md`](skills_docs/SKILLS_KG_MCP_RUNBOOK.md).

## Development setup

```bash
python3 -m pip install -e ".[dev]"
./scripts/install_git_hooks.sh    # or: pre-commit install
./scripts/ci_local.sh             # mirrors CI tiers locally
```

Set `SKILLS_EMBEDDING_PROVIDER=deterministic` for offline CI-parity work.

## Pull requests

1. Branch from `main`.
2. Keep changes small and testable.
3. Run `./scripts/ci_local.sh` (or the relevant subset) before opening a PR.
4. Fill out the pull request template.
5. Ensure required CI checks pass: `markdownlint`, `ruff`, `mypy`, `pytest`, `pre-commit`.

## Commit hygiene

- Pre-commit runs on `git commit` (secrets scan, validators, lint, tests for touched paths).
- Emergency bypass only: `SKIP_PRECOMMIT=1 git commit ...`
- Do not commit secrets, credentials, or local-only archive content under `skills_docs/archive/`.

## Code of conduct

This project follows the [Contributor Covenant](CODE_OF_CONDUCT.md). Report unacceptable behaviour to the repository owner.

## Licence

By contributing, you agree that your contributions are licensed under the [Apache License 2.0](LICENSE) (`SPDX-License-Identifier: Apache-2.0`).
