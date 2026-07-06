#!/usr/bin/env python3
"""Scan all tracked files for likely secrets before making the repository public."""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]

PATTERNS: tuple[tuple[re.Pattern[str], str], ...] = (
    (re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH |DSA )?PRIVATE KEY-----"), "private-key"),
    (re.compile(r"AKIA[0-9A-Z]{16}"), "aws-access-key-id"),
    (re.compile(r"(?i)api[_-]?key\s*[:=]\s*['\"][A-Za-z0-9_\-]{20,}"), "api-key-assignment"),
    (re.compile(r"(?i)secret\s*[:=]\s*['\"][^'\"]{12,}"), "secret-assignment"),
    (re.compile(r"ghp_[A-Za-z0-9]{36}"), "github-pat"),
    (re.compile(r"xox[baprs]-[A-Za-z0-9-]{10,}"), "slack-token"),
)

ALLOW_PREFIXES = ("tests/fixtures/skill_trust/malicious/",)


def tracked_files() -> list[str]:
    proc = subprocess.run(
        ["git", "ls-files"],
        cwd=REPO_ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    return [line.strip() for line in proc.stdout.splitlines() if line.strip()]


def scan() -> list[str]:
    failures: list[str] = []
    for relative in tracked_files():
        if any(relative.startswith(prefix) for prefix in ALLOW_PREFIXES):
            continue
        path = REPO_ROOT / relative
        if not path.is_file():
            continue
        try:
            content = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        for pattern, name in PATTERNS:
            if pattern.search(content):
                failures.append(f"{relative}: possible {name}")
    return failures


def main() -> int:
    failures = scan()
    if failures:
        print("pre_public_secret_scan: FAIL", file=sys.stderr)
        for item in failures:
            print(f"  - {item}", file=sys.stderr)
        return 1
    print("pre_public_secret_scan: OK (no supported secret patterns in tracked files)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
