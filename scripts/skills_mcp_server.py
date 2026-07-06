#!/usr/bin/env python3
"""Backward-compatible entrypoint for skills-kg MCP (moved to runtime/mcp/)."""

from __future__ import annotations

import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[1]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from scripts.runtime.mcp.skills_mcp_server import main  # noqa: E402

if __name__ == "__main__":
    raise SystemExit(main())
