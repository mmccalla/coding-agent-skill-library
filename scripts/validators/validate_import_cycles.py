#!/usr/bin/env python3
"""Detect circular module-level imports within the scripts package."""

from __future__ import annotations

import argparse
import ast
import sys
from dataclasses import dataclass
from pathlib import Path

from scripts.lib.config.repo_paths import REPO_ROOT

SCRIPTS_ROOT = REPO_ROOT / "scripts"
PACKAGE_PREFIX = "scripts"
EXCLUDED_FILENAME_PREFIXES = ("apply_phase",)


@dataclass(frozen=True)
class ImportCycle:
    modules: tuple[str, ...]

    def format(self) -> str:
        return " -> ".join((*self.modules, self.modules[0]))


def _is_excluded(path: Path) -> bool:
    return any(path.name.startswith(prefix) for prefix in EXCLUDED_FILENAME_PREFIXES)


def module_name_for_path(path: Path, scripts_root: Path) -> str | None:
    try:
        rel = path.relative_to(scripts_root)
    except ValueError:
        return None

    parts = list(rel.parts)
    if parts[-1] == "__init__.py":
        parts = parts[:-1]
    else:
        parts[-1] = parts[-1].removesuffix(".py")

    if not parts:
        return PACKAGE_PREFIX
    return f"{PACKAGE_PREFIX}.{'.'.join(parts)}"


def build_module_index(scripts_root: Path) -> dict[str, Path]:
    index: dict[str, Path] = {}
    for path in scripts_root.rglob("*.py"):
        if _is_excluded(path):
            continue
        module_name = module_name_for_path(path, scripts_root)
        if module_name is not None:
            index[module_name] = path
    return index


def resolve_relative_import(current_module: str, level: int, module: str | None) -> str:
    parts = current_module.split(".")
    if level > len(parts):
        msg = f"invalid relative import level {level} in {current_module}"
        raise ValueError(msg)

    base_parts = parts[: len(parts) - level]
    if module:
        base_parts.extend(module.split("."))
    return ".".join(base_parts)


def _is_type_checking_if(node: ast.If) -> bool:
    test = node.test
    return isinstance(test, ast.Name) and test.id == "TYPE_CHECKING"


class TopLevelImportCollector(ast.NodeVisitor):
    def __init__(self, current_module: str, module_index: dict[str, Path]) -> None:
        self.current_module = current_module
        self.module_index = module_index
        self.dependencies: set[str] = set()
        self._scope_depth = 0
        self._skip_depth = 0

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        self._scope_depth += 1
        self.generic_visit(node)
        self._scope_depth -= 1

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        self._scope_depth += 1
        self.generic_visit(node)
        self._scope_depth -= 1

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        self._scope_depth += 1
        self.generic_visit(node)
        self._scope_depth -= 1

    def visit_If(self, node: ast.If) -> None:
        if _is_type_checking_if(node):
            self._skip_depth += 1
            self.generic_visit(node)
            self._skip_depth -= 1
            return
        self.generic_visit(node)

    def visit_Import(self, node: ast.Import) -> None:
        if self._scope_depth or self._skip_depth:
            return
        for alias in node.names:
            self._add_module(alias.name)

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        if self._scope_depth or self._skip_depth:
            return
        if node.module is None and node.level == 0:
            return

        if node.level:
            target_module = resolve_relative_import(
                self.current_module,
                node.level,
                node.module,
            )
        else:
            target_module = node.module or ""

        if not target_module.startswith(PACKAGE_PREFIX):
            return

        self._add_module(target_module)
        for alias in node.names:
            if alias.name == "*":
                continue
            submodule = f"{target_module}.{alias.name}"
            if submodule in self.module_index:
                self.dependencies.add(submodule)

    def _add_module(self, module_name: str) -> None:
        if not module_name.startswith(PACKAGE_PREFIX):
            return
        if module_name in self.module_index:
            self.dependencies.add(module_name)
            return

        parts = module_name.split(".")
        while parts:
            candidate = ".".join(parts)
            if candidate in self.module_index:
                self.dependencies.add(candidate)
                return
            parts.pop()


def extract_dependencies(
    path: Path,
    current_module: str,
    module_index: dict[str, Path],
) -> set[str]:
    source = path.read_text(encoding="utf-8")
    tree = ast.parse(source, filename=str(path))
    collector = TopLevelImportCollector(current_module, module_index)
    collector.visit(tree)
    return collector.dependencies


def build_import_graph(
    scripts_root: Path,
    module_index: dict[str, Path],
) -> dict[str, set[str]]:
    graph: dict[str, set[str]] = {module: set() for module in module_index}
    for module_name, path in sorted(module_index.items()):
        dependencies = extract_dependencies(path, module_name, module_index)
        graph[module_name].update(dependencies)
    return graph


def _normalize_cycle(cycle: list[str]) -> tuple[str, ...]:
    if not cycle or cycle[0] == cycle[-1]:
        body = cycle[:-1] if cycle and cycle[0] == cycle[-1] else cycle
    else:
        body = cycle

    if not body:
        return tuple()

    start = min(range(len(body)), key=body.__getitem__)
    rotated = body[start:] + body[:start]
    return tuple(rotated)


def find_cycles_in_graph(graph: dict[str, set[str]]) -> list[tuple[str, ...]]:
    cycles: list[tuple[str, ...]] = []
    seen: set[tuple[str, ...]] = set()
    visited: set[str] = set()
    stack: list[str] = []
    in_stack: set[str] = set()
    path_index: dict[str, int] = {}

    def record_cycle(cycle: list[str]) -> None:
        normalized = _normalize_cycle(cycle)
        if not normalized or normalized in seen:
            return
        seen.add(normalized)
        cycles.append(normalized)

    def dfs(node: str) -> None:
        visited.add(node)
        stack.append(node)
        in_stack.add(node)
        path_index[node] = len(stack) - 1

        for neighbor in sorted(graph.get(node, ())):
            if neighbor not in graph:
                continue
            if neighbor not in visited:
                dfs(neighbor)
            elif neighbor in in_stack:
                start = path_index[neighbor]
                record_cycle(stack[start:] + [neighbor])

        stack.pop()
        in_stack.remove(node)
        path_index.pop(node, None)

    for node in sorted(graph):
        if node not in visited:
            dfs(node)

    return sorted(cycles)


def find_import_cycles(scripts_root: Path = SCRIPTS_ROOT) -> list[tuple[str, ...]]:
    module_index = build_module_index(scripts_root)
    graph = build_import_graph(scripts_root, module_index)
    return find_cycles_in_graph(graph)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.parse_args(argv)

    cycles = find_import_cycles()
    if not cycles:
        print("validate_import_cycles: OK (no circular imports in scripts package)")
        return 0

    print("validate_import_cycles: FAIL — circular imports detected", file=sys.stderr)
    for cycle in cycles:
        print(f"  - {ImportCycle(cycle).format()}", file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
