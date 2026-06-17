---
name: shipping-and-launch
description: Use when preparing a change for launch, staged rollout or post-launch monitoring.
---

# Shipping and Launch

## When to use
Use this skill when a change is ready to leave the repository, reach users or be published as part of a release or rollout.

## Objective

Launch changes with a clear preflight check, a safe rollout path, post-launch monitoring and an understood rollback option.

## Procedure

1. Confirm the release scope and launch owner.
2. Check that the change is ready for release.
3. Verify monitoring, alerts and rollback paths.
4. Launch in the smallest safe step available.
5. Watch the key signals after launch.
6. Record anything that still needs follow-up.

## Rules

- Do not launch without an explicit owner and monitoring signal.
- Do not skip the rollback path just because the change looks small.
- Do not consider a merge equivalent to a launch.
- Do not ignore early post-launch evidence.

## Verification

- [ ] Launch scope and rollout plan stated.
- [ ] Pre-launch checks and monitoring plan documented.
- [ ] Rollback or mitigation path defined.
- [ ] Residual launch risks stated.

