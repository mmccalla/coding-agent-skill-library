---
name: accessibility-wcag
description: Applies WCAG 2.2 AA-aligned accessibility checks to interfaces, forms, dashboards and components. Use when building or reviewing any user-facing UI, content, or agent supervision screen.
---

# Accessibility and WCAG Practice

## When to use
Use this skill for any user-facing work: pages, forms, dashboards, tables, modals, navigation, charts, notifications, approval workflows, agent supervision interfaces and design-system components.

## Objective

Ensure interfaces are perceivable, operable, understandable and robust, with practical alignment to WCAG 2.2 AA expectations.

## Operating procedure

1. Use semantic HTML or accessible component primitives.
2. Ensure all interactive controls are keyboard reachable.
3. Provide visible focus states.
4. Provide accessible names for buttons, links, inputs and icons.
5. Associate labels, hints and errors with form controls.
6. Do not rely on colour alone to communicate meaning.
7. Check text contrast and visual hierarchy.
8. Provide meaningful headings and landmarks.
9. Ensure tables have appropriate headers and captions where needed.
10. Provide accessible alternatives for charts and diagrams.
11. Ensure dynamic updates are announced where appropriate.
12. Test common flows using keyboard-only interaction.

## Rules

- Do not use clickable `div` or `span` elements where a button or link is appropriate.
- Do not remove focus outlines without providing an accessible replacement.
- Do not encode meaning only through colour, position or iconography.
- Do not show validation errors only after form submission when earlier feedback is possible.
- Do not create modals that trap users without an escape path.
- Do not use placeholder text as the only label.

## DataOps-specific guidance

For data-quality and quarantine interfaces, show pass/fail status with text and icon, provide table captions and column headers, make failed rules readable by screen readers, expose long-running job status accessibly, and require confirmation for high-impact actions.

## Related skills

- `ux-design-principles` — task-centred design before a11y checks
- `ui-component-design` — accessible component primitives
- `frontend-state-and-interaction-design` — keyboard and state accessibility
## Verification

- [ ] Keyboard interaction checked.
- [ ] Labels, accessible names and focus states checked.
- [ ] Colour-only meaning avoided.
- [ ] Table or chart accessibility considered.
- [ ] Tests or manual checks performed and residual risks stated.

