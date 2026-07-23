---
name: documentation-and-adrs
description: Use when a change needs durable documentation, an architecture decision record or maintainership guidance.
aliases:
  - architecture-decision-record
  - architecture-decision-records
  - api-change-adr
  - docs-and-adrs
  - write-adr
---

# Documentation and ADRs

## When to use

Use this skill when a decision needs to be captured for future maintainers, or when the change alters repository conventions, usage guidance or release behaviour.

## Objective

Capture the reason for the change, the options considered and the consequences so future work remains coherent.

## Procedure

1. State the decision or guidance that needs recording.
2. Summarise the context and constraints.
3. Record the chosen option and why it won.
4. List meaningful alternatives that were rejected.
5. Capture any follow-up or compatibility notes.
6. Link the documentation to the files or skills it explains.

## Rules

- Do not write prose that does not help a future maintainer make a decision.
- Do not document implementation trivia when the architectural why matters more.
- Do not let docs drift away from the actual repo structure.
- Do not duplicate the same explanation in multiple places without a reason.

## Example

For a validator rule change, document why the rule exists, which files it affects, what alternatives were considered and how maintainers validate compliance. Avoid repeating the implementation details from the script; focus on the decision, consequences and how future contributors should apply the rule.

## References

- [Documenting Architecture Decisions (Michael Nygard)](https://cognitect.com/blog/2011/11/15/documenting-architecture-decisions)
- [Diátaxis documentation framework](https://diataxis.fr/)

## Verification

- [ ] Documentation or ADR artefacts produced listed.
- [ ] Decision, context and consequences captured.
- [ ] Alternatives considered noted.
- [ ] Residual documentation gaps stated.
