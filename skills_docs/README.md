# Skills Docs

Documentation for agents and humans. Pick one path — you do not need every file.

## Choose your path

| Goal | Start here |
| --- | --- |
| **Use skills in an agent** | `HOW_TO_FIND_THE_RIGHT_SKILL.md` (after `apply-laws-of-ai`) — Path A MCP or Path B filesystem |
| **Configure Cursor (MCP vs filesystem)** | `CURSOR_IDE_SETUP.md` |
| **Copy the library to another repo** | `GETTING_STARTED.md` → `DROP_IN_BOOTSTRAP.md` |
| **Run MCP / Docker / Neo4j locally** | `GETTING_STARTED.md` → `SKILLS_KG_MCP_RUNBOOK.md` |
| **Write or change skills** | `SKILL_AUTHORING_GUIDE.md` |
| **Domain gap-close backlog** | `GAP_CLOSE_BACKLOG.md` |
| **KRAG roadmap and status** | `krag/STATUS.md` |
| **Measured retrieval quality** | `krag/EVALUATION.md` |

## Portable library (always relevant)

1. `LIBRARY_CONTRACT.md` — mandatory startup order and portable rules
2. `HOW_TO_FIND_THE_RIGHT_SKILL.md` — route by task shape (MCP and filesystem)
3. `SKILL_AUTHORING_GUIDE.md` — authoring standards
4. `DROP_IN_BOOTSTRAP.md` — drop-in install model
5. `CHANGELOG.md` — release-level changes
6. `../skills/README.md` and `../skills/MANIFEST.md` — inventory

## KRAG service

- `krag/README.md` — short KRAG overview
- `krag/STATUS.md` — done, in progress, to-do
- `krag/CONTRACTS.md` — ingest, runtime, trust, eval gates
- `krag/ONTOLOGY.md` — semantic model narrative
- `krag/EVALUATION.md` — measured retrieval quality
- `krag/CLOSEOUT_PLAN.md` — golden corpus realism and closeout waves
- `krag/EVALUATION_CORPUS_CONTRACT.md` — tiered eval corpus schema and gates
- `ontology/` — TTL and SHACL source (`ontology/README.md`)
- `SKILLS_KG_MCP_RUNBOOK.md` — operator runbook

Local experiment write-ups (if present) live under `krag/experiments/` and are not part of the portable product docs.

## Other

- `templates/` — optional epic and story templates
- `overlays/` — product-specific guidance overlays
- `security/OWASP_ASI_CROSSWALK.md` — agentic security control map (see also root `SECURE_AGENTIC_DEVELOPMENT.md`, `SECURITY_HARDENING.md` for Docker)

## Principle

- Root `README.md` — short billboard for the whole repository
- `skills_docs/` — how to route and operate
- `skills/` — portable operational core (`SKILL.md` files)
