---
name: source-driven-development
description: Use when a decision must be grounded in authoritative source material before implementation or documentation work continues.
---

# Source-Driven Development

## When to use
Use this skill when the work depends on framework docs, repository conventions, upstream behavior or other source material that should be verified rather than remembered.

## Objective

Base the implementation or guidance on the most authoritative available source and make unverified assumptions explicit.

## Operating procedure

1. Identify the source of truth.
2. Verify version-specific or repo-specific behavior directly from that source.
3. Extract only the facts needed for the task.
4. Note anything that remains unverified.
5. Align the implementation or documentation with the verified source.

## Rules

- Do not trust memory when the source can be checked.
- Do not mix authoritative docs with guesses without labelling the difference.
- Do not broaden the source set unless a second source is genuinely needed.
- Prefer exact behaviour over generic advice.

## Verification

- [ ] Authoritative sources cited.
- [ ] Claims mapped to source evidence.
- [ ] Gaps where sources are silent or conflicting stated.
- [ ] Implementation or documentation aligned to sources.

