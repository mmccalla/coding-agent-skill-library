# Skill Trust Contract (KRAG v2)

## Purpose

Define deterministic pre-ingest trust gates for `SKILL.md` content before graph promotion or MCP exposure.

Skills are **untrusted content** until validators pass. Agents consuming MCP output must not receive prompt-injection payloads, instruction-override exploits, or procedurally unsafe guidance.

## Validation layers

| Layer | Script | Blocks ingest? | Scope |
| --- | --- | --- | --- |
| L1 Structural | `scripts/validate_skills.py` | Yes | Template, frontmatter, sections, aliases, duplication |
| L2 Security | `scripts/validate_skill_security.py` | Yes | Injection, override, secrets, destructive guidance |
| L3 Best practice | `scripts/validate_skill_practice.py` | Yes (new skills); warn (legacy) | Procedure, verification, boundaries |
| L4 Semantic readiness | `scripts/validate_skill_mapping.py` | Quarantine if fail | TaskIntent mapping, related skills |
| Orchestrator | `scripts/validate_skill_trust.py` | Aggregates L1–L4 | CI, upload preview, local author feedback |

## L2 Security policy categories

Mapped to `skills_docs/security/OWASP_ASI_CROSSWALK.md` (ASI01, ASI04, ASI05).

| Category | Example patterns | Rationale |
| --- | --- | --- |
| `instruction_override` | ignore previous instructions, disregard system prompt, you are now | Agent goal hijack (ASI01) |
| `privilege_escalation` | disable tests, skip lint, bypass approval without guardrail context | Unsafe automation |
| `secret_exfiltration` | BEGIN PRIVATE KEY, high-entropy credential blocks | Credential leakage (ASI04) |
| `destructive_commands` | rm -rf /, drop database, force push without escalation language | Unexpected execution (ASI05) |

False-positive control: `tests/fixtures/skill_security_allowlist.json` for skills that **teach** secure handling of these topics.

## L3 Best practice rubric

| Check | Source |
| --- | --- |
| `## Procedure` has numbered steps | `skills_docs/SKILL_AUTHORING_GUIDE.md` |
| `## Verification` has at least one checkbox | Library contract |
| Frontmatter `description` includes `Use when` | Discovery metadata policy |

## Promotion states

| Status | Meaning | MCP / graph |
| --- | --- | --- |
| `rejected` | Hard policy or security violation | Excluded |
| `quarantined` | Structural OK; semantic mapping incomplete | Excluded from retrieval projections |
| `promoted` | Required gates passed | Full MCP + graph |

## Evidence and audit

- Trust reports are machine-readable (JSON) and suitable for CI and upload preview.
- Admin ingest must record trust report hash, actor, and outcome (Phase 10).

## Related documents

- `skills_docs/ontology/krag_v2/SEMANTIC_SELECTION_PHASED_PLAN.md` — phased delivery plan
- `skills_docs/LIBRARY_CONTRACT.md` — portable authoring contract
- `skills_docs/SKILL_AUTHORING_GUIDE.md` — author guidance
