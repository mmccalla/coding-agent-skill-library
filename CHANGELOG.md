# Changelog

Release-level changes for the portable skills library and Skills KG service.

Detailed history: [`skills_docs/CHANGELOG.md`](skills_docs/CHANGELOG.md).

## v0.1.11 — 2026-07-23

- L3 discovery promote: aliases and description triggers for hold-out soft misses (ADR, CI, review, threat, UX/a11y, incident/obs, ontology, supply-chain, guardrails/HITL, event-driven, and related)
- Vague-filler OOD abstention in hybrid retrieval (queries with only filler tokens abstain even with strong vector scores)
- Paired live evidence vs `main` @ v0.1.10: hold-out B1 soft 0.875 → 1.000; Δ vs B2-lex +0.083 → +0.167; OOD empty 1.0 / false_hit 0; does **not** claim beats live Cursor IDE activation
- Expand gitignore for local L3/Arm-B/pair experiment harnesses and design write-ups

## v0.1.10 — 2026-07-22

- P1-RAG discovery surfaces: enrich `knowledge-retrieval-rag` and `evaluation-and-monitoring` metadata; narrow `krag-evaluation-governance` to KRAG/GraphRAG-scoped language
- Improves natural hold-out soft_hit on `multi_rag_eval` without changing hybrid weights or abstention gates
- Gitignore local retrieval experiment harnesses and `skills_docs/krag/experiments/` write-ups

## v0.1.9 — 2026-07-22

- Remove hybrid body-text scoring channel (NOTEXT); rank with metadata, vector, graph, and bridge only
- Promote OOD-safe hybrid defaults from MV70 evidence: `metadata=0.70`, `vector=0.25`, `min_top1_margin=0.01` (`graph=0.15`, `bridge=0.60`, `min_confident_score=0.35` unchanged)
- Keep BGE-M3 as the production embedding provider; deterministic remains CI-only

## v0.1.8 — 2026-07-15

- Lean MCP/API wire payloads: omit fat `selection_trace` from `recommend_skills` and `route_skill_query`; keep full audit traces in `skills_usage` logs correlated by `usage.selection_run_id`
- Dedupe `recommend_skills` evidence fields on the wire (anchors + snippets + source paths; `section_ids` / graph `evidence_paths` audit-only)
- Omit execution-guide graph `evidence_paths` from the wire while keeping non-empty evidence anchors and `related_skill_ids`
- Hybrid ranking and route classification unchanged (verified live Cursor MCP + e2e A/B vs main)

## v0.1.7 — 2026-07-11

- Add project-specific `.cursorignore` (secrets, Docker volumes, caches, UI build trees, large assets)

## v0.1.6 — 2026-07-11

- Purged `.cursor/` from git history; ignore `/.cursor` locally
- Track compressed `hero_image_2.jpg`; ignore large `hero_image_2.png` source asset
- Note: `v0.1.3`–`v0.1.5` tag names are reserved by GitHub immutable-release rules, so **v0.1.6** is the published successor after the history purge

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
