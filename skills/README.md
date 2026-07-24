# Skills Library Index

This `skills/` directory is the portable core of the library.

## Read in this order

1. `../skills_docs/HOW_TO_FIND_THE_RIGHT_SKILL.md` for routing by task shape (MCP Path A or filesystem Path B).
2. `PACK_METADATA.json` for machine-readable category membership when routing or ingesting.
3. `MANIFEST.md` for the human-readable inventory when needed.
4. The smallest matching `SKILL.md` for the actual operating procedure.
5. Load `apply-laws-of-ai` **only when** the task involves material AI/agent harm risk, unlawful or unauthorised instructions, or explicit safety-law trade-offs — not as a tax on every session.

## Directory roles

- `README.md`: quick routing for humans and agents
- `PACK_METADATA.json`: machine-readable pack identity and category membership
- `MANIFEST.md`: fuller inventory and category guidance
- `SKILL.md`: the operative instructions for a specific task shape

## Layout model

- one folder per skill directly under `skills/`
- semantic category grouping lives in `PACK_METADATA.json`; `MANIFEST.md` mirrors it for humans
- `apply-laws-of-ai` remains available as a control skill when the task shape warrants it
