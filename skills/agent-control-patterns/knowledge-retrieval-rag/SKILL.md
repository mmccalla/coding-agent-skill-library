---
name: knowledge-retrieval-rag
description: Use when implementing retrieval-augmented generation, document-grounded coding agents, semantic search, citation-backed answers, or repository/document knowledge lookup.
---

# Knowledge Retrieval (RAG)

## When to use

Use this skill when an agent needs facts from external documents, code repositories, wikis, tickets, logs, APIs, or other knowledge stores before answering or modifying code.

For GraphRAG, Neo4j-native retrieval, text-to-Cypher, provenance-first graph ingestion, or KG-backed answer generation, pair this skill with `skills/data-architecture/kg-enabled-rag/SKILL.md`.

## Core pattern

1. Ingest documents or code into clean text.
2. Split content into meaningful chunks that preserve context.
3. Store metadata: source path, section, timestamp, owner, commit, permissions and content type.
4. Index chunks using embeddings and, where useful, keyword search.
5. Retrieve relevant chunks for the user query.
6. Rerank or filter results for relevance, freshness and permissions.
7. Generate an answer grounded only in retrieved evidence.
8. Cite sources or file paths so claims are inspectable.

## Retrieval strategy

Prefer hybrid retrieval for coding agents:

- keyword/BM25 for exact symbols, filenames, errors and API names;
- vector search for semantic questions and conceptual similarity;
- structural search for AST symbols, imports, tests and dependency graphs;
- reranking for final context selection.

## Implementation guidance

Chunk code differently from prose. Keep functions, classes, configuration blocks and tests intact where possible. Preserve import context and neighbouring comments.

Add retrieval tests with known questions and expected source files. Measure recall before tuning generation prompts.

## Guardrails

- Do not answer from memory when repository evidence is required.
- Do not mix authorised and unauthorised content in one context.
- Do not cite chunks that do not support the claim.
- Do not use raw PDFs or binary files directly if the agent cannot parse them reliably; convert to agent-readable text first.

## Related skills

- `kg-enabled-rag` — graph-native retrieval when Neo4j applies
- `context-engineering` — assemble retrieval context efficiently
- `guardrails-safety-patterns` — validate retrieved and generated content

## Verification
- [ ] Sources are parsed into clean text.
- [ ] Chunking preserves useful context.
- [ ] Metadata and permissions are retained.
- [ ] Retrieval quality is tested.
- [ ] Generated output cites supporting sources.
