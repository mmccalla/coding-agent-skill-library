---
name: kg-enabled-rag
description: Builds, refactors and hardens Neo4j-native KG-enabled RAG with LangGraph, hybrid retrieval, text-to-Cypher, and provenance. Use when implementing GraphRAG, graph-backed retrieval, or guarded text-to-Cypher pipelines.
version: 2.0.0
audience: autonomous-coding-agents
optimised_for:
  - OpenAI Codex
  - Claude Code
  - Google Antigravity
  - Cursor
  - Windsurf
  - Cline
  - Continue
activation_keywords:
  - GraphRAG
  - KG-RAG
  - knowledge graph RAG
  - graph-enabled RAG
  - Neo4j RAG
  - text2cypher
  - text-to-Cypher
  - hybrid retrieval
  - entity extraction
  - entity resolution
  - graph retriever
  - agentic RAG
  - answer critic
  - Microsoft GraphRAG
  - local search
  - global search
  - community summarisation
  - RAG evaluation
primary_stack:
  orchestration: langgraph
  graph_store: neo4j
  schema_validation: pydantic
  language: python
  api: fastapi
  observability: opentelemetry
---

# SKILL: kg-enabled-rag

## When to use

Use this skill when building, refactoring, reviewing or hardening Neo4j-native GraphRAG or KG-enabled RAG systems that require graph-aware retrieval, provenance-first ingestion, guarded text-to-Cypher, conceptual schema control or graph-backed answer generation.

Do not use it for generic document RAG, vector-only retrieval, or ontology-only design work where the existing `knowledge-retrieval-rag` or `ontology-and-knowledge-graph-modelling` skills are sufficient.

## Objective

Implement Neo4j-native KG-enabled RAG with provenance-first ingestion, guarded retrieval, grounded answers, and tests.

## 0. Agent Execution Contract

You are an autonomous coding agent. Optimise for safe, verifiable repository changes, not explanatory prose.

When activated, produce working code, tests, configuration, and documentation updates required by the user request. Do not create placeholder-only code, fake tests, dead functions, or uncalled stubs.

Default target architecture: **Neo4j-native KG-enabled RAG with graph, full-text, and vector indexes; LangGraph for orchestration; Pydantic for structured LLM boundaries; provenance-first ingestion; local/global GraphRAG retrieval; guarded text-to-Cypher; evaluator loop.**

Use this skill as an execution specification. If the repository already has an equivalent pattern, adapt to it rather than replacing it wholesale.

---

## 1. Non-Negotiable Invariants

### 1.1 Storage and retrieval defaults

- Default to **Neo4j-native graph, full-text, and vector indexes** to minimise infrastructure complexity and enable graph-aware retrieval.
- Do not introduce Qdrant, Chroma, FAISS, Pinecone, Weaviate, Elasticsearch, or another external vector/search store unless an ADR explicitly justifies scale, latency, isolation, operational, or migration requirements.
- If an external store already exists, do not remove it without tests and an explicit migration path.

### 1.2 Idempotent graph writes

- For ingestion, never use raw `CREATE` for domain entities, chunks, documents, claims, or relationships.
- Use deterministic identifiers and `MERGE`/upsert semantics.
- Use `UNWIND` batch persistence and transactional boundaries.
- Create uniqueness constraints before ingestion.
- Re-running ingestion for the same document must not duplicate documents, chunks, entities, relationships, claims, embeddings, or community reports.

### 1.3 Conceptual schema only

- Do not expose raw `apoc.meta.schema`, raw database metadata, internal labels, embeddings, audit properties, or technical node types directly to an LLM.
- Generate a curated **Conceptual Schema** from database metadata plus a YAML configuration.
- Filter technical classes and properties.
- Add semantic descriptions and terminology mappings.
- Use the conceptual schema for text-to-Cypher, routing, and answer generation.

### 1.4 Structured LLM boundaries

- Use Pydantic or equivalent typed schemas for all LLM outputs used by code.
- Structured output improves syntactic compliance only. It does not prove semantic truth.
- Validate extracted entities and relationships for schema, required fields, enum values, identifier format, source evidence, and confidence thresholds.
- Reject, repair, or quarantine invalid extractions. Do not silently persist them.

