---
name: code-review-and-quality
description: Use when reviewing code before merge to assess correctness, tests, maintainability, security and user impact.
---

# Code Review and Quality

## When to use
Use this skill when reviewing a diff written by yourself, another agent or a human, or when deciding whether a change is ready to merge.

## Objective

Identify correctness risks, test gaps, maintainability problems, hidden regressions and security concerns before the change lands.

## Operating procedure

1. Read the change in the context of the surrounding code.
2. Identify the intended behaviour and any behaviour change.
3. Check correctness, edge cases, tests and public contracts.
4. Assess maintainability, duplication and naming only after correctness is clear.
5. Classify findings by severity and impact.
6. Suggest the smallest fix or follow-up needed to close each finding.

## Rules

- Do not review in isolation from the code the diff touches.
- Do not let style preferences outrank correctness or safety.
- Do not suppress a real issue just because the diff is small.
- Do not approve a change without checking the relevant tests or evidence.

## Related skills

- `tdd-practice` — tests as review evidence
- `git-workflow-and-versioning` — reviewable atomic changes
- `guardrails-safety-patterns` — security findings in review

## Verification

- [ ] Findings listed with severity and evidence.
- [ ] Tests or checks run reported.
- [ ] Correctness assessed before style concerns.
- [ ] Residual risks requiring follow-up stated.

## Additional guidelines

Improve code review effectiveness by considering the following:

- **Risk‑based triage:** Prioritise review comments based on their severity and potential impact, addressing critical issues before stylistic or minor suggestions.
- **Small, coherent changes:** Encourage small, coherent pull requests accompanied by clear context so that reviewers can focus on the intended behaviour.
- **Baseline automation:** Run automated baseline checks—such as linting, unit tests and secret scanning—before human review to offload trivial findings.
- **Evidence‑based discussion:** When disagreeing with feedback, provide evidence‑based reasoning and suggest alternative solutions constructively.
- **Review metrics:** Track review metrics (cycle time, number of comments) to identify bottlenecks and continuously improve the review process.
