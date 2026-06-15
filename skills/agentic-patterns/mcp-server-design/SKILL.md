---
name: mcp-server-design
description: Use when designing, implementing, reviewing or securing Model Context Protocol servers/clients, including tools, resources, prompts, FastMCP servers and agent-friendly API wrappers.
---

# MCP Server Design

## When to use

Use this skill when external capabilities should be exposed to agents through a reusable, discoverable interface rather than hard-coded function calls. MCP is suitable for complex, evolving or enterprise tool ecosystems.

For a small fixed set of functions in one app, direct tool/function calling may be simpler.

## Design principles

- Expose agent-friendly capabilities, not raw legacy APIs.
- Prefer filtered, sorted and scoped operations over bulk unstructured retrieval.
- Return text, JSON or structured data that the consuming agent can parse.
- Separate resources, tools and prompts clearly.
- Use least privilege for every server and tool.

## Implementation pattern

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

## Verification
- [ ] Tool/resource/prompt boundaries are clear.
- [ ] Schemas are typed and agent-readable.
- [ ] Discovery works from an MCP client.
- [ ] Authentication and authorisation are enforced.
- [ ] Error responses are structured.
- [ ] Security tests cover injection and unauthorised access.
