# KRAG v2 Semantic Selection — TDD Phased Delivery Plan

## Version 2.3.0 — agent-first, ingest-only, trust-gated, usage-measured, admin-upload capable

## North star

> **An engineer adds or updates a `SKILL.md` and merges — or a system admin uploads via the Skills UI Upload tab after trust validation.** CI and UI share the same pre-ingest gates. Only trusted skills reach the graph. A coding agent working through MCP receives the right skill(s), in the right order, with evidence — without anyone editing retrieval rules, bridge tables, or Python intent boosts. Platform operators and pack owners see per-skill hits and usage in metrics and dashboards.

Skills are **untrusted content** until they pass deterministic pre-ingest gates. The agent that consumes MCP output is a user; it must not receive prompt-injection payloads, instruction-override exploits, or procedurally unsafe guidance from the skills graph. **Every MCP tool call that materialises a skill is counted** — usage informs governance, not manual tuning.

---

## Users and personas

| Persona | Role | Success criterion |
| --- | --- | --- |
| **Coding agent** (primary) | Invokes MCP tools during plan → implement → verify → ship | Correct skill selection; **safe** execution guides; citations; abstention |
| **Delegating engineer** | Assigns task to agent; may add skills to the library | Merge skill PR; **no manual security review** for standard in-repo skills |
| **Skill author** | Writes `SKILL.md` using the authoring guide | Passes automated trust gates; fixable violation report on failure |
| **Platform operator** | Runs CI, Docker Compose reload, Neo4j load | Trust pipeline blocks bad skills; quarantine auditable |
| **KRAG maintainer** (rare) | Owns platform vocabulary and security policy packs | Updates policy rules from new abuse cases — not per-skill tuning |
| **Skill pack owner** | Owns category or skill quality over time | Sees usage hits, zero-use skills, and eval drift for owned skills |
| **System admin** | Operates Skills KG UI and platform ingest | Uploads new `SKILL.md` via UI after trust validation; triggers graph reload — **not** via MCP |

---

## Placement in the IDP lifecycle

```text
┌──────────────────────────────────────────────────────────────────────────────┐
│                         Integrated development platform                         │
├──────────────────────────────────────────────────────────────────────────────┤
│  Git / PR ─────────────┐                                                        │
│       │              │                                                        │
│       ▼              ▼                                                        │
│  ┌──────── PRE-INGEST TRUST GATE (deterministic, no LLM judge) ────────────┐  │
│  │ L1 validate_skills.py      structural + authoring contract               │  │
│  │ L2 validate_skill_security.py  injection / override / unsafe patterns    │  │
│  │ L3 validate_skill_practice.py  best-practice rubric                      │  │
│  │ L4 validate_skill_mapping.py semantic readiness (warn / quarantine)      │  │
│  └───────────────────────────────┬──────────────────────────────────────────┘  │
│                                  │ pass only                                   │
│                                  ▼                                             │
│  extract → SHACL → eval subset → graph load (promoted skills only)             │
│                                  ▲                                             │
│  Skills UI (Upload tab) ──admin──┘  preview → trust report → ingest (HTTP)   │
│       │                              (agents: read-only MCP; no write tools)   │
│  IDE / Cursor agent ──MCP stdio──▶ skills-kg (read-only, promoted skills)    │
│       │                              │                                       │
│       └──────── usage events ────────┴──▶ metrics + selection traces         │
│                                              (hits, rank, tool, abstention)   │
└──────────────────────────────────────────────────────────────────────────────┘
```

### Agent lifecycle touchpoints (MCP contract)

| Development phase | Agent intent | MCP tool(s) | Graph contribution |
| --- | --- | --- | --- |
| Session start | Safety baseline | `resolve_skill` → `get_skill_execution_guide` | `governs` edges to baseline skill |
| Ambiguous task | What skill fits? | `route_skill_query` → `recommend_skills` | TaskIntent filter + hybrid rank |
| Named skill | Load exact skill | `resolve_skill` → `get_skill` | Alias resolution |
| Multi-step work | What else / what order? | `get_skill_context` | `precedes`, `complements`, `validates` traversal |
| Before acting | How to execute? | `get_skill_execution_guide` | Procedure + verification anchors |
| Out of scope | Abstain | `recommend_skills` (empty + uncertainty) | Constraint / abstention rules |

Agent journeys must be first-class evaluation fixtures — not only keyword golden queries.

---

## Admin UI skill upload architecture

### Current state (baseline)

The **Upload** tab in `skills-ui/` calls `POST /skills/upload/preview` only. It validates filename, frontmatter and sections but sets `persisted: false` — **no write to `skills/` or Neo4j**. This is correct for agents; **system admins** need a gated second step to ingest.

### Target workflow (two-step, trust-gated)

```text
1. Admin selects SKILL.md in UI Upload tab
2. Preview  → POST /skills/upload/preview
              returns trust report (L1–L4), warnings, promotion prediction
3. Review   → admin sees violations, security findings, mapping status
4. Ingest   → POST /skills/admin/ingest  (enabled only when L1–L3 pass)
              → write skills/{name}/SKILL.md (or configured staging root)
              → extract → validate graph → load Neo4j → rebuild projections
              → audit log + metrics event
5. Verify   → UI shows promotion_status, resolve_skill smoke, graph node count
```

### Hard boundaries (non-negotiable)

| Rule | Rationale |
| --- | --- |
| **No MCP write tool** for agents | OWASP ASI02/ASI03; agents must not persist skills |
| **Admin HTTP only** | `POST /skills/admin/ingest` behind authn/authz — not in MCP tool list |
| **Trust gate before write** | Same `validate_skill_trust.py` as CI; ingest button disabled on fail |
| **Audit every admin ingest** | Who, when, skill_id, trust report hash, outcome |
| **Size limit** | Keep 256 KiB cap (`MAX_UPLOAD_BYTES`) |
| **Idempotent ingest** | Re-upload same checksum → no duplicate graph nodes |

### Deployment modes

| Mode | `SKILLS_ADMIN_WRITE_ROOT` | Use case |
| --- | --- | --- |
| **Local / Docker Compose** | `skills/` in mounted repo volume | Admin uploads → immediate graph reload for agents |
| **Staging** | `var/staging/skills/` | File held until git PR merged; graph can load staging pack separately |
| **Production IDP** | Staging default | UI ingest creates PR artefact or staging blob; **git remains source of truth** for prod |

