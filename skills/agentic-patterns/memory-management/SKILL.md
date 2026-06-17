---
name: memory-management
description: Use when implementing short-term state, conversation history, long-term memory, RAG, user preferences, episodic examples, procedural instructions or memory update policies for agents.
---

# Memory Management

## When to use

Use this skill when an agent must retain context across steps, resume conversations, recall user/project facts, use previous successful patterns, or maintain persistent knowledge.

Do not store sensitive or irrelevant data. Do not add memory when the task can be solved statelessly.

## Objective

Retain useful agent context while controlling sensitivity, relevance, provenance, retention, and deletion.

## Memory types

- Short-term memory: current thread/session state, recent messages, tool observations and working variables.
- Long-term semantic memory: facts, preferences, domain knowledge and project context.
- Episodic memory: examples of past tasks, decisions and successful workflows.
- Procedural memory: instructions, rules and behaviours used to perform tasks.

## Procedure

1. Classify the information by retention need and sensitivity.
2. Define memory schemas and namespaces.
3. Store only minimal, useful and permission-appropriate data.
4. Retrieve memory based on task relevance, not blindly.
5. Validate retrieved memory against current repository state where applicable.
6. Summarise or evict stale short-term history when context grows too large.
7. Log memory writes and provide a way to inspect or delete memory.

## Coding guidance

- Prefer append/event-based state updates over direct mutation.
- Use clear keys and shallow structures.
- Keep vector/RAG retrieval results attributable to their source.
- Treat retrieved memory as context, not truth.
- Add tests for retrieval, update, deletion and stale-memory handling.

## OWASP ASI mapping

Use `skills_docs/security/OWASP_ASI_CROSSWALK.md` for the shared risk map.

| ASI risk | Memory control |
| --- | --- |
| ASI01 Agent Goal Hijack | Do not let retrieved memory override system, developer or authorised user instructions. |
| ASI06 Memory and Context Poisoning | Validate memory writes, retain provenance, isolate tenants and support forgetting/deletion. |
| ASI08 Cascading Failures | Prevent poisoned shared memory from propagating by scoping retrieval and re-validating before hand-off. |
| ASI10 Rogue Agents | Monitor unexpected memory writes, reads and preference changes as behavioural drift signals. |

## Verification

- [ ] Short-term and long-term memory are separated.
- [ ] Memory schema and namespace are explicit.
- [ ] Memory writes are controlled and auditable.
- [ ] Retrieval is scoped and relevance-filtered.
- [ ] Sensitive data handling is documented.
