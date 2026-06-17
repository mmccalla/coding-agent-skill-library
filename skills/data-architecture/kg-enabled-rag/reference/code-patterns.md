# KG-Enabled RAG Code Patterns

Detailed code and query patterns for `kg-enabled-rag/SKILL.md`. Load this file when generating or reviewing KG-RAG schemas, persistence, retrieval or evaluator code.

## 4. Code Generation Patterns

### 4.1 Conceptual schema config

Create or use `configs/conceptual_schema.yaml`:

```yaml
skip:
  classes:
    - Chunk
    - ParentChunk
    - ChildChunk
    - Document
    - ExtractionRun
    - Answer
  properties:
    - id
    - embedding
    - createdAt
    - updatedAt
    - checksum
    - traceId

descriptions:
  classes:
    Person: "A human actor, customer, employee, author, or named individual."
    Organisation: "A legal or organisational entity such as a company, charity, regulator, supplier, or business unit."
    Document: "A source document. Excluded from text-to-Cypher unless provenance is requested."
  relationships:
    OWNS: "Ownership or control relationship between an actor and an asset or organisation."
    WORKS_FOR: "Employment or formal role relationship between a person and an organisation."
    MENTIONS: "Evidence relationship from a source chunk to an extracted entity."

terminology:
  customer: ["client", "account holder", "party"]
  supplier: ["vendor", "third party", "provider"]
```

### 4.2 Structured extraction models

```python
from pydantic import BaseModel, Field
from typing import Literal

class ExtractedEntity(BaseModel):
    name: str = Field(min_length=1)
    type: str = Field(min_length=1)
    aliases: list[str] = []
    evidence_child_chunk_ids: list[str] = Field(min_length=1)
    confidence: float = Field(ge=0.0, le=1.0)

class ExtractedRelationship(BaseModel):
    source_name: str
    source_type: str
    relationship_type: str
    target_name: str
    target_type: str
    evidence_child_chunk_ids: list[str] = Field(min_length=1)
    confidence: float = Field(ge=0.0, le=1.0)

class ExtractionResult(BaseModel):
    entities: list[ExtractedEntity]
    relationships: list[ExtractedRelationship]
```

### 4.3 Idempotent Neo4j persistence

```cypher
UNWIND $entities AS entity
MERGE (e:__Entity__ {canonical_key: entity.canonical_key})
ON CREATE SET e.created_at = datetime(), e.name = entity.name, e.type = entity.type
SET e.updated_at = datetime(), e.confidence = entity.confidence
WITH e, entity
UNWIND entity.evidence_child_chunk_ids AS chunk_id
MATCH (c:ChildChunk {id: chunk_id})
MERGE (c)-[m:MENTIONS]->(e)
ON CREATE SET m.created_at = datetime()
SET m.confidence = entity.confidence
```

### 4.4 Local search Cypher

```cypher
CALL db.index.vector.queryNodes($index_name, $k, $query_embedding)
YIELD node, score
WITH collect({node: node, score: score}) AS hits
UNWIND hits AS hit
WITH hit.node AS entity, hit.score AS score
OPTIONAL MATCH (entity)<-[:MENTIONS]-(chunk:ChildChunk)
OPTIONAL MATCH (entity)-[r]-(neighbour:__Entity__)
OPTIONAL MATCH (entity)-[:IN_COMMUNITY]->(community:__Community__)
RETURN
  entity {.id, .name, .type} AS entity,
  score,
  collect(DISTINCT chunk {.id, .text, .document_id})[0..$top_chunks] AS chunks,
  collect(DISTINCT {type: type(r), neighbour: neighbour {.id, .name, .type}})[0..$top_neighbours] AS neighbourhood,
  collect(DISTINCT community {.id, .summary, .rating})[0..$top_communities] AS communities
ORDER BY score DESC
LIMIT $limit
```

### 4.5 Global search map-reduce skeleton

```python
def global_retriever(query: str, *, min_rating: float, llm, neo4j):
    communities = neo4j.execute_query(
        """
        MATCH (c:__Community__)
        WHERE coalesce(c.rating, 0) >= $min_rating
        RETURN c.id AS id, c.summary AS summary, c.rating AS rating
        ORDER BY c.rating DESC
        """,
        min_rating=min_rating,
    )

    mapped = []
    for community in communities:
        result = llm.generate_structured(
            prompt=MAP_COMMUNITY_PROMPT,
            input={"question": query, "community": community},
            schema=CommunityMapResult,
        )
        mapped.extend(result.points)

    selected = sorted(mapped, key=lambda p: p.importance, reverse=True)[:20]
    return llm.generate_structured(
        prompt=REDUCE_COMMUNITY_PROMPT,
        input={"question": query, "points": selected},
        schema=GroundedAnswer,
    )
```

### 4.6 Evaluator node

```python
def critic_node(state: AgentState) -> dict:
    critique = llm.generate_structured(
        prompt=ANSWER_CRITIC_PROMPT,
        input={
            "question": state["question"],
            "context": state.get("documents", []) + state.get("graph_context", []),
            "draft_answer": state["draft_answer"],
        },
        schema=CritiqueResult,
    )

    retries = state.get("retries", 0)
    if critique.verdict == "revise" and retries < settings.max_retries:
        return {
            "issues": critique.issues,
            "reflections": critique.required_fixes,
            "retries": retries + 1,
        }

    if critique.verdict != "approve":
        return {
            "final_answer": "The available evidence is insufficient to answer reliably.",
            "issues": critique.issues,
        }

    return {"final_answer": state["draft_answer"], "issues": critique.issues}
```

---
