---
name: interview-me
description: Use when a request is underspecified and the user's actual goal, constraints or success criteria must be elicited before implementation.
---

# Interview Me

## When to use
Use this skill when the request is ambiguous, has multiple plausible interpretations, or is missing user, scope, constraint or acceptance details.

## Objective

Extract enough intent to make the next implementation decision complete and low risk.

## Procedure

1. State the current understanding of the request.
2. Identify the highest-impact unknown.
3. Ask one focused question at a time.
4. Prefer concrete options when the tradeoff is known.
5. Record constraints, exclusions and success criteria as they become clear.
6. Stop asking once the problem, audience, scope and desired outcome are clear enough to plan.

## Rules

- Do not ask broad, open-ended questions when a narrow one would resolve the ambiguity.
- Do not bundle unrelated decisions into a single question.
- Do not assume requirements that were not confirmed.
- Do not proceed to implementation until the outcome criteria are explicit.

## Example

If the user says `make the agent safer`, ask which risk matters most before planning: tool permissions, prompt injection, data leakage, approval gates or audit evidence. Offer concrete options and recommend the lowest-risk default when enough context exists. Stop interviewing once the next action and acceptance evidence are clear.

## Verification

- [ ] Clarifying questions asked or assumptions stated explicitly.
- [ ] User goal, constraints and success criteria captured.
- [ ] Scope boundaries and out-of-scope items noted.
- [ ] Ready-to-proceed signal or remaining gaps stated.

