---
name: git-workflow-and-versioning
description: Use when making code changes that should stay atomic, reversible and easy to review through disciplined Git workflow and versioning.
---

# Git Workflow and Versioning

## When to use
Use this skill when creating commits, branching work, preparing changes for review, or planning version-aware changes and migrations.

## Objective

Keep change history small, coherent and easy to understand while preserving the ability to revert or bisect if needed.

## Procedure

1. Keep each commit or change slice focused on one logical purpose.
2. Avoid mixing unrelated fixes, refactors and documentation changes.
3. Use descriptive commit messages or change notes.
4. Preserve a clean working tree before handing off work.
5. Treat versioned or compatibility-sensitive changes deliberately.

## Rules

- Do not rewrite shared history unless explicitly authorised.
- Do not combine unrelated changes just to reduce the number of commits.
- Do not hide partial work in ambiguous commit messages.
- Do not change versioning semantics without checking downstream impact.

## Example

For a phased refactor, branch from updated `main`, commit one phase at a time, run validation before hand-off and merge only after approval. If a hook rewrites files, review the resulting diff before committing. Prefer a clear revertable commit over a broad mixed commit that hides documentation, tests and implementation together.

## Verification

- [ ] Logical change boundaries described.
- [ ] Working tree state reported.
- [ ] Versioning or compatibility considerations noted.
- [ ] Reversibility of the change confirmed.
