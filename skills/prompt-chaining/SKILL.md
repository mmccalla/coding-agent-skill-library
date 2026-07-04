---
name: prompt-chaining
description: Use when implementing or refactoring multi-step LLM workflows where outputs from one step feed later steps; especially useful for extraction, normalisation, generation, code refinement, and report synthesis.
---

# Prompt Chaining

## When to use

Use this skill when a single prompt or function is overloaded with multiple responsibilities. Apply it when the task has distinct stages, when intermediate outputs should be inspected, or when reliability depends on passing structured data between steps.

Do not use it for a trivial one-step task.

## Objective

Decompose overloaded prompts into validated, single-purpose stages with testable hand-offs.

## Procedure

1. Identify each logically independent transformation.
2. Define a narrow contract for each step: input schema, output schema, success criteria and error case.
3. Use JSON, XML, Pydantic, Zod or another schema mechanism for hand-offs.
4. Validate each intermediate output before passing it to the next step.
5. Make every step independently testable.
6. Persist or log intermediate artefacts where debugging or auditability matters.

## Coding guidance

- Prefer pure functions for deterministic pre/post-processing.
- Keep LLM prompts single-purpose.
- Use a named pipeline object or graph rather than ad hoc nested calls.
- Fail fast on malformed intermediate outputs.
- Include unit tests for every stage and an integration test for the whole chain.

## References

- Anthropic — Building effective agents (prompt chaining pattern): https://www.anthropic.com/research/building-effective-agents

## Verification
- [ ] Pipeline stages are named and documented.
- [ ] Each stage has a clear input/output contract.
- [ ] Structured output validation exists between stages.
- [ ] Tests cover at least one happy path and one malformed intermediate output.
- [ ] Logging makes it possible to identify which stage failed.
