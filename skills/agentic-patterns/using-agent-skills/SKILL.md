---
name: using-agent-skills
description: Use when starting a session or deciding which local skill applies; acts as the meta-skill for discovering and loading the smallest relevant skill.
---

# Using Agent Skills

## When to use this skill

Use this skill when starting a new task, resuming context, or choosing among overlapping local skills in this repository.

## Objective

Select the smallest relevant skill or skill combination and explain why it was chosen.

## Operating procedure

1. Read `skills/MANIFEST.md` first.
2. Identify the task shape: discovery, refinement, planning, implementation, verification or release.
3. Pick the smallest relevant local skill set.
4. Prefer the repo's native categories and naming over remote terminology unless the remote term is the clearer local analogue.
5. Load only the supporting docs needed for the task.
6. Re-evaluate if the task shape changes or new constraints appear.

## Rules

- Do not load broad skill sets by default.
- Do not choose a skill based only on its name.
- Do not duplicate planning, verification or release work when an existing local skill already covers it.
- Prefer local analogues when they are more coherent with this repository's structure.

## Verification

Report the selected skill or skills, why they were chosen, what was intentionally not loaded, and any remaining ambiguity.
