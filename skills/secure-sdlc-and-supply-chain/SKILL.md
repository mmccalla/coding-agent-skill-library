---
name: secure-sdlc-and-supply-chain
description: Applies NIST SSDF (SP 800-218) secure development and supply-chain controls including SBOM, pinning, secrets, SAST and MCP/A2A integrity. Use when hardening builds, dependencies, CI/CD, releases or agent tool supply chains.
aliases:
  - secure-sdlc
  - software-supply-chain-security
  - ssdf-practice
  - nist-800-218
---

# Secure SDLC and Supply Chain

## When to use

Use this skill when establishing or changing how software is prepared, protected, produced and released: dependency management, build pipelines, artefact integrity, secret handling, static analysis, SBOM generation, or the supply chain of MCP servers, A2A agents and third-party tools that coding agents invoke.

## When not to use

- Use `threat-modeling` to identify STRIDE threats and trust boundaries before selecting controls.
- Use `guardrails-safety-patterns` for runtime agent policy, input/output checks and tool allow-lists.
- Use `ci-cd-and-automation` for pipeline structure, permissions and job design without a full SSDF/supply-chain focus.
- Use `release-engineering-and-progressive-delivery` for canaries, rollback and progressive exposure once artefacts are already trustworthy.

## Objective

Embed NIST SSDF (SP 800-218) practices into the development and delivery path so source, dependencies, builds, secrets, scans and agent-facing supply chains remain integrity-preserving, auditable and least-privilege by default.

## Procedure

1. Map the change to SSDF practice groups: prepare the organisation (standards, approved sources), protect software (source and build integrity), produce well-secured software (secure coding and review), and respond to vulnerabilities (fix and regression).
2. Inventory third-party and first-party dependencies, actions, base images, MCP servers, A2A peers and plugins. Prefer approved registries and signed or verified sources where the project supports them.
3. Pin versions for packages, container images and GitHub Actions (or equivalent). Record justification when floating tags are unavoidable and schedule follow-up.
4. Keep secrets out of source, logs and model context. Use secret stores, short-lived credentials and rotation paths; fail closed when secrets are missing rather than embedding defaults.
5. Enable or preserve SAST, dependency scanning and secret scanning in CI. Treat findings as release-relevant; do not disable gates to force a green build.
6. Produce or update an SBOM for released artefacts and retain it with the build provenance needed for incident response.
7. For MCP/A2A supply chain: pin server versions or digests, restrict tool permissions, validate schemas, log peer identity and refuse unreviewed remote tools that can execute privileged actions.
8. Document how vulnerabilities are triaged, fixed and regression-tested, including who owns response for agent-tool dependencies.

## Required outputs

```markdown
# Secure SDLC / supply-chain checklist: <change>

## SSDF mapping
- Prepare:
- Protect:
- Produce:
- Respond:

## Dependencies and pins
| Component | Version / digest | Source | Notes |

## Secrets and credentials
- Storage:
- Rotation:
- Log / context redaction:

## Scanning and gates
- SAST:
- Dependency / secret scan:
- Release blockers:

## SBOM and provenance
- SBOM location:
- Build identity / attestation (if any):

## MCP / A2A supply chain
- Peers and versions:
- Permission scope:
- Validation and audit:

## Residual risks
```

## Rules

- Do not commit secrets, tokens or private keys.
- Do not unpin or broaden dependencies without recording risk and owner.
- Do not bypass SAST, secret scan or dependency gates without explicit human approval.
- Do not treat an SBOM as optional documentation; keep it with release artefacts when releasing.
- Do not trust MCP/A2A peers solely because they are configured in a client; validate identity, version and permissions.
- Do not claim full NIST certification; align practices to SP 800-218 intent and project policy.

## Related skills

- `ci-cd-and-automation` — safe pipeline design and least-privilege jobs
- `guardrails-safety-patterns` — runtime agent and application controls
- `threat-modeling` — identify threats that supply-chain controls must address
- `release-engineering-and-progressive-delivery` — safe rollout after integrity gates pass

## References

- [NIST SP 800-218 SSDF](https://csrc.nist.gov/pubs/sp/800/218/final)
- [OWASP Software Component Verification Standard](https://owasp.org/www-project-software-component-verification-standard/)

## Verification

- [ ] SSDF practice groups are reflected for the change.
- [ ] Dependencies, actions and agent tools are inventoried and pinned where practical.
- [ ] Secrets handling is explicit and non-leaking.
- [ ] SAST / dependency / secret scans are enabled or justified.
- [ ] SBOM and provenance expectations are stated for releases.
- [ ] MCP/A2A supply-chain controls are addressed when applicable.
