---
name: deprecation-and-migration
description: Use when retiring an old path, replacing a legacy behaviour or moving users to a new interface or workflow.
---

# Deprecation and Migration

## When to use
Use this skill when removing or replacing a skill, doc path, workflow, API surface or other user-facing behaviour that still has active dependents.

## Objective

Remove old paths safely by providing a clear replacement, a controlled transition period and a verified end state.

## Procedure

1. Identify what is being replaced and why.
2. Define the replacement path and compatibility expectations.
3. Mark the old path clearly with deprecation guidance.
4. Migrate dependents in small, observable steps.
5. Remove the old path only after usage is confirmed to be gone or intentionally waived.

## Rules

- Do not delete a legacy path before the replacement is valid.
- Do not surprise users with a silent incompatibility break.
- Do not leave parallel paths undocumented.
- Do not treat migration as complete until the old path is no longer needed.

## Verification

- [ ] Deprecated surface and timeline stated.
- [ ] Migration path and consumer communication documented.
- [ ] Compatibility or dual-run period noted.
- [ ] Residual migration risks stated.

