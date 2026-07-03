# Skills Docs

Documentation for agents and humans. Pick one path — you do not need every file.

## Choose your path

| Goal | Start here |
| --- | --- |
| **Use skills in an agent** | `HOW_TO_FIND_THE_RIGHT_SKILL.md` (after `apply-laws-of-ai`) |
| **Copy the library to another repo** | `GETTING_STARTED.md` → `DROP_IN_BOOTSTRAP.md` |
| **Run MCP / Docker / Neo4j locally** | `GETTING_STARTED.md` → `SKILLS_KG_MCP_RUNBOOK.md` |
| **Write or change skills** | `SKILL_AUTHORING_GUIDE.md` |
| **KRAG roadmap and status** | `krag/STATUS.md` |
| **Measured retrieval quality** | `krag/EVALUATION.md` |

## Portable library (always relevant)

1. `LIBRARY_CONTRACT.md` — mandatory startup order and portable rules
2. `HOW_TO_FIND_THE_RIGHT_SKILL.md` — route by task shape
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
- `ontology/` — TTL and SHACL source (`ontology/README.md`)
- `ontology/krag_v2/` — legacy paths (archived in Wave C)
- `SKILLS_KG_MCP_RUNBOOK.md` — operator runbook

## Other

- `templates/` — optional epic and story templates
- `overlays/` — product-specific guidance overlays
- `security/OWASP_ASI_CROSSWALK.md` — agentic security control map

## Principle

- Root `README.md` — short billboard for the whole repository
- `skills_docs/` — how to route and operate
- `skills/` — portable operational core (`SKILL.md` files)
