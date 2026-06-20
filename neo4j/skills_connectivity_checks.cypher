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

// missing semantic bridge
MATCH (s:Skill)
WHERE NOT (
  (s)-[:HAS_CONTROL_THEME|HAS_KNOWLEDGE_DOMAIN]-()
  OR (s)-[:RELATED_TO|PRECEDES|SUPPORTS|SPECIALISES|REQUIRES]-(:Skill)
  OR (:Skill)-[:RELATED_TO|PRECEDES|SUPPORTS|SPECIALISES|REQUIRES]-(s)
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
      |HAS_CONTROL_THEME
      |HAS_KNOWLEDGE_DOMAIN
      |RELATED_TO
      |PRECEDES
      |SUPPORTS
      |SPECIALISES
      |REQUIRES*
    ]-(s)
    RETURN path
  }
RETURN
  "unreachable from root" AS check,
  s.id AS skill_id,
  s.name AS skill_name
ORDER BY skill_name;

// weakly connected component check for Neo4j GDS users.
// Requires a projected graph named "skills-connectivity".
CALL gds.wcc.stream("skills-connectivity")
YIELD nodeId, componentId
WITH componentId, collect(gds.util.asNode(nodeId).name) AS skill_names
RETURN
  "weakly connected" AS check,
  componentId,
  size(skill_names) AS component_size,
  skill_names
ORDER BY component_size DESC;
