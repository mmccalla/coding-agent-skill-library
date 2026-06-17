---
name: routing
description: Use when implementing conditional control flow in an agent or coding workflow, including intent classification, tool selection, sub-agent selection, escalation, or language/framework-specific dispatch.
---

# Routing

## When to use

Use this skill when an agent must decide between multiple possible paths based on user intent, repository state, file type, language, confidence, policy or prior tool results.

Use deterministic routing first when criteria are explicit. Use LLM routing only when semantic judgement is genuinely required.

## Objective

Select execution paths predictably using constrained route definitions, confidence thresholds, and safe fallbacks.

## Routing methods

Choose the lightest reliable router:

1. Rule-based router: keywords, file extensions, config flags, explicit metadata.
2. Schema-based router: validated structured task type or command object.
3. Embedding router: semantic similarity between request and capability descriptions.
4. LLM router: nuanced classification with constrained labels.
5. Trained classifier: repeated high-volume routing with labelled examples.

## Procedure

1. Define the allowed routes as an enum.
2. Define route descriptions, entry conditions and prohibited cases.
3. Make the router return only the route, confidence and rationale.
4. Add a fallback route for ambiguity or insufficient confidence.
5. Log route decisions and inputs used.
6. Add regression tests for ambiguous and boundary cases.

## Guardrails

- Never let an LLM invent route names.
- Never execute privileged tools from an uncertain route.
- Escalate or ask for clarification when route confidence is low.
- Keep routing separate from execution so routes are testable.

## Verification
- [ ] Route enum exists.
- [ ] Fallback/clarification route exists.
- [ ] Route confidence threshold is explicit.
- [ ] Unit tests cover each route.
- [ ] Logs capture routing decision, confidence and selected handler.
