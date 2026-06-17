---
name: reflection-and-verification
description: Use when generated code, plans, tests, prompts or architecture need critique, repair and verification before completion; especially for coding tasks requiring self-review, test-driven repair or quality gates.
---

# Reflection and Verification

## When to use

Use this skill after an initial implementation, plan or generated artefact exists and quality matters. Apply it to code generation, debugging, planning, documentation, prompts, tests and architecture proposals.

Reflection must not replace deterministic verification. Run tests, linters, type checks and static analysis wherever available.

## Implementation pattern

1. Produce an initial artefact.
2. Evaluate it against explicit criteria: correctness, completeness, security, maintainability, performance and instruction adherence.
3. Use deterministic checks first: tests, type checks, linters, formatters, schema validators.
4. Use LLM critique for gaps not covered by deterministic checks.
5. Apply targeted fixes.
6. Repeat until checks pass or a clear stopping condition is reached.

## Coding guidance

- Keep critique separate from implementation.
- Do not rewrite working code wholesale when a targeted patch is sufficient.
- Record failed checks and fixes.
- Stop after a bounded number of repair cycles and report unresolved failures.

## Related skills

- `tdd-practice` — executable verification first
- `code-review-and-quality` — human or agent review loop
- `apply-laws-of-ai` — safety gates before claiming completion

## Verification
- [ ] Acceptance criteria are explicit.
- [ ] Tests or validation checks were run.
- [ ] Failures were repaired or reported.
- [ ] Final answer includes residual risks.
- [ ] No unverified claim of success is made.

## Additional guidance

Ensure robust verification by incorporating these practices:

- **Definition‑of‑Done alignment:** Align verification criteria with the team’s Definition of Done, including functional and non‑functional requirements.
- **Evidence specification:** Specify what evidence is required for different claim types—such as passing unit tests, performance benchmarks, security scans or updated documentation.
- **Automated verification:** Use continuous integration pipelines to automate testing, static analysis and deployment checks, reducing human error.
- **Evidence review:** Have peers review verification evidence or rely on automated validators to reduce confirmation bias before claiming success.
