#!/usr/bin/env python3
"""Build and apply idempotent Neo4j load plans for the skills KG."""

from __future__ import annotations

import json
import os
import re
import sys
from argparse import ArgumentParser
from collections import Counter
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any, NamedTuple, Protocol, cast

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.extract_skills_graph import extract_skills_graph_records
from scripts.map_skills_bridges import apply_semantic_bridge_mappings
from scripts.skills_config import Neo4jSettings, load_settings
from scripts.validate_skills_graph import validate_graph_records

REQUIRED_SCHEMA_ITEMS = frozenset(
    {
        "skill_id_unique",
        "skill_name_unique",
        "skill_section_id_unique",
        "retrieval_unit_id_unique",
        "skill_category_id_unique",
        "task_shape_id_unique",
        "workflow_stage_id_unique",
        "capability_id_unique",
        "control_theme_id_unique",
        "knowledge_domain_id_unique",
        "bridge_assertion_id_unique",
        "source_id_unique",
        "reference_document_id_unique",
        "validation_rule_id_unique",
    }
)
REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SCHEMA_PATH = REPO_ROOT / "neo4j" / "skills_schema.cypher"
SCHEMA_NAME_PATTERN = re.compile(
    r"^CREATE\s+(?:CONSTRAINT|INDEX|FULLTEXT\s+INDEX|VECTOR\s+INDEX)\s+([A-Za-z][A-Za-z0-9_]*)",
    flags=re.I,
)

BRIDGE_KIND_TO_LABEL_AND_REL = {
    "task_shape": ("TaskShape", "HAS_TASK_SHAPE"),
    "workflow_stage": ("WorkflowStage", "HAS_WORKFLOW_STAGE"),
    "capability": ("Capability", "HAS_CAPABILITY"),
    "control_theme": ("ControlTheme", "HAS_CONTROL_THEME"),
    "knowledge_domain": ("KnowledgeDomain", "HAS_KNOWLEDGE_DOMAIN"),
}
TOKEN_PATTERN = re.compile(r"[a-z0-9]+")


class MissingSchemaItemError(RuntimeError):
    """Raised before writes when required Neo4j schema is absent."""


class GraphNode(NamedTuple):
    """A deterministic node upsert keyed by label and id."""

    label: str
    id: str
    properties: Mapping[str, object]


class GraphRelationship(NamedTuple):
    """A deterministic relationship upsert between two keyed nodes."""

    type: str
    source_label: str
    source_id: str
    target_label: str
    target_id: str
    properties: Mapping[str, object]


class LoadPlan(NamedTuple):
    """All node and relationship merges needed for one load."""

    nodes: tuple[GraphNode, ...]
    relationships: tuple[GraphRelationship, ...]


class LoadReport(NamedTuple):
    """Logical counts and batch count for audit-friendly run output."""

    logical_counts: Mapping[str, int]
    batches: int


class MergeGraph(Protocol):
    """Minimal graph write contract for tests and Neo4j adapters."""

    def available_schema_items(self) -> set[str]:
        """Return installed constraint/index names."""

    def apply_schema(
        self,
        statements: Sequence[str],
        parameters: Mapping[str, object] | None = None,
    ) -> None:
        """Apply schema statements transactionally where the backend supports it."""

    def merge_nodes(self, nodes: Sequence[GraphNode]) -> None:
        """Merge a batch of nodes transactionally."""

    def merge_relationships(self, relationships: Sequence[GraphRelationship]) -> None:
        """Merge a batch of relationships transactionally."""

    def node_counts(self) -> Mapping[str, int]:
        """Return logical node counts by label."""

    def relationship_counts(self) -> Mapping[str, int]:
        """Return logical relationship counts by type."""


