---
name: data-product-dashboard-design
description: Designs actionable data product dashboards for quality, lineage, validation, quarantine and operations. Use when building data-ops, quality, or lineage dashboards.
---

# Data Product Dashboard Design

## When to use
Use this skill when building dashboards or analytical screens for data quality, schema discovery, metadata, profiling, rule generation, validation, cleansing, quarantine, refined datasets, lineage, audit or operations.

## Objective

Create dashboards that help users make decisions, investigate issues and take action without confusing operational metrics, quality evidence and governance evidence.

## Operating procedure

1. Identify the dashboard user and decision.
2. Define the primary question the dashboard must answer.
3. Select the minimum useful metrics.
4. Show trend, current status and threshold where relevant.
5. Make filters explicit: source, domain, table, batch, rule, severity, time and owner.
6. Provide drill-down from summary to record, rule or evidence.
7. Distinguish quality status, operational status and governance status.
8. Provide clear next actions.
9. Include empty, loading, error and stale-data states.
10. Provide export or evidence links where required.

## Recommended dashboard areas

Source overview, schema discovery, profiling, rule management, validation, cleansing, quarantine, refined data, lineage, audit and operations.

## Recommended metrics

`validation_pass_rate`, `validation_failure_rate`, `quarantine_rate`, `quarantine_record_count`, `refined_record_count`, `cleansing_success_rate`, `rule_failure_count`, `top_failed_rules`, `schema_change_count`, `approval_backlog_count`, `mean_workflow_duration`, `p95_workflow_duration`, `policy_denial_rate`, `source_freshness`, `quality_score`.

## Rules

- Do not create dashboards that only display data without supporting a decision.
- Do not mix unrelated metrics without grouping or explanation.
- Do not use charts where a table, status list or evidence panel is clearer.
- Do not hide denominator values behind percentages.
- Do not show stale data without a timestamp.
- Do not make users jump across multiple screens to understand a single failure.

## Verification

- [ ] Dashboard user and decision stated.
- [ ] Metrics, filters and drill-downs documented.
- [ ] Evidence links and accessibility considerations noted.
- [ ] Residual dashboard risks stated.