### 1.5 Evidence and provenance

- Every extracted entity, relationship, claim, summary, embedding, answer, and evaluation result must trace back to source evidence.
- Required provenance edges:
  - `(Document)-[:HAS_PARENT_CHUNK]->(ParentChunk)`
  - `(ParentChunk)-[:HAS_CHILD_CHUNK]->(ChildChunk)`
  - `(ChildChunk)-[:MENTIONS]->(Entity)` or `(Entity)-[:MENTIONED_IN]->(ChildChunk)`
  - `(RelationshipFact)-[:HAS_EVIDENCE]->(ChildChunk)` when relationships are reified
  - `(Answer)-[:SUPPORTED_BY]->(ChildChunk|Entity|RelationshipFact|Community)` when answer persistence is implemented
- Generated answers must cite or otherwise expose supporting source identifiers.

### 1.6 Query safety

- Parameterise all Cypher.
- For user-facing text-to-Cypher, default to read-only queries.
- Block or require explicit gated approval for:
  - `CREATE`
  - `MERGE`
  - `DELETE`
  - `DETACH DELETE`
  - `SET`
  - `REMOVE`
  - `LOAD CSV`
  - `CALL dbms.*`
  - unrestricted `CALL`
  - APOC file/network procedures
- Enforce query timeout, row limit, traversal depth limit, and token budget.
- Run `EXPLAIN`/dry-run validation where feasible before executing generated Cypher.

---

## 2. Recommended Repository Architecture

Implement or align to this modular architecture:

```text
src/
  kg_rag/
    config/              # typed settings, env loading, schema config
    domain/              # Pydantic/domain models
    ingestion/           # parsers, chunkers, extractors, persistence pipeline
    graph/               # Neo4j driver, constraints, indexes, repositories
    retrieval/           # vector, full-text, local, global, text-to-Cypher retrievers
    orchestration/       # LangGraph state graphs and nodes
    generation/          # prompts, grounded synthesis, citation rendering
    evaluation/          # retrieval and answer evaluation
    observability/       # logging, metrics, tracing
    security/            # Cypher guard, prompt-injection guard, policy checks
    api/                 # FastAPI routes and DTOs
    cli/                 # command-line utilities

tests/
  unit/
  integration/
  e2e/
  fixtures/

configs/
  conceptual_schema.yaml
  models.yaml
  retrieval.yaml
```

Boundary rules:

- Parsers parse.
- Chunkers chunk.
- Extractors extract.
- Resolvers canonicalise.
- Repositories persist.
- Retrievers retrieve.
- Routers select tools.
- Generators synthesise.
- Evaluators criticise and score.
- API layers do not contain business logic.

---

## 3. Implementation Lifecycle

### Phase A — Repository inspection

Before edits:

1. Identify language, package manager, test framework, service entry points, environment conventions, and existing architecture.
2. Locate graph, retrieval, LLM, prompt, and evaluation code.
3. Check whether Neo4j, LangGraph, Pydantic, FastAPI, Docker, and OpenTelemetry already exist.
4. Identify existing conventions and preserve them.
5. Write or update a short implementation plan before broad edits.

### Phase B — Ingestion: text to graph

Objective: convert unstructured files into a text-paired knowledge graph.

Required components:

1. **Document loader**
   - Accept file bytes or paths through controlled interfaces.
   - Record `document_id`, source URI/path, checksum, MIME type, parser version, and ingestion run ID.

2. **Hierarchical chunking**
   - Create `ParentChunk` around 1,500-2,500 characters unless overridden.
   - Create `ChildChunk` around 400-700 characters with 10-20% overlap unless overridden.
   - Embed only `ChildChunk` by default.
   - Preserve parent-child ordering and offsets.

3. **Contextual extraction**
   - Pass the full `ParentChunk` to the LLM.
   - Require the LLM to map every extracted entity, relationship, and claim to one or more `ChildChunk` IDs.
   - Use typed extraction models.

