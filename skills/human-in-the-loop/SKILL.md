---
name: human-in-the-loop
description: Use when a coding agent must request approval, expert judgement, clarification, review, or intervention before proceeding with high-risk or ambiguous work.
---

# Human-in-the-Loop

## When to use

Use this skill when automation alone is insufficient because the task is ambiguous, high-impact, irreversible, privacy-sensitive, legally/materially significant, or requires domain judgement.

## Objective

Introduce human judgement at the right decision points without slowing safe, reversible work unnecessarily. Approval must use **architectural enforcement outside the model** (tool dispatcher, policy engine or workflow gate), not prompt-only instructions the agent can ignore.

## Procedure

1. Detect the need for human judgement using confidence, impact, reversibility and policy checks.
2. Pause execution before the risky action at a gate enforced outside the LLM (dispatcher or policy engine refuses execution until approval clears).
3. Present a concise decision packet: context, options, recommendation, trade-off, risk and required approval.
4. Resume only after clear approval or revised instructions recorded by the gate.
5. Record the decision and rationale in the implementation notes.

## Intervention points

Ask for human input before:

- deleting, overwriting or migrating important data;
- changing security, authentication, permissions or secrets;
- making architectural choices with material trade-offs;
- accepting low-confidence model output;
- merging code when tests or validation are incomplete;
- exposing sensitive data to external services.

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
- Do not rely on prompt text alone as the approval control; enforce the gate outside the model.
- Redact secrets and minimise personal data in review packets.

## OWASP ASI09 controls

Use `skills_docs/security/OWASP_ASI_CROSSWALK.md` for the shared risk map. For ASI09 Human-Agent Trust Exploitation, approval requests must include evidence, uncertainty, consequences, alternatives and the exact action being authorised.

## Related skills

- `apply-laws-of-ai` — escalation aligned with safety laws
- `guardrails-safety-patterns` — policy gates before human review
- `agentic-ux-patterns` — approval and evidence UI patterns

## References

- OWASP Top 10 for Agentic Applications (ASI09 Human-Agent Trust Exploitation): https://genai.owasp.org/resource/owasp-top-10-for-agentic-applications-for-2026/
- OWASP AI Agent Security Cheat Sheet (HITL controls): https://cheatsheetseries.owasp.org/cheatsheets/AI_Agent_Security_Cheat_Sheet.html

## Verification

- [ ] HITL trigger is explicit.
- [ ] Options are clear and bounded.
- [ ] Recommendation and risk are stated.
- [ ] Approval action is unambiguous.
- [ ] Decision is recorded.
