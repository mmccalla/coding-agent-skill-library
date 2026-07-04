---
name: test-strategy
description: Defines risk-based test strategy, test pyramid, levels, automation versus manual balance and exit criteria. Use when planning how a system or change will be tested across the delivery lifecycle.
aliases:
  - testing-strategy
  - risk-based-testing
  - test-pyramid-strategy
  - quality-test-plan
---

# Test Strategy

## When to use

Use this skill when planning how quality will be proven for a product, service, agent workflow or material change: risk-based prioritisation, test pyramid balance, test levels, what to automate versus exercise manually, environments, data and explicit exit criteria before release or hand-off.

## When not to use

- Use `tdd-practice` for the red–green–refactor loop on a single behaviour unit, not programme-level strategy.
- Use `bdd-practice` alone for business-readable scenarios and acceptance examples without overall level and risk planning.
- Use `browser-testing-with-devtools` for concrete browser evidence and UI interaction checks.
- Use `evaluation-and-monitoring` for model/agent metrics, drift and operational monitoring rather than classical test levels.
- Use `reflection-and-verification` for critique–repair loops on a specific artefact, not a delivery-wide test strategy.

## Objective

Produce a risk-based test strategy that places the right checks at the right level of the test pyramid, balances automation and manual exploration, and states exit criteria so teams know when testing is sufficient to release or escalate.

## Procedure

1. Identify scope, quality objectives and stakeholders. List critical user journeys, compliance obligations and failure modes that matter most.
2. Perform risk-based prioritisation: rate features and interfaces by impact and likelihood of failure; allocate deeper testing to higher risk.
3. Map the test pyramid: favour many fast unit and contract tests, fewer integration tests, and a thin set of end-to-end or exploratory checks. Justify any inversion (for example UI-heavy legacy systems).
4. Assign levels: unit, component, contract, integration, end-to-end, performance, security and accessibility as applicable. State owners and tools per level.
5. Decide automation versus manual: automate deterministic, repetitive, regression-prone checks; reserve manual or exploratory testing for usability, novel risk and judgement-heavy paths.
6. Define environments, test data, secrets handling, isolation and how flaky tests are quarantined or fixed.
7. Set exit criteria: required suites green, coverage or risk items closed, known defects accepted with owners, and any mandatory non-functional evidence.
8. Plan feedback into delivery: when tests run (PR, merge, nightly, pre-release) and how failures block or inform release decisions.

## Required outputs

```markdown
# Test strategy: <system or change>

## Scope and quality objectives
## Risk-based priorities
| Area | Risk (impact × likelihood) | Test depth |

## Test pyramid
- Unit / component:
- Contract / integration:
- End-to-end / exploratory:
- Rationale for balance:

## Levels and ownership
| Level | Scope | Owner | Automation |

## Automation vs manual
- Automate:
- Manual / exploratory:

## Environments and data
## Exit criteria
- [ ] ...
## Residual risks and known gaps
```

## Rules

- Do not equate “we use TDD” with a complete test strategy.
- Do not invert the test pyramid without documenting cost and risk.
- Do not treat flaky end-to-end suites as a substitute for fast lower-level tests.
- Do not omit exit criteria; “test until confident” is not auditable.
- Do not store production secrets in test fixtures or logs.
- Do not claim coverage percentage alone proves risk is managed.

## Related skills

- `tdd-practice` — red–green–refactor for behaviour changes
- `bdd-practice` — business-readable acceptance scenarios
- `browser-testing-with-devtools` — browser-level evidence
- `evaluation-and-monitoring` — metrics and operational evaluation
- `reflection-and-verification` — critique and repair loops

## References

- ISTQB risk-based testing overview: https://www.istqb.org/
- Martin Fowler on the test pyramid: https://martinfowler.com/articles/practical-test-pyramid.html
- Google Testing Blog (testing strategies): https://testing.googleblog.com/

## Verification

- [ ] Scope and quality objectives are explicit.
- [ ] Risk-based priorities drive test depth.
- [ ] Test pyramid (or justified alternative) is documented.
- [ ] Levels, ownership and automation versus manual split are clear.
- [ ] Exit criteria are measurable and agreed.
- [ ] Residual risks and gaps are recorded.