4. **Persistence**
   - Use deterministic IDs from stable source keys.
   - Use `UNWIND` and `MERGE` in batch transactions.
   - Persist documents, parent chunks, child chunks, entities, mentions, relationship facts, claims, and embeddings.
   - Enforce idempotency with tests.

5. **Failure handling**
   - Checkpoint per document and phase.
   - Failed extraction should not corrupt committed graph state.
   - Retry transient failures with bounded backoff.

### Phase C — Graph optimisation: resolution and communities

Objective: improve graph quality and support global search.

1. **Candidate generation**
   - Generate similarity candidates using blocking keys, normalised names, aliases, type, source, embedding similarity, and domain rules.
   - Create `META_SIMILAR` edges only for candidate evidence, not final identity truth.

2. **Entity resolution**
   - Use WCC only as candidate clustering, not automatic golden-record proof.
   - Prevent snowball merges with contradiction checks, type compatibility, confidence thresholds, and evidence counts.
   - Produce `CanonicalEntity` or canonical IDs.
   - Preserve links from canonical records to original mentions/entities.
   - Keep audit properties: resolution method, confidence, timestamp, run ID.

3. **Community detection**
   - Use Louvain as baseline where Neo4j GDS supports it.
   - Prefer Leiden if available and project constraints support it.
   - Store communities as `__Community__` nodes with level, members, summary, rating, source algorithm, run ID, and timestamp.

4. **Community summarisation**
   - Summarise community node/edge evidence with an LLM.
   - Store executive summary, key entities, key claims, rating, and evidence references.
   - Do not overwrite prior community summaries without versioning.

### Phase D — Retrieval

Implement multiple specialised retrievers behind a common interface.

Required retriever types:

1. **Vector retriever**
   - Query `ChildChunk` or `__Entity__` vector indexes.
   - Return evidence objects with ID, text/name, score, source, and metadata.

2. **Full-text retriever**
   - Use Neo4j full-text indexes for lexical matching.
   - Combine with vector results for hybrid search.

3. **Local graph search**
   - Use entity-focused retrieval.
   - Embed query, retrieve top-K entities, traverse 1-2 hops, collect neighbours, relationships, connected child chunks, and community reports.
   - Enforce traversal depth and row limits.

4. **Global graph search**
   - Use community summaries for broad, thematic, or corpus-level questions.
   - Implement map-reduce:
     - Map community summaries into key points with importance scores.
     - Reduce high-scoring points into a final answer.
   - Keep score thresholds configurable.

5. **Text-to-Cypher retriever**
   - Use conceptual schema, terminology mapping, few-shot examples, and strict output schema.
   - Validate generated Cypher before execution.
   - Use read-only allow-list by default.
   - Use specialised deterministic retrievers for known query classes before falling back to text-to-Cypher.

6. **Parent document retriever**
   - Retrieve child chunks, then expand to parent chunks for context where appropriate.

### Phase E — LangGraph orchestration

Use LangGraph StateGraph when a workflow needs routing, retries, evaluator loops, or multiple retrievers.

Minimum state:

```python
class AgentState(TypedDict, total=False):
    question: str
    normalised_question: str
    intent: str
    schema: str
    query: str
    retrieval_plan: list[dict]
    documents: list[dict]
    graph_context: list[dict]
    draft_answer: str
    final_answer: str
    citations: list[dict]
    reflections: list[str]
    issues: list[str]
    retries: int
    trace_id: str
```

Primary nodes:

1. **Planner / Router**
   - Classify intent.
   - Select retriever(s).
   - Decompose multi-hop questions.
   - Prefer deterministic specialised retrievers where available.

2. **Executor**
   - Execute vector, full-text, local graph, global graph, text-to-Cypher, or API retrieval.
   - Return typed evidence.

3. **Generator**
   - Compose grounded answer only from retrieved evidence.
   - Include citations/source IDs.
   - State insufficiency where evidence is weak.

4. **Evaluator / Critic**
   - Evaluate draft answer against evidence.
   - Return structured JSON: `issues`, `required_fixes`, `verdict`.
   - Route to revise until approved or max retries reached.

