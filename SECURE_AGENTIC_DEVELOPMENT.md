# Secure Agentic Development Instructions

Use this file alongside `AGENTIC_CODING_GLOBAL_SAFETY.md` for security-sensitive coding-agent work.

It applies OWASP and NIST-aligned practices to agentic software development, including LLM-enabled applications, tools, CI/CD workflows, MCP/A2A integrations, APIs and automation.

## 1. Security objective

Build software that is secure by design, secure by default, auditable, testable and resilient.

Security is not a final review activity. It must be embedded into requirements, design, implementation, testing, deployment and operation.

## 2. Security baseline

Apply these controls by default:

1. least privilege for users, tools, agents, service accounts and API tokens;
2. explicit allow-lists for dangerous operations;
3. input validation at trust boundaries;
4. output encoding or escaping where data crosses rendering boundaries;
5. authentication and authorisation checks on every protected operation;
6. secrets stored outside source code;
7. dependency pinning and supply-chain checks;
8. audit logging for sensitive actions;
9. secure error handling that avoids information disclosure;
10. tests for security-critical behaviour.

## 3. NIST SSDF-aligned development workflow

NIST SP 800-218 SSDF groups secure software development into practices for preparing the organisation, protecting software, producing well-secured software and responding to vulnerabilities.

For coding-agent work, operationalise this as:

### 3.1 Prepare the organisation

- follow project security standards;
- use approved languages, frameworks and package sources;
- document threat assumptions;
- define secure defaults;
- ensure security checks are automated where practical.

### 3.2 Protect the software

- do not commit secrets;
- protect source, build scripts, CI/CD credentials and artefacts;
- use signed or verified artefacts where the project supports it;
- avoid unauthorised changes to release, deployment or infrastructure files.

### 3.3 Produce well-secured software

- validate all untrusted input;
- enforce authorisation server-side;
- use parameterised database queries;
- avoid unsafe deserialisation;
- apply secure session and token handling;
- implement structured errors and safe logging;
- add tests for abuse cases and edge cases;
- prefer simple designs that are easier to reason about.

### 3.4 Respond to vulnerabilities

- make fixes targeted and traceable;
- add regression tests for the vulnerability class;
- document impact, affected paths and remediation;
- recommend secret rotation when exposure is possible;
- avoid public disclosure of exploitable detail unless explicitly appropriate.

## 4. NIST AI RMF-aligned agent controls

NIST AI RMF is organised around Govern, Map, Measure and Manage. Apply these to agentic systems as follows.

### 4.1 Govern

- define agent purpose, authority and prohibited actions;
- identify accountable owners;
- maintain human approval paths for high-risk actions;
- document data sources, tools, prompts and model dependencies;
- define acceptable performance and safety thresholds.

### 4.2 Map

- identify users, affected stakeholders and misuse cases;
- map trust boundaries: user input, retrieved content, tools, APIs, memory, logs and outputs;
- classify data sensitivity;
- identify legal, privacy, safety and operational impacts;
- define where deterministic controls are required.

### 4.3 Measure

- test for prompt injection, data leakage, unsafe tool calls and hallucinated actions;
- monitor quality, latency, cost, refusal rate, policy violations and escalation rate;
- evaluate RAG faithfulness and source attribution;
- run security tests for conventional application risks;
- record evidence from tests and reviews.

### 4.4 Manage

- block or escalate unsafe requests;
- rate-limit expensive or sensitive operations;
- revoke or rotate credentials after exposure;
- patch vulnerable dependencies;
- tune guardrails based on measured failures;
- maintain rollback and incident-response procedures.

## 5. OWASP-aligned application security rules

For web, API and service code, check at minimum:

| Risk area | Required control |
|---|---|
| Broken access control | Enforce server-side authorisation on every protected operation. |
| Cryptographic failures | Use approved libraries; never invent crypto; protect secrets and keys. |
| Injection | Use parameterised queries, safe command execution and strict input validation. |
| Insecure design | threat-model high-risk flows and prefer secure-by-default designs. |
| Security misconfiguration | secure defaults, minimal permissions, safe headers and disabled debug modes in production. |
| Vulnerable components | pin, scan and update dependencies; avoid unmaintained packages. |
| Identification/authentication failures | use robust auth flows, secure session handling and MFA where supported. |
| Software/data integrity failures | protect CI/CD, verify artefacts and avoid untrusted code execution. |
| Logging/monitoring failures | log security events without secrets; create actionable alerts. |
| SSRF and unsafe outbound requests | restrict destinations, validate URLs and block metadata-service access. |

## 6. OWASP LLM and agent-specific rules

Treat LLM applications as systems with untrusted inputs, probabilistic outputs and privileged tool risks.

### 6.1 Prompt injection and instruction hierarchy

- never let retrieved content override system, developer or tool instructions;
- wrap retrieved content as data, not instructions;
- strip or neutralise instruction-like content from documents where appropriate;
- use allow-listed tool calls rather than free-form shell execution;
- require confirmation for sensitive actions.

### 6.2 Sensitive information disclosure

- do not expose prompts, hidden instructions, secrets, credentials or private data;
- redact logs and error messages;
- minimise data sent to models and external tools;
- classify retrieved documents and memory before use.

### 6.3 Insecure output handling

- treat model output as untrusted;
- validate JSON against schemas;
- escape generated HTML/Markdown where rendered;
- do not directly execute generated code, SQL, shell commands or infrastructure actions.

### 6.4 Excessive agency