class InMemoryNeo4jGraph:
    """Deterministic in-memory graph used for idempotency tests."""

    def __init__(self, schema_items: set[str] | frozenset[str]) -> None:
        self._schema_items = set(schema_items)
        self._nodes: dict[tuple[str, str], Mapping[str, object]] = {}
        self._relationships: dict[tuple[str, str, str, str, str], Mapping[str, object]] = {}

    def available_schema_items(self) -> set[str]:
        return set(self._schema_items)

    def apply_schema(
        self,
        statements: Sequence[str],
        parameters: Mapping[str, object] | None = None,
    ) -> None:
        del parameters
        for statement in statements:
            match = SCHEMA_NAME_PATTERN.search(statement.strip())
            if match is not None:
                self._schema_items.add(match.group(1))

    def merge_nodes(self, nodes: Sequence[GraphNode]) -> None:
        for node in nodes:
            self._nodes[(node.label, node.id)] = dict(node.properties)

    def merge_relationships(self, relationships: Sequence[GraphRelationship]) -> None:
        for relationship in relationships:
            key = (
                relationship.type,
                relationship.source_label,
                relationship.source_id,
                relationship.target_label,
                relationship.target_id,
            )
            self._relationships[key] = dict(relationship.properties)

    def node_counts(self) -> Mapping[str, int]:
        counts: Counter[str] = Counter(label for label, _ in self._nodes)
        return dict(sorted(counts.items()))

    def relationship_counts(self) -> Mapping[str, int]:
        counts: Counter[str] = Counter(key[0] for key in self._relationships)
        return dict(sorted(counts.items()))


class Neo4jMergeGraph:
    """Neo4j driver-backed implementation of the merge graph protocol."""

    def __init__(self, driver: Any, database: str | None = None) -> None:
        self._driver = driver
        self._database = database

    @property
    def driver(self) -> Any:
        """Return the underlying Neo4j driver for read-only integration checks."""

        return self._driver

    def available_schema_items(self) -> set[str]:
        with self._session() as session:
            records = session.run("SHOW CONSTRAINTS YIELD name RETURN name")
            return {str(record["name"]) for record in records}

    def apply_schema(
        self,
        statements: Sequence[str],
        parameters: Mapping[str, object] | None = None,
    ) -> None:
        safe_parameters = dict(parameters or {})
        with self._session() as session:
            for statement in statements:
                session.run(statement, safe_parameters)

    def merge_nodes(self, nodes: Sequence[GraphNode]) -> None:
        with self._session() as session:
            session.execute_write(self._merge_nodes_tx, tuple(nodes))

    def merge_relationships(self, relationships: Sequence[GraphRelationship]) -> None:
        with self._session() as session:
            session.execute_write(self._merge_relationships_tx, tuple(relationships))

    def node_counts(self) -> Mapping[str, int]:
        with self._session() as session:
            records = session.run(
                "MATCH (n) UNWIND labels(n) AS label RETURN label, count(*) AS count"
            )
            return dict(sorted((str(record["label"]), int(record["count"])) for record in records))

    def relationship_counts(self) -> Mapping[str, int]:
        with self._session() as session:
            records = session.run("MATCH ()-[r]->() RETURN type(r) AS type, count(*) AS count")
            return dict(sorted((str(record["type"]), int(record["count"])) for record in records))

    def _session(self) -> Any:
        return self._driver.session(database=self._database)

    @staticmethod
    def _safe_identifier(identifier: str) -> str:
        if not re.fullmatch(r"[A-Za-z][A-Za-z0-9_]*", identifier):
            raise ValueError(f"Unsafe Neo4j identifier: {identifier}")
        return identifier

    @classmethod
    def _merge_nodes_tx(cls, tx: Any, nodes: Sequence[GraphNode]) -> None:
        for node in nodes:
            label = cls._safe_identifier(node.label)
            tx.run(
                f"MERGE (n:{label} {{id: $id}}) SET n += $properties",
                id=node.id,
                properties=dict(node.properties),
            )

    @classmethod
    def _merge_relationships_tx(
        cls,
        tx: Any,
        relationships: Sequence[GraphRelationship],
    ) -> None:
        for relationship in relationships:
            source_label = cls._safe_identifier(relationship.source_label)
            target_label = cls._safe_identifier(relationship.target_label)
            rel_type = cls._safe_identifier(relationship.type)
            tx.run(
                (
                    f"MATCH (source:{source_label} {{id: $source_id}}) "
                    f"MATCH (target:{target_label} {{id: $target_id}}) "
                    f"MERGE (source)-[r:{rel_type}]->(target) "
                    "SET r += $properties"
                ),
                source_id=relationship.source_id,
                target_id=relationship.target_id,
                properties=dict(relationship.properties),
            )


