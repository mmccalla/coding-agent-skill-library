---
name: context-engineering
description: Use when a task needs the right repository, file and document context assembled without unnecessary noise.
aliases:
  - context-selection
  - context-assembly
---

# Context Engineering

## When to use

Use this skill when starting a session, switching tasks, or preparing context for a workflow that depends on the right local files and guidance.

## Objective

Load enough context to work accurately while avoiding irrelevant material that dilutes attention or exceeds the useful scope.

## Procedure

1. Identify the authoritative sources for the task.
2. Load the smallest relevant docs, manifests and files.
3. Summarise conventions instead of copying whole files when possible.
4. Keep task-specific context separate from general repository guidance.
5. Refresh context only when the task shape or evidence changes.

## Rules

- Do not paste the whole repository into context by default.
- Do not rely on stale assumptions when better source files exist.
- Do not mix instructions, evidence and speculation without labelling them.
- Prefer explicit file references over memory.

## Example

For a validator change, load the validator, its tests, the library contract and only the skill files affected by the new rule. Do not load unrelated UX or reliability skills unless the failing evidence points there. If a later test reveals more affected files, refresh context and record why the scope expanded.

## References

- [Anthropic — Equipping agents with skills (progressive disclosure / context)](https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills)

## Verification

- [ ] Context sources selected and justified.
- [ ] Excluded or truncated context noted.
- [ ] Token or noise trade-offs stated.
- [ ] Residual context gaps or risks reported.
