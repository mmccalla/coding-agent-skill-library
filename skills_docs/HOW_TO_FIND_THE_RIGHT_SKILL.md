# How to Find the Right Skill

Use this page as the shortest path from a task to the right local skill.

## Start here

1. Read `skills/README.md` for the structure of the portable subtree.
2. Classify the task by shape, not by technology buzzwords.
3. Choose the smallest category that matches the core problem.
4. Open the category `README.md`.
5. Open the category `MANIFEST.md` only if you need more inventory detail.
6. Load the smallest relevant `SKILL.md` or skill combination.

## Choose by task shape

| If the task is mainly about... | Start in |
|---|---|
| Session setup, planning, specs, implementation flow, source grounding | `skills/agentic-patterns/` |
| Safety, approval, recovery, RAG, evaluation, prioritisation | `skills/agent-control-patterns/` |
| Code quality, testing, refactoring, domain modelling, review | `skills/engineering-practices/` |
| UI, accessibility, dashboards, interaction states, agent supervision | `skills/user-experience/` |
| Reliability, incidents, observability, CI/CD, release, launch | `skills/reliability-and-delivery/` |
| Events, CDC, stream processing, real-time operations | `skills/event-driven-and-real-time-data/` |
| Capabilities, value streams, processes, operating model, traceability | `skills/business-architecture/` |
| Data models, products, contracts, governance, lineage, knowledge graphs | `skills/data-architecture/` |

## Choose by common scenarios

| Scenario | Recommended starting skill(s) |
|---|---|
| Ambiguous request | `using-agent-skills`, then `interview-me` if intent is still unclear |
| Multi-step implementation | `planning-and-task-decomposition`, then `incremental-implementation` |
| Generic document-grounded RAG | `knowledge-retrieval-rag` |
| GraphRAG or Neo4j-native KG-backed RAG | `kg-enabled-rag`, plus `knowledge-retrieval-rag` |
| Knowledge graph design | `ontology-and-knowledge-graph-modelling` |
| Business-facing behaviour change | `bdd-practice`, then `tdd-practice` |
| Complex domain logic | `ddd-practice` |
| Code review | `code-review-and-quality` |
| CI/CD or release workflow | `ci-cd-and-automation` or `shipping-and-launch` |
| User-facing screen or workflow | `ux-design-principles`, `accessibility-wcag` |

## Selection rules

- Prefer the smallest useful skill set.
- Do not load a whole category when one skill is enough.
- Use category docs for orientation and `SKILL.md` files for actual operating procedure.
- When two skills overlap, choose the more specific one.
- When a task crosses boundaries, combine one primary skill with the smallest supporting skills.

## Navigation map

- Portable subtree index: `skills/README.md`
- Full inventory: `skills/MANIFEST.md`
- Category entrypoints:
  - `skills/agentic-patterns/README.md`
  - `skills/agent-control-patterns/README.md`
  - `skills/engineering-practices/README.md`
  - `skills/user-experience/README.md`
  - `skills/reliability-and-delivery/README.md`
  - `skills/event-driven-and-real-time-data/README.md`
  - `skills/business-architecture/README.md`
  - `skills/data-architecture/README.md`
