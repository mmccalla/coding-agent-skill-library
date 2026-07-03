#!/usr/bin/env python3
"""Report Skills KG usage metrics and zero-hit promoted skills."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.evaluate_skill_retrieval import load_promoted_skill_ids
from scripts.skills_usage import usage_metrics_text

_COUNTER_LINE = re.compile(
    r"^skills_usage_hits_total\{skill_id=\"([^\"]+)\",tool=\"([^\"]+)\"\} (\d+(?:\.\d+)?)$"
)


def parse_skill_hit_counts(metrics_text: str) -> dict[str, int]:
    """Parse skills_usage_hits_total counters from Prometheus exposition text."""

    counts: dict[str, int] = {}
    for line in metrics_text.splitlines():
        match = _COUNTER_LINE.match(line.strip())
        if not match:
            continue
        skill_id, _tool, value = match.group(1), match.group(2), match.group(3)
        counts[skill_id] = counts.get(skill_id, 0) + int(float(value))
    return counts


def zero_hit_promoted_skills(
    promoted_ids: frozenset[str],
    hit_counts: dict[str, int],
) -> tuple[str, ...]:
    """Return promoted skill ids with no recorded usage hits."""

    return tuple(
        sorted(skill_id for skill_id in promoted_ids if hit_counts.get(skill_id, 0) == 0)
    )


def build_usage_report(*, skills_root: Path | None = None) -> dict[str, object]:
    """Build an operator snapshot from in-process usage metrics."""

    metrics_text = usage_metrics_text()
    hit_counts = parse_skill_hit_counts(metrics_text)
    promoted_ids = load_promoted_skill_ids(skills_root)
    zero_hits = zero_hit_promoted_skills(promoted_ids, hit_counts)
    return {
        "promoted_skill_count": len(promoted_ids),
        "skills_with_hits": len([skill_id for skill_id in promoted_ids if hit_counts.get(skill_id, 0) > 0]),
        "zero_hit_promoted_skills": list(zero_hits),
        "hit_counts": {skill_id: hit_counts[skill_id] for skill_id in sorted(hit_counts)},
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Report Skills KG usage metrics snapshot.")
    parser.add_argument("--skills-root", default="skills")
    parser.add_argument("--json", action="store_true", help="Emit JSON report")
    args = parser.parse_args(argv)

    report = build_usage_report(skills_root=Path(args.skills_root))
    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        print(f"Promoted skills: {report['promoted_skill_count']}")
        print(f"Skills with hits: {report['skills_with_hits']}")
        zero_hits = report["zero_hit_promoted_skills"]
        print(f"Zero-hit promoted skills: {len(zero_hits)}")
        for skill_id in zero_hits[:20]:
            print(f"- {skill_id}")
        if len(zero_hits) > 20:
            print(f"... and {len(zero_hits) - 20} more")
    return 0


if __name__ == "__main__":
    sys.exit(main())