Default for Phase 10: **local/direct-write** in Compose; staging mode behind env flag for production.

### UI changes (`skills-ui` Upload tab)

| Element | Behaviour |
| --- | --- |
| Trust report panel | Show L1–L3 pass/fail, security violations, practice score |
| **Preview upload** | Existing; enhanced with full trust report (replaces warnings-only) |
| **Ingest skill** | New primary action; disabled until trust pass; confirmation modal with consequences |
| Post-ingest status | `promotion_status`, skill id, graph reload result, link to Graph tab |
| Accessibility | Keyboard path, labels, error states per `accessibility-wcag` |

### API surface (admin only)

| Endpoint | Auth | Action |
| --- | --- | --- |
| `POST /skills/upload/preview` | Authenticated admin (or open in local dev) | Trust report only; no persist |
| `POST /skills/admin/ingest` | **Admin role required** | Write file + run ingest pipeline |
| `GET /skills/admin/ingests` | Admin | Audit list of recent UI ingests |

Not exposed on MCP `list-tools` or `skills://contract` agent workflow.

---

## Skill usage and hit metrics architecture

### Why usage metrics matter

Retrieval quality (eval recall@k) proves the system *can* select correctly on benchmarks. **Usage metrics** prove which skills agents *actually* use in production — supporting:

- deprecation and retirement of zero-hit skills;
- authoring investment (expand high-use skills, fix low-precision high-hit skills);
- graph vocabulary growth (task intents with traffic but poor precision);
- IDP governance (pack owners accountable for adoption, not just ingest).

The **coding agent is the user**; every MCP tool call that materialises a skill id is a measurable **hit**.

### What counts as a hit

| Event | MCP tool(s) | Hit definition | Labels (no raw query text) |
| --- | --- | --- | --- |
| **Direct resolve** | `resolve_skill` | Canonical skill id returned | `skill_id`, `tool`, `outcome=resolved\|miss` |
| **Lookup** | `get_skill` | Skill body served | `skill_id`, `tool` |
| **Recommendation** | `recommend_skills` | Skill appears in result set | `skill_id`, `tool`, `rank` (1, 2–3, 4–k) |
| **Route selection** | `route_skill_query` | Route implies a skill path | `route`, `tool` |
| **Context expansion** | `get_skill_context` | Related skill surfaced | `skill_id`, `tool`, `edge_type` |
| **Execution** | `get_skill_execution_guide` | Agent loaded procedure to act | `skill_id`, `tool` — **strongest usage signal** |
| **Abstention** | any recommend/route | No skill promoted | `tool`, `query_intent`, `outcome=abstain` |

**Privacy:** never put raw user query strings on Prometheus labels. Use `query_intent`, `tool`, `skill_id`, `rank`, `outcome` only. Optional hashed `query_fingerprint` for deduplication in logs, not metrics.

### Three measurement layers

```text
Layer A — Real-time ops metrics (Prometheus)
  Counters/histograms per skill_id + tool; API and MCP stdio paths

Layer B — Selection traces (ontology-aligned, structured logs)
  SkillSelectionRun → SelectionCandidate → SkillSelectionDecision per invocation

Layer C — Usage analytics rollups (periodic / dashboard)
  Top skills, zero-hit skills, hit rate by category, execution-guide conversion
```

### Layer A — Prometheus metrics (extend existing `skills_api`)

Today: `skills_api_retrieval_requests_total`, `skills_api_retrieval_recommendation_count`, `skills_api_retrieval_top_score` — **aggregate only, no per-skill id**.

**Add (Phase 7–9):**

| Metric | Type | Labels | Purpose |
| --- | --- | --- | --- |
| `skills_usage_hits_total` | Counter | `skill_id`, `tool`, `event` | All material skill appearances |
| `skills_usage_recommend_rank_total` | Counter | `skill_id`, `rank_bucket` | Recommendation position distribution |
| `skills_usage_execution_guide_total` | Counter | `skill_id` | Agents that loaded procedure before acting |
| `skills_usage_context_surfaced_total` | Counter | `skill_id`, `edge_type` | Orchestration bundle usage |
| `skills_usage_resolve_total` | Counter | `skill_id`, `outcome` | Direct name resolution success/fail |
| `skills_usage_abstention_total` | Counter | `tool`, `query_intent` | Out-of-domain / low-confidence |
| `skills_usage_latency_seconds` | Histogram | `tool` | MCP path latency (existing API histogram extended to stdio) |

MCP stdio server must emit the **same** usage events as FastAPI (shared `skills_usage.py` module).

### Layer B — Selection traces (`SkillSelectionRun`)

Align with `SKILLS_ONTOLOGY.md` runtime selection layer and `RUNTIME_CONTRACT.md` observability:

| Field | Source |
| --- | --- |
| `selection_run_id` | Per MCP / API invocation |
| `query_intent` | Classifier output |
| `tool` | MCP tool name |
| `candidates[]` | skill_id, rank, score, rejected_reason |
| `selected[]` | final skill ids returned |
| `evidence_anchor_ids[]` | anchors cited |
| `abstention_reason` | if applicable |
| `latency_ms` | end-to-end |

**Phase 7:** emit structured JSON logs + in-memory trace on MCP response metadata.

**Phase 9 (optional persist):** append-only `SkillSelectionRun` nodes in Neo4j for audit — bounded retention; not required for v1 counters.

### Layer C — Usage analytics rollups

| Report | Consumer | Cadence | Source |
| --- | --- | --- | --- |
| Top-N skills by hits (7d) | KRAG maintainer | Daily | Prometheus or rollup job |
| Zero-hit promoted skills (30d) | Pack owner / deprecation | Weekly | hits == 0 AND promoted |
| Recommend rank@1 rate per skill | Authoring quality | Weekly | rank_bucket=1 / total recommends |
| Execution-guide conversion | Agent workflow health | Weekly | execution_guide / recommend hits |
| Abstention rate by query_intent | Vocabulary gaps | Daily | abstention / total queries |
| Eval vs ops divergence | KRAG governance | Per release | golden recall vs live hit precision |

