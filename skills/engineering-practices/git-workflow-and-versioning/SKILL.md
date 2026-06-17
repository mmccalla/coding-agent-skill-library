---
name: git-workflow-and-versioning
description: Use when making code changes that should stay atomic, reversible and easy to review through disciplined Git workflow and versioning.
---

# Git Workflow and Versioning

## When to use
Use this skill when creating commits, branching work, preparing changes for review, or planning version-aware changes and migrations.

## Objective

Keep change history small, coherent and easy to understand while preserving the ability to revert or bisect if needed.

## Operating procedure

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

## Verification

- [ ] Logical change boundaries described.
- [ ] Working tree state reported.
- [ ] Versioning or compatibility considerations noted.
- [ ] Reversibility of the change confirmed.

## Additional guidelines

Adopt the following practices to enhance your Git workflow:

- **Definition‑of‑Done compliance:** Confirm that all Definition‑of‑Done criteria—including peer reviews, acceptance criteria and non‑functional requirements—are satisfied before merging or closing a branch.
- **Risk‑based review:** Perform risk‑based code reviews, prioritising high‑impact or security‑sensitive changes and allocating appropriate scrutiny.
- **Small, focused pull requests:** Keep pull requests small and cohesive to improve review effectiveness and reduce merge conflicts.
- **Automated quality gates:** Run automated checks (static analysis, secret scanning, test suites) before merging to catch issues early and reduce reviewer burden.
- **Branch closure and cleanup:** Document the branch closure process and routinely clean up unused branches and worktrees to maintain repository hygiene.