def neo4j_graph_from_settings(settings: Neo4jSettings) -> Neo4jMergeGraph:
    """Create a Neo4j graph adapter from typed settings without logging secrets."""

    uri = settings.uri
    user = settings.user
    password = settings.password
    missing = [
        name
        for name, value in (
            ("NEO4J_URI", uri),
            ("NEO4J_USER", user),
            ("NEO4J_PASSWORD", password),
        )
        if not value
    ]
    if missing:
        raise RuntimeError(f"Missing Neo4j environment variable(s): {', '.join(missing)}")

    try:
        from neo4j import GraphDatabase
    except ModuleNotFoundError as exc:
        raise RuntimeError("Install the neo4j Python package to use --apply") from exc

    return Neo4jMergeGraph(
        GraphDatabase.driver(uri, auth=(user, password)), database=settings.database
    )


def neo4j_graph_from_env(environ: Mapping[str, str] | None = None) -> Neo4jMergeGraph:
    """Create a Neo4j graph adapter from environment variables without logging secrets."""

    return neo4j_graph_from_settings(
        load_settings(environ=os.environ if environ is None else environ).neo4j
    )


def load_plan_from_neo4j(driver: Any, settings: Neo4jSettings) -> LoadPlan:
    """Read the live Neo4j graph into the existing read-only MCP load-plan contract."""

    with driver.session(database=settings.database) as session:
        node_records = session.run(
            "MATCH (n) RETURN labels(n) AS labels, n.id AS id, properties(n) AS properties"
        )
        relationship_records = session.run(
            "MATCH (source)-[r]->(target) "
            "RETURN type(r) AS type, labels(source) AS source_labels, "
            "source.id AS source_id, labels(target) AS target_labels, "
            "target.id AS target_id, properties(r) AS properties"
        )
        nodes = tuple(
            GraphNode(
                label=_primary_label(record["labels"]),
                id=str(record["id"]),
                properties=cast(Mapping[str, object], dict(record["properties"])),
            )
            for record in node_records
            if record.get("id") is not None
        )
        relationships = tuple(
            GraphRelationship(
                type=str(record["type"]),
                source_label=_primary_label(record["source_labels"]),
                source_id=str(record["source_id"]),
                target_label=_primary_label(record["target_labels"]),
                target_id=str(record["target_id"]),
                properties=cast(Mapping[str, object], dict(record["properties"])),
            )
            for record in relationship_records
            if record.get("source_id") is not None and record.get("target_id") is not None
        )
    return LoadPlan(nodes=nodes, relationships=relationships)


def _primary_label(labels: object) -> str:
    if isinstance(labels, list) and labels and isinstance(labels[0], str):
        return labels[0]
    if isinstance(labels, tuple) and labels and isinstance(labels[0], str):
        return labels[0]
    raise ValueError(f"Neo4j record has no usable label: {labels!r}")


def _records_list(records: Mapping[str, object], key: str) -> tuple[Mapping[str, object], ...]:
    value = records.get(key)
    if not isinstance(value, list):
        return ()
    return tuple(cast(Mapping[str, object], item) for item in value if isinstance(item, dict))


def _string(record: Mapping[str, object], key: str) -> str:
    value = record.get(key)
    return value if isinstance(value, str) else ""


def _node(label: str, node_id: str, properties: Mapping[str, object]) -> GraphNode:
    return GraphNode(label=label, id=node_id, properties={"id": node_id, **dict(properties)})


