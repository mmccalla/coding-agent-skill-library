---
name: reasoning-techniques
description: Use when a coding agent needs robust problem solving, explicit decomposition, alternative-path exploration, program-aided reasoning, ReAct loops, or self-correction.
aliases:
  - problem-solving
  - reasoning-patterns
---

# Reasoning Techniques

## When to use

Use this skill for non-trivial coding and analysis tasks where a direct answer is likely to be brittle: debugging, architecture design, algorithm selection, test failure diagnosis, migration planning, security review or multi-step repository changes.

## Objective

Select a reasoning approach that matches task complexity and produces externally verifiable engineering evidence.

## Procedure

1. Restate the objective and constraints.
2. Identify unknowns and gather evidence.
3. Select a reasoning strategy appropriate to risk and complexity.
4. Execute small verifiable steps.
5. Use tool observations to revise the plan.
6. Validate the result with deterministic checks.
7. Present concise rationale, not hidden internal reasoning.

## Technique selection

- Use decomposition for most engineering tasks: break the problem into inspect, plan, edit, test and summarise.
- Use alternative-path exploration when there are several viable designs.
- Use program-aided reasoning for calculations, parsing, data transformation or proof by executable check.
- Use ReAct when tool results should change the next action.
- Use self-correction when tests, static analysis or critique reveal defects.

## Coding-agent guidance

Prefer externally verifiable reasoning over persuasive explanation. For code, the strongest reasoning evidence is a passing test, type check, reproducible command, benchmark, schema validation or diff review.

## Guardrails

- Do not expose private chain-of-thought; provide a concise rationale and evidence summary.
- Do not overthink simple deterministic tasks.
- Do not use LLM reasoning where a compiler, linter, parser or test can decide.
- Do not continue a failing reasoning path without new evidence.

## Related skills

- `logical-fallacy-review` — audit whether premises validly support conclusions in draft arguments
- `cognitive-bias-review` — check judgement distortion in rankings and recommendations
- `reflection-and-verification` — deterministic checks and repair loops before rhetorical critique

## References

- [ReAct: Synergizing Reasoning and Acting](https://arxiv.org/abs/2210.03629)
- [Chain-of-Thought Prompting Elicits Reasoning](https://arxiv.org/abs/2201.11903)

## Verification

- [ ] Objective and constraints are clear.
- [ ] Evidence gathering occurred before major changes.
- [ ] Reasoning method matches task complexity.
- [ ] Tool observations influenced the plan.
- [ ] Final answer includes verification evidence.
