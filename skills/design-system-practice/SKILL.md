---
name: design-system-practice
description: Maintains consistent, accessible design systems using tokens, components and documented patterns. Use when creating or evolving a shared UI component library or design tokens.
---

# Design System Practice

## When to use
Use this skill when creating or modifying design tokens, component libraries, shared UI patterns, typography, spacing, colour usage, component variants, interaction standards, layout systems or frontend conventions.

## Objective

Create a coherent design system that reduces UI inconsistency, improves accessibility, speeds delivery and avoids one-off interface decisions.

## Procedure

1. Identify whether the change belongs in the design system or a feature-specific component.
2. Use existing tokens, components and patterns before adding new ones.
3. Define tokens for colour, spacing, typography, radius, elevation and motion where applicable.
4. Define component variants based on real usage.
5. Document usage, accessibility notes and examples.
6. Keep variants small and meaningful.
7. Update tests, stories or examples where available.
8. Avoid breaking existing component contracts without migration guidance.

## Rules

- Do not introduce new colours, spacing values or typography styles ad hoc.
- Do not create a component variant for a single unproven use case.
- Do not make design tokens encode business state unless intentional.
- Do not create inaccessible visual-only states.
- Prefer reusable primitives over copied UI fragments.
- Keep design-system components domain-neutral unless deliberately building a domain component library.

## Verification

- [ ] Design-system artefacts changed listed.
- [ ] Tokens or components added or updated with rationale.
- [ ] Accessibility notes and examples or tests updated.
- [ ] Residual consistency risks stated.

