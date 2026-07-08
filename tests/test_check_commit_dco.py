"""Tests for DCO commit-message enforcement."""

from __future__ import annotations

import tempfile
import unittest

from scripts.dev_workflow import check_commit_dco


class CheckCommitDcoTests(unittest.TestCase):
    def test_accepts_signed_off_by_line(self) -> None:
        message = "feat: add hook\n\nSigned-off-by: Pat Contributor <pat@example.com>\n"
        self.assertTrue(check_commit_dco.commit_message_requires_signoff(message))

    def test_rejects_missing_signoff(self) -> None:
        self.assertFalse(check_commit_dco.commit_message_requires_signoff("feat: no signoff\n"))

    def test_main_returns_zero_for_valid_commit_msg_file(self) -> None:
        with tempfile.NamedTemporaryFile("w", encoding="utf-8", delete=False) as handle:
            handle.write("fix: thing\n\nSigned-off-by: Pat <pat@example.com>\n")
            path = handle.name
        self.assertEqual(check_commit_dco.main([path]), 0)

    def test_main_returns_one_for_missing_signoff(self) -> None:
        with tempfile.NamedTemporaryFile("w", encoding="utf-8", delete=False) as handle:
            handle.write("fix: thing\n")
            path = handle.name
        self.assertEqual(check_commit_dco.main([path]), 1)


if __name__ == "__main__":
    unittest.main()
