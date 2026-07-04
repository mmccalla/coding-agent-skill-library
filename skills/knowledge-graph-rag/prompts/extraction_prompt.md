# Extraction Prompt Contract

System: Extract domain entities, relationships, and claims from the provided parent chunk. Return only data matching the supplied structured schema. Do not infer facts that are not evidenced in the text.

Inputs:

- document_id
- parent_chunk_id
- child_chunks: list of `{id, text, start_offset, end_offset}`
- allowed_entity_types
- allowed_relationship_types
- extraction_schema

Rules:

1. Use the parent chunk for context.
2. Every extracted entity, relationship, and claim must cite one or more child chunk IDs.
3. Preserve exact source wording where useful for evidence.
4. Do not create entities for generic nouns unless domain-relevant.
5. Set lower confidence for ambiguous references.
6. Return empty arrays when no valid extraction exists.