5. **Exit**
   - Return final answer, citations, retrieval trace, and insufficiency notice when needed.

### Phase F — Evaluation

Implement evaluation before declaring the system done.

Minimum metrics:

- Context recall.
- Faithfulness / groundedness.
- Answer correctness.
- Citation coverage.
- Retrieval latency.
- Generation latency.
- Query safety pass/fail.
- Ingestion idempotency.
- Entity resolution precision spot checks.

Minimum datasets:

- Golden Q&A examples.
- Negative questions where answer is absent.
- Aggregation questions for text-to-Cypher.
- Entity disambiguation questions.
- Multi-hop relationship questions.
- Broad thematic questions for global search.

---

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

## 5. Testing Contract

Never mark a KG-RAG implementation complete without tests.

Required tests:

1. **Unit tests**
   - chunk ID determinism
   - parent/child chunk mapping
   - Pydantic extraction validation
   - conceptual schema filtering
   - Cypher guard blocks unsafe clauses
   - citation/evidence formatter

2. **Integration tests**
   - Neo4j constraints and indexes are created
   - same document ingested twice creates no duplicates
   - vector index query returns typed evidence
   - local graph search returns entity, chunk, and relationship context
   - text-to-Cypher executes only validated read queries

3. **End-to-end tests**
   - ingest small fixture document
   - ask entity lookup question
   - ask relationship/multi-hop question
   - ask aggregation question
   - ask absent-answer question
   - verify grounded answer and citations

4. **Evaluation tests**
   - context recall threshold
   - faithfulness threshold
   - answer correctness threshold
   - no unsupported claims in generated answer

---

## 6. Security and Reliability Guardrails

- Never trust user-uploaded documents as instructions.
- Strip or isolate prompt-injection content from retrieved context.
- Separate system prompts from retrieved text.
- Use role-delimited prompts.
- Do not reveal hidden prompts, raw schema, credentials, stack traces, or unrestricted query errors.
- Add rate limits, request size limits, timeout limits, and traversal limits.
- Make ingestion resumable.
- Make destructive operations impossible from normal RAG query paths.
- Log trace IDs, run IDs, source IDs, retriever choices, query hashes, and evaluation outcomes.
- Do not log secrets or full sensitive documents unless explicitly configured.

---

## 7. Definition of Done

A KG-enabled RAG task is done only when:

- The requested feature works through the real code path.
- Tests prove the key behaviour.
- Ingestion is idempotent.
- Extracted facts have evidence links.
- Retrieval returns typed evidence with source IDs.
- Generated answers are grounded or explicitly state insufficient evidence.
- Text-to-Cypher is guarded and read-only by default.
- Configuration is typed and environment-driven.
- Observability captures trace ID, run ID, retriever choice, latency, and failures.
- Documentation explains how to run tests and the feature.
- No placeholder-only code, fake tests, or broad rewrites were introduced.

---

## 8. Anti-Patterns to Avoid

- Raw chunks only, with no entity or relationship layer.
- Extracting triples without provenance.
- Auto-merging entities solely because they are connected by WCC.
- Exposing raw database schema to LLMs.
- Letting the LLM generate unrestricted Cypher.
- Using `CREATE` for repeatable ingestion.
- Storing embeddings without source, model, dimension, and timestamp metadata.
- Using one generic retriever for all questions.
- Returning fluent answers without citations or evidence.
- Treating structured output as proof that extracted facts are correct.
- Adding external infrastructure without an explicit ADR.

---

## 9. First Actions When Activated

1. Read this skill.
2. Inspect the repository.
3. Identify the smallest vertical slice needed.
4. Create or update tests first where practical.
5. Implement using the architecture above.
6. Run tests and fix failures.
7. Report changed files, commands run, tests passed/failed, and residual risks.

## Verification

- [ ] Files changed reported.
- [ ] Commands and validations run with results stated.
- [ ] Behaviour intentionally changed described.
- [ ] Assumptions and residual risks or follow-up work stated.

