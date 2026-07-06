"""Tests for documentation hygiene validator."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from scripts.validators import validate_docs

REPO_ROOT = Path(__file__).resolve().parents[1]


class ValidateDocsTests(unittest.TestCase):
    def test_scan_docs_passes_on_current_active_tree(self) -> None:
        violations = validate_docs.scan_docs(REPO_ROOT / "skills_docs")
        messages = [f"{v.path.name}: {v.phrase}" for v in violations]
        self.assertEqual(violations, [], f"unexpected violations: {messages}")

    def test_scan_docs_flags_stale_phrase_outside_archive(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            active = root / "krag"
            active.mkdir(parents=True)
            (active / "STATUS.md").write_text(
                "phase 0 only\n",
                encoding="utf-8",
            )
            violations = validate_docs.scan_docs(root)
            self.assertEqual(len(violations), 1)
            self.assertEqual(violations[0].phrase, "phase 0 only")


if __name__ == "__main__":
    unittest.main()
