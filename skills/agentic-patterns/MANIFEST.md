# Skills Manifest

This category covers the agent workflow spine: discovery, specification, planning, incremental implementation, context preparation, source grounding and verification.

| Skill | Primary trigger | Avoid when |
|---|---|---|
| skill-discovery-and-selection | Starting a session or choosing which local skill applies | The task is already unambiguous and a specific skill is obvious |
| requirements-elicitation | The user's request is underspecified and intent must be extracted | The goal, audience and constraints are already clear |
| idea-refinement | A rough idea needs structured shaping before implementation | A formal spec already exists |
| prompt-chaining | Sequential multi-stage LLM workflow | Single-step task |
| routing | Conditional dispatch between paths/tools/agents | Criteria are fixed and already handled by ordinary code |
| parallelization | Independent concurrent branches | Shared mutable state or dependent steps |
| reflection-and-verification | Critique, repair, tests and quality gates | No artefact exists yet |
| planning-and-task-decomposition | Complex goal needs ordered implementation plan | Small routine edit |
| spec-driven-development | A feature or significant change needs a decision-complete spec | The work is already captured in a good spec |
| incremental-implementation | A change should land in small, verifiable vertical slices | A one-line edit is clearly sufficient |
| context-engineering | A task needs the right repo, file or document context without noise | The task is isolated and context is already obvious |
| source-driven-development | An implementation decision must be grounded in authoritative source material | The behaviour is already stable and well-known |
| uncertainty-driven-development | A high-stakes or unfamiliar decision should be challenged before coding | The path is obvious and low risk |
| tool-use-and-function-calling | Direct external tool/API/database/code execution | Reusable ecosystem/discovery is required; prefer MCP |
| multi-agent-collaboration | Distinct specialised roles or tools | Single agent plus tools is adequate |
| memory-management | Stateful, persistent or personalised agent behaviour | Stateless task is adequate |
| learning-and-adaptation | Measured improvement over time | No metric/benchmark exists |
| mcp-server-design | Reusable discoverable agent interface to external systems | One-off direct function call is simpler |

## Coverage notes

- Existing local skills already cover `prompt-chaining`, `routing`, `parallelization`, `reflection-and-verification`, `tool-use-and-function-calling`, `planning-and-task-decomposition`, `multi-agent-collaboration`, `memory-management`, `learning-and-adaptation` and `mcp-server-design`.
- This category adds the missing workflow spine skills that make the library usable from session start through specification, implementation and source-grounded review.
