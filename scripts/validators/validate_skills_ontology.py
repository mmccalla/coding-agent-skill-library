#!/usr/bin/env python3
"""Validate the repository ontology and SHACL shapes with pySHACL."""

from __future__ import annotations

import os
import sys
from argparse import ArgumentParser
from pathlib import Path
from typing import NamedTuple

from rdflib import Graph
from rdflib.util import guess_format

from scripts.lib.config.repo_paths import REPO_ROOT

ONTOLOGY_DIR = REPO_ROOT / "skills_docs" / "ontology"
DEFAULT_DATA_GRAPH = REPO_ROOT / "skills_docs" / "ontology" / "skills.ttl"
DEFAULT_SHAPES_GRAPH = ONTOLOGY_DIR / "skills.shacl.ttl"
INSTANCE_GRAPHS = (
    ONTOLOGY_DIR / "instances" / "task-intents.ttl",
    ONTOLOGY_DIR / "instances" / "workflow-stages.ttl",
)
PROFILE_SHAPES_GRAPHS = {
    "canonical-core": ONTOLOGY_DIR / "canonical-core.shacl.ttl",
    "retrieval-projection": ONTOLOGY_DIR / "retrieval-projection.shacl.ttl",
    "runtime-selection": ONTOLOGY_DIR / "runtime-selection.shacl.ttl",
}


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


def build_data_graph(
    data_graph_path: Path = DEFAULT_DATA_GRAPH,
    *,
    include_instances: bool = False,
) -> Graph:
    """Load the ontology TBox and optionally merge governed vocabulary instances."""

    data_graph = _load_graph(data_graph_path)
    if not include_instances:
        return data_graph
    for instance_path in INSTANCE_GRAPHS:
        if instance_path.is_file():
            data_graph += _load_graph(instance_path)
    return data_graph


def _validate_graphs(
    data_graph_path: Path,
    shapes_graph_path: Path,
    *,
    include_instances: bool = False,
) -> ValidationResult:
    data_graph = build_data_graph(data_graph_path, include_instances=include_instances)
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

    instance_note = " (with instances)" if include_instances else ""
    if conforms:
        report = (
            "SHACL PASS\n"
            f"- data graph: {data_graph_path}{instance_note}\n"
            f"- shapes graph: {shapes_graph_path}\n"
            f"- triples: data={len(data_graph)}, shapes={len(shapes_graph)}\n"
            f"- report triples: {len(report_graph)}"
        )
        return ValidationResult(True, report)

    report = (
        "SHACL FAIL\n"
        f"- data graph: {data_graph_path}{instance_note}\n"
        f"- shapes graph: {shapes_graph_path}\n"
        f"- triples: data={len(data_graph)}, shapes={len(shapes_graph)}\n"
        f"{report_text.strip()}"
    )
    return ValidationResult(False, report)


def validate_ontology_profile(
    profile: str,
    data_graph_path: Path = DEFAULT_DATA_GRAPH,
    *,
    include_instances: bool = False,
) -> ValidationResult:
    """Validate one named SHACL profile against the ontology data graph."""

    if profile == "combined":
        return _validate_graphs(
            data_graph_path,
            DEFAULT_SHAPES_GRAPH,
            include_instances=include_instances,
        )
    try:
        shapes_graph_path = PROFILE_SHAPES_GRAPHS[profile]
    except KeyError as exc:
        raise ValueError(
            f"Unknown ontology validation profile '{profile}'. "
            f"Expected one of: combined, {', '.join(sorted(PROFILE_SHAPES_GRAPHS))}, all"
        ) from exc
    return _validate_graphs(
        data_graph_path,
        shapes_graph_path,
        include_instances=include_instances,
    )


def validate_skills_ontology(
    data_graph_path: Path = DEFAULT_DATA_GRAPH,
    shapes_graph_path: Path = DEFAULT_SHAPES_GRAPH,
    *,
    profile: str | None = None,
    include_instances: bool = False,
) -> ValidationResult:
    """Validate ontology data and shapes graph conformance with pySHACL."""

    selected_profile = profile or "combined"
    if shapes_graph_path != DEFAULT_SHAPES_GRAPH and profile is None:
        return _validate_graphs(
            data_graph_path,
            shapes_graph_path,
            include_instances=include_instances,
        )
    if selected_profile == "all":
        results: list[str] = []
        all_valid = True
        for profile_name in ("combined", *PROFILE_SHAPES_GRAPHS):
            profile_result = validate_ontology_profile(
                profile_name,
                data_graph_path,
                include_instances=include_instances,
            )
            all_valid = all_valid and profile_result.valid
            results.append(f"[profile: {profile_name}]\n{profile_result.report}")
        return ValidationResult(all_valid, "\n\n".join(results))
    return validate_ontology_profile(
        selected_profile,
        data_graph_path,
        include_instances=include_instances,
    )


def _build_argument_parser() -> ArgumentParser:
    parser = ArgumentParser(
        description="Validate the repository ontology and SHACL profiles with pySHACL."
    )
    parser.add_argument("data_graph", nargs="?", default=str(DEFAULT_DATA_GRAPH))
    parser.add_argument("shapes_graph", nargs="?")
    parser.add_argument(
        "--profile",
        choices=("combined", "canonical-core", "retrieval-projection", "runtime-selection", "all"),
        help="Run the combined shapes graph, one split profile, or all available profiles.",
    )
    parser.add_argument(
        "--include-instances",
        action="store_true",
        help="Merge governed vocabulary instance graphs before SHACL validation.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = _build_argument_parser()
    args = parser.parse_args(sys.argv[1:] if argv is None else argv)

    data_graph_path = Path(args.data_graph)
    shapes_graph_path = Path(args.shapes_graph) if args.shapes_graph else DEFAULT_SHAPES_GRAPH

    missing = [str(path) for path in (data_graph_path,) if not path.is_file()]
    if args.shapes_graph:
        if not shapes_graph_path.is_file():
            missing.append(str(shapes_graph_path))
    elif args.profile == "all":
        missing.extend(
            str(path)
            for path in (DEFAULT_SHAPES_GRAPH, *PROFILE_SHAPES_GRAPHS.values())
            if not path.is_file()
        )
    elif args.profile and args.profile != "combined":
        profile_path = PROFILE_SHAPES_GRAPHS[args.profile]
        if not profile_path.is_file():
            missing.append(str(profile_path))
    elif not DEFAULT_SHAPES_GRAPH.is_file():
        missing.append(str(DEFAULT_SHAPES_GRAPH))

    missing = sorted(dict.fromkeys(missing))
    if missing:
        print("FAIL")
        for path in missing:
            print(f"- missing file: {path}")
        return 1

    try:
        result = validate_skills_ontology(
            data_graph_path,
            shapes_graph_path,
            profile=args.profile,
            include_instances=args.include_instances,
        )
    except Exception as exc:  # pragma: no cover - defensive CLI path
        print("FAIL")
        print(f"- ontology validation error: {exc}")
        return 1

    print(result.report)
    return 0 if result.valid else 1


if __name__ == "__main__":
    raise SystemExit(main())
