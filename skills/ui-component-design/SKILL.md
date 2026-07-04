---
name: ui-component-design
description: Designs reusable, accessible UI components with clear props, states, variants and tests. Use when building tables, forms, modals, cards, or design-system components.
---

# UI Component Design

## When to use
Use this skill when creating or modifying reusable components, forms, tables, cards, modals, drawers, navigation, badges, alerts, charts, approval panels, data-quality result components or quarantine triage components.

## Objective

Build components that are reusable, accessible, predictable, composable, visually consistent and easy to test.

## Procedure

1. Identify the component's purpose and user-facing responsibility.
2. Define the component API with clear props and typed contracts.
3. Define supported states: default, loading, disabled, error, empty, warning, success and selected.
4. Define variants only when they represent real design or behaviour differences.
5. Use semantic markup and accessible names.
6. Separate presentation, state management and data fetching where practical.
7. Keep components small and composable.
8. Add tests for key behaviour and states.
9. Document examples for common usage.
10. Avoid embedding domain-specific business logic in generic components.

## Rules

- Do not build one component that handles unrelated responsibilities.
- Do not add variants for speculative future needs.
- Do not hide required labels, errors or descriptions.
- Do not hard-code data access inside reusable display components.
- Prefer composition over deep prop branching.
- Keep public component APIs stable where possible.

## Recommended categories

Layout, feedback, input, data display, workflow, evidence and agentic UI components.

## References

- W3C ARIA Authoring Practices Guide: https://www.w3.org/WAI/ARIA/apg/

## Verification

- [ ] Component purpose and interface changes stated.
- [ ] States and variants handled documented.
- [ ] Accessibility checks performed.
- [ ] Tests added or updated; residual risks stated.

