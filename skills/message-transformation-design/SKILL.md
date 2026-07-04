---
name: message-transformation-design
description: Designs message translation, enrichment, filtering and normalisation. Use when mapping schemas, enriching payloads, applying claim check, or defining canonical models.
aliases:
  - eip-message-transformation
  - design-message-transformation
  - messaging-transformation-design
---

# Message Transformation Design

## When to use

Use when mapping between schemas, enriching payloads, reducing payloads, wrapping envelopes, normalising formats or defining canonical models in message-based integrations.

## Objective

Design message transformations that translate, enrich, filter and normalise messages without creating hidden coupling or uncontrolled data semantics.

## Procedure

1. Identify transformation intent:
   - Message Translator for schema or format conversion.
   - Envelope Wrapper to add or adapt metadata without changing the payload semantics.
   - Content Enricher to add missing data from another source.
   - Content Filter to remove unnecessary or unauthorised data.
   - Claim Check to replace bulky or sensitive data with a retrievable reference.
   - Normalizer to convert multiple input formats into a standard internal form.
   - Canonical Data Model where many systems require a shared integration vocabulary.
2. Define source-to-target mappings with field-level semantics, type rules, units, constraints and null handling.
3. Separate syntactic transformation from semantic translation.
4. Validate transformations with contract tests, golden messages and negative tests.
5. Define ownership and lifecycle for canonical models; avoid enterprise-wide models without domain governance.
6. Preserve traceability from output fields back to source fields and enrichment sources.

## Required outputs

- Transformation pattern used
- Mapping specification
- Validation rules
- Data minimisation and privacy controls
- Error-handling approach
- Contract-test examples

## Guardrails

- Do not create a canonical data model as a dumping ground for every system field.
- Do not enrich messages from unauthorised or stale sources.
- Do not silently drop fields without documenting consumer impact.
- Do not confuse name mapping with semantic equivalence.

## Related skills

- `message-based-integration-design`
- `integration-message-construction`
- `message-routing-design`
- `message-endpoint-design`
- `data-contract-design`
- `logical-data-modeling`
- `data-lineage-and-provenance`

## Verification

- [ ] Transformation pattern and mappings are explicit.
- [ ] Semantic ownership and privacy controls are defined.
- [ ] Validation and error handling are stated.
- [ ] Traceability from output to source is preserved.
- [ ] Residual risks and assumptions are recorded.

## References

- [EIP — Message Translator](https://www.enterpriseintegrationpatterns.com/patterns/messaging/MessageTranslator.html)
- [EIP — Envelope Wrapper](https://www.enterpriseintegrationpatterns.com/patterns/messaging/EnvelopeWrapper.html)
- [EIP — Content Enricher](https://www.enterpriseintegrationpatterns.com/patterns/messaging/DataEnricher.html)
- [EIP — Content Filter](https://www.enterpriseintegrationpatterns.com/patterns/messaging/ContentFilter.html)
- [EIP — Claim Check](https://www.enterpriseintegrationpatterns.com/patterns/messaging/StoreInLibrary.html)
- [EIP — Normalizer](https://www.enterpriseintegrationpatterns.com/patterns/messaging/Normalizer.html)
- [EIP — Canonical Data Model](https://www.enterpriseintegrationpatterns.com/patterns/messaging/CanonicalDataModel.html)
