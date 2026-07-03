# MAS DataOps MCP Overlay

This optional overlay preserves product-specific guidance extracted from the portable skill library. Load it only when the repository, product or delivery context explicitly involves MAS DataOps MCP or an equivalent source-to-refined data-quality workflow.

## When to use

Use this overlay alongside the relevant core skill when work concerns:

- source onboarding;
- schema discovery;
- metadata generation;
- profiling;
- generated data-quality rules;
- validation, cleansing, quarantine and refined writes;
- lineage, audit and evidence bundles;
- policy decisions and approval workflows;
- workflow replay, idempotency and operational recovery.

## Observability and Telemetry

Required metrics for MAS DataOps MCP:

```text
source_onboarding_count
schema_discovery_success_rate
metadata_generation_success_rate
profiling_success_rate
rule_generation_acceptance_rate
validation_pass_rate
validation_failure_rate
cleansing_success_rate
quarantine_record_count
quarantine_rate
refined_record_count
refined_write_success_rate
evidence_bundle_completion_rate
policy_denial_rate
tool_error_rate
workflow_success_rate
workflow_failure_rate
workflow_duration_seconds
```

## SRE Practice

For source-to-refined workflows, reliability must cover source connection availability, schema discovery success, profiling completion, validation engine availability, quarantine write reliability, refined write reliability, evidence bundle persistence, workflow replay and idempotency, and alerting on failed or stuck batches.

## SLO and Error Budget Management

Recommended SLO candidates include `source_onboarding_success_rate`, `schema_discovery_success_rate`, `validation_run_success_rate`, `quarantine_write_success_rate`, `refined_write_success_rate`, `evidence_bundle_completion_rate`, `workflow_completion_latency` and `policy_decision_latency`.

## DORA Delivery Metrics

Use DORA metrics (throughput: deployment frequency, lead time, failed deployment recovery time; instability: change failure rate, deployment rework rate) for API/service deployments, validation-rule release process, source adapter changes, workflow engine changes, MCP tool changes, UI/dashboard releases and infrastructure changes.

For data-quality rules, define related metrics:

```text
rule_lead_time = draft created -> approved and safely active
rule_failure_rate = approved rule changes causing incorrect quarantine/refined routing
rule_recovery_time = time to disable or correct a faulty rule
```

## Incident Response and Postmortems

Examples include source-to-refined workflows stuck in running state, failed records not written to quarantine, passing records not written to refined, validation rules incorrectly promoted, evidence bundles missing and dashboards showing stale quality status.

## Release Engineering and Progressive Delivery

Use progressive delivery for new validation rules, generated expectation suites, cleansing rules, quarantine writer changes, refined writer changes, policy changes, source adapter changes and workflow routing changes.

Recommended pattern for new data-quality rules:

```text
draft
-> evaluate on sample
-> approve
-> shadow mode
-> warning-only mode
-> blocking mode for limited scope
-> broader production rollout
```

## Toil Reduction and Automation

Good candidates include routine validation summaries, quarantine review tasks, re-running validation after approved remediation, collecting evidence bundles, checking stale rule sets, schema-change alerts and runbook diagnostics.

High-risk automation requiring approval includes promoting generated rules, writing to refined production datasets, accepting quarantine exceptions, deleting quarantined records, changing policy and modifying source system records.

## Accessibility and WCAG

For data-quality and quarantine interfaces, show pass/fail status with text and icon, provide table captions and column headers, make failed rules readable by screen readers, expose long-running job status accessibly, and require confirmation for high-impact actions.

## UX Design Principles

For source-to-refined and quarantine workflows, users must be able to understand which source is being processed, what metadata was generated, which rules were applied, which records passed, which records failed, why records were quarantined, what cleansing was applied, what approvals are required, and what evidence supports the result.

## Frontend State and Interaction Design

For source-to-refined workflows, show workflow run status, current step, timestamps, records processed, records passed, cleansed and quarantined, rule progress, approval status, retry/cancel options and links to audit, lineage and validation evidence.

## Agentic UX Patterns

For generated data-quality rules, show rule name, rule type, target table/columns, rationale, profiling evidence, sample impact or aggregate evidence, expected failure rate, severity, approval status, impact on quarantine/refined split, version and reviewer decision.

## User Research and Usability Testing

Test whether users can onboard a source, understand schema, review metadata, approve rules, interpret validation failures, identify why records were quarantined, find lineage evidence, approve remediation and understand an agent recommendation.
