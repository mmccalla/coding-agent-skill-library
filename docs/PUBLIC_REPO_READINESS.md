# Public repository readiness

Use this checklist before changing visibility to **public**, or to verify readiness after visibility changes.

## Repository settings (GitHub)

| Setting | Target | Apply |
| --- | --- | --- |
| Visibility | Public only after review | Manual: Settings → General → Change visibility |
| Licence | Apache-2.0 | `LICENSE`, `NOTICE`, `pyproject.toml` |
| Template repository | On | Settings → General → Template repository |
| Issues | On | Configured |
| Discussions | Off initially | Configured |
| Wiki | Off | Configured |
| Projects | Off initially | Configured |
| Pull requests | On, all users | Default for public repos |
| Merge strategy | Squash only | Configured |
| Auto-delete head branches | On | Configured |
| DCO / sign-off | On | `web_commit_signoff_required`; see `CONTRIBUTING.md` |
| Release immutability | On before publishing releases | Settings → General → Releases |
| Branch protection / ruleset | Required PR, 1 approval, CI checks, no force push | **Requires public repo or GitHub Pro** — apply after visibility change |
| Secret scanning + push protection | On | **Free when public** — Settings → Code security |
| CodeQL | On | `.github/workflows/codeql.yml` |
| Dependabot alerts + security updates | On | Settings → Code security and analysis |
| Actions token | Read-only default | Settings → Actions → General |
| First-time contributor workflow approval | On | Settings → Actions → General |

Required CI contexts for branch protection: `markdownlint`, `ruff`, `mypy`, `pytest`, `pre-commit`.

## Files and layout

| Item | Location |
| --- | --- |
| README, licence, governance | Repository root |
| Skills library | `skills/` |
| Documentation | `skills_docs/` and `docs/` |
| Schemas / ontology | `schemas/` → `skills_docs/ontology/`, `neo4j/` |
| Examples | `examples/` → fixtures and runbooks |
| Tests | `tests/` |
| CI | `.github/workflows/ci.yml` |

## Pre-publication checks

Run locally:

```bash
./scripts/ci_local.sh
python3 -m pytest -q tests/test_github_repo_hygiene.py
```

| Check | Required |
| --- | --- |
| GitHub secret scanning + push protection | Yes — enable in repository settings |
| Review commit history for confidential material | Yes — manual |
| CI green on `main` | Yes |
| No local-only archive paths committed | Yes — `skills_docs/archive/*` is gitignored |
| First release tagged (optional) | Recommended — see `CHANGELOG.md` |

## Support model

This is an open **skills library** and optional **Skills KG** reference implementation. Issues and pull requests are welcome; there is no SLA. Security reports use [private vulnerability reporting](../SECURITY.md) when enabled.
