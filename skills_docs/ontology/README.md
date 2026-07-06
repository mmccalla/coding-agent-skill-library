# Ontology artefacts

**Narrative documentation:** [`../krag/ONTOLOGY.md`](../krag/ONTOLOGY.md)

This directory holds machine-readable schema and instance data:

| File | Role |
| --- | --- |
| `skills.ttl` | Canonical ontology (includes optional `skills:standardsReference` on skill versions) |
| `canonical-core.shacl.ttl` | Core graph validation |
| `retrieval-projection.shacl.ttl` | Retrieval projection validation |
| `runtime-selection.shacl.ttl` | Selection trace validation |
| `skills.shacl.ttl` | Combined shapes (optional `skills:standardsReference` on `SkillVersion`) |
| `instances/task-intents.ttl` | Governed task intent instances |
| `instances/workflow-stages.ttl` | Governed workflow stage instances |

Primary-source URLs in skill `## References` sections are extracted into graph records as `standardsReferences` / reference documents. Content-level enforcement lives in `scripts/validators/validate_skill_practice.py`.

Validate:

```bash
python3 scripts/validators/validate_skills_ontology.py
python3 scripts/validators/validate_skills_ontology.py --include-instances
```

Human-readable KRAG contracts and status: [`../krag/`](../krag/).