Deliverable: Grafana dashboard **Skills KG Usage** (extend existing API observability board) + `scripts/report_skill_usage.py` for CLI/CI summary.

### Usage-informed governance (no manual retrieval tuning)

| Signal | Automated response |
| --- | --- |
| Skill promoted but **zero hits 90d** | Flag in usage report; candidate for `owl:deprecated` review — not auto-delete |
| High hits, low eval precision | Quarantine mapping review; authoring fix — not intent boosts |
| High abstention on task intent | Propose new governed TaskIntent (E5) — vocabulary change, not Python |
| `execution_guide` ≪ `recommend` | Agent journey gap; improve MCP contract docs or procedure anchors |

---

## Pre-ingest validation architecture

### Trust model

| State | Meaning | Agent exposure | CI behaviour |
| --- | --- | --- | --- |
| **rejected** | Hard policy or security violation | Not in graph; not in MCP | PR fails |
| **quarantined** | Structural OK; semantic mapping incomplete or practice warnings | Not in retrieval projections | PR may pass with warning label; operator audit |
| **promoted** | All required gates passed | Full MCP + graph | PR passes; ingest runs |

**Principle:** treat every `SKILL.md` like untrusted retrieved content (OWASP ASI01 Agent Goal Hijack) until deterministic validators pass. Do **not** rely on an LLM to approve skills for ingest.

### Validation layers

| Layer | Script | Blocks ingest? | What it proves |
| --- | --- | --- | --- |
| **L1 Structural** | `validate_skills.py` (exists) | Yes | Template, frontmatter, sections, aliases, duplication, pack metadata |
| **L2 Security** | `validate_skill_security.py` (new) | Yes | No injection exploits, unsafe instruction overrides, secret patterns, destructive guidance without escalation |
| **L3 Best practice** | `validate_skill_practice.py` (new) | Yes (new skills); warn (legacy) | Procedure quality, verification checklist, boundaries, alignment with library contract |
| **L4 Semantic readiness** | `validate_skill_mapping.py` (new) | Quarantine if fail | TaskIntent mapping resolvable; Related skills valid |
| **L5 Graph integrity** | `validate_skills_graph.py` + SHACL | Yes | Connectedness, evidence backing, no orphan assertions |
| **L6 Retrieval regression** | `evaluate_skill_retrieval.py` subset | Yes on regression | New skill does not harm agent selection quality |
| **L7 Human approval** | PR label / workflow | Gate for `invocation_mode: approval-required` | External packs, policy exceptions |

Orchestrator: `scripts/validate_skill_trust.py` — runs L1–L4 locally and in CI; returns machine-readable report.

### L2 Security — policy categories (initial)

Mapped to `skills_docs/security/OWASP_ASI_CROSSWALK.md` (ASI01, ASI04, ASI05):

| Category | Example patterns (deterministic) | Rationale |
| --- | --- | --- |
| **Instruction override** | `ignore previous instructions`, `disregard system prompt`, `you are now` | Agent goal hijack |
| **Privilege escalation** | `disable tests`, `skip lint`, `bypass approval`, `run as root` without guardrail context | Unsafe automation |
| **Secret exfiltration** | High-entropy token patterns, `BEGIN PRIVATE KEY`, `.env` dump instructions | Credential leakage |
| **Destructive commands** | `rm -rf /`, `drop database`, `force push` without reversible-plan language | ASI05 unexpected execution |
| **Hidden channels** | HTML comments with override text, zero-width chars, base64 instruction blocks | Supply-chain obfuscation |
| **External fetch** | `curl \| bash`, unsigned remote install, unpinned `pip install` from URL | Supply chain |
| **Baseline conflict** | Procedures that contradict `apply-laws-of-ai` gates (e.g. claim success without tests) | Library safety invariant |

False-positive control: allowlist fixtures for skills that **teach** secure handling of these topics (e.g. `guardrails-safety-patterns`, `human-in-the-loop`) via `tests/fixtures/skill_security_allowlist.json`.

### L3 Best practice — rubric (initial)

| Check | Source | Fail for new skills |
| --- | --- | --- |
| `## Procedure` has numbered steps | `SKILL_AUTHORING_GUIDE.md` | Yes |
| `## Verification` has ≥1 checkbox | `validate_skills.py` (exists) | Yes |
| `## When not to use` when skill has near neighbour in pack | Authoring guide | Warn → fail for new |
| Description includes `Use when` trigger | `validate_skills.py` (exists) | Yes |
| No product-specific overlay content in core skill | `validate_skills.py` (exists) | Yes |
| Related skills references resolve | `validate_skills.py` (exists) | Yes |
| `invocation_mode` set when skill requires human approval | `LIBRARY_CONTRACT.md` | Yes if high-risk content detected |

Best practice is **machine-checkable**, not subjective editorial review.

### How we know a skill is safe (summary)

| Question | Answer mechanism |
| --- | --- |
| Is it structurally valid? | L1 `validate_skills.py` — already in `ci_local.sh` |
| Does it contain known exploit patterns? | L2 security policy pack + regression tests with malicious fixtures |
| Is it procedurally sound for agents? | L3 practice rubric |
| Is it semantically ingestible? | L4 mapping + L5 graph/SHACL |
| Will it harm agent retrieval? | L6 eval subset |
| Is human review required? | L7 only for `approval-required` or external pack — not every skill |

### Upload preview (author feedback loop)

Extend `POST /skills/upload/preview` to run `validate_skill_trust.py` on uploaded bytes — same gates as CI, **before** PR. Engineers and agents drafting skills get immediate violation report; still no persist.

---

## Zero-maintenance contract

What **must not** be required when a new skill is ingested:

| Forbidden operator action | Replaced by |
| --- | --- |
| Manual security review per standard in-repo skill | L2 security policy pack in CI |
| Manual best-practice editorial sign-off | L3 practice rubric |
| Edit `INTENT_BOOST_RULES` in Python | Ingestion-promoted TaskIntent + Constraint |
| Hand-wire Neo4j bridges | `BridgeAssertion` from `## When to use` |
| Curate per-skill ontology TTL | Deterministic `MappingRule` from `SKILL.md` sections |

What **is** required of skill authors:

