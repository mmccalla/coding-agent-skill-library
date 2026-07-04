---
name: uncertainty-driven-development
description: Use when a high-stakes, unfamiliar or overconfident decision should be challenged before implementation proceeds.
aliases:
  - doubt-driven-development
  - assumption-checking
---

# Doubt-Driven Development

## When to use
Use this skill when the first answer feels too easy, the codebase is unfamiliar, or the cost of a wrong assumption is high enough to justify adversarial checking.

## Objective

Turn confidence into evidence by stress-testing the current hypothesis before committing to it.

## Procedure

1. State the leading hypothesis.
2. Identify the claims that hypothesis depends on.
3. Look for evidence that would falsify those claims.
4. Compare alternative explanations or implementations.
5. Reconcile the evidence and choose the smallest defensible path.
6. Record what remains uncertain.

## Rules

- Do not treat the first plausible path as proven.
- Do not skip challenge questions just because the task is familiar.
- Do not hide uncertainty; surface it before implementation.
- Prefer explicit evidence over intuitive certainty.

## Doubt log template

Use this lightweight log before committing to a risky assumption:

```markdown
Hypothesis: <current best answer>
Depends on: <claims that must be true>
Falsifying evidence sought: <file, test, source or counterexample>
Alternative considered: <simpler or safer path>
Decision: proceed / constrain / escalate
Residual uncertainty: <what remains unknown>
```

Keep the log short. Its purpose is to expose decision quality, not to create process theatre.

## References

- ISO 31000 risk management: https://www.iso.org/iso-31000-risk-management.html

## Verification

- [ ] Doubts, assumptions and failure modes logged.
- [ ] Evidence sought or experiments defined.
- [ ] Proceed, constrain or escalate decision stated.
- [ ] Residual uncertainty reported.
