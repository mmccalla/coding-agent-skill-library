// Skills KG connectivity validation checks.
// These read-only checks are designed for CI or operator review after loading.

// missing task/capability bridge
MATCH (s:Skill)
WHERE NOT (s)-[:HAS_TASK_SHAPE|HAS_CAPABILITY]-()
RETURN
  "missing task/capability bridge" AS check,
  s.id AS skill_id,
  s.name AS skill_name
ORDER BY skill_name;

// missing workflow stage
MATCH (s:Skill)
WHERE NOT (s)-[:HAS_WORKFLOW_STAGE]-()
RETURN
  "missing workflow stage" AS check,
  s.id AS skill_id,
  s.name AS skill_name
ORDER BY skill_name;

// missing bridge assertion
MATCH (s:Skill)
WHERE NOT (s)-[:ASSERTS_BRIDGE]->(:BridgeAssertion)
RETURN
  "missing bridge assertion" AS check,
  s.id AS skill_id,
  s.name AS skill_name
ORDER BY skill_name;

// invalid bridge assertion provenance
MATCH (s:Skill)-[:ASSERTS_BRIDGE]->(b:BridgeAssertion)
WHERE b.source IS NULL
  OR trim(b.source) = ""
  OR b.path IS NULL
  OR trim(b.path) = ""
  OR b.confidence IS NULL
  OR b.confidence < 0.0
  OR b.confidence > 1.0
RETURN
  "invalid bridge assertion provenance" AS check,
  s.id AS skill_id,
  s.name AS skill_name,
  b.id AS bridge_assertion_id
ORDER BY skill_name, bridge_assertion_id;

// invalid relationship provenance
MATCH (s:Skill)-[r:RELATED_TO|PRECEDES|REQUIRES|COMPLEMENTS|REFINES|GOVERNS|VALIDATES]-(t:Skill)
WHERE r.source_path IS NULL
  OR trim(r.source_path) = ""
  OR (
    type(r) = "RELATED_TO"
    AND (r.source_section_id IS NULL OR trim(r.source_section_id) = "")
  )
  OR (
    type(r) <> "RELATED_TO"
    AND (r.mapping_rule_id IS NULL OR trim(r.mapping_rule_id) = "")
  )
RETURN
  "invalid relationship provenance" AS check,
  s.id AS skill_id,
  s.name AS skill_name,
  type(r) AS relationship_type,
  t.id AS target_skill_id
ORDER BY skill_name, relationship_type, target_skill_id;

// missing semantic bridge
MATCH (s:Skill)
WHERE NOT (
  (s)-[:HAS_CONTROL_THEME|HAS_KNOWLEDGE_DOMAIN]-()
  OR (s)-[:RELATED_TO|PRECEDES|REQUIRES|COMPLEMENTS|REFINES|GOVERNS|VALIDATES]-(:Skill)
  OR (:Skill)-[:RELATED_TO|PRECEDES|REQUIRES|COMPLEMENTS|REFINES|GOVERNS|VALIDATES]-(s)
)
RETURN
  "missing semantic bridge" AS check,
  s.id AS skill_id,
  s.name AS skill_name
ORDER BY skill_name;

// unreachable from root
MATCH (root:Skill {name: "apply-laws-of-ai"})
MATCH (s:Skill)
WHERE s <> root
  AND NOT EXISTS {
    MATCH path = (root)-[
      :HAS_TASK_SHAPE
      |HAS_WORKFLOW_STAGE
      |HAS_CAPABILITY
      |RELATED_TO
      |PRECEDES
      |REQUIRES
      |COMPLEMENTS
      |REFINES
      |GOVERNS
      |VALIDATES*
    ]-(s)
    RETURN path
  }
RETURN
  "unreachable from root" AS check,
  s.id AS skill_id,
  s.name AS skill_name
ORDER BY skill_name;
