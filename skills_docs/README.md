# Skills Docs

This directory contains the lightweight documentation layer that helps agents and humans enter the library consistently.

## Read in this order

1. `LIBRARY_CONTRACT.md` for mandatory startup order and portable rules.
2. `SKILL_AUTHORING_GUIDE.md` when creating or revising skills.
3. `HOW_TO_FIND_THE_RIGHT_SKILL.md` for routing by task shape (after executing `apply-laws-of-ai`).
4. `DROP_IN_BOOTSTRAP.md` for the portable installation model.
5. `../skills/README.md` for the structure of the portable flat `skills/` library.
6. `../skills/MANIFEST.md` for the full inventory.

## Document roles

- `LIBRARY_CONTRACT.md`: portable consistency rules and immutable baseline
- `SKILL_AUTHORING_GUIDE.md`: authoring standards, progressive disclosure and validation guidance
- `HOW_TO_FIND_THE_RIGHT_SKILL.md`: fastest routing guide
- `CHANGELOG.md`: phased library changes and validation notes
- `DROP_IN_BOOTSTRAP.md`: opinionated drop-in install model
- `templates/`: optional spec and backlog templates
- `README.md`: docs hub for this directory

## Principle

This directory should not compete with the root `README.md`.

- Root `README.md` explains what the library is and how to install it.
- `skills_docs/` explains how to route through it quickly.
- `skills/` contains the portable operational core.
