---
name: parallelisation
description: Use when independent coding-agent tasks, LLM calls, file analyses, API calls or sub-agents can safely run concurrently to reduce latency without creating ordering dependencies.
---

# Parallelisation

## When to use

Use this skill only when tasks are independent and the result can be merged deterministically. Typical cases include analysing multiple files, querying independent sources, generating alternatives, running independent validations, or executing independent research branches.

Do not parallelise when tasks depend on each other, share mutable state unsafely, or when debugging simplicity is more important than latency.

## Implementation pattern

1. Identify independent tasks and their inputs.
2. Define per-task timeout, retry and error semantics.
3. Run tasks concurrently using the platform's standard concurrency primitive.
4. Collect results into a typed aggregate object.
5. Merge results with a deterministic reducer.
6. Preserve partial failures where useful rather than discarding all progress.

## Coding guidance

- In Python, prefer `asyncio` for I/O-bound work and processes for CPU-bound work.
- Make shared state immutable or protected.
- Include cancellation and timeout handling.
- Use bounded concurrency to avoid rate-limit or resource exhaustion.
- Record per-branch timings and errors.

## Verification
- [ ] Independence assumptions are documented.
- [ ] Bounded concurrency is used.
- [ ] Timeouts and partial failures are handled.
- [ ] Merge step is deterministic and tested.
- [ ] Logs identify each parallel branch.

## Additional guidance

Enhance parallel execution robustness with these practices:

- **Dependency mapping:** Document task dependencies to ensure only truly independent tasks are run concurrently.
- **Risk‑based prioritisation:** Allocate concurrency resources based on risk and business impact, giving high‑impact tasks appropriate attention.
- **Explicit task contracts:** Provide clear descriptions, expected outputs and failure‑handling instructions for each parallel branch.
- **Retry and error handling:** Incorporate retry logic and error‑handling strategies so that branch failures can be recovered gracefully.
- **Consistent integration:** Use standard naming conventions and interfaces when merging results to simplify integration and reduce confusion.
