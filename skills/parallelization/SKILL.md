---
name: parallelization
description: Use when independent coding-agent tasks, LLM calls, file analyses, API calls or sub-agents can safely run concurrently to reduce latency without creating ordering dependencies.
aliases:
  - parallelisation
  - parallel-execution
---

# Parallelisation

## When to use

Use this skill only when tasks are independent and the result can be merged deterministically. Typical cases include analysing multiple files, querying independent sources, generating alternatives, running independent validations, or executing independent research branches.

Do not parallelise when tasks depend on each other, share mutable state unsafely, or when debugging simplicity is more important than latency.

## Objective

Run only independent work concurrently and merge results deterministically with bounded resource use.

## Procedure

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

## References

- LangGraph — map-reduce / fan-out parallelism: https://langchain-ai.github.io/langgraph/how-tos/map-reduce/

## Verification
- [ ] Independence assumptions are documented.
- [ ] Bounded concurrency is used.
- [ ] Timeouts and partial failures are handled.
- [ ] Merge step is deterministic and tested.
- [ ] Logs identify each parallel branch.
