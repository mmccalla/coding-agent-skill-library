# OWASP Agentic Security Initiative Crosswalk

This crosswalk maps the OWASP Top 10 for Agentic Applications risk categories to reusable controls in this skill library.

Primary source: [OWASP Top 10 for Agentic Applications - The Benchmark for Agentic Security in the Age of Autonomous AI](https://genai.owasp.org/2025/12/09/owasp-top-10-for-agentic-applications-the-benchmark-for-agentic-security-in-the-age-of-autonomous-ai/).

## ASI Risk Map

| ASI ID | Risk | Control focus | Primary local skills |
| --- | --- | --- | --- |
| ASI01 | Agent Goal Hijack | Treat external instructions as data, constrain planning, validate goals before action. | `guardrails-safety-patterns`, `tool-use-function-calling` |
| ASI02 | Tool Misuse | Least-privilege tools, argument schemas, side-effect gates, structured observations. | `tool-use-function-calling`, `mcp-server-design` |
| ASI03 | Identity and Privilege Abuse | Task-scoped identity, authorisation checks, approval for privileged actions. | `guardrails-safety-patterns`, `mcp-server-design`, `human-in-the-loop` |
| ASI04 | Agentic Supply Chain Vulnerabilities | Pin dependencies, verify tools/servers, review dynamic MCP/A2A components. | `mcp-server-design`, `inter-agent-communication-a2a` |
| ASI05 | Unexpected Code Execution | Sandbox execution, deny generated command execution, review code paths. | `guardrails-safety-patterns`, `tool-use-function-calling` |
| ASI06 | Memory and Context Poisoning | Validate memory writes, preserve provenance, isolate tenants, allow deletion. | `memory-management`, `knowledge-retrieval-rag` |
| ASI07 | Insecure Inter-Agent Communication | Authenticated agent cards, message schemas, task states, trust boundaries. | `inter-agent-communication-a2a`, `mcp-server-design` |
| ASI08 | Cascading Failures | Bounded retries, circuit breakers, fan-out limits, cancellation and rollback. | `inter-agent-communication-a2a`, `exception-handling-and-recovery` |
| ASI09 | Human-Agent Trust Exploitation | Evidence-first approval, uncertainty display, decision packets, audit trails. | `human-in-the-loop`, `agentic-ux-patterns` |
| ASI10 | Rogue Agents | Behavioural telemetry, scoped credentials, kill switches, audit and containment. | `guardrails-safety-patterns`, `inter-agent-communication-a2a` |

## Minimum Control Pattern

- Define the agent goal, authority, allowed tools and prohibited actions before execution.
- Treat user input, retrieved content, memory, tool outputs and peer-agent messages as untrusted until validated.
- Use strict schemas for tool arguments, memory writes, inter-agent messages and generated plans.
- Scope credentials and permissions per task, tenant and environment.
- Require human approval for privileged, destructive, irreversible or high-trust actions.
- Log decisions, tool calls, memory writes, peer messages and approvals without secrets.
- Test abuse cases for prompt injection, unsafe tool use, memory poisoning, identity abuse and cascading failures.
