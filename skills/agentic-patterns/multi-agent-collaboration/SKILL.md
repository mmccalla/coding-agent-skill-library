---
name: multi-agent-collaboration
description: Use when designing or implementing systems with multiple specialised agents, including supervisor-worker, sequential hand-off, parallel specialists, debate/review, or agents-as-tools patterns.
---

# Multi-Agent Collaboration

## When to use

Use this skill only when a single agent becomes a bottleneck because the task needs distinct expertise, tools, permissions, workstreams or review roles. Prefer a single agent plus tools for simple workflows.

## Collaboration patterns

- Sequential hand-off: one specialist produces an output for the next.
- Parallel specialists: independent branches work concurrently and merge results.
- Supervisor-worker: a coordinator assigns tasks and synthesises outputs.
- Debate/review: agents critique alternatives before a decision.
- Agent as tool: a specialist agent is exposed behind a narrow callable interface.

## Implementation pattern

1. Define each agent's role, goal, allowed tools and boundaries.
2. Define message schemas and hand-off contracts.
3. Define the orchestration pattern and stopping conditions.
4. Use deterministic validators between agents.
5. Add observability: trace ID, agent name, input, output, tool calls and errors.
6. Test each agent independently and the orchestration end-to-end.

## Guardrails

- Avoid peer-to-peer free-for-all communication unless there is a clear need.
- Do not let worker agents change shared state without a coordinator or transaction boundary.
- Keep privileges minimal by role.
- Make final synthesis grounded only in supplied agent outputs unless external retrieval is explicitly part of the workflow.

## Verification
- [ ] Roles and responsibilities are non-overlapping.
- [ ] Communication schema is explicit.
- [ ] Orchestration pattern is documented.
- [ ] Failure and retry behaviour is defined.
- [ ] End-to-end traceability exists.
