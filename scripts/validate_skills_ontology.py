#!/usr/bin/env python3
"""Validate the repository ontology and SHACL shapes with pySHACL."""

from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import NamedTuple

from rdflib import Graph
from rdflib.util import guess_format

REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DATA_GRAPH = REPO_ROOT / "skills_docs" / "ontology" / "skills.ttl"
DEFAULT_SHAPES_GRAPH = REPO_ROOT / "skills_docs" / "ontology" / "skills.shacl.ttl"


class ValidationResult(NamedTuple):
    """Validation outcome suitable for CLI and tests."""

    valid: bool
    report: str


def _ensure_valid_cwd() -> None:
    try:
        os.getcwd()
    except FileNotFoundError:
        os.chdir(REPO_ROOT)


def _load_graph(path: Path) -> Graph:
    _ensure_valid_cwd()
    resolved = path.resolve(strict=True)
    graph = Graph()
    graph.parse(
        data=resolved.read_text(encoding="utf-8"),
        format=guess_format(resolved.name),
    )
    return graph


def _pyshacl_validate():
    try:
        from pyshacl import validate as validate_fn
    except ModuleNotFoundError as exc:  # pragma: no cover - environment-specific
        raise RuntimeError(
            "pyshacl is not installed in the active interpreter; use the project venv or `uv run`"
        ) from exc
    return validate_fn


def validate_skills_ontology(
    data_graph_path: Path = DEFAULT_DATA_GRAPH,
    shapes_graph_path: Path = DEFAULT_SHAPES_GRAPH,
) -> ValidationResult:
    """Validate ontology data and shapes graph conformance with pySHACL."""

    data_graph = _load_graph(data_graph_path)
    shapes_graph = _load_graph(shapes_graph_path)
    validate_fn = _pyshacl_validate()

    conforms, report_graph, report_text = validate_fn(
        data_graph=data_graph,
        shacl_graph=shapes_graph,
        ont_graph=None,
        inference="rdfs",
        abort_on_first=False,
        allow_infos=True,
        allow_warnings=True,
        meta_shacl=True,
        advanced=True,
    )

    if conforms:
        report = (
            "SHACL PASS\n"
            f"- data graph: {data_graph_path}\n"
            f"- shapes graph: {shapes_graph_path}\n"
            f"- triples: data={len(data_graph)}, shapes={len(shapes_graph)}\n"
            f"- report triples: {len(report_graph)}"
        )
        return ValidationResult(True, report)

    report = (
        "SHACL FAIL\n"
        f"- data graph: {data_graph_path}\n"
        f"- shapes graph: {shapes_graph_path}\n"
        f"- triples: data={len(data_graph)}, shapes={len(shapes_graph)}\n"
        f"{report_text.strip()}"
    )
    return ValidationResult(False, report)


def main(argv: list[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    if len(args) > 2:
        print("Usage: validate_skills_ontology.py [skills.ttl] [skills.shacl.ttl]")
        return 2

    data_graph_path = Path(args[0]) if args else DEFAULT_DATA_GRAPH
    shapes_graph_path = Path(args[1]) if len(args) == 2 else DEFAULT_SHAPES_GRAPH

    missing = [str(path) for path in (data_graph_path, shapes_graph_path) if not path.is_file()]
    if missing:
        print("FAIL")
        for path in missing:
            print(f"- missing file: {path}")
        return 1

    try:
        result = validate_skills_ontology(data_graph_path, shapes_graph_path)
    except Exception as exc:  # pragma: no cover - defensive CLI path
        print("FAIL")
        print(f"- ontology validation error: {exc}")
        return 1

    print(result.report)
    return 0 if result.valid else 1


if __name__ == "__main__":
    raise SystemExit(main())
