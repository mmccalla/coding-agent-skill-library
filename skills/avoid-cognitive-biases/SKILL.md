---
name: avoid-cognitive-biases
description: Use when reviewing plans, recommendations, prioritisation, risk registers, retrospectives or agent outputs for systematic cognitive bias that could distort engineering, security or delivery decisions.
aliases:
  - avoid-cognitive-bias
  - cognitive-bias-check
  - debias-review
---

# Avoid Cognitive Biases

## When to use

Use this skill after an initial plan, recommendation, review, retrospective or architecture proposal exists and quality matters. Apply it when an agent or team is ranking options, interpreting ambiguous evidence, estimating effort, assessing risk, choosing a design, closing an incident, or claiming that a change is low risk.

Use it alongside deterministic verification; bias review does not replace tests, metrics or explicit criteria.

## When not to use

Do not use this skill for purely mechanical tasks with no judgement, ranking or interpretation. Do not invoke it when the only remaining work is executing an already verified checklist with no open decisions.

## Objective

Detect and mitigate common cognitive biases in engineering reasoning so decisions rest on explicit evidence, criteria and reversible checks rather than persuasive narrative alone.

## Procedure

1. Name the decision, recommendation or artefact under review.
2. List the explicit criteria that should govern the outcome (safety, evidence, reversibility, user impact, cost, dependencies).
3. Scan for high-risk biases using the checklist below; record which bias type is suspected and what evidence would falsify it.
4. Seek disconfirming evidence: run a targeted check, alternative query, metric or peer review before accepting the conclusion.
5. Revise the recommendation, defer the decision, or escalate when bias cannot be ruled out and impact is material.
6. Document residual bias risk and the evidence that remains uncertain.

## Bias checklist (coding-agent focus)

- **Confirmation bias:** only citing evidence that supports the preferred option; ignoring failing tests or contradictory logs.
- **Anchoring:** treating the first estimate, first design sketch or first error hypothesis as the anchor for all later reasoning.
- **Availability heuristic:** overweighting recent incidents, vivid failures or memorable chat examples versus base rates.
- **Sunk-cost fallacy:** continuing a path because effort was already invested despite new evidence that another option is better.
- **Bandwagon / authority bias:** accepting a choice because a tool, vendor, senior person or popular pattern said so without local verification.
- **Optimism bias:** assuming integration, migration, performance or security work will be faster or safer than evidence supports.
- **Hindsight bias:** rewriting the narrative after the outcome as if it was obvious all along; weakening learning from surprise.
- **Survivorship bias:** generalising from successful paths while ignoring quarantined, rolled-back or untested alternatives.

## Related skills

- `avoid-fallacies` — invalid argument structure and rhetorical errors
- `reflection-and-verification` — critique loops with deterministic checks
- `reasoning-techniques` — structured problem solving and evidence gathering
- `prioritization` — explicit ranking criteria under constraints
- `risk-management` — risk register, treatment and ownership

## References

- [Cognitive bias (Wikipedia)](https://en.wikipedia.org/wiki/Cognitive_bias)
- [Thinking, Fast and Slow — bounded rationality and bias awareness](https://en.wikipedia.org/wiki/Thinking,_Fast_and_Slow)

## Verification

- [ ] Decision criteria are stated before the final recommendation.
- [ ] At least one disconfirming check or alternative was considered.
- [ ] Suspected biases are named with falsifiable evidence gaps.
- [ ] Material uncertainty is escalated rather than smoothed over.
- [ ] Residual bias risk is recorded when the decision proceeds.
