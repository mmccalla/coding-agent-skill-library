# Skills Manifest

| Skill | Primary trigger | Avoid when |
|---|---|---|
| prompt-chaining | Sequential multi-stage LLM workflow | Single-step task |
| routing | Conditional dispatch between paths/tools/agents | Criteria are fixed and already handled by ordinary code |
| parallelisation | Independent concurrent branches | Shared mutable state or dependent steps |
| reflection-and-verification | Critique, repair, tests and quality gates | No artefact exists yet |
| tool-use-function-calling | Direct external tool/API/database/code execution | Reusable ecosystem/discovery is required; prefer MCP |
| planning-and-task-decomposition | Complex goal needs ordered implementation plan | Small routine edit |
| multi-agent-collaboration | Distinct specialised roles or tools | Single agent plus tools is adequate |
| memory-management | Stateful, persistent or personalised agent behaviour | Stateless task is adequate |
| learning-and-adaptation | Measured improvement over time | No metric/benchmark exists |
| mcp-server-design | Reusable discoverable agent interface to external systems | One-off direct function call is simpler |
