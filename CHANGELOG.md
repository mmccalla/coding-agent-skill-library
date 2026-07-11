# Changelog

Release-level changes for the portable skills library and Skills KG service.

Detailed history: [`skills_docs/CHANGELOG.md`](skills_docs/CHANGELOG.md).

## v0.1.5 — 2026-07-11

- Purged `.cursor/` from git history; ignore `/.cursor` locally
- Track compressed `hero_image_2.jpg`; ignore large `hero_image_2.png` source asset
- Note: `v0.1.4` tag/release name was reserved by GitHub immutable-release rules, so this is the published successor

## v0.1.3 — 2026-07-08

- Tiered local gates: fast **pre-commit** (~5s), **pre-push** validators and parallel pytest, full suite in CI
- CI: parallel `library-validators`, `pytest -n auto` via `pytest-xdist`, slim pre-commit job
- DCO commit-msg hook, gitleaks, import-cycle validator, shared `run_library_validators.sh`
- MCP: canonical skill id resolution for bare slugs in `get_skill_execution_guide`

## v0.1.2 — 2026-07-08

- Renamed `avoid-cognitive-biases` → **`cognitive-bias-review`** and `avoid-fallacies` → **`logical-fallacy-review`** for clearer discovery and symmetric naming
- Old `avoid-*` IDs retained as **aliases until v0.2.0** (remove from eval smoke after that release)
- Added confuser pairs (bias↔fallacy, reflection, prioritisation, reasoning) and neighbour cross-links
- Eval corpora refreshed: realistic **62**, confuser pairs **38**

## v0.1.1 — 2026-07-07

- Documentation aligned to **113-skill** library and tiered eval corpora
- `avoid-cognitive-biases` and `avoid-fallacies` skills added; later renamed in v0.1.2 (see below)
- `scripts/` domain package layout; MCP legacy entrypoint shim
- Stale-path guards in `validate_docs.py`

## v0.1.0 — 2026-07-06

- Apache License 2.0 (`SPDX-License-Identifier: Apache-2.0`)
- Fast skills-kg MCP stdio startup (deterministic embeddings, background Ollama upgrade)
- Cursor-friendly MCP tool parameter schema
- 111-skill flat library with Neo4j GraphRAG service (MCP, API, UI) at initial public release
