"""Tests for scripts package circular import detection."""

from __future__ import annotations

import tempfile
import textwrap
import unittest
from pathlib import Path

from scripts.validators import validate_import_cycles


class ValidateImportCyclesTests(unittest.TestCase):
    def test_current_scripts_tree_has_no_import_cycles(self) -> None:
        cycles = validate_import_cycles.find_import_cycles()
        self.assertEqual(cycles, [], f"unexpected import cycles: {cycles}")

    def test_detects_direct_two_module_cycle(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            scripts = root / "scripts" / "pkg"
            scripts.mkdir(parents=True)
            (scripts / "module_a.py").write_text(
                textwrap.dedent(
                    """\
                    from scripts.pkg.module_b import helper

                    VALUE = 1
                    """
                ),
                encoding="utf-8",
            )
            (scripts / "module_b.py").write_text(
                textwrap.dedent(
                    """\
                    from scripts.pkg.module_a import VALUE

                    helper = VALUE
                    """
                ),
                encoding="utf-8",
            )

            cycles = validate_import_cycles.find_import_cycles(scripts_root=root / "scripts")
            self.assertEqual(len(cycles), 1)
            self.assertIn("scripts.pkg.module_a", cycles[0])
            self.assertIn("scripts.pkg.module_b", cycles[0])

    def test_ignores_type_checking_imports(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            scripts = root / "scripts" / "pkg"
            scripts.mkdir(parents=True)
            (scripts / "module_a.py").write_text(
                textwrap.dedent(
                    """\
                    from typing import TYPE_CHECKING

                    if TYPE_CHECKING:
                        from scripts.pkg.module_b import helper

                    VALUE = 1
                    """
                ),
                encoding="utf-8",
            )
            (scripts / "module_b.py").write_text(
                "from scripts.pkg.module_a import VALUE\n",
                encoding="utf-8",
            )

            cycles = validate_import_cycles.find_import_cycles(scripts_root=root / "scripts")
            self.assertEqual(cycles, [])

    def test_ignores_function_local_imports(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            scripts = root / "scripts" / "pkg"
            scripts.mkdir(parents=True)
            (scripts / "module_a.py").write_text(
                textwrap.dedent(
                    """\
                    def load() -> int:
                        from scripts.pkg.module_b import helper
                        return helper
                    """
                ),
                encoding="utf-8",
            )
            (scripts / "module_b.py").write_text(
                "from scripts.pkg.module_a import load\n",
                encoding="utf-8",
            )

            cycles = validate_import_cycles.find_import_cycles(scripts_root=root / "scripts")
            self.assertEqual(cycles, [])


if __name__ == "__main__":
    unittest.main()
