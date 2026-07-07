# Changelog

Release-level changes for the portable skills library and Skills KG service.

Detailed history: [`skills_docs/CHANGELOG.md`](skills_docs/CHANGELOG.md).

## v0.1.1 — 2026-07-07

- Documentation aligned to **113-skill** library and tiered eval corpora
- `avoid-cognitive-biases` and `avoid-fallacies` skills; MCP journeys JRN-12, JRN-13
- `scripts/` domain package layout; MCP legacy entrypoint shim
- Stale-path guards in `validate_docs.py`

## v0.1.0 — 2026-07-06

- Apache License 2.0 (`SPDX-License-Identifier: Apache-2.0`)
- Fast skills-kg MCP stdio startup (deterministic embeddings, background Ollama upgrade)
- Cursor-friendly MCP tool parameter schema
- 111-skill flat library with Neo4j GraphRAG service (MCP, API, UI) at initial public release
