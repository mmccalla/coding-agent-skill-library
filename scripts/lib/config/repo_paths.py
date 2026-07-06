"""Shared repository path helpers for scripts packages."""

from __future__ import annotations

from pathlib import Path


def repo_root() -> Path:
    """Return the repository root (directory containing pyproject.toml)."""

    for parent in Path(__file__).resolve().parents:
        if (parent / "pyproject.toml").is_file():
            return parent
    msg = "Could not locate repository root from scripts package"
    raise RuntimeError(msg)


REPO_ROOT = repo_root()