def _relationship(
    relationship_type: str,
    source_label: str,
    source_id: str,
    target_label: str,
    target_id: str,
    properties: Mapping[str, object] | None = None,
) -> GraphRelationship:
    return GraphRelationship(
        type=relationship_type,
        source_label=source_label,
        source_id=source_id,
        target_label=target_label,
        target_id=target_id,
        properties=dict(properties or {}),
    )


def _unique_strings(values: Sequence[str]) -> list[str]:
    seen: set[str] = set()
    unique_values: list[str] = []
    for value in values:
        cleaned = value.strip()
        if cleaned and cleaned not in seen:
            seen.add(cleaned)
            unique_values.append(cleaned)
    return unique_values


def _token_terms(value: str) -> list[str]:
    return [token for token in TOKEN_PATTERN.findall(value.lower()) if len(token) > 2]


def _priority_weight(section_heading: str) -> float:
    heading = section_heading.lower()
    if heading == "when to use":
        return 1.35
    if heading in {"objective", "verification"}:
        return 1.15
    if heading == "related skills":
        return 0.7
    return 1.0


def _retrieval_unit_from_section(
    section: Mapping[str, object],
    skill: Mapping[str, object],
) -> GraphNode:
    section_id = _string(section, "id")
    content_hash = _string(section, "contentHash")
    skill_name = _string(skill, "name")
    skill_path = _string(skill, "path")
    aliases = tuple(str(alias).strip() for alias in skill.get("aliases", []) if isinstance(alias, str))
    task_shapes = tuple(
        str(task_shape).strip()
        for task_shape in skill.get("task_shapes", [])
        if isinstance(task_shape, str)
    )
    capabilities = tuple(
        str(capability).strip()
        for capability in skill.get("capabilities", [])
        if isinstance(capability, str)
    )
    section_heading = _string(section, "heading")
    lexical_boost_terms = _unique_strings(
        [
            skill_name,
            *aliases,
            section_heading,
            *task_shapes[:4],
            *capabilities[:4],
            *_token_terms(section_heading),
        ]
    )
    semantic_aliases = _unique_strings(
        [
            *aliases,
            *task_shapes,
            *capabilities,
        ]
    )
    unit_id = f"retrieval:{_string(section, 'skill_id')}:section:{section.get('order', 0)}:{content_hash[:12]}"
    return _node(
        "RetrievalUnit",
        unit_id,
        {
            "section_id": section_id,
            "skill_id": _string(section, "skill_id"),
            "unit_type": "section",
            "retrieval_unit_type": "skill-section",
            "title": _string(section, "name"),
            "text": _string(section, "text"),
            "retrieval_text": _string(section, "text"),
            "content_hash": content_hash,
            "source_path": skill_path,
            "section_heading": section_heading,
            "ordinal": section.get("order", 0),
            "lexical_boost_terms": lexical_boost_terms,
            "semantic_aliases": semantic_aliases,
            "priority_weight": _priority_weight(section_heading),
            "embedding_model": "not-embedded",
            "embedding_version": "pending",
            "vector_dimension": 0,
            "retrieval_profile": "skill-section-v1",
        },
    )


