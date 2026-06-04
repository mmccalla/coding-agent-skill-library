# Global Search Prompt Contracts

## Map Prompt

Extract key points from a community summary that help answer the user question.

Return:
- points: list of `{text, importance: 0-100, supporting_community_id, evidence_ids}`

Rules:
1. Only use the community summary and attached evidence IDs.
2. Rate importance by relevance to the question.
3. Exclude generic background.

## Reduce Prompt

Synthesize the highest-rated mapped points into a grounded answer.

Rules:
1. Preserve source IDs.
2. Resolve contradictions explicitly.
3. State insufficient evidence where points do not answer the question.
4. Do not introduce facts not present in mapped points.
