#!/usr/bin/env python3
"""Require Developer Certificate of Origin sign-off in commit messages."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

SIGNED_OFF_BY = re.compile(r"^Signed-off-by:\s+.+\s<[^@\s]+@[^@\s]+>", re.MULTILINE)


def commit_message_requires_signoff(message: str) -> bool:
    return bool(SIGNED_OFF_BY.search(message))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "commit_msg_file",
        nargs="?",
        help="Path to the commit message file (commit-msg hook)",
    )
    args = parser.parse_args(argv)

    if not args.commit_msg_file:
        print("check_commit_dco: missing commit message file path", file=sys.stderr)
        return 1

    message = Path(args.commit_msg_file).read_text(encoding="utf-8")
    if commit_message_requires_signoff(message):
        return 0

    print(
        "check_commit_dco: FAIL — commit message must include a DCO sign-off line.\n"
        "  Example: Signed-off-by: Pat Contributor <pat@example.com>\n"
        "  Use: git commit -s",
        file=sys.stderr,
    )
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
