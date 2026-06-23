# Agent Control Patterns

Use this category when the task is mainly about safety, approval, recovery, evaluation, prioritization or grounded retrieval.

## Mandatory baseline (every session)

Execute **`apply-laws-of-ai/SKILL.md` first** — before routing, planning, edits, or any other skill. It is the immutable safety baseline for all agent reasoning. See `skills_docs/LIBRARY_CONTRACT.md`.

## Start here when

- the agent needs explicit control loops, safety policies or approval paths;
- the task depends on RAG, ranking, evaluation or failure recovery;
- cost, latency or risk must be constrained deliberately.

## Skills in this category

- `apply-laws-of-ai/` — **mandatory first** at every session
- `goal-setting-and-monitoring/`
- `exception-handling-and-recovery/`
- `human-in-the-loop/`
- `knowledge-retrieval-rag/`
- `inter-agent-communication-a2a/`
- `resource-aware-optimization/`
- `reasoning-techniques/`
- `guardrails-safety-patterns/`
- `evaluation-and-monitoring/`
- `prioritization/`

## Choose the smallest fit

- Start with `guardrails-safety-patterns` for safety-sensitive behaviour.
- Use `knowledge-retrieval-rag` for generic grounded retrieval.
- Use `exception-handling-and-recovery` when retries, rollback or escalation matter.
- Use `evaluation-and-monitoring` when quality must be measured over time.

## Next step

Open `MANIFEST.md` in this folder, then load the smallest relevant `SKILL.md`.
