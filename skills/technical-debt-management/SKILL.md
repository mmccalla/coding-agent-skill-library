---
name: technical-debt-management
description: Inventories technical debt, estimates interest, prioritises paydown and tracks remediation. Use when managing sustained engineering debt rather than only ranking the next task.
aliases:
  - tech-debt
  - debt-paydown
  - technical-debt-paydown
---

# Technical Debt Management

## When to use

Use this skill when a codebase, platform or delivery organisation must **inventory technical debt**, estimate the ongoing **interest** (extra cost, risk or slowdown), prioritise **paydown**, and track remediation to completion. Apply it to brittle modules, missing tests, outdated platforms, duplicated logic, unsafe workarounds, incomplete migrations and agent or automation shortcuts that increase future change cost. Use it when debt is recurring and needs a managed backlog, not a one-off tidy-up.

## When not to use

- Do not use this skill only to rank today’s tasks or bugs — use `prioritization` for ordering work; use this skill when debt items need inventory, interest and paydown plans.
- Do not use it as a substitute for writing tests while changing behaviour — use `tdd-practice` for the red-green-refactor loop on active changes.
- Do not use it only to retire a public API or migrate users — use `deprecation-and-migration` for consumer-facing transitions (debt inventory may still list the legacy path).
- Do not use it only for a single review comment — use `code-review-and-quality` for review practice; promote systemic issues into the debt register here.

## Objective

Maintain a visible technical-debt inventory with estimated interest, explicit prioritisation for paydown, owners and verification so debt is reduced deliberately rather than accumulated invisibly.

## Procedure

1. Inventory debt items with location, description, how the debt was incurred and who is affected (developers, operators, users or agents).
2. Estimate **interest**: extra effort per change, incident likelihood, security exposure, onboarding cost or delivery delay if the debt remains.
3. Classify debt (for example design, code quality, test, platform, operational, documentation or security-related) and note dependencies between items.
4. Prioritise paydown using interest, risk, strategic alignment and cost of remediation—not only developer preference.
5. Define a paydown plan: smallest safe slice, success criteria, tests or checks that prove improvement, and whether work is embedded in feature delivery or scheduled explicitly.
6. Execute paydown in small, reversible steps; avoid large rewrites without incremental verification.
7. Update the inventory: mark paid-down items, record residual debt and prevent reintroduction via review or lint/policy checks where practical.
8. Report interest reduced and remaining high-interest debt to stakeholders on a regular cadence.

## Required outputs or templates

```markdown
# Technical debt register entry

| Field | Value |
|---|---|
| Debt ID | DEBT-NNN |
| Title | <short name> |
| Location | <paths, services or modules> |
| Description | <what is wrong> |
| Interest | <ongoing cost or risk if unpaid> |
| Category | design / test / platform / security / operational / other |
| Paydown approach | <smallest safe remediation> |
| Effort | <rough size> |
| Priority | <rank or score> |
| Owner | <role> |
| Success criteria | <tests, metrics or behaviours> |
| Status | identified / planned / in progress / paid down / accepted |

## Paydown slice
- Scope for this iteration:
- Verification:
- Residual debt after slice:
```

## Rules

- Do not equate a prioritised task list with a debt register that tracks interest and paydown.
- Do not schedule large rewrites as the default paydown strategy when incremental improvement works.
- Do not accept high-interest security or data-integrity debt without explicit authority and review cadence.
- Do not remove “dead” code or paths without checking dependents and tests.
- Do not claim paydown complete without success criteria (tests, metrics or operational evidence).
- Do not use debt language to block all delivery; balance interest reduction with committed outcomes.

## Related skills

- `prioritization`
- `tdd-practice`
- `deprecation-and-migration`
- `code-review-and-quality`

## References

- Martin Fowler on technical debt: https://martinfowler.com/bliki/TechnicalDebt.html
- Martin Fowler on technical debt quadrant: https://martinfowler.com/bliki/TechnicalDebtQuadrant.html

## Verification

- [ ] Debt inventory entries exist for material items.
- [ ] Interest (ongoing cost or risk) is estimated.
- [ ] Paydown priority and owner are assigned.
- [ ] Paydown slices have success criteria and verification.
- [ ] Register status is updated after remediation.
- [ ] High-interest residual debt is visible to stakeholders.
