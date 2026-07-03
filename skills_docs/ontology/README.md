# Ontology artefacts

**Narrative documentation:** [`../krag/ONTOLOGY.md`](../krag/ONTOLOGY.md)

This directory holds machine-readable schema and instance data:

| File | Role |
| --- | --- |
| `skills.ttl` | Canonical ontology |
| `canonical-core.shacl.ttl` | Core graph validation |
| `retrieval-projection.shacl.ttl` | Retrieval projection validation |
| `runtime-selection.shacl.ttl` | Selection trace validation |
| `skills.shacl.ttl` | Legacy combined shapes (if present) |
| `instances/task-intents.ttl` | Governed task intent instances |
| `instances/workflow-stages.ttl` | Governed workflow stage instances |

Validate:

```bash
python3 scripts/validate_skills_ontology.py
python3 scripts/validate_skills_ontology.py --include-instances
```

Human-readable KRAG contracts and status: [`../krag/`](../krag/).
