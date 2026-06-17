---
name: learning-and-adaptation
description: Use when building measured improvement loops for coding agents, including benchmark-driven repair, preference-data feedback, self-improvement archives, prompt optimisation and pattern learning.
---

# Learning and Adaptation

## When to use

Use this skill when an agent should improve over time based on measured outcomes, user feedback, benchmark results, failed tasks or successful patterns.

Do not allow autonomous self-modification without version control, tests, rollback and human-review boundaries.

## Objective

Improve agent behaviour through measured, versioned, reversible changes rather than unbounded self-modification.

## Procedure

1. Define the performance objective and metric.
2. Capture task trajectories: prompt/input, selected tools, code changes, tests, errors, outputs and user feedback.
3. Store examples in an improvement archive.
4. Analyse failures and successful strategies.
5. Propose a bounded change: prompt, tool, retrieval rule, test, benchmark or code patch.
6. Evaluate the modified agent/system against a fixed benchmark set.
7. Promote only if it improves the target metric without unacceptable regressions.

## Coding guidance

- Use versioned experiment artefacts.
- Keep training/evaluation/test sets separate.
- Prefer prompt/tool/retrieval changes before model fine-tuning.
- Require deterministic tests for self-edited code.
- Record cost, latency and failure rate, not only success rate.

## Verification
- [ ] Metric and benchmark are defined.
- [ ] Improvement data is captured with provenance.
- [ ] Changes are versioned and reversible.
- [ ] Regression tests are run before promotion.
- [ ] Human approval boundary exists for risky changes.
