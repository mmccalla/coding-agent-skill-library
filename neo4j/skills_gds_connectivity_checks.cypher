// Optional Skills KG connectivity validation checks for Neo4j GDS users.
// Requires Graph Data Science and a projected graph named "skills-connectivity".

CALL gds.wcc.stream("skills-connectivity")
YIELD nodeId, componentId
WITH componentId, collect(gds.util.asNode(nodeId).name) AS skill_names
RETURN
  "weakly connected" AS check,
  componentId,
  size(skill_names) AS component_size,
  skill_names
ORDER BY component_size DESC;
