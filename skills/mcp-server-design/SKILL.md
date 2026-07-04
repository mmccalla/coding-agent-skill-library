---
name: mcp-server-design
description: Use when designing, implementing, reviewing or securing Model Context Protocol servers/clients, including tools, resources, prompts, FastMCP servers and agent-friendly API wrappers.
aliases:
  - mcp-server
  - model-context-protocol
---

# MCP Server Design

## When to use

Use this skill when external capabilities should be exposed to agents through a reusable, discoverable interface rather than hard-coded function calls. MCP is suitable for complex, evolving or enterprise tool ecosystems.

For a small fixed set of functions in one app, direct tool/function calling may be simpler.

## Objective

Expose external capabilities through narrow, typed, discoverable, least-privilege MCP interfaces.

## Design principles

- Expose agent-friendly capabilities, not raw legacy APIs.
- Prefer filtered, sorted and scoped operations over bulk unstructured retrieval.
- Return text, JSON or structured data that the consuming agent can parse.
- Separate resources, tools and prompts clearly.
- Use least privilege for every server and tool.

## MCP source-aligned guidance

The MCP server guide distinguishes resources, tools and prompts as the three main server capability types. For stdio transports, never write logs or diagnostics to stdout because stdout carries JSON-RPC messages; send logs to stderr or files instead. Tool inputs should use explicit schemas such as JSON Schema or SDK schema helpers, with clear descriptions and examples so clients can discover and call tools safely.

When reviewing an MCP server, check capability discovery, schema clarity, transport-specific logging, least-privilege authentication, and whether the exposed operation is agent-friendly rather than a raw legacy API wrapper.

Source: [Model Context Protocol — Build a server](https://modelcontextprotocol.io/docs/develop/build-server).

## Procedure

1. Identify the external system capability to expose.
2. Decide whether it is a resource, tool or prompt.
3. Design an agent-friendly schema with clear descriptions and examples.
4. Add authentication, authorisation and allow-listing.
5. Implement the MCP server with explicit errors and typed returns.
6. Add client integration tests for discovery and execution.
7. Threat-model prompt injection, data exfiltration and destructive actions.

## Guardrails

- Do not wrap an API unchanged if it returns data the agent cannot understand.
- Do not expose broad filesystem, shell, database or network access by default.
- Redact secrets and sensitive data from observations.
- Require confirmation for destructive operations.
- Prefer local servers for sensitive data and remote servers for shared scalable tools only when access control is mature.

## OWASP ASI mapping

Use `skills_docs/security/OWASP_ASI_CROSSWALK.md` for the shared risk map.

| ASI risk | MCP control |
| --- | --- |
| ASI02 Tool Misuse | Expose narrow tools with strict schemas, typed errors and documented side effects. |
| ASI03 Identity and Privilege Abuse | Enforce authentication, authorisation, tenant scoping and least-privilege credentials at the server. |
| ASI04 Agentic Supply Chain Vulnerabilities | Pin and review MCP servers, tools, prompts and dynamic discovery sources. |
| ASI07 Insecure Inter-Agent Communication | Authenticate clients, restrict discovery and version tool/resource contracts. |

## Related skills

- `tool-use-and-function-calling` — direct tool calling when MCP is unnecessary
- `guardrails-safety-patterns` — auth, validation and least privilege
- `knowledge-retrieval-rag` — document grounding alongside tools

## References

- Model Context Protocol — Build a server: https://modelcontextprotocol.io/docs/develop/build-server
- Model Context Protocol specification: https://modelcontextprotocol.io/specification/2025-11-25
## Verification

- [ ] Tool/resource/prompt boundaries are clear.
- [ ] Schemas are typed and agent-readable.
- [ ] Discovery works from an MCP client.
- [ ] Authentication and authorisation are enforced.
- [ ] Error responses are structured.
- [ ] Security tests cover injection and unauthorised access.
