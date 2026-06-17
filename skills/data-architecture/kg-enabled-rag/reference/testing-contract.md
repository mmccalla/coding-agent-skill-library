# KG-Enabled RAG Testing Contract

Testing expectations for `kg-enabled-rag/SKILL.md`. Load this file before claiming a KG-RAG implementation, refactor or hardening task is complete.

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
