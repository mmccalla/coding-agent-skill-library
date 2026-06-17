---
name: inter-agent-communication-a2a
description: Use when designing agent-to-agent communication, delegation protocols, agent cards, asynchronous task exchange, or interoperable multi-agent systems.
---

# Inter-Agent Communication (A2A)

## When to use

Use this skill when multiple agents must collaborate across process, service, framework, repository or organisation boundaries. Apply it for delegation, capability discovery, task status tracking, streaming results and standardised hand-offs.

## Objective

Define safe, interoperable contracts for agent identity, delegation, task exchange, and result hand-off.

## Core pattern

1. Define each agent as an opaque service with a clear public contract.
2. Publish an agent card describing identity, endpoint, version, capabilities, skills, input/output modes and authentication.
3. Represent work as tasks with unique identifiers and explicit states.
4. Exchange messages containing metadata and content parts.
5. Return artefacts as structured outputs, files or streamed parts.
6. Preserve context using a context identifier where multi-step collaboration is required.

## Task lifecycle

Use a minimal lifecycle unless the domain needs more detail:

`submitted -> working -> input_required -> completed | failed | cancelled`

Every state transition should include timestamp, actor, reason and optional artefact references.

## Implementation guidance

For coding agents, keep payloads structured:

```json
{
  "task_id": "task-123",
  "context_id": "ctx-456",
  "skill": "run_tests",
  "input": {"path": "tests/"},
  "constraints": ["no network", "read-only except reports/"],
  "expected_output": "test_report"
}
```

## Guardrails

- Do not expose internal prompts, secrets or private state through agent cards.
- Authenticate server endpoints and restrict discovery where capabilities are sensitive.
- Treat remote agents as untrusted until validated.
- Use timeouts and cancellation for long-running tasks.

## Verification
- [ ] Agent card exists.
- [ ] Task states are explicit.
- [ ] Message schema is versioned.
- [ ] Authentication and authorisation are defined.
- [ ] Failure and cancellation paths are implemented.