- Valid `SKILL.md` passing **L1–L3** (and L4 or quarantine)
- Standard sections per authoring guide
- Fix violations reported by `validate_skill_trust.py` locally or in CI

What **is** required of platform (rare):

- Update security policy when new abuse class discovered (TDD: failing malicious fixture first)
- Approve `invocation_mode: approval-required` skills via PR workflow

---

## Skill discovery report

| Dimension | Value |
| --- | --- |
| Task shape | IDP KRAG delivery — trust gates, agent UX, ingest-only ops |
| Risk | **High** — skills execute as agent instructions; supply-chain surface |
| Mandatory baseline | `apply-laws-of-ai` |
| Primary skills | `spec-driven-development`, `planning-and-task-decomposition`, `incremental-implementation`, `tdd-practice`, `bdd-practice` |
| Security skills | `guardrails-safety-patterns`, `human-in-the-loop`, `mcp-server-design`, `tool-use-and-function-calling` |
| KRAG skills | `krag-system-design`, `krag-ingestion-graph-construction`, `krag-retrieval-answering`, `krag-evaluation-governance` |
| Agent / platform UX | `agentic-ux-patterns`, `code-review-and-quality` |
| Data / ontology | `ontology-and-knowledge-graph-modeling` |
| Delivery | `git-workflow-and-versioning`, `ci-cd-and-automation`, `shipping-and-launch`, `documentation-and-adrs` |
| UX / admin | `agentic-ux-patterns`, `accessibility-wcag`, `human-in-the-loop`, `ux-design-principles` |
| Observability | `observability-and-telemetry`, `evaluation-and-monitoring`, `sre-practice`, `data-product-dashboard-design` |
| Intentionally deferred | LLM-as-judge skill approval, full red-team programme, external pack marketplace |

---

## Epics

| Epic ID | Name | Primary persona | Outcome |
| --- | --- | --- | --- |
| **E1** | Ingest-only skill promotion | Delegating engineer | Trusted `SKILL.md` → graph without retrieval code changes |
| **E2** | Agent skill selection | Coding agent | Correct top-1 / top-k skill for natural-language tasks |
| **E3** | Agent orchestration | Coding agent | Ordered bundles via typed edges |
| **E4** | Evidence-backed trust | Agent + engineer | Every recommendation cites `EvidenceAnchor` |
| **E5** | Platform vocabulary | KRAG maintainer | Stable TaskIntent set |
| **E6** | IDP gates and observability | Platform operator | CI blocks regressions and unsafe skills |
| **E7** | Pre-ingest trust and quality | Skill author + operator | Deterministic safety and best-practice gates before graph |
| **E8** | Skill usage and hit analytics | Pack owner + KRAG maintainer | Per-skill hits, rank, execution usage, abstention, rollups |
| **E9** | Admin UI skill upload | System admin | Trust-gated preview → ingest via Upload tab; agents stay read-only |

---

## Story backlog

### E7 — Pre-ingest trust and quality (new)

| Story ID | User story | Acceptance criteria | Phase | TDD tasks |
| --- | --- | --- | --- | --- |
| E7-S01 | As a **platform operator**, I run `validate_skill_trust.py` so that skills with instruction-override text are **rejected** before ingest. | Malicious fixtures fail; allowlisted teaching skills pass | 3 | `test_security_blocks_instruction_override`; `test_security_allowlist_guardrails_skill` |
| E7-S02 | As a **platform operator**, I block skills that instruct disabling tests, lint or security checks. | ASI01/ASI05 patterns detected | 3 | `test_security_blocks_disable_checks` |
| E7-S03 | As a **platform operator**, I block obvious secret material in skill bodies. | PEM, API key patterns, `.env` exfil instructions | 3 | `test_security_blocks_secrets` |
| E7-S04 | As a **skill author**, I run trust validation locally before PR so that I get a fixable report. | CLI exit 1 + JSON/text report per skill | 3 | `test_trust_cli_report_format` |
| E7-S05 | As a **system admin**, I upload a draft skill to preview so that I see the same gates as CI. | `POST /skills/upload/preview` runs L1–L4 trust report | 3, 10 | `test_upload_preview_runs_trust_validation`; `test_upload_preview_trust_report_shape` |
| E7-S06 | As a **platform operator**, quarantined skills are excluded from MCP retrieval. | `promotion_status != promoted` → not in projections | 4 | `test_quarantined_skill_not_retrieved` |
| E7-S07 | As a **KRAG maintainer**, I add a new abuse pattern via TDD so that policy evolves safely. | Failing malicious fixture → rule → pass | 3 | `test_security_policy_extensible` |
| E7-S08 | As a **coding agent**, I only receive **promoted** skills from MCP so that quarantined content never shapes behaviour. | MCP tools filter by promotion status | 7 | `test_mcp_excludes_quarantined_skills` |

### E1 — Ingest-only skill promotion

| Story ID | User story | Acceptance criteria | Phase | TDD tasks |
| --- | --- | --- | --- | --- |
| E1-S01 | As a **delegating engineer**, I merge a trusted `SKILL.md` so that ingestion promotes aliases and evidence anchors. | Extract after trust pass only | 4 | `test_extract_skips_rejected`; `test_extract_new_skill_emits_anchors` |
| E1-S02 | As a **delegating engineer**, I update `## When to use` so that assertions refresh on re-ingest. | Versioned `BridgeAssertion` update | 4 | `test_reingest_updates_bridge_assertion` |
| E1-S03 | As a **platform operator**, I run `skills-loader` idempotently. | No duplicates on reload | 4, 9 | `test_load_idempotent_merge` |
| E1-S04 | As a **delegating engineer**, I never edit Python retrieval rules for new skills. | No intent boost entries | 7 | `test_new_skill_recall_without_intent_boost` |
| E1-S05 | As a **skill author**, I use the standard template. | L1–L3 pass; L4 maps or quarantines | 2, 3 | `test_validate_skills_new_fixture`; `test_mapping_quarantine_message` |

### E2 — Agent skill selection

