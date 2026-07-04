---
name: skill-discovery-and-selection
description: Use when starting a session or deciding which local skill applies; acts as the meta-skill for discovering and loading the smallest relevant skill.
aliases:
  - using-agent-skills
  - skill-routing
---

# Using Agent Skills

## When to use

Use this skill when starting a new task, resuming context, or choosing among overlapping local skills in this repository — **after** executing `apply-laws-of-ai`.

## Objective

Select the smallest relevant skill or skill combination and explain why it was chosen.

## Procedure

1. Confirm `skills/apply-laws-of-ai/SKILL.md` has been executed in full for this session.
2. Read `skills_docs/HOW_TO_FIND_THE_RIGHT_SKILL.md` for routing by task shape.
3. Open `skills/MANIFEST.md` or the relevant category `MANIFEST.md` when inventory detail is needed.
4. Identify the task shape: discovery, refinement, planning, implementation, verification or release.
5. Pick the smallest relevant local skill set.
6. Prefer the repo's native categories and naming over remote terminology unless the remote term is the clearer local analogue.
7. Load only the supporting docs needed for the task.
8. Re-evaluate if the task shape changes or new constraints appear.

## Rules

- Never skip or defer `apply-laws-of-ai`.
- Do not load broad skill sets by default.
- Do not choose a skill based only on its name.
- Do not duplicate planning, verification or release work when an existing local skill already covers it.
- Prefer local analogues when they are more coherent with this repository's structure.

## Related skills

- `apply-laws-of-ai` — mandatory baseline before routing
- `planning-and-task-decomposition` — multi-step work decomposition
- `requirements-elicitation` — underspecified requests

## References

- [Anthropic — Equipping agents for the real world with Agent Skills](https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills)

## Verification

- [ ] `apply-laws-of-ai` execution confirmed.
- [ ] Selected skill(s) and selection rationale reported.
- [ ] Intentionally excluded skills noted.
- [ ] Remaining ambiguity or re-check triggers stated.
