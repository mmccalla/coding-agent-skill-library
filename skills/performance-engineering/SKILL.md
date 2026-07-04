---
name: performance-engineering
description: Improves system latency and throughput using SLIs, profiling, load tests and capacity planning. Use when diagnosing slow paths, sizing capacity, or validating performance under load—not for policy-only SLOs or per-session agent budgets.
aliases:
  - performance-testing
  - capacity-and-performance
  - latency-throughput-engineering
---

# Performance Engineering

## When to use

Use this skill when a system, API, pipeline, data platform or agent-serving path must meet **latency** or **throughput** goals backed by measurement. Apply it to profiling hot paths, load and stress testing, capacity planning, concurrency limits, cache and I/O tuning, and regression detection for performance SLIs. Use it when evidence must show where time is spent and whether the system sustains target load.

## When not to use

- Do not use this skill only to set reliability policy, error budgets or release freezes — use `slo-error-budget-management` for policy; use this skill to engineer the performance that feeds those SLIs.
- Do not use it for a single agent session’s token, model or context budget — use `resource-aware-optimization`.
- Do not use it only to add dashboards without a performance hypothesis — use `observability-and-telemetry` for instrumentation, then profile and load-test here.
- Do not use it as a substitute for overall service ownership and resilience design — use `sre-practice` for operability, with performance engineering as a focused practice inside it.

## Objective

Establish measurable latency and throughput SLIs, find bottlenecks through profiling and load tests, and size capacity so the system meets targets under realistic load with known headroom and failure behaviour.

## Procedure

1. Define user-visible performance SLIs (for example p50/p95/p99 latency, requests per second, events processed per minute, time-to-first-token for inference) and success criteria for the change.
2. Establish a baseline under representative load and data shape; record environment, version and configuration.
3. Profile the critical path (CPU, memory, I/O, locks, network, database, model inference) to locate dominant contributors to latency or limited throughput.
4. Form a hypothesis and apply the smallest change likely to improve the bottleneck; avoid speculative micro-optimisations.
5. Run load tests (and stress or soak tests where relevant) that reflect production concurrency, payload sizes and dependency behaviour.
6. Plan capacity: peak load, headroom, autoscaling limits, queue depths and dependency quotas; document what happens when limits are hit.
7. Add or update performance regression checks and telemetry so regressions are visible in delivery and operations.
8. Report results against SLIs, residual risk and recommended next measurement.

## Required outputs or templates

```markdown
# Performance engineering report

## Targets
| SLI | Target | Measurement method |
|---|---|---|
| p95 latency | <value> | <endpoint / journey> |
| throughput | <value> | <sustained load> |

## Baseline
- Environment and version:
- Load profile:
- Observed latency / throughput:

## Profiling findings
- Hot path / bottleneck:
- Evidence (profile, trace, query plan):

## Experiments
| Change | Result vs baseline | Keep? |
|---|---|---|
| ... | ... | ... |

## Capacity
- Peak design load:
- Headroom:
- Saturation behaviour:

## Residual risk
- ...
```

## Rules

- Do not optimise without a baseline and a performance SLI.
- Do not treat SLO policy documents as proof that the system is fast enough under load.
- Do not confuse agent session resource budgets with system capacity planning.
- Do not rely on a single local profile run as proof of production behaviour.
- Do not increase parallelism without understanding lock contention, downstream quotas and failure amplification.
- Do not claim success without load-test or production evidence against the stated SLIs.

## Related skills

- `slo-error-budget-management`
- `observability-and-telemetry`
- `resource-aware-optimization`
- `sre-practice`

## References

- Microsoft Azure Well-Architected — Performance testing: https://learn.microsoft.com/en-us/azure/architecture/framework/scalability/performance-test
- Brendan Gregg — Systems Performance Methodologies: https://www.brendangregg.com/methodology.html

## Verification

- [ ] Latency and/or throughput SLIs and targets are explicit.
- [ ] Baseline measurement exists.
- [ ] Profiling evidence identifies the bottleneck.
- [ ] Load or capacity tests support the conclusion.
- [ ] Capacity headroom and saturation behaviour are stated.
- [ ] Residual performance risk is recorded.