- give agents the minimum tools required;
- scope credentials per environment and task;
- use approval gates for writes, deletes, deployments, payments, emails and production operations;
- set timeouts, retry limits and spend limits.

### 6.5 RAG and retrieval safety

- retrieve only from approved sources;
- cite sources where answers depend on retrieved knowledge;
- rank and filter documents by relevance and sensitivity;
- prevent poisoned documents from issuing instructions;
- separate context used for facts from instructions used for behaviour.

### 6.6 Tool, MCP and A2A security

- expose only agent-friendly, least-privilege tools;
- prefer narrow tools over broad shell or database tools;
- validate tool arguments with typed schemas;
- enforce authentication and authorisation at the tool server;
- log tool calls, caller identity, arguments metadata and outcomes;
- avoid returning secrets or excessive raw records;
- rate-limit tool endpoints;
- version tool contracts.

## 7. CI/CD security controls

For changes to build, test, release or deployment automation:

- require explicit approval before modifying CI/CD secrets, permissions or deployment steps;
- pin third-party GitHub Actions or equivalent CI plugins by version or commit where project policy requires it;
- avoid privileged runners for untrusted code;
- separate build, test and deploy permissions;
- never echo secrets in logs;
- use least-privilege tokens;
- protect artefact integrity;
- add security checks to pipelines rather than bypassing them.

## 8. Secure coding checklist by change type

### 8.1 API endpoint

- validate request body, path and query parameters;
- authenticate and authorise;
- use safe defaults for pagination and filtering;
- handle errors without leaking internals;
- add tests for unauthorised, invalid and boundary cases.

### 8.2 Database change

- use parameterised queries;
- avoid destructive migrations without backup and approval;
- protect PII and secrets;
- test rollback or recovery path;
- add indexes thoughtfully, not speculatively.

### 8.3 Authentication or authorisation change

- deny by default;
- check permissions server-side;
- add negative tests;
- avoid trusting client-side claims;
- log security-relevant decisions.

### 8.4 Dependency change

- justify why it is needed;
- prefer maintained packages;
- update lock files;
- run tests;
- check for known vulnerabilities where tooling exists.

### 8.5 Agent/tool change

- define tool schema;
- restrict permissions;
- add timeout and retry limits;
- validate model output;
- add human approval for high-impact actions;
- log tool calls safely.

## 8.6 User interface, accessibility and agentic UX change

For user-facing UI, dashboard, approval or agent-supervision changes:

- use semantic markup and accessible components;
- preserve keyboard access and visible focus states;
- provide accessible names, labels, hints and error messages;
- do not rely on colour alone for status, severity or quality outcomes;
- distinguish validation failure, policy denial, system error and partial success states;
- escape or sanitise untrusted content before rendering;
- do not render model output as trusted HTML unless sanitised;
- show evidence and provenance for agent-generated recommendations;
- require explicit confirmation for high-risk actions;
- log approval decisions without exposing secrets or unnecessary sensitive data;
- test critical user journeys and accessibility-relevant states.

For data-quality, quarantine, lineage and audit dashboards, expose sufficient evidence for the user to understand the decision without exposing raw sensitive values unnecessarily.

## 9. Threat-modelling prompt for coding agents

Before implementing a security-sensitive change, answer:

```text
Asset: What are we protecting?
Actor: Who could misuse this?
Entry point: Where does untrusted input enter?
Trust boundary: Where does data cross privilege or system boundaries?
Abuse case: What is the simplest harmful misuse?
Control: What prevents, detects or limits it?
Test: How will we verify the control?
Residual risk: What remains?
```

## 10. Security validation commands

Use project-appropriate tools. Examples:

```bash
npm audit --omit=dev
pip-audit
python -m bandit -r <package>
semgrep --config auto <path>
gitleaks detect --source .
trufflehog filesystem .
docker scout cves <image>
```

Do not install or run security tools that upload code externally without user approval.

## 11. Security-focused final response standard

For security-sensitive work, report:

```text
Security impact:
- <what improved or changed>

Controls implemented:
- <control>

Validation:
- <command/test>: <result>

Evidence:
- <file/test/log reference>

Residual risk:
- <remaining risk>

Recommended next action:
- <action>
```

## 12. Non-negotiable prohibitions

Do not:

- bypass authentication or authorisation checks;
- weaken validation to make tests pass;
- disable security tooling without approval;
- expose secrets or private data;
- add broad shell/database/cloud tools where narrow tools are sufficient;
- execute generated commands without inspection;
- deploy to production without explicit authorisation;
- conceal errors, logs or audit evidence.

## 13. One-line security principle

Every agent action should be least-privilege, validated, observable, reversible where possible, and proportionate to the risk.

## References

1. OWASP Foundation. OWASP Top 10. https://owasp.org/www-project-top-ten/
2. OWASP Foundation. OWASP Top 10 for Large Language Model Applications. https://owasp.org/www-project-top-10-for-large-language-model-applications/
3. OWASP Foundation. OWASP Top 10 CI/CD Security Risks. https://owasp.org/www-project-top-10-ci-cd-security-risks/
4. OWASP Foundation. OWASP Cheat Sheet Series: CI/CD Security. https://cheatsheetseries.owasp.org/cheatsheets/CI_CD_Security_Cheat_Sheet.html
5. National Institute of Standards and Technology. NIST AI Risk Management Framework 1.0. https://www.nist.gov/itl/ai-risk-management-framework
6. National Institute of Standards and Technology. NIST SP 800-218: Secure Software Development Framework Version 1.1. https://csrc.nist.gov/pubs/sp/800/218/final
