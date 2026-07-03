"""Shared pytest fixtures and CI-safe defaults."""

from __future__ import annotations

import os

# Unit/integration tests and PR CI must not require Ollama/BGE.
os.environ.setdefault("SKILLS_EMBEDDING_PROVIDER", "deterministic")
