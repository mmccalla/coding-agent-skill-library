---
name: evaluation-and-monitoring
description: Use when measuring coding-agent quality, regression risk, latency, cost, reliability, safety, drift, or production performance.
---

# Evaluation and Monitoring

## When to use

Use this skill when an agent or generated system must be measured objectively before, during or after deployment. Apply it to coding-agent changes, RAG systems, tool-use workflows, multi-agent systems and production assistants.

## Objective

Measure agent or system quality with explicit metrics, representative scenarios, and actionable monitoring evidence.

## Procedure

1. Define measurable objectives and indicators.
2. Select quantitative and qualitative metrics.
3. Build an evaluation dataset or scenario set.
4. Run baseline evaluation before changes.
5. Evaluate after each material change.
6. Monitor production behaviour continuously.
7. Feed results into prioritization, rollback, tuning or human review.

## Core pattern

1. Define measurable objectives and indicators.
2. Select quantitative and qualitative metrics.
3. Build an evaluation dataset or scenario set.
4. Run baseline evaluation before changes.
5. Evaluate after each material change.
6. Monitor production behaviour continuously.
7. Feed results into prioritization, rollback, tuning or human review.

## Metrics catalogue

- Quality: correctness, relevance, completeness, faithfulness, pass rate.
- Engineering: test coverage, build success, type-check success, defect rate.
- Runtime: latency, throughput, timeout rate, retry rate.
- Cost: tokens, API spend, compute, storage, human review effort.
- Safety: policy violation rate, unsafe tool attempt rate, escalation rate.
- Reliability: availability, failure recovery rate, mean time to recovery.

## Implementation guidance

For coding agents, treat tests as first-class evaluations. Add targeted regression tests for every bug fix. For RAG, measure retrieval recall, answer faithfulness and citation accuracy. For tool-use agents, measure tool-call correctness and error recovery.

## Guardrails

- Do not rely on exact string match for semantic answers except where exactness is required.
- Do not use LLM-as-judge without calibration examples and spot checks.
- Do not optimise a single metric if it harms safety or reliability.
- Alert on drift, unusual tool behaviour and repeated recovery failures.

## Verification
- [ ] Baseline exists.
- [ ] Metrics are tied to objectives.
- [ ] Evaluation set covers edge cases.
- [ ] Monitoring captures latency, cost and failures.
- [ ] Findings drive concrete action.