| Story ID | User story | Acceptance criteria | Phase | TDD tasks |
| --- | --- | --- | --- | --- |
| E2-S01 | As a **coding agent**, I call `resolve_skill` by alias. | Alias resolution on golden tag | 7 | `test_mcp_resolve_skill_alias` |
| E2-S02 | As a **coding agent**, I call `recommend_skills` for a task. | Recall@3 on agent journeys | 7 | `test_mcp_recommend_skills_shape` |
| E2-S03 | As a **coding agent**, near-neighbour queries disambiguate via constraints. | No intent boosts | 4, 7 | `test_near_neighbour_tdd_vs_reflection` |
| E2-S04 | As a **coding agent**, out-of-domain queries abstain. | `expect_uncertain` pass | 7 | `test_abstention_out_of_domain` |
| E2-S05 | As a **coding agent**, `route_skill_query` selects correct tool path. | Journey route accuracy | 7 | `test_router_agent_journey_routes` |

### E3 — Agent orchestration

| Story ID | User story | Acceptance criteria | Phase | TDD tasks |
| --- | --- | --- | --- | --- |
| E3-S01 | As a **coding agent**, `get_skill_context` returns **precedes** chain. | Ordered predecessors + evidence | 5, 7 | `test_context_precedes_chain` |
| E3-S02 | As a **coding agent**, `get_skill_context` returns **complements** bundle. | Security + build journey | 5, 7 | `test_context_complements_bundle` |
| E3-S03 | As a **coding agent**, `get_skill_context` returns **validates** skills. | Post-impl review journey | 5, 7 | `test_context_validates_edges` |
| E3-S04 | As a **coding agent**, session start finds safety baseline. | `apply-laws-of-ai` governing | 5, 7 | `test_session_start_recommends_baseline` |
| E3-S05 | As a **coding agent**, KRAG work returns spine order. | Precedes chain journey | 5 | `test_krag_spine_precedes_order` |

### E4 — Evidence-backed trust

| Story ID | User story | Acceptance criteria | Phase | TDD tasks |
| --- | --- | --- | --- | --- |
| E4-S01 | As a **coding agent**, MCP returns evidence coordinates. | path, heading, lines | 4, 7 | `test_mcp_response_evidence_coordinates` |
| E4-S02 | As a **delegating engineer**, I audit selection traces. | intent, filter, rank, anchors, usage event ids | 7 | `test_selection_trace_fields` |
| E4-S03 | As a **coding agent**, execution guide includes checklist. | Verification anchors | 7 | `test_execution_guide_checklist` |
| E4-S04 | As a **platform operator**, SHACL rejects assertions without evidence. | Quarantine not promote | 4 | `test_promotion_fails_without_anchor` |

### E5 — Platform vocabulary

| Story ID | User story | Acceptance criteria | Phase | TDD tasks |
| --- | --- | --- | --- | --- |
| E5-S01 | As a **KRAG maintainer**, I publish TaskIntent scheme. | 15–25 governed concepts | 1 | `test_governed_vocabulary` |
| E5-S02 | As a **KRAG maintainer**, TaskShape ↔ TaskIntent aligned. | Contract doc + tests | 1 | `test_vocabulary_contract_aliases` |
| E5-S03 | As a **skill author**, I do not edit TTL. | Prose → concept mapping | 2, 4 | `test_when_to_use_maps_to_task_intent` |

### E6 — IDP gates and observability

| Story ID | User story | Acceptance criteria | Phase | TDD tasks |
| --- | --- | --- | --- | --- |
| E6-S01 | As a **platform operator**, CI runs trust + eval on `skills/**` PRs. | Workflow fails on L2 or regression | 9 | `test_ci_trust_gate_workflow` |
| E6-S02 | As a **platform operator**, I see per-tool agent metrics including per-skill hits. | Prometheus: usage + retrieval + abstention labels | 7, 9 | `test_metrics_agent_query_labels`; `test_usage_hits_exported` |
| E6-S03 | As a **KRAG maintainer**, graph beats vector on `graph_required`. | `graphLiftRecallAtK` > 0 | 8 | `test_three_arm_eval_graph_lift` |
| E6-S04 | As a **delegating engineer**, parent merges to main only after gates pass. | Cutover checklist | 8 | `krag_cutover_acceptance.py` PASS |
| E6-S05 | As a **coding agent**, MCP matches `skills://contract`. | Contract compliance tests | 7, 9 | `test_mcp_contract_compliance` |

### E8 — Skill usage and hit analytics (new)

| Story ID | User story | Acceptance criteria | Phase | TDD tasks |
| --- | --- | --- | --- | --- |
| E8-S01 | As a **platform operator**, I see per-skill hit counts when agents call MCP tools. | `skills_usage_hits_total{skill_id,tool,event}` increments | 7, 9 | `test_usage_counter_on_recommend`; `test_usage_counter_on_execution_guide` |
| E8-S02 | As a **KRAG maintainer**, I see recommendation rank distribution per skill. | `skills_usage_recommend_rank_total` by rank_bucket | 7 | `test_usage_recommend_rank_labels` |
| E8-S03 | As a **pack owner**, I can list zero-hit promoted skills for a period. | `report_skill_usage.py --zero-hits 30d` | 9 | `test_usage_report_zero_hits` |
| E8-S04 | As a **delegating engineer**, I can audit a selection via structured trace. | `SkillSelectionRun` fields in MCP response metadata + logs | 7 | `test_selection_trace_emitted_per_mcp_call` |
| E8-S05 | As a **platform operator**, Grafana shows top skills and abstention rate. | Dashboard panels wired to new metrics | 9 | `test_metrics_registered_for_prometheus_export` |
| E8-S06 | As a **KRAG maintainer**, I compare eval recall vs live hit rank@1 per skill. | Usage vs eval divergence report | 8, 9 | `test_usage_eval_divergence_report` |
| E8-S07 | As a **coding agent** on MCP stdio, my usage is counted same as HTTP API. | stdio and FastAPI share `skills_usage.py` | 9 | `test_mcp_stdio_usage_parity_with_api` |

### E9 — Admin UI skill upload (new)

