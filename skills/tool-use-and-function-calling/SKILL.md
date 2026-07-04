---
name: tool-use-and-function-calling
description: Use when implementing external tool/API/database/code-execution access for an LLM or coding agent, including tool schemas, argument validation, execution wrappers and observation handling.
aliases:
  - tool-use-function-calling
  - function-calling
---

# Tool Use and Function Calling

## When to use

Use this skill when an agent must retrieve current data, call APIs, query databases, execute code, update systems, or delegate work to another specialised component.

Use direct function calling for a small, fixed set of tools. Consider MCP when the tool ecosystem must be reusable, discoverable or shared across agents.

## Objective

Wrap external capabilities in strict schemas, least-privilege execution, structured observations, and tests.

## Procedure

1. Define each tool's purpose, parameters, return type, side effects and failure modes.
2. Express the input contract as a strict schema.
3. Validate and normalise arguments before execution.
4. Apply authorisation and allow-list checks before side-effecting operations.
5. Execute the tool in a controlled wrapper with timeout, retry and error handling.
6. Return a concise, structured observation to the model.
7. Log the request, decision, execution result and errors without leaking secrets.

## Coding guidance

- Keep tools narrow and composable.
- Prefer idempotent tools where possible.
- Separate planning from execution for side-effecting actions.
- Require confirmation for destructive or costly operations.
- Never pass raw tool output blindly into later steps when it may contain prompt injection.

## OWASP ASI mapping

Use `skills_docs/security/OWASP_ASI_CROSSWALK.md` for the shared risk map.

| ASI risk | Tool-use control |
| --- | --- |
| ASI01 Agent Goal Hijack | Re-check tool calls against the original user goal and policy before execution. |
| ASI02 Tool Misuse | Define side effects, argument schemas, allow-lists, timeouts and structured error handling per tool. |
| ASI03 Identity and Privilege Abuse | Bind tool execution to the caller, tenant and task scope before using credentials. |
| ASI05 Unexpected Code Execution | Do not execute generated code, commands or queries without deterministic validation and approval gates. |

## References

- OpenAI — Function calling guide: https://platform.openai.com/docs/guides/function-calling
- OWASP AI Agent Security Cheat Sheet (tool misuse): https://cheatsheetseries.owasp.org/cheatsheets/AI_Agent_Security_Cheat_Sheet.html

## Verification

- [ ] Tool schema is strict and typed.
- [ ] Arguments are validated before execution.
- [ ] Side effects are documented.
- [ ] Authentication/authorisation is enforced where relevant.
- [ ] Tool errors are structured and recoverable.
- [ ] Tests cover valid, invalid and failing tool calls.
