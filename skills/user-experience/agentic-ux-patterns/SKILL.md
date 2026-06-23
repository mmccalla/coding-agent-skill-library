---
name: agentic-ux-patterns
description: Designs interfaces for supervising, approving, steering and auditing AI agent actions with evidence and uncertainty surfaced. Use when building agent workflows, approval gates, or audit surfaces.
aliases:
  - ai-agent-ux
  - human-ai-supervision-ux
---

# Agentic UX Patterns

## When to use
Use this skill when designing interfaces for agent recommendations, generated metadata, generated data-quality rules, approval workflows, tool-call previews, workflow plans, autonomous or semi-autonomous actions, evidence review, exception triage or human-in-the-loop decisions.

## Objective

Help users understand, supervise and control agent behaviour safely, with clear visibility of intent, evidence, uncertainty, consequences and approval requirements.

## Procedure

1. Identify the agent action or recommendation.
2. Classify the action risk: low, medium, high or critical.
3. Show what the agent plans to do before material execution.
4. Show why the agent recommends it.
5. Show the evidence used.
6. Show uncertainty, assumptions and missing information.
7. Show expected consequences.
8. Provide approve, reject, edit, request more evidence or escalate actions where appropriate.
9. Require explicit confirmation for high-risk or irreversible actions.
10. Record the user's decision and rationale.

## Required UI patterns

Agent plan preview, tool-call preview, evidence panel, confidence and uncertainty display, approval panel, diff view, audit trail, rollback guidance and escalation path.

## Rules

- Do not present generated output as authoritative without evidence.
- Do not hide which actions were performed by an agent.
- Do not let agents perform privileged writes without policy and approval where required.
- Do not use vague confidence labels without explaining evidence and uncertainty.
- Do not make approval visually easier than rejection or review for high-risk actions.
- Do not bury consequences of approval.
- Do not use dark patterns to encourage acceptance of agent recommendations.

## Optional overlay

For product-specific DataOps/MCP examples, load `skills_docs/overlays/mas-dataops-mcp-overlay.md`.

## Verification

- [ ] Agent action and risk level stated.
- [ ] Evidence, approval mechanism and uncertainty display documented.
- [ ] Auditability considered.
- [ ] Residual safety or UX risks stated.
