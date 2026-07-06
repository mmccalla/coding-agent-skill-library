---
name: avoid-fallacies
description: Use when evaluating arguments in plans, ADRs, reviews, security justifications, prioritisation rationales or agent recommendations for logical fallacies that undermine valid engineering conclusions.
aliases:
  - logical-fallacy-check
  - argument-quality-review
  - avoid-logical-fallacies
---

# Avoid Fallacies

## When to use

Use this skill after an initial implementation plan, architecture option set, review comment, risk justification or recommendation exists and quality matters. Apply it when reasoning chains influence merge decisions, security posture, scope cuts, incident root cause, test strategy or tool selection.

Fallacy review complements deterministic validation; invalid rhetoric does not override failing tests or policy gates.

## When not to use

Do not use this skill when the task is purely syntactic or already decided by executable checks alone. Do not treat fallacy spotting as a substitute for reproduction steps, metrics or contract tests.

## Objective

Identify logical fallacies in technical arguments so conclusions follow from valid evidence and explicit premises rather than rhetorical force or missing steps.

## Procedure

1. Extract the claim, stated premises and intended conclusion from the artefact.
2. Check whether the conclusion follows from the premises or smuggles unstated assumptions.
3. Scan for common fallacies using the checklist below; cite the exact phrase or reasoning gap.
4. Repair the argument: add missing premises, narrow the claim, gather evidence, or reject the conclusion.
5. Re-run deterministic checks where the fallacy affected a technical decision (tests, threat model, benchmarks).
6. Record unresolved logical gaps and whether the decision should be deferred or escalated.

## Fallacy checklist (engineering contexts)

- **False dichotomy:** presenting only two options when more exist (for example rewrite vs do nothing).
- **Straw man:** attacking a weaker version of an alternative design or review comment.
- **Hasty generalisation:** inferring universal rules from one repo, one incident or one flaky test run.
- **Appeal to authority / popularity:** choosing a stack or pattern because it is fashionable without local fit evidence.
- **Slippery slope:** claiming a small change inevitably leads to catastrophic outcomes without causal steps.
- **Circular reasoning:** using the conclusion as its own premise (for example “it is safe because we always do it this way”).
- **Post hoc ergo propter hoc:** assuming A caused B because B followed A in time without isolation evidence.
- **Moving the goalposts:** changing success criteria after results are known to preserve a preferred outcome.
- **Red herring:** introducing irrelevant concerns to avoid addressing the actual defect or trade-off.

## Related skills

- `avoid-cognitive-biases` — systematic distortion in judgement under uncertainty
- `reflection-and-verification` — bounded critique and repair loops
- `reasoning-techniques` — decomposition and alternative-path exploration
- `documentation-and-adrs` — durable decision records with explicit options and consequences
- `code-review-and-quality` — review comments grounded in verifiable defects

## References

- [Fallacy (Wikipedia)](https://en.wikipedia.org/wiki/Fallacy)
- [List of fallacies (Wikipedia)](https://en.wikipedia.org/wiki/List_of_fallacies)

## Verification

- [ ] Claim, premises and conclusion are explicitly separated.
- [ ] Identified fallacies reference concrete text or reasoning gaps.
- [ ] Repaired arguments include testable or measurable evidence where possible.
- [ ] Decisions deferred or escalated when logic remains invalid and impact is material.
- [ ] Residual logical uncertainty is documented.