def build_load_plan(records: Mapping[str, object]) -> LoadPlan:
    """Convert validated graph records into deterministic Neo4j upserts."""

    validation = validate_graph_records(records)
    if not validation.valid:
        raise ValueError("; ".join(validation.errors))

    skills = _records_list(records, "skills")
    sections = _records_list(records, "sections")
    bridges = _records_list(records, "bridges")
    references = _records_list(records, "references")
    source_relationships = _records_list(records, "relationships")
    skill_pack = (
        records.get("skill_pack") if isinstance(records.get("skill_pack"), dict) else None
    )
    skills_by_id = {_string(skill, "id"): skill for skill in skills}
    nodes: dict[tuple[str, str], GraphNode] = {}
    relationships: dict[tuple[str, str, str, str, str], GraphRelationship] = {}

    def add_node(node: GraphNode) -> None:
        nodes[(node.label, node.id)] = node

    def add_relationship(relationship: GraphRelationship) -> None:
        key = (
            relationship.type,
            relationship.source_label,
            relationship.source_id,
            relationship.target_label,
            relationship.target_id,
        )
        relationships[key] = relationship

    for skill in skills:
        skill_id = _string(skill, "id")
        category = _string(skill, "category")
        add_node(_node("Skill", skill_id, skill))
        add_node(_node("SkillCategory", category, {"name": category}))
        add_relationship(
            _relationship("BELONGS_TO_CATEGORY", "Skill", skill_id, "SkillCategory", category)
        )

    if isinstance(skill_pack, Mapping):
        skill_pack_id = _string(skill_pack, "id")
        if skill_pack_id:
            add_node(
                _node(
                    "SkillPack",
                    skill_pack_id,
                    {
                        **dict(skill_pack),
                        "versionIdentifier": _string(skill_pack, "version"),
                    },
                )
            )
            for skill in skills:
                if _string(skill, "skill_pack_id") == skill_pack_id:
                    add_relationship(
                        _relationship("CONTAINS_SKILL", "SkillPack", skill_pack_id, "Skill", _string(skill, "id"))
                    )

    for section in sections:
        section_id = _string(section, "id")
        skill_id = _string(section, "skill_id")
        add_node(_node("SkillSection", section_id, section))
        add_relationship(
            _relationship("HAS_SECTION", "Skill", skill_id, "SkillSection", section_id)
        )
        retrieval_unit = _retrieval_unit_from_section(section, skills_by_id.get(skill_id, {}))
        add_node(retrieval_unit)
        add_relationship(
            _relationship(
                "HAS_RETRIEVAL_UNIT",
                "SkillSection",
                section_id,
                "RetrievalUnit",
                retrieval_unit.id,
            )
        )
        add_relationship(
            _relationship(
                "DERIVED_FROM",
                "RetrievalUnit",
                retrieval_unit.id,
                "SkillSection",
                section_id,
            )
        )

    for bridge in bridges:
        bridge_id = _string(bridge, "id")
        skill_id = _string(bridge, "skill_id")
        bridge_kind = _string(bridge, "kind")
        bridge_value = _string(bridge, "value")
        add_node(_node("BridgeAssertion", bridge_id, bridge))
        add_relationship(
            _relationship("ASSERTS_BRIDGE", "Skill", skill_id, "BridgeAssertion", bridge_id)
        )
        label_and_relationship = BRIDGE_KIND_TO_LABEL_AND_REL.get(bridge_kind)
        if label_and_relationship is not None:
            label, relationship_type = label_and_relationship
            add_node(_node(label, bridge_value, {"name": bridge_value}))
            add_relationship(
                _relationship(relationship_type, "Skill", skill_id, label, bridge_value)
            )

    for reference in references:
        reference_id = _string(reference, "id")
        skill_id = _string(reference, "skill_id")
        add_node(_node("ReferenceDocument", reference_id, reference))
        add_relationship(
            _relationship("HAS_REFERENCE", "Skill", skill_id, "ReferenceDocument", reference_id)
        )

    for relationship in source_relationships:
        add_relationship(
            _relationship(
                _string(relationship, "type"),
                "Skill",
                _string(relationship, "source"),
                "Skill",
                _string(relationship, "target"),
                relationship,
            )
        )

    return LoadPlan(
        nodes=tuple(nodes[key] for key in sorted(nodes)),
        relationships=tuple(relationships[key] for key in sorted(relationships)),
    )


def ensure_required_schema(graph: MergeGraph) -> None:
    missing = sorted(REQUIRED_SCHEMA_ITEMS - graph.available_schema_items())
    if missing:
        raise MissingSchemaItemError(f"Missing Neo4j schema item(s): {', '.join(missing)}")


