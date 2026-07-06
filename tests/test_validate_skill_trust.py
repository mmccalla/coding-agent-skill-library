"""Tests for scripts/validate_skill_trust.py orchestrator."""

from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
ORCHESTRATOR = REPO_ROOT / "scripts/validators/validate_skill_trust.py"
FIXTURES = REPO_ROOT / "tests" / "fixtures" / "skill_trust"
ALLOWLIST = REPO_ROOT / "tests" / "fixtures" / "skill_security_allowlist.json"


def load_orchestrator_module():
    spec = importlib.util.spec_from_file_location("validate_skill_trust", ORCHESTRATOR)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules["validate_skill_trust"] = module
    spec.loader.exec_module(module)
    return module


class ValidateSkillTrustTests(unittest.TestCase):
    def setUp(self) -> None:
        self.module = load_orchestrator_module()

    def test_trust_rejects_malicious_fixture(self) -> None:
        path = FIXTURES / "malicious" / "instruction-override.md"
        report = self.module.validate_skill_trust_file(str(path), allowlist_path=str(ALLOWLIST))
        self.assertFalse(report.passed)
        self.assertEqual("fail", report.layers["L2_security"].status)
        self.assertFalse(report.layers["L2_security"].passed)

    def test_trust_passes_benign_teaching_fixture(self) -> None:
        path = FIXTURES / "benign" / "guardrails-teaching.md"
        report = self.module.validate_skill_trust_file(str(path), allowlist_path=str(ALLOWLIST))
        self.assertTrue(report.passed)
        self.assertTrue(report.layers["L2_security"].passed)
        self.assertTrue(report.layers["L3_practice"].passed)

    def test_trust_cli_report_format(self) -> None:
        path = FIXTURES / "malicious" / "disable-checks.md"
        result = subprocess.run(
            [
                sys.executable,
                str(ORCHESTRATOR),
                "--json",
                str(path),
            ],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(1, result.returncode)
        payload = json.loads(result.stdout)
        self.assertIn("passed", payload)
        self.assertIn("layers", payload)
        self.assertIn("L2_security", payload["layers"])
        self.assertIn("L3_practice", payload["layers"])

    def test_trust_report_serialises_layers(self) -> None:
        path = FIXTURES / "benign" / "guardrails-teaching.md"
        report = self.module.validate_skill_trust_file(str(path), allowlist_path=str(ALLOWLIST))
        payload = report.to_dict()
        self.assertIn("skill_path", payload)
        self.assertIn("layers", payload)
        json.dumps(payload)

    def test_ci_gate_blocks_only_on_l2_security(self) -> None:
        malicious = FIXTURES / "malicious" / "instruction-override.md"
        report = self.module.validate_skill_trust_file(
            str(malicious), allowlist_path=str(ALLOWLIST)
        )
        self.assertFalse(self.module.ci_ingest_gate_passed(report))

        benign = FIXTURES / "benign" / "guardrails-teaching.md"
        benign_report = self.module.validate_skill_trust_file(
            str(benign), allowlist_path=str(ALLOWLIST)
        )
        self.assertTrue(self.module.ci_ingest_gate_passed(benign_report))


if __name__ == "__main__":
    unittest.main()
