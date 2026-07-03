#!/usr/bin/env python3
"""Weekly operator rollup for Skills KG usage analytics."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import UTC, datetime, timedelta
from pathlib import Path

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.report_skill_usage import build_usage_report


def build_weekly_rollup(*, skills_root: Path, period_days: int = 7) -> dict[str, object]:
    """Build a bounded weekly usage rollup for operator review."""

    now = datetime.now(UTC)
    window_start = now - timedelta(days=period_days)
    usage = build_usage_report(skills_root=skills_root)
    zero_hits = usage["zero_hit_promoted_skills"]
    return {
        "rollup_type": "weekly_skill_usage",
        "period_days": period_days,
        "window_start": window_start.isoformat(),
        "window_end": now.isoformat(),
        "promoted_skill_count": usage["promoted_skill_count"],
        "skills_with_hits": usage["skills_with_hits"],
        "zero_hit_promoted_skill_count": len(zero_hits),
        "zero_hit_promoted_skills": zero_hits,
        "hit_counts": usage["hit_counts"],
        "notes": (
            "Counters reflect in-process Prometheus state for the running API/MCP process. "
            "For durable weekly history, scrape /metrics into Prometheus and query rate() over the window."
        ),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Emit weekly Skills KG usage rollup.")
    parser.add_argument("--skills-root", default="skills")
    parser.add_argument("--period-days", type=int, default=7)
    parser.add_argument("--json", action="store_true", help="Emit JSON rollup")
    args = parser.parse_args(argv)

    rollup = build_weekly_rollup(
        skills_root=Path(args.skills_root),
        period_days=args.period_days,
    )
    if args.json:
        print(json.dumps(rollup, indent=2, sort_keys=True))
        return 0

    print(f"Weekly Skills KG usage rollup ({rollup['period_days']}d)")
    print(f"Promoted skills: {rollup['promoted_skill_count']}")
    print(f"Skills with hits: {rollup['skills_with_hits']}")
    zero_hits = rollup["zero_hit_promoted_skills"]
    print(f"Zero-hit promoted skills: {len(zero_hits)}")
    for skill_id in zero_hits[:25]:
        print(f"- {skill_id}")
    if len(zero_hits) > 25:
        print(f"... and {len(zero_hits) - 25} more")
    print(rollup["notes"])
    return 0


if __name__ == "__main__":
    sys.exit(main())
