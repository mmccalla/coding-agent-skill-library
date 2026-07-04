---
name: threat-modeling
description: Identifies assets, trust boundaries, threats and mitigations for systems and agents. Use when designing security-sensitive features, reviewing attack surface, or planning abuse-case tests.
aliases:
  - threat-modelling
  - stride-threat-modeling
---

# Threat Modelling

## When to use

Use when designing or reviewing security-sensitive applications, APIs, data flows, agent tools, MCP/A2A integrations or any change that expands trust boundaries.

## When not to use

- For runtime input/output and tool allow-lists alone, use `guardrails-safety-patterns`.
- For classification, masking and entitlement design alone, use `data-security-and-privacy-architecture`.
- For pipeline controls and SBOM, use `secure-sdlc-and-supply-chain`.

## Objective

Produce a concise threat model that links assets and trust boundaries to threats, mitigations, residual risk and testable abuse cases.

## Procedure

1. Identify assets (data, credentials, models, tools, infrastructure) and actors (users, agents, services, attackers).
2. Draw trust boundaries and data flows across them, including agent tool and retrieval paths.
3. Enumerate threats using STRIDE or an equivalent structured method per boundary and asset.
4. Rate likelihood and impact; prioritise threats that affect safety, privacy or integrity.
5. Define mitigations (prevent, detect, respond) and map each to an owner and control.
6. Record residual risk and whether human approval is required for remaining exposure.
7. Derive abuse-case tests and monitoring signals for the highest-priority threats.
8. Update the model when architecture, tools or data classification change.

## Required outputs

- Asset and actor list
- Trust-boundary diagram or equivalent description
- Threat list with STRIDE (or equivalent) categories
- Mitigations and residual risk
- Abuse-case tests or monitoring checks

## Rules

- Do not treat a prompt instruction as a trust boundary.
- Do not ignore agent tools, memory, retrieval and inter-agent channels.
- Do not list threats without mitigations or explicit acceptance.
- Do not skip abuse-case tests for high-impact threats.

## Related skills

- `guardrails-safety-patterns` — runtime controls after threats are known
- `data-security-and-privacy-architecture` — data controls and privacy obligations
- `secure-sdlc-and-supply-chain` — pipeline and dependency mitigations
- `human-in-the-loop` — approval for residual high-impact risk

## References

- OWASP Threat Modeling: https://owasp.org/www-community/Threat_Modeling
- NIST Secure Software Development Framework (SSDF): https://csrc.nist.gov/projects/ssdf

## Verification

- [ ] Assets, actors and trust boundaries identified.
- [ ] Threats structured (for example STRIDE) and prioritised.
- [ ] Mitigations and residual risk recorded.
- [ ] Abuse-case tests or monitoring defined for top threats.