| Story ID | User story | Acceptance criteria | Phase | TDD tasks |
| --- | --- | --- | --- | --- |
| E9-S01 | As a **system admin**, I preview an upload and see the full trust report in the UI. | Preview response includes L1–L3 results, not just warnings | 10 | `test_upload_preview_trust_report_shape`; `App.test.tsx` trust panel |
| E9-S02 | As a **system admin**, I cannot ingest until trust validation passes. | Ingest button disabled; API returns 422 if forced | 10 | `test_admin_ingest_blocked_on_trust_fail` |
| E9-S03 | As a **system admin**, I ingest a trusted skill so it appears in the graph. | File written + extract + load; `resolve_skill` works | 10 | `test_admin_ingest_persists_and_loads`; `JRN-11-admin-upload` |
| E9-S04 | As a **coding agent**, I cannot call admin ingest via MCP. | No write tool; HTTP 403 without admin role | 10 | `test_mcp_has_no_ingest_tool`; `test_admin_ingest_requires_auth` |
| E9-S05 | As a **platform operator**, every admin ingest is audit-logged. | actor, timestamp, skill_id, trust_hash, outcome | 10 | `test_admin_ingest_audit_record` |
| E9-S06 | As a **system admin**, I see post-ingest promotion status in the UI. | Upload tab shows promoted/quarantined + graph refresh | 10 | `App.test.tsx` post-ingest status |
| E9-S07 | As a **system admin**, I use an accessible upload workflow. | WCAG: labels, focus, errors, confirm dialog | 10 | `App.test.tsx` a11y smoke; manual checklist |
| E9-S08 | As a **system admin** in staging mode, ingest writes to staging root not live `skills/`. | Env `SKILLS_ADMIN_WRITE_MODE=staging` | 10 | `test_admin_ingest_staging_path` |

---

## Agent journey fixtures

| Journey ID | Agent narrative | Expected outcome | Tags |
| --- | --- | --- | --- |
| `JRN-01-session-start` | Load safety baseline first | `apply-laws-of-ai` execution guide | `baseline` |
| `JRN-02-ambiguous-feature` | OAuth API feature | Relevant skills ranked | `vague` |
| `JRN-03-tdd-defect` | Failing test first | `tdd-practice` not reflection | `near_neighbour` |
| `JRN-04-post-impl-review` | Review before merge | `code-review-and-quality` | `near_neighbour` |
| `JRN-05-build-with-security` | Secure endpoint | complements bundle | `multi_skill` |
| `JRN-06-krag-delivery` | KRAG ingestion feature | precedes spine | `traversal` |
| `JRN-07-ingest-new-skill` | New skill after PR merge | `resolve_skill` works post-reload | `ingest` |
| `JRN-08-out-of-domain` | Weather question | Abstain | `abstention` |
| `JRN-09-malicious-blocked` | PR adds skill with injection text | CI rejects; MCP never serves it | `security`, `trust` |
| `JRN-10-usage-trace` | Agent recommends then loads execution guide | Hits + rank + execution_guide metrics increment | `usage` |
| `JRN-11-admin-upload` | Admin uploads trusted skill via UI | Ingest → agent `resolve_skill` without code deploy | `admin`, `ingest` |

Fixture files:

- `tests/fixtures/retrieval_evaluation/agent_journeys.json`
- `tests/fixtures/skill_trust/malicious/` (injection, override, secrets)
- `tests/fixtures/skill_trust/benign/` (teaching security topics)

---

## Design constraints (non-negotiable)

- **Trust before ingest:** no graph promotion without L1–L3 pass.
- **Deterministic security:** policy-as-code; not LLM approval of skills.
- **Agent-first:** acceptance criteria from coding agent perspective.
- **Ingest-only ops:** no per-skill retrieval tuning.
- **TDD first:** malicious fixtures precede new rules.
- **Evidence-backed promotion:** no triples without `EvidenceAnchor`.
- **Promoted-only MCP:** quarantined/rejected skills invisible to agents.
- **Usage measured:** every material skill appearance emits metrics and trace fields; no raw query on labels.
- **Admin upload gated:** UI ingest runs the same trust pipeline as CI; never bypasses L1–L3.
- **Agents read-only:** no MCP write path for skill persistence.
- **British English** in docs and commits.

---

## Delivery phases

| Phase | Branch | Epic focus | Outcome |
| --- | --- | --- | --- |
| **1** | `phase-01` | E5 | Platform vocabulary |
| **2** | `phase-02` | E1, E5 | Authoring + mapping contract |
| **3** | `phase-03` | **E7**, E6 | **Pre-ingest trust gates (L1–L4 orchestrator)** |
| **4** | `phase-04` | E1, E4, E7, E2 | Ingest promotes only **trusted** skills |
| **5** | `phase-05` | E3, E1 | Typed dependencies |
| **6** | `phase-06` | E1, E2 | Retrieval projections |
| **7** | `phase-07` | E2, E3, E4, E7, **E8** | Agent MCP + **usage instrumentation** |
| **8** | `phase-08` | E6, **E8** | Eval cutover + usage/eval divergence |
| **9** | `phase-09` | E6, E1, E7, **E8** | IDP CI + **Grafana usage dashboard** |
| **10** | `phase-10` | **E9**, E7, E1 | **Admin UI upload** (preview → trust → ingest) |

```text
Phase 1–2: vocabulary + authoring
Phase 3:   TRUST GATE (security + practice)  ← blocks unsafe skills
Phase 4–6: ingest + deps + projections
Phase 7–9: agent MCP + usage metrics + eval + CI
Phase 10:  admin UI upload (depends on Phase 3 trust + Phase 4 ingest)
```

---

## Branch strategy

```text
main
 └── krag-v2/semantic-selection
      ├── phase-01 … phase-10
      └── parent → main after Phase 8 + 9 + 10 gates
```

---

## Phase details

### Phase 1 — Platform vocabulary (E5)

**Skills:** `apply-laws-of-ai`, `spec-driven-development`, `ontology-and-knowledge-graph-modeling`, `krag-system-design`, `tdd-practice`, `documentation-and-adrs`

**Deliverables:** `task-intents.ttl`, `workflow-stages.ttl`, `VOCABULARY_CONTRACT.md`

---

### Phase 2 — Authoring contract (E1, E5)

**Skills:** `apply-laws-of-ai`, `bdd-practice`, `spec-driven-development`, `krag-ingestion-graph-construction`, `documentation-and-adrs`, `tdd-practice`

**Deliverables:** `MAPPING_RULES.md`, `SKILL_DEPENDENCY_MAPPING.md`, `skill_section_mapping.py`, authoring guide

