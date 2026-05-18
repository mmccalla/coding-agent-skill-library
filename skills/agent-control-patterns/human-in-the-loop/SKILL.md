---
name: human-in-the-loop
description: Use when a coding agent must request approval, expert judgement, clarification, review, or intervention before proceeding with high-risk or ambiguous work.
---

# Human-in-the-Loop

## When to use

Use this skill when automation alone is insufficient because the task is ambiguous, high-impact, irreversible, privacy-sensitive, legally/materially significant, or requires domain judgement.

## Intervention points

Ask for human input before:

- deleting, overwriting or migrating important data;
- changing security, authentication, permissions or secrets;
- making architectural choices with material trade-offs;
- accepting low-confidence model output;
- merging code when tests or validation are incomplete;
- exposing sensitive data to external services.

## Core pattern

1. Detect the need for human judgement using confidence, impact, reversibility and policy checks.
2. Pause execution before the risky action.
3. Present a concise decision packet: context, options, recommendation, trade-off, risk and required approval.
4. Resume only after clear approval or revised instructions.
5. Record the decision and rationale in the implementation notes.

## Decision packet template

```markdown
Decision required: <short title>
Context: <what led to this point>
Options: A / B / C
Recommendation: <preferred option>
Main trade-off: <cost of the recommendation>
Risk if wrong: <consequence>
Approval needed: <exact action>
```

## Guardrails

- Do not bury approval requests in long prose.
- Do not ask for approval for trivial reversible steps.
- Do not proceed on implied approval for destructive or privileged operations.
- Redact secrets and minimise personal data in review packets.

## Output checklist

- [ ] HITL trigger is explicit.
- [ ] Options are clear and bounded.
- [ ] Recommendation and risk are stated.
- [ ] Approval action is unambiguous.
- [ ] Decision is recorded.

