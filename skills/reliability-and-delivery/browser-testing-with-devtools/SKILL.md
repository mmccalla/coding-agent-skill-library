---
name: browser-testing-with-devtools
description: Use when verifying browser-based behaviour with Chrome DevTools, including DOM state, console output, network activity and performance evidence.
---

# Browser Testing With DevTools

## When to use this skill

Use this skill when a change affects a browser-rendered interface and you need runtime evidence from the browser rather than static code inspection alone.

## Objective

Verify user-facing behaviour with DevTools evidence so frontend or browser issues are reproduced, localized and confirmed with the actual runtime state.

## Operating procedure

1. Reproduce the issue or feature in the browser.
2. Inspect the DOM, console and network activity.
3. Check state changes, errors and timing at the point of failure.
4. Use performance or network traces when latency or rendering is relevant.
5. Confirm the fix with the same browser path.

## Rules

- Do not rely on screenshots alone when runtime evidence is available.
- Do not treat a successful page load as proof of correct behaviour.
- Do not skip console or network checks when a browser bug is involved.
- Do not use performance traces without first reproducing the user-visible problem.

## Verification

Report the browser path exercised, the DevTools evidence captured, the issue localized, and the behaviour confirmed after the fix.
