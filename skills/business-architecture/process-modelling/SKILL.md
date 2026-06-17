---
name: process-modelling
description: Models operational steps, decisions, hand-offs, controls, exceptions and automation opportunities. Use when documenting processes, BPMN workflows, or automation candidates.
---

# Process Modelling

## When to use
Use when clarifying how work is performed.

## Objective
Produce a practical, concise, traceable architecture artefact that a coding agent can use to guide implementation or review.

## Procedure
1. Define start/end.
2. Identify actors/swimlanes.
3. Capture steps and decisions.
4. Capture inputs/outputs.
5. Add controls and exceptions.
6. Identify systems and data.
7. Mark automation candidates.
8. Define process metrics.

## Required outputs
- Process steps
- Decisions
- Hand-offs
- Controls/exceptions
- Systems/data touched
- Automation candidates

## Best-practice alignment
Keep capabilities, value streams, processes, organisation, information concepts, initiatives and metrics separate, then link them from strategy to execution.

## Quality checks
- Exceptions are shown.
- Controls are not hidden.
- Automation candidates distinguish rules from judgement.

## Avoid
Do not use process modelling when capability modelling is needed.

## Mini example

For invoice exception handling, map the start event, supplier operations swimlane, finance approval decision, system checks, exception paths and control evidence. Mark automation candidates only where rules are explicit, such as duplicate invoice detection. Keep human judgement steps visible when fraud risk or policy interpretation is involved.

## Verification

- [ ] Required artefacts produced and linked to scope.
- [ ] Decisions, assumptions and risks stated explicitly.
- [ ] Quality checks or validation performed.
- [ ] Files changed reported with traceability preserved.

