---
name: reasoning-techniques
description: Use when a coding agent needs robust problem solving, explicit decomposition, alternative-path exploration, program-aided reasoning, ReAct loops, or self-correction.
---

# Reasoning Techniques

## When to use

Use this skill for non-trivial coding and analysis tasks where a direct answer is likely to be brittle: debugging, architecture design, algorithm selection, test failure diagnosis, migration planning, security review or multi-step repository changes.

## Technique selection

- Use decomposition for most engineering tasks: break the problem into inspect, plan, edit, test and summarise.
- Use alternative-path exploration when there are several viable designs.
- Use program-aided reasoning for calculations, parsing, data transformation or proof by executable check.
- Use ReAct when tool results should change the next action.
- Use self-correction when tests, static analysis or critique reveal defects.

## Core pattern

1. Restate the objective and constraints.
2. Identify unknowns and gather evidence.
3. Select a reasoning strategy appropriate to risk and complexity.
4. Execute small verifiable steps.
5. Use tool observations to revise the plan.
6. Validate the result with deterministic checks.
7. Present concise rationale, not hidden internal reasoning.

## Coding-agent guidance

Prefer externally verifiable reasoning over persuasive explanation. For code, the strongest reasoning evidence is a passing test, type check, reproducible command, benchmark, schema validation or diff review.

## Guardrails

- Do not expose private chain-of-thought; provide a concise rationale and evidence summary.
- Do not overthink simple deterministic tasks.
- Do not use LLM reasoning where a compiler, linter, parser or test can decide.
- Do not continue a failing reasoning path without new evidence.

## Verification
- [ ] Objective and constraints are clear.
- [ ] Evidence gathering occurred before major changes.
- [ ] Reasoning method matches task complexity.
- [ ] Tool observations influenced the plan.
- [ ] Final answer includes verification evidence.

