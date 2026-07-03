---
name: exception-handling-and-recovery
description: Use when building resilient agent workflows that must detect failures, retry safely, degrade gracefully, rollback state, or escalate to a human/operator.
---

# Exception Handling and Recovery

## When to use

Use this skill when an agent calls tools, edits files, executes code, uses network services, invokes models, or performs any multi-step workflow where failures are likely.

## Objective

Make failures explicit, recover safely where possible, and preserve enough evidence to repair or escalate.

## Procedure

1. Detect errors early: tool exceptions, malformed outputs, timeout, unavailable service, failed tests, invalid schema, unexpected state.
2. Classify the failure as transient, deterministic, recoverable, unsafe, or unknown.
3. Select a recovery strategy: retry, fallback, rollback, repair, degrade, ask clarification, or escalate.
4. Preserve evidence: error message, stack trace, command, inputs, outputs and affected files.
5. Resume only from a known-good state.

## Core pattern

1. Detect errors early: tool exceptions, malformed outputs, timeout, unavailable service, failed tests, invalid schema, unexpected state.
2. Classify the failure as transient, deterministic, recoverable, unsafe, or unknown.
3. Select a recovery strategy: retry, fallback, rollback, repair, degrade, ask clarification, or escalate.
4. Preserve evidence: error message, stack trace, command, inputs, outputs and affected files.
5. Resume only from a known-good state.

## Recovery strategies

- Retry transient failures with bounded attempts and back-off.
- Use fallbacks for unavailable services, models or tools.
- Roll back partial file or state changes before trying a different approach.
- Reduce scope when a full solution is blocked.
- Escalate when credentials, permissions, destructive actions or ambiguous requirements are involved.

## Implementation guidance

Wrap risky operations with typed outcomes:

```python
@dataclass
class OperationResult:
    ok: bool
    value: Any | None = None
    error_type: str | None = None
    error_message: str | None = None
    recoverable: bool = False
```

Never hide failures. Convert raw exceptions into actionable diagnostics and include the next safe step.

## Guardrails

- Never retry indefinitely.
- Never retry a destructive operation unless it is idempotent or explicitly safe.
- Never proceed after failed validation without documenting the risk.
- Prefer controlled failure over silent corruption.

## Verification
- [ ] Failure modes are identified.
- [ ] Retry and fallback limits are explicit.
- [ ] Rollback or cleanup path exists.
- [ ] Errors are logged with enough context.
- [ ] Escalation condition is defined.

