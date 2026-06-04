# Definition of Done Checklist

- [ ] Repository inspected before changes.
- [ ] Minimal coherent vertical slice implemented.
- [ ] Tests added or updated.
- [ ] Ingestion is idempotent.
- [ ] Graph constraints and indexes are created or migrated.
- [ ] Every extracted entity and relationship links to source chunks.
- [ ] Structured LLM output is schema-validated.
- [ ] Unsafe Cypher clauses are blocked.
- [ ] Text-to-Cypher is read-only by default.
- [ ] Retrieval returns typed evidence with source IDs.
- [ ] Generated answers include evidence references or state insufficiency.
- [ ] Evaluation covers recall, faithfulness, correctness, and absent-answer cases.
- [ ] No secrets, placeholders, fake tests, or dead stubs.
