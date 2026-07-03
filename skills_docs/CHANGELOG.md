# Changelog

Release-level changes to the portable skills library and Skills KG service.

## 2026-07-03

### Skills KG

- Full-library promotion: **91/91** skills promoted; quarantine cleared via Procedure sections and intent registry.
- Golden evaluation corpus regenerated: **1,194** cases with `promotion_tier=release`.
- CI ingest gate (`ci_ingest_gate.py`) wired into `ci_local.sh`.
- Usage and trust metrics on `GET /metrics`; Grafana `Skills KG Usage` dashboard.
- E2E evaluation report consolidated to `krag/EVALUATION.md`.
- Docker loader fix: nested Neo4j property sanitisation.

### Documentation

- Documentation consolidation started: `GETTING_STARTED.md`, `krag/STATUS.md`, updated doc hubs (Waves A–D).
- Waves A–D: consolidated `krag/` docs, archived planning/backlog, added `validate_docs.py` CI gate.

## Earlier

- KRAG v2 cutover: ontology-backed hybrid retrieval, read-only MCP, FastAPI + UI stack.
- Mandatory `apply-laws-of-ai` baseline; flat **91-skill** library with nine semantic categories.
