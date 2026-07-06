"""Tests for the pre-public secret scan helper."""

from __future__ import annotations

import subprocess
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = REPO_ROOT / "scripts" / "pre_public_secret_scan.py"


class PrePublicSecretScanTests(unittest.TestCase):
    def test_scan_passes_on_repository_tree(self) -> None:
        proc = subprocess.run(
            ["python3", str(SCRIPT)],
            cwd=REPO_ROOT,
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(
            0,
            proc.returncode,
            msg=proc.stdout + proc.stderr,
        )


if __name__ == "__main__":
    unittest.main()