---

### Phase 3 — Pre-ingest trust gates (E7, E6) ★ new

**Skills:** `apply-laws-of-ai`, `tdd-practice`, `bdd-practice`, `guardrails-safety-patterns`, `human-in-the-loop`, `mcp-server-design`, `tool-use-and-function-calling`, `code-review-and-quality`, `documentation-and-adrs`

**Stories:** E7-S01 … E7-S05, E7-S07

**TDD — write first:**

| Test | Behaviour |
| --- | --- |
| `tests/test_validate_skill_security.py` | Blocks instruction override, disable-checks, secrets, destructive patterns |
| `tests/test_validate_skill_practice.py` | Enforces procedure steps, verification, boundaries |
| `tests/test_validate_skill_trust.py` | Orchestrator runs L1–L4; aggregated report |
| `tests/fixtures/skill_trust/malicious/*.md` | Known-bad samples (red fixtures) |

**Deliverables:**

- `scripts/validate_skill_security.py`
- `scripts/validate_skill_practice.py`
- `scripts/validate_skill_mapping.py` (readiness only; quarantine semantics)
- `scripts/validate_skill_trust.py` (orchestrator)
- `skills_docs/ontology/krag_v2/SKILL_TRUST_CONTRACT.md` (policy catalogue + ASI map)
- `tests/fixtures/skill_security_allowlist.json`
- Wire into `ci_local.sh` **before** `extract_skills_graph.py`

**Exit:** Malicious fixtures rejected; existing 91 skills pass or get documented legacy waiver with expiry; `JRN-09` passes.

---

### Phase 4 — Ingestion promotion (E1, E4, E7, E2)

**Skills:** `apply-laws-of-ai`, `tdd-practice`, `krag-ingestion-graph-construction`, `ontology-and-knowledge-graph-modeling`, `dry-principle`, `incremental-implementation`

**Stories:** E1-S01, E1-S02, E4-S04, E7-S06, E2-S03 (partial)

**Deliverables:** `extract_skills_graph.py` calls trust gate; `promotion_status` on `SkillVersion`; quarantine path

**Exit:** Only `promoted` skills in graph projections; E7-S06 green.

---

### Phase 5 — Typed dependencies (E3, E1)

**Skills:** `apply-laws-of-ai`, `tdd-practice`, `krag-ingestion-graph-construction`, `ontology-and-knowledge-graph-modeling`, `solid-principles`, `mcp-server-design`

**Deliverables:** Replace `RELATED_TO`; Related skills table parser; context traversal

---

### Phase 6 — Retrieval projections (E1, E2)

**Skills:** `apply-laws-of-ai`, `tdd-practice`, `krag-system-design`, `krag-ingestion-graph-construction`, `dry-principle`

**Deliverables:** `build_retrieval_projections.py`; promoted skills only

---

### Phase 7 — Agent MCP experience + usage instrumentation (E2, E3, E4, E7, E8)

**Skills:** `apply-laws-of-ai`, `tdd-practice`, `bdd-practice`, `krag-retrieval-answering`, `agentic-ux-patterns`, `mcp-server-design`, `tool-use-and-function-calling`, `kiss-principle`, `guardrails-safety-patterns`, `exception-handling-and-recovery`, **`observability-and-telemetry`**

**Stories:** E2-*, E3-*, E4-*, E1-S04, E6-S05, E7-S08, **E8-S01, E8-S02, E8-S04**

**Deliverables:**

- Intent-class hybrid retriever (no `INTENT_BOOST_RULES`)
- MCP tools return selection trace + evidence
- `agent_journeys.json` fixture suite
- **`scripts/skills_usage.py`** — shared usage event recorder (API + MCP stdio)
- Prometheus counters: `skills_usage_hits_total`, `skills_usage_recommend_rank_total`, `skills_usage_execution_guide_total`
- Structured log: `skill_selection_run` JSON per invocation
- Update `SKILLS_KG_MCP_RUNBOOK.md` — agent workflows + usage fields

**Exit:** Agent journeys pass; **JRN-10** usage trace passes; per-skill counters increment in tests.

---

### Phase 8 — Evaluation cutover + usage baseline (E6, E8)

**Skills:** `apply-laws-of-ai`, `krag-evaluation-governance`, `evaluation-and-monitoring`, `ci-cd-and-automation`, `shipping-and-launch`, `reflection-and-verification`, **`observability-and-telemetry`**

**Stories:** E6-S03, E6-S04, **E8-S06**

**Deliverables:** Three-arm eval; golden tags; cutover report; **`scripts/report_skill_usage.py`** (ops snapshot from metrics or trace log); eval-vs-usage divergence section in acceptance report

**Exit:** Graph lift proven; usage report runs in cutover acceptance; parent → `main` PR ready (pending Phase 9 CI).

---

### Phase 9 — IDP integration + usage dashboard (E6, E1, E7, E8)

**Skills:** `apply-laws-of-ai`, `ci-cd-and-automation`, `release-engineering-and-progressive-delivery`, `toil-reduction-and-automation`, `observability-and-telemetry`, `sre-practice`, `human-in-the-loop`, **`data-product-dashboard-design`**

**Stories:** E6-S01, E6-S02, E1-S03, E7-S05, E6-S05, **E8-S03, E8-S05, E8-S07**

**Deliverables:**

```text
skills/** PR workflow:
  validate_skill_trust.py → validate_skills_graph.py → extract → SHACL
  → evaluate_skill_retrieval (subset) → dry-run load
  → block merge on L2 fail or retrieval regression
```

- Trust metrics: `skills_trust_rejected_total`, `skills_quarantined_total`
- **Usage metrics:** full Layer A catalogue on `/metrics` (API + MCP stdio parity)
- **Grafana:** `Skills KG Usage` dashboard — top skills, hits by tool, abstention rate, execution-guide conversion, zero-hit table
- Weekly rollup job (CI cron or operator script): zero-hit promoted skills report
- Upload preview runs full trust report

**Exit:** Engineer merges skill → trust + ingest → agent safe; usage visible in Grafana; **JRN-07** + **JRN-09** + **JRN-10** in CI.

---

### Phase 10 — Admin UI skill upload (E9, E7, E1)

