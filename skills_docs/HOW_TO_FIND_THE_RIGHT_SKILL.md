# How to Find the Right Skill

Shortest path from a task to the right skill. Agents should use this after safety baselines and `apply-laws-of-ai`.

## Mandatory startup order

Before routing:

1. Read `AGENTIC_CODING_GLOBAL_SAFETY.md` when present.
2. Read `SECURE_AGENTIC_DEVELOPMENT.md` when present.
3. **Execute `apply-laws-of-ai` in full** — immutable baseline for all reasoning.
   - **MCP mode:** `get_skill` / `get_skill_execution_guide` with skill id `apply-laws-of-ai`.
   - **Filesystem mode:** read `skills/apply-laws-of-ai/SKILL.md`.

Then choose an access path below. Portable rules: `LIBRARY_CONTRACT.md`. Cursor mode wiring: `CURSOR_IDE_SETUP.md`.

## Choose your access path

| Mode | When | How agents load skills |
| --- | --- | --- |
| **A — skills-kg MCP** | This repo’s Cursor default; any harness with `skills-kg` connected | MCP tools only — do **not** read `skills/**/SKILL.md` for day-to-day work |
| **B — filesystem** | Drop-in copy, Claude Code, Codex, or MCP unavailable | Progressive disclosure via `skills/` + this guide |

Do not mix modes in one session unless the user explicitly authorises filesystem fallback while MCP is down.

---

## Path A — skills-kg MCP (IDE agents)

Use the **`skills-kg`** MCP server. Prefer `skills://contract` when tool choice is unclear.

| Need | Tool |
| --- | --- |
| Ambiguous task → route | `route_skill_query` |
| Human-readable name → id | `resolve_skill` |
| Known skill id → content | `get_skill` |
| Checklists / procedures | `get_skill_execution_guide` |
| Task-oriented shortlist | `recommend_skills` |
| Related skills / context | `get_skill_context` |
| Browse / search library | `search_skills` |

### MCP workflow

1. Call `route_skill_query` for natural-language skill questions unless the user gave an exact skill id.
2. Load the **smallest** relevant content (`get_skill`, `get_skill_execution_guide`, or the route’s suggested tool). Do not invent skill text.
3. Treat MCP responses as bounded evidence; prefer abstention over guessing when retrieval is empty or low confidence.
4. If MCP is disconnected, say so and ask the user to enable **Cursor → Settings → MCP** (or authorise filesystem fallback). Do not silently scan `skills/`.

Use the **task-shape** and **scenario** tables below to phrase better queries and to sanity-check the route — not as a substitute for MCP retrieval.

---

## Path B — filesystem (portable / drop-in)

1. Read `skills/README.md` for the flat-library structure.
2. Classify the task by shape (tables below), not by technology buzzwords.
3. Choose the smallest semantic category that matches the core problem.
4. Use `skills/MANIFEST.md` when category confirmation helps.
5. Match frontmatter `name`, `aliases` and `description` before opening bodies.
6. Load the smallest relevant `SKILL.md` or skill combination.

---

## Choose by task shape

| If the task is mainly about… | Start with category group |
| --- | --- |
| Session setup, planning, specs, implementation flow, source grounding | `agentic-patterns` |
| Safety baseline, approval, recovery, RAG, evaluation, prioritisation, threat modelling, model governance, risk | `agent-control-patterns` (`apply-laws-of-ai` first) |
| Code quality, testing strategy, technical debt, refactoring, domain modelling, review | `engineering-practices` |
| UI, accessibility, dashboards, interaction states, agent supervision | `user-experience` |
| Reliability, incidents, observability, CI/CD, secure SDLC, FinOps, performance, IaC, release, launch | `reliability-and-delivery` |
| Events, CDC, stream processing, real-time operations | `event-driven-and-real-time-data` |
| Message-based enterprise integration, channels, routing, endpoints, API lifecycle | `enterprise-integration-patterns` |
| Capabilities, value streams, processes, operating model, traceability | `business-architecture` |
| Solution options/NFRs, cloud landing zones and shared platforms | `solution-and-platform-architecture` |
| Data models, products, contracts, governance, lineage, knowledge graphs | `data-architecture` |
| End-to-end KRAG system design, graph construction, retrieval or KRAG evaluation | `krag-systems` |

## Choose by common scenarios

| Scenario | Recommended starting skill(s) |
| --- | --- |
| Every session | `apply-laws-of-ai` (mandatory first) |
| Ambiguous request | `skill-discovery-and-selection`, then `requirements-elicitation` if intent is still unclear |
| Multi-step implementation | `planning-and-task-decomposition`, then `incremental-implementation` |
| Generic document-grounded RAG | `knowledge-retrieval-rag` |
| GraphRAG or Neo4j-native KG-backed RAG | `knowledge-graph-rag`, plus `knowledge-retrieval-rag` |
| Message-based enterprise integration / EIP | `message-based-integration-design`, then the smallest EIP skill; use `eip-integration-validation` after design |
| HTTP/RPC API design | `api-design-and-lifecycle` |
| Threat modelling / attack surface | `threat-modeling` |
| Secure pipeline and supply chain | `secure-sdlc-and-supply-chain` |
| Model inventory and approval | `ai-model-governance` |
| Solution options and NFRs | `solution-architecture` |
| Cloud landing zone / shared platform | `cloud-platform-architecture` |
| Platform cloud cost / FinOps | `finops-practice` (not `resource-aware-optimization`) |
| Agent-run token/model budget | `resource-aware-optimization` (not `finops-practice`) |
| Risk register and treatments | `risk-management` |
| Test approach / pyramid | `test-strategy` |
| Technical debt inventory | `technical-debt-management` |
| End-to-end KRAG system delivery | `krag-system-design`, then the smallest relevant KRAG systems skill |
| Knowledge graph design | `ontology-and-knowledge-graph-modeling` |
| Business-facing behaviour change | `bdd-practice`, then `tdd-practice` |
| Complex domain logic | `ddd-practice` |
| Code review | `code-review-and-quality` |
| Cognitive bias in plans or retrospectives | `cognitive-bias-review` (after `reflection-and-verification` when checks matter) |
| Logical fallacies in ADRs or arguments | `logical-fallacy-review` |
| CI/CD or release workflow | `ci-cd-and-automation` or `shipping-and-launch` |
| User-facing screen or workflow | `ux-design-principles`, `accessibility-wcag` |

## Selection rules

- `apply-laws-of-ai` always runs before any other skill.
- Prefer the smallest useful skill set.
- Do not load a whole category when one skill is enough.
- Prefer MCP tool results (or frontmatter) over guessing from folder names.
- When two skills overlap, choose the more specific one.
- When a task crosses boundaries, combine one primary skill with the smallest supporting skills.
- Prefer abstention or clarification over inventing skill content.

## Navigation map

- Library contract: `LIBRARY_CONTRACT.md`
- Cursor MCP vs filesystem: `CURSOR_IDE_SETUP.md`
- Portable flat-library index: `skills/README.md`
- Full inventory: `skills/MANIFEST.md`
- Category grouping: `skills/MANIFEST.md` and skill frontmatter
- Operator runbook: `SKILLS_KG_MCP_RUNBOOK.md`
