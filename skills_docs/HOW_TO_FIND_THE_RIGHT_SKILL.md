# How to Find the Right Skill

Use this page as the shortest path from a task to the right local skill.

## Mandatory startup order

Before using this routing guide:

1. Read `AGENTIC_CODING_GLOBAL_SAFETY.md` when present.
2. Read `SECURE_AGENTIC_DEVELOPMENT.md` when present.
3. **Execute `skills/apply-laws-of-ai/SKILL.md` in full** — immutable baseline for all reasoning.

Then continue with the steps below. See `LIBRARY_CONTRACT.md` for portable consistency rules.

## Start here

1. Read `skills/README.md` for the structure of the portable flat library.
2. Classify the task by shape, not by technology buzzwords.
3. Choose the smallest semantic category that matches the core problem.
4. Use `skills/MANIFEST.md` to confirm category grouping when needed.
5. Prefer frontmatter `name`, `aliases` and `description` over filesystem assumptions.
6. Load the smallest relevant `SKILL.md` or skill combination.

## Choose by task shape

| If the task is mainly about... | Start with category group |
|---|---|
| Session setup, planning, specs, implementation flow, source grounding | `agentic-patterns` |
| Safety baseline, approval, recovery, RAG, evaluation, prioritization | `agent-control-patterns` (`apply-laws-of-ai` first) |
| Code quality, testing, refactoring, domain modelling, review | `engineering-practices` |
| UI, accessibility, dashboards, interaction states, agent supervision | `user-experience` |
| Reliability, incidents, observability, CI/CD, release, launch | `reliability-and-delivery` |
| Events, CDC, stream processing, real-time operations | `event-driven-and-real-time-data` |
| Capabilities, value streams, processes, operating model, traceability | `business-architecture` |
| Data models, products, contracts, governance, lineage, knowledge graphs | `data-architecture` |
| End-to-end KRAG system design, graph construction, retrieval or KRAG evaluation | `krag-systems` |

## Choose by common scenarios

| Scenario | Recommended starting skill(s) |
|---|---|
| Every session | `apply-laws-of-ai` (mandatory first) |
| Ambiguous request | `skill-discovery-and-selection`, then `requirements-elicitation` if intent is still unclear |
| Multi-step implementation | `planning-and-task-decomposition`, then `incremental-implementation` |
| Generic document-grounded RAG | `knowledge-retrieval-rag` |
| GraphRAG or Neo4j-native KG-backed RAG | `knowledge-graph-rag`, plus `knowledge-retrieval-rag` |
| End-to-end KRAG system delivery | `krag-system-design`, then the smallest relevant KRAG systems skill |
| Knowledge graph design | `ontology-and-knowledge-graph-modeling` |
| Business-facing behaviour change | `bdd-practice`, then `tdd-practice` |
| Complex domain logic | `ddd-practice` |
| Code review | `code-review-and-quality` |
| CI/CD or release workflow | `ci-cd-and-automation` or `shipping-and-launch` |
| User-facing screen or workflow | `ux-design-principles`, `accessibility-wcag` |

## Selection rules

- `apply-laws-of-ai` always runs before any other skill.
- Prefer the smallest useful skill set.
- Do not load a whole category when one skill is enough.
- Use category docs for orientation and `SKILL.md` files for actual operating procedure.
- When two skills overlap, choose the more specific one.
- When a task crosses boundaries, combine one primary skill with the smallest supporting skills.

## Navigation map

- Library contract: `LIBRARY_CONTRACT.md`
- Portable flat-library index: `skills/README.md`
- Full inventory: `skills/MANIFEST.md`
- Category grouping lives in `skills/MANIFEST.md` and in each skill's frontmatter metadata.
