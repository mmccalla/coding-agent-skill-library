---
name: api-design-and-lifecycle
description: Designs HTTP/service APIs with OpenAPI, resource models, authZ, versioning, deprecation and contract tests. Use when defining or evolving service APIs, not dataset or event contracts.
aliases:
  - openapi-design
  - rest-api-design
  - api-lifecycle-management
  - service-api-design
---

# API Design and Lifecycle

## When to use

Use this skill when designing, reviewing or evolving application or service APIs: resource models, request/response schemas, authentication and authorisation, versioning, deprecation, OpenAPI specifications and consumer-facing contract tests. Apply it to REST-style and similar request/response service interfaces that agents or clients call.

## When not to use

- Use `data-contract-design` for producer–consumer agreements on datasets, tables, files or data products (quality, freshness, semantics).
- Use `schema-registry-and-contracts` for event schemas, compatibility modes and streaming registry governance.
- Use `message-based-integration-design` when the primary style is messaging, brokers or EIP topology rather than a service API.
- Use `deprecation-and-migration` alone when the work is a general migration plan without API resource or OpenAPI design.

## Objective

Produce a clear, implementable API design and lifecycle plan: resources, operations, authZ, OpenAPI contract, versioning and deprecation rules, and executable contract tests that protect consumers without conflating service APIs with data or event contracts.

## Procedure

1. Clarify consumers, use cases and success criteria. Prefer resource-oriented models over ad-hoc RPC bags of endpoints unless an RPC style is already established.
2. Define resources, identifiers, relationships, collections, error shapes and idempotency expectations for write operations.
3. Specify authentication and authorisation per operation: who may call, which scopes or roles apply, and how denial is represented. Enforce authZ server-side.
4. Author or update an OpenAPI description as the source of truth for paths, methods, parameters, schemas and status codes. Keep examples realistic and non-secret.
5. Choose a versioning strategy (URI, header or negotiated) and compatibility rules for additive versus breaking changes. Document how clients discover versions.
6. Define deprecation: announcement, sunset timeline, migration guidance and monitoring of deprecated usage before removal.
7. Add contract tests (consumer-driven or provider-side schema/status checks) in CI so breaking changes fail before release.
8. Record operational concerns: rate limits, pagination, correlation IDs, safe error messages and observability hooks.

## Required outputs

```markdown
# API design: <service or capability>

## Consumers and use cases
## Resource model
| Resource | Identifier | Operations | Notes |

## AuthN / AuthZ
| Operation | AuthN | AuthZ rule | Denial behaviour |

## OpenAPI
- Spec path:
- Notable schemas / status codes:

## Versioning and compatibility
- Strategy:
- Breaking-change policy:

## Deprecation
- Announcement:
- Sunset date / criteria:
- Migration path:

## Contract tests
| Test | Consumer / provider | Assertion |

## Risks and open questions
```

## Rules

- Do not design dataset or event payloads here; route those to `data-contract-design` or `schema-registry-and-contracts`.
- Do not rely on client-only authorisation or hidden “admin” query flags.
- Do not break consumers without a versioning or deprecation path.
- Do not treat OpenAPI as optional documentation; keep it aligned with implementation and tests.
- Do not return stack traces or secrets in error bodies.
- Do not invent fields in production responses that are absent from the published contract.

## Related skills

- `data-contract-design` — dataset and data-product contracts
- `schema-registry-and-contracts` — event schema registry and compatibility
- `message-based-integration-design` — messaging and EIP style selection
- `deprecation-and-migration` — broader deprecation and migration discipline

## References

- OpenAPI Specification: https://spec.openapis.org/oas/latest.html
- OpenAPI Initiative: https://www.openapis.org/
- Swagger OpenAPI resources: https://swagger.io/specification/

## Verification

- [ ] Resource model and operations are explicit.
- [ ] AuthN/AuthZ rules are defined per sensitive operation.
- [ ] OpenAPI (or equivalent) contract is identified and kept current.
- [ ] Versioning and deprecation paths are documented.
- [ ] Contract tests are specified for CI.
- [ ] Scope excludes dataset/event contract design unless explicitly linked.
