# Reliability and Delivery Skills Manifest

Use these skills for production reliability, service ownership, incident response, observability, release safety, browser-based verification, CI/CD automation, deprecation, documentation, launch discipline, toil reduction and DORA Four Keys delivery performance.

DORA means **DevOps Research and Assessment** in this library.

| Skill | Use when | Avoid when |
|---|---|---|
| `sre-practice` | Designing, operating or reviewing production services for reliability, operability, resilience and service ownership. | The work is a local-only prototype with no operational expectation. |
| `slo-error-budget-management` | Defining SLIs, SLOs, error budgets, burn rates, reliability targets or release gates. | There is no user-visible service or measurable reliability objective. |
| `incident-response-and-postmortems` | Handling incidents, operational failures, recovery, postmortems, learning reviews or corrective actions. | The issue is a simple local development error with no service impact. |
| `observability-and-telemetry` | Adding or reviewing logs, metrics, traces, dashboards, alerts or telemetry standards. | The task has no runtime behaviour or operational monitoring need. |
| `browser-testing-with-devtools` | Verifying browser behaviour, console output, network activity or frontend performance with Chrome DevTools. | The change is backend-only or does not run in a browser. |
| `toil-reduction-and-automation` | Reducing repetitive manual operational work through safe, tested and auditable automation. | Automation would increase risk, hide judgement or remove necessary human approval. |
| `release-engineering-and-progressive-delivery` | Improving deployment safety through rollback, canary, blue/green, feature flags, release gates or staged rollout. | The task has no deployment or release impact. |
| `dora-four-keys` | Improving deployment frequency, lead time for changes, change failure rate or failed deployment recovery time. | The task is unrelated to software delivery performance. |
| `ci-cd-and-automation` | Designing or changing build, test or deployment pipelines with explicit safety checks. | The work has no pipeline or automation impact. |
| `deprecation-and-migration` | Retiring old paths, migrating users or sunsetting obsolete behaviour safely. | There is no legacy path to remove or replace. |
| `documentation-and-adrs` | Recording architectural decisions, release notes or maintainership guidance. | The change is purely internal and needs no durable explanation. |
| `shipping-and-launch` | Preparing a change for launch, staged rollout or post-launch monitoring. | The work is not being released or published yet. |

## Recommended combinations

| Scenario | Recommended skill sequence |
|---|---|
| Production service design | `sre-practice` → `slo-error-budget-management` → `observability-and-telemetry` |
| Browser verification | `browser-testing-with-devtools` → `frontend-state-and-interaction-design` where UI behaviour is involved |
| New operational dashboard | `observability-and-telemetry` → `slo-error-budget-management` → `data-product-dashboard-design` where UI is involved |
| Incident fix | `incident-response-and-postmortems` → `exception-handling-and-recovery` → `tdd-practice` → `observability-and-telemetry` |
| Release pipeline improvement | `release-engineering-and-progressive-delivery` → `dora-four-keys` → `evaluation-and-monitoring` |
| CI/CD change | `ci-cd-and-automation` → `guardrails-safety-patterns` → `evaluation-and-monitoring` |
| Toil reduction | `toil-reduction-and-automation` → `sre-practice` → `guardrails-safety-patterns` → `tdd-practice` |
| Reliability regression | `slo-error-budget-management` → `observability-and-telemetry` → `incident-response-and-postmortems` |
| Delivery performance review | `dora-four-keys` → `prioritisation` → `toil-reduction-and-automation` |
| Release launch | `shipping-and-launch` → `release-engineering-and-progressive-delivery` → `observability-and-telemetry` |

## General rules

- Connect reliability work to user impact, not only infrastructure health.
- Prefer measurable service objectives over vague “make it reliable” goals.
- Define operational evidence before claiming improvement.
- Alerts must be actionable and tied to symptoms users or services experience.
- Automate toil only when the automation is safer, tested, observable and reversible.
- Progressive delivery should reduce blast radius and improve rollback speed.
- DORA metrics should drive learning and improvement, not individual performance management.
