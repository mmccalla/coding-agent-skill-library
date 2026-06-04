# Security Review Checklist

- [ ] No hard-coded secrets or credentials.
- [ ] All database queries are parameterised.
- [ ] Generated Cypher is validated before execution.
- [ ] User-facing query generation is read-only by default.
- [ ] Prompt-injection text from retrieved documents cannot override system instructions.
- [ ] Raw schema, prompts, stack traces, and connection strings are not exposed.
- [ ] Request size, traversal depth, row count, timeout, and retry limits are configured.
- [ ] Logs include traceability but exclude secrets and sensitive raw content by default.
