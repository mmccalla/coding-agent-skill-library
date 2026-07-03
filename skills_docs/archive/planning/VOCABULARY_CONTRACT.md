# Governed Vocabulary Contract

## Purpose

Define the canonical mapping between KRAG v2 **TaskIntent** (contract language) and ontology **TaskShape** (TTL class) instances used for routing, negative applicability and evaluation.

## Naming policy

| KRAG v2 term | Ontology TTL | Instance id pattern | Mapping slug |
| --- | --- | --- | --- |
| TaskIntent | `skills:TaskShape` | `skills:task-intent-{slug}` | `{slug}` kebab-case |
| WorkflowStage | `skills:WorkflowStage` | `skills:workflow-stage-{slug}` | `{slug}` |
| Constraint | `skills:InvocationCondition` | (Phase 4+) | `{slug}` in `skill_section_mapping.py` |

**Rule:** the mapping slug in `scripts/skill_section_mapping.py` must match the suffix of the TTL instance id after `task-intent-`.

## Instance graphs

- `skills_docs/ontology/instances/task-intents.ttl`
- `skills_docs/ontology/instances/workflow-stages.ttl`

Loaded with `skills.ttl` for SHACL validation via `validate_skills_ontology.py --include-instances`.

## Near-neighbour disambiguation concepts

| Slug | Distinguishes |
| --- | --- |
| `defect-fix-with-tests` | TDD-first defect work vs post-artefact review |
| `post-artefact-review` | Critique/repair after artefact exists |
| `spec-before-build` | Specification before implementation |
| `code-review` | Merge-time review vs TDD implementation |

## Governance

- Pack owners do not edit instance TTL per skill.
- KRAG maintainers extend vocabulary from eval failure clusters.
- New slugs require: TTL instance, mapping rule (if prose-mapped), golden eval case.
