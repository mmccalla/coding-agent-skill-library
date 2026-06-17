---
name: using-agent-skills
description: Use when starting a session or deciding which local skill applies; acts as the meta-skill for discovering and loading the smallest relevant skill.
---

# Using Agent Skills

## When to use
Use this skill when starting a new task, resuming context, or choosing among overlapping local skills in this repository — **after** executing `apply-laws-of-ai`.

## Objective

Select the smallest relevant skill or skill combination and explain why it was chosen.

## Operating procedure

1. Confirm `skills/agent-control-patterns/apply-laws-of-ai/SKILL.md` has been executed in full for this session.
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

## Verification

Report confirmation that `apply-laws-of-ai` was executed, the selected skill or skills, why they were chosen, what was intentionally not loaded, and any remaining ambiguity.

## Additional guidance

Enhance your skill selection process by adopting these practices:

- **Maintain a searchable index:** Keep the skills manifest up to date and searchable, with clear triggers and descriptions for each skill.
- **Change management:** Define procedures for adding, updating and deprecating skills to maintain consistency and avoid outdated guidance.
- **Automated discovery:** Implement scripts or tooling that analyse task context and suggest relevant skills to reduce reliance on memory.
- **Fallback guidance:** When no existing skill applies, document the gap, consider escalating to a human reviewer and propose the creation of a new skill.