**Skills:** `apply-laws-of-ai`, `tdd-practice`, `bdd-practice`, `guardrails-safety-patterns`, `human-in-the-loop`, `mcp-server-design`, `agentic-ux-patterns`, `accessibility-wcag`, `ux-design-principles`, `krag-ingestion-graph-construction`, `observability-and-telemetry`

**Stories:** E9-S01 … E9-S08; extends E7-S05 (preview trust report)

**Depends on:** Phase 3 (trust orchestrator), Phase 4 (ingest pipeline), Phase 6 (projections optional but recommended)

**TDD — write first:**

| Test | Behaviour |
| --- | --- |
| `tests/test_skills_api.py` | `POST /skills/admin/ingest` auth, trust block, success path |
| `tests/test_admin_skill_ingest.py` (new) | filesystem write, extract hook, idempotency |
| `skills-ui/src/App.test.tsx` | trust report UI, disabled ingest, post-ingest status |
| `tests/test_skills_mcp_server.py` | ingest endpoint absent from MCP tools |

**Deliverables:**

- `POST /skills/admin/ingest` in `scripts/skills_api.py` (admin auth middleware / API key / role header — configurable)
- `scripts/admin_skill_ingest.py` — write file, run `validate_skill_trust`, extract, load, projection rebuild
- Enhance `POST /skills/upload/preview` to return full trust report JSON
- `skills-ui` Upload tab: trust report panel, **Ingest skill** button, confirmation modal, post-ingest status
- `skills_docs/SKILLS_KG_MCP_RUNBOOK.md` — admin upload section; clarify agents use read-only MCP
- Env: `SKILLS_ADMIN_WRITE_MODE=direct|staging`, `SKILLS_ADMIN_API_KEY` (local dev)
- Audit log: structured `admin_skill_ingest` events + optional `GET /skills/admin/ingests`
- Prometheus: `skills_admin_ingest_total{outcome}`

**Exit:** Admin uploads trusted `SKILL.md` in UI → graph reloads → agent resolves new skill (**JRN-11**); malicious upload blocked in UI and API; MCP has no write tool.

---

## TDD rhythm (every story)

```text
1. BDD / abuse-case scenario (especially E7)
2. Red: failing pytest with malicious or golden fixture
3. Green: minimal policy or implementation
4. Refactor: tighten allowlist; remove false positives
5. Regression: ci_local.sh trust stage
6. Mark story done
```

### Standard commands

```bash
PYTHONPATH=. uv run python scripts/validate_skill_trust.py
PYTHONPATH=. uv run pytest tests/test_validate_skill_security.py tests/test_validate_skill_practice.py -q
PYTHONPATH=. uv run python scripts/validate_skills_ontology.py
PYTHONPATH=. uv run pytest tests/test_extract_skills_graph.py tests/test_load_skills_neo4j.py -q
PYTHONPATH=. uv run pytest tests/test_skills_usage.py tests/test_skills_mcp_server.py -q
./scripts/ci_local.sh
```

---

## Skill usage metrics quick reference

| Question | Metric / artefact |
| --- | --- |
| How often is skill X used? | `skills_usage_hits_total{skill_id="skill:tdd-practice"}` |
| Is X only ever ranked 2nd? | `skills_usage_recommend_rank_total` by rank_bucket |
| Do agents act after recommending X? | `skills_usage_execution_guide_total` / hits ratio |
| Which skills are never used? | `report_skill_usage.py --zero-hits 30d` |
| Why was X selected? | `SkillSelectionRun` trace in logs / response metadata |
| Is live usage worse than eval? | E8-S06 divergence report |

---

## Risk register

| Risk | Mitigation |
| --- | --- |
| False positives on security skills teaching attack patterns | Allowlist + context-aware rules (heading-scoped) |
| Legacy 91 skills fail new L3 rubric | Grandfather waiver with expiry; fix in parallel track |
| Deterministic rules miss novel injection | E7-S07 extensibility; periodic red-team fixtures |
| Agent reads `SKILL.md` from git bypassing MCP | Document IDE policy; trust gate still protects contributors |
| Engineer expects zero authoring effort | Zero **retrieval** maintenance; quality + security authoring required |
| Quarantine skills leak via vector index | Projections + MCP filter `promotion_status=promoted` only |
| Cardinality explosion on `skill_id` labels | Bounded skill catalogue (~100); use logs for drill-down; no query text labels |
| MCP stdio usage invisible to metrics | E8-S07: shared `skills_usage.py` in stdio + HTTP paths |
| High-cardinality Grafana from per-agent ids | Do not label by agent/session; use tool + skill_id only |
| Admin upload bypasses git review | Staging mode default in prod; direct-write documented for local Compose only |
| Agent obtains admin ingest URL | Separate auth; not in MCP contract; rate limit ingest endpoint |

---

## Suggested schedule

| Phase | Effort | Capability |
| --- | --- | --- |
| 1 | 1–2 d | Vocabulary |
| 2 | 1–2 d | Authoring template |
| **3** | **2–3 d** | **Trust gates — safe to ingest** |
| 4 | 2–3 d | Trusted semantic promotion |
| 5 | 2 d | Typed orchestration |
| 6 | 2 d | Projections |
| 7 | 3–4 d | Agent MCP UX + per-skill usage counters |
| 8 | 2–3 d | Eval cutover + usage/eval divergence |
| 9 | 2–3 d | IDP CI + Grafana usage dashboard |
| 10 | 2–3 d | Admin UI trust-gated upload + ingest |

**Total:** ~20–27 days.

---

## Document control

| Field | Value |
| --- | --- |
| Version | 2.3.0 |
| Status | Approved for execution |
| Parent branch | `krag-v2/semantic-selection` |
| Primary user | Coding agent (MCP) |
| Admin user | System admin (Skills UI Upload tab — HTTP only) |
| Trust model | Rejected / quarantined / promoted |
| Usage model | Per-skill hits, rank, execution-guide, abstention (Prometheus + traces) |
| Operator model | Ingest-only + automated trust gates + optional UI admin ingest |
| Related | `SKILL_TRUST_CONTRACT.md`, `SKILLS_KG_MCP_RUNBOOK.md`, `skills-ui/` Upload tab |
