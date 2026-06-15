#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

echo "==> validate_skills.py"
python3 scripts/validate_skills.py

echo "==> unittest"
python3 -m unittest discover -s tests -p 'test_*.py' -q

echo "==> skill count"
count="$(find skills -name 'SKILL.md' | wc -l | tr -d ' ')"
if [ "$count" != "87" ]; then
  echo "expected 87 SKILL.md files, found $count" >&2
  exit 1
fi

echo "CI local checks passed."
