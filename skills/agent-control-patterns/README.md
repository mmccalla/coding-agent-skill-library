# Agent Control Patterns

Use this category when the task is mainly about safety, approval, recovery, evaluation, prioritisation or grounded retrieval.

## Start here when

- the agent needs explicit control loops, safety policies or approval paths;
- the task depends on RAG, ranking, evaluation or failure recovery;
- cost, latency or risk must be constrained deliberately.

## Skills in this category

- `goal-setting-and-monitoring/`
- `exception-handling-and-recovery/`
- `human-in-the-loop/`
- `knowledge-retrieval-rag/`
- `inter-agent-communication-a2a/`
- `resource-aware-optimisation/`
- `reasoning-techniques/`
- `guardrails-safety-patterns/`
- `evaluation-and-monitoring/`
- `prioritisation/`

## Choose the smallest fit

- Start with `guardrails-safety-patterns` for safety-sensitive behaviour.
- Use `knowledge-retrieval-rag` for generic grounded retrieval.
- Use `exception-handling-and-recovery` when retries, rollback or escalation matter.
- Use `evaluation-and-monitoring` when quality must be measured over time.

## Next step

Open `MANIFEST.md` in this folder, then load the smallest relevant `SKILL.md`.
