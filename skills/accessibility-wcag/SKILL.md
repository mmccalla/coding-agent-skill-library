---
name: accessibility-wcag
description: Applies WCAG 2.2 AA-aligned accessibility checks to interfaces, forms, dashboards and components. Use when building or reviewing any user-facing UI, content, or agent supervision screen.
aliases:
  - accessibility
  - wcag
---

# Accessibility and WCAG Practice

## When to use

Use this skill for any user-facing work: pages, forms, dashboards, tables, modals, navigation, charts, notifications, approval workflows, agent supervision interfaces and design-system components.

## Objective

Ensure interfaces are perceivable, operable, understandable and robust, with practical alignment to WCAG 2.2 AA expectations.

## Procedure

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

## WCAG 2.2 AA focus areas

For WCAG 2.2 AA alignment, explicitly check the newer AA success criteria as well as the long-standing basics:

- `2.4.11 Focus Not Obscured (Minimum)`: author-created content must not fully hide the focused component.
- `2.5.7 Dragging Movements`: functionality using dragging should also support a single-pointer alternative unless dragging is essential.
- `2.5.8 Target Size (Minimum)`: pointer targets must meet the minimum target-size expectation or a documented exception.
- `3.3.8 Accessible Authentication (Minimum)`: authentication should not require a cognitive-function test unless an accessible alternative or assistance mechanism exists.

Also check Level A criteria that commonly affect agent and approval UIs:

- `3.2.6 Consistent Help`: help mechanisms (contact, chat, self-help, human contact) appear in the same relative order across pages when present.
- `3.3.7 Redundant Entry`: do not require users to re-enter information already provided in the same process unless essential or security-related.

Source: [W3C WCAG 2.2](https://www.w3.org/TR/WCAG22/).

## References

- W3C WCAG 2.2: https://www.w3.org/TR/WCAG22/
- W3C — What's New in WCAG 2.2: https://www.w3.org/WAI/standards-guidelines/wcag/new-in-22/

## Rules

- Do not use clickable `div` or `span` elements where a button or link is appropriate.
- Do not remove focus outlines without providing an accessible replacement.
- Do not encode meaning only through colour, position or iconography.
- Do not show validation errors only after form submission when earlier feedback is possible.
- Do not create modals that trap users without an escape path.
- Do not use placeholder text as the only label.

## Optional overlay

For product-specific DataOps/MCP examples, load `skills_docs/overlays/mas-dataops-mcp-overlay.md`.

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
