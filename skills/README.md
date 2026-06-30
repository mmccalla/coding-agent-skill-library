# Skills Library Index

This `skills/` directory is the portable core of the library.

## Mandatory first skill

Before any other skill in this tree, execute:

`apply-laws-of-ai/SKILL.md`

See `../skills_docs/LIBRARY_CONTRACT.md` for the full portable startup order.

## Read in this order

1. Confirm `apply-laws-of-ai` has been executed for the session.
2. `../skills_docs/HOW_TO_FIND_THE_RIGHT_SKILL.md` for routing by task shape.
3. `PACK_METADATA.json` for machine-readable category membership when routing or ingesting.
4. `MANIFEST.md` for the human-readable inventory when needed.
5. The smallest matching `SKILL.md` for the actual operating procedure.

## Directory roles

- `README.md`: quick routing for humans and agents
- `PACK_METADATA.json`: machine-readable pack identity and category membership
- `MANIFEST.md`: fuller inventory and category guidance
- `SKILL.md`: the operative instructions for a specific task shape

## Layout model

- one folder per skill directly under `skills/`
- semantic category grouping lives in `PACK_METADATA.json`; `MANIFEST.md` mirrors it for humans
- `apply-laws-of-ai` remains the mandatory first skill