def read_schema_statements(schema_path: Path = DEFAULT_SCHEMA_PATH) -> tuple[str, ...]:
    """Read Neo4j schema statements, excluding Browser-only parameter directives."""

    lines = []
    for line in schema_path.read_text(encoding="utf-8").splitlines():
        stripped_line = line.strip()
        if stripped_line.startswith("//") or stripped_line.startswith(":param"):
            continue
        lines.append(line)
    text = "\n".join(lines)
    statements: list[str] = []
    for statement in text.split(";"):
        stripped = statement.strip()
        if stripped and not stripped.startswith(":param"):
            statements.append(stripped)
    return tuple(statements)


def _batches(items: Sequence[object], batch_size: int) -> int:
    if not items:
        return 0
    return (len(items) + batch_size - 1) // batch_size


def load_plan(
    graph: MergeGraph,
    plan: LoadPlan,
    batch_size: int = 500,
    schema_statements: Sequence[str] | None = None,
    schema_parameters: Mapping[str, object] | None = None,
) -> LoadReport:
    """Preflight schema and merge all records in deterministic batches."""

    if schema_statements is not None:
        graph.apply_schema(schema_statements, schema_parameters)
    ensure_required_schema(graph)
    batches = 0
    for index in range(0, len(plan.nodes), batch_size):
        graph.merge_nodes(plan.nodes[index : index + batch_size])
        batches += 1
    for index in range(0, len(plan.relationships), batch_size):
        graph.merge_relationships(plan.relationships[index : index + batch_size])
        batches += 1
    logical_counts = {
        **{f"node:{key}": value for key, value in graph.node_counts().items()},
        **{f"relationship:{key}": value for key, value in graph.relationship_counts().items()},
    }
    return LoadReport(logical_counts=dict(sorted(logical_counts.items())), batches=batches)


def dry_run_report(plan: LoadPlan) -> str:
    node_counts: Counter[str] = Counter(node.label for node in plan.nodes)
    relationship_counts: Counter[str] = Counter(
        relationship.type for relationship in plan.relationships
    )
    lines = ["Skills KG dry-run load report", "Nodes:"]
    lines.extend(f"- {label}: {count}" for label, count in sorted(node_counts.items()))
    lines.append("Relationships:")
    lines.extend(
        f"- {rel_type}: {count}" for rel_type, count in sorted(relationship_counts.items())
    )
    return "\n".join(lines)


def build_repository_load_plan(skills_root: Path = Path("skills")) -> LoadPlan:
    records = extract_skills_graph_records(skills_root)
    mapped_records = apply_semantic_bridge_mappings(records)
    return build_load_plan(mapped_records)


def main(argv: Sequence[str] | None = None) -> int:  # pragma: no cover
    parser = ArgumentParser(description="Load skills KG records into Neo4j.")
    parser.add_argument("records_json", nargs="?", help="Optional exported records JSON file.")
    parser.add_argument(
        "--apply", action="store_true", help="Write to Neo4j using environment settings."
    )
    parser.add_argument("--batch-size", type=int, default=500, help="Transactional batch size.")
    args = parser.parse_args(list(sys.argv[1:] if argv is None else argv))

    if args.records_json:
        records = json.loads(Path(args.records_json).read_text(encoding="utf-8"))
        if not isinstance(records, dict):
            print("FAIL: exported records must be a JSON object")
            return 1
        plan = build_load_plan(cast(Mapping[str, object], records))
    else:
        plan = build_repository_load_plan()

    if args.apply:
        settings = load_settings()
        graph = neo4j_graph_from_settings(settings.neo4j)
        report = load_plan(
            graph,
            plan,
            batch_size=args.batch_size,
            schema_statements=read_schema_statements(),
            schema_parameters={"embedding_dimensions": settings.neo4j.embedding_dimensions},
        )
        print("Skills KG load report")
        for key, value in report.logical_counts.items():
            print(f"- {key}: {value}")
        print(f"- batches: {report.batches}")
        return 0

    print(dry_run_report(plan))
    return 0


if __name__ == "__main__":
    sys.exit(main())
