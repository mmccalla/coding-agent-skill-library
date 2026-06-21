// Skills KG Neo4j schema.
// Run before loading data. Defaults mirror configs/skills_kg.yaml.

:param embedding_dimensions => 1536;

CREATE CONSTRAINT skill_id_unique IF NOT EXISTS
FOR (n:Skill) REQUIRE n.id IS UNIQUE;

CREATE CONSTRAINT skill_name_unique IF NOT EXISTS
FOR (n:Skill) REQUIRE n.name IS UNIQUE;

CREATE CONSTRAINT skill_section_id_unique IF NOT EXISTS
FOR (n:SkillSection) REQUIRE n.id IS UNIQUE;

CREATE CONSTRAINT retrieval_unit_id_unique IF NOT EXISTS
FOR (n:RetrievalUnit) REQUIRE n.id IS UNIQUE;

CREATE CONSTRAINT skill_category_id_unique IF NOT EXISTS
FOR (n:SkillCategory) REQUIRE n.id IS UNIQUE;

CREATE CONSTRAINT task_shape_id_unique IF NOT EXISTS
FOR (n:TaskShape) REQUIRE n.id IS UNIQUE;

CREATE CONSTRAINT workflow_stage_id_unique IF NOT EXISTS
FOR (n:WorkflowStage) REQUIRE n.id IS UNIQUE;

CREATE CONSTRAINT capability_id_unique IF NOT EXISTS
FOR (n:Capability) REQUIRE n.id IS UNIQUE;

CREATE CONSTRAINT control_theme_id_unique IF NOT EXISTS
FOR (n:ControlTheme) REQUIRE n.id IS UNIQUE;

CREATE CONSTRAINT knowledge_domain_id_unique IF NOT EXISTS
FOR (n:KnowledgeDomain) REQUIRE n.id IS UNIQUE;

CREATE CONSTRAINT bridge_assertion_id_unique IF NOT EXISTS
FOR (n:BridgeAssertion) REQUIRE n.id IS UNIQUE;

CREATE CONSTRAINT source_id_unique IF NOT EXISTS
FOR (n:Source) REQUIRE n.id IS UNIQUE;

CREATE CONSTRAINT reference_document_id_unique IF NOT EXISTS
FOR (n:ReferenceDocument) REQUIRE n.id IS UNIQUE;

CREATE CONSTRAINT validation_rule_id_unique IF NOT EXISTS
FOR (n:ValidationRule) REQUIRE n.id IS UNIQUE;

CREATE INDEX skill_category_lookup IF NOT EXISTS
FOR (n:Skill) ON (n.category);

CREATE INDEX skill_path_lookup IF NOT EXISTS
FOR (n:Skill) ON (n.path);

CREATE INDEX bridge_assertion_source_lookup IF NOT EXISTS
FOR (n:BridgeAssertion) ON (n.source);

CREATE INDEX retrieval_unit_source_lookup IF NOT EXISTS
FOR (n:RetrievalUnit) ON (n.source_path);

CREATE FULLTEXT INDEX skill_metadata_fulltext IF NOT EXISTS
FOR (n:Skill) ON EACH [n.name, n.title, n.description, n.category];

CREATE FULLTEXT INDEX retrieval_unit_text_fulltext IF NOT EXISTS
FOR (n:RetrievalUnit) ON EACH [n.text, n.path, n.source_path];

CREATE VECTOR INDEX retrieval_unit_embedding_vector IF NOT EXISTS
FOR (n:RetrievalUnit) ON (n.embedding)
OPTIONS {
  indexConfig: {
    `vector.dimensions`: $embedding_dimensions,
    `vector.similarity_function`: "cosine"
  }
};
