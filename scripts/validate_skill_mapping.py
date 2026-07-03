#!/usr/bin/env python3
"""L4 semantic mapping readiness validation for SKILL.md content."""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass
from pathlib import Path

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.skill_section_mapping import (
    PROMOTION_READY_SOURCES,
    map_skill_sections,
    promotion_ready_task_intents,
)

REPO_ROOT = Path(__file__).resolve().parents[1]


@dataclass(frozen=True)
class MappingReadinessResult:
    skill_path: str
    skill_name: str
    promotion_prediction: str
    passed: bool
    ready_intent_count: int
    total_intent_count: int
    mapping_sources: tuple[str, ...]
    task_intents: tuple[dict[str, object], ...]

    def to_dict(self) -> dict[str, object]:
        return {
            "skill_path": self.skill_path,
            "skill_name": self.skill_name,
            "promotion_prediction": self.promotion_prediction,
            "passed": self.passed,
            "ready_intent_count": self.ready_intent_count,
            "total_intent_count": self.total_intent_count,
            "mapping_sources": list(self.mapping_sources),
            "task_intents": list(self.task_intents),
        }


def _skill_name_from_path(path: str) -> str:
    return Path(path).parent.name or Path(path).stem


def validate_skill_mapping_file(
    skill_path: str, markdown: str | None = None
) -> MappingReadinessResult:
    """Predict promotion readiness from semantic mapping sources."""

    text = markdown if markdown is not None else Path(skill_path).read_text(encoding="utf-8")
    skill_name = _skill_name_from_path(skill_path)
    mapping = map_skill_sections(text, skill_name=skill_name)
    ready = promotion_ready_task_intents(mapping.task_intents)
    sources = tuple(sorted({intent.mapping_source for intent in ready}))
    promotion_prediction = "promoted" if ready else "quarantined"
    task_intents = tuple(
        {
            "task_intent_id": intent.task_intent_id,
            "mapping_source": intent.mapping_source,
            "confidence": intent.confidence,
            "matched_phrase": intent.matched_phrase,
        }
        for intent in mapping.task_intents
    )
    return MappingReadinessResult(
        skill_path=skill_path,
        skill_name=skill_name,
        promotion_prediction=promotion_prediction,
        passed=bool(ready),
        ready_intent_count=len(ready),
        total_intent_count=len(mapping.task_intents),
        mapping_sources=sources,
        task_intents=task_intents,
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate semantic mapping readiness for skills.")
    parser.add_argument("paths", nargs="+", help="Skill markdown paths")
    parser.add_argument("--json", action="store_true", help="Emit JSON")
    args = parser.parse_args(argv)

    results = [validate_skill_mapping_file(path) for path in args.paths]
    passed = all(result.passed for result in results)

    if args.json:
        payload: dict[str, object]
        if len(results) == 1:
            payload = results[0].to_dict()
        else:
            payload = {
                "passed": passed,
                "promotion_ready_sources": sorted(PROMOTION_READY_SOURCES),
                "results": [result.to_dict() for result in results],
            }
        print(json.dumps(payload))
    else:
        if passed:
            print(f"PASS: mapping readiness for {len(results)} skill(s).")
        else:
            print("FAIL")
            for result in results:
                if result.passed:
                    continue
                print(
                    f"- {result.skill_path}: prediction={result.promotion_prediction} "
                    f"ready={result.ready_intent_count}/{result.total_intent_count}"
                )
    return 0 if passed else 1


if __name__ == "__main__":
    sys.exit(main())
