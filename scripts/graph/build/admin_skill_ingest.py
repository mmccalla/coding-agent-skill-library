#!/usr/bin/env python3
"""Admin-gated skill ingest: write SKILL.md, trust-validate, extract and reload graph plan."""

from __future__ import annotations

import hashlib
import json
import os
import re
import tempfile
from collections import deque
from collections.abc import Mapping
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from scripts.graph.build import embed_skill_chunks, extract_skills_graph
from scripts.graph.load import load_skills_neo4j
from scripts.lib.config.repo_paths import REPO_ROOT
from scripts.lib.config.skills_inventory import PACK_METADATA_FILENAME
from scripts.validators import validate_skills_graph
from scripts.validators.validate_skill_trust import TrustReport, validate_skill_trust_file

DEFAULT_SKILLS_ROOT = REPO_ROOT / "skills"
DEFAULT_INGEST_CATEGORY = "engineering-practices"
_AUDIT_LOG: deque[dict[str, object]] = deque(maxlen=100)


@dataclass(frozen=True)
class AdminIngestConfig:
    api_key: str
    write_mode: str
    write_root: Path


@dataclass(frozen=True)
class AdminIngestResult:
    outcome: str
    skill_name: str
    skill_id: str
    promotion_status: str
    trust_hash: str
    trust: dict[str, object]
    written_path: str
    persisted: bool
    message: str
    actor: str

    def to_dict(self) -> dict[str, object]:
        return {
            "outcome": self.outcome,
            "skill_name": self.skill_name,
            "skill_id": self.skill_id,
            "promotion_status": self.promotion_status,
            "trust_hash": self.trust_hash,
            "trust": self.trust,
            "written_path": self.written_path,
            "persisted": self.persisted,
            "message": self.message,
            "actor": self.actor,
        }


def load_admin_config(
    environ: Mapping[str, str] | None = None,
    *,
    repo_root: Path = REPO_ROOT,
) -> AdminIngestConfig:
    env = environ or os.environ
    api_key = env.get("SKILLS_ADMIN_API_KEY", "").strip()
    write_mode = env.get("SKILLS_ADMIN_WRITE_MODE", "direct").strip().lower()
    if write_mode not in {"direct", "staging"}:
        write_mode = "direct"
    override = env.get("SKILLS_ADMIN_WRITE_ROOT", "").strip()
    if override:
        write_root = Path(override)
    elif write_mode == "staging":
        write_root = repo_root / "var" / "staging" / "skills"
    else:
        write_root = repo_root / "skills"
    return AdminIngestConfig(api_key=api_key, write_mode=write_mode, write_root=write_root)


def admin_ingest_enabled(config: AdminIngestConfig) -> bool:
    return bool(config.api_key)


def trust_report_hash(report: TrustReport) -> str:
    payload = json.dumps(report.to_dict(), sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def _extract_skill_name(content: str) -> str:
    if not content.startswith("---\n"):
        return ""
    end = content.find("\n---\n", 4)
    if end == -1:
        return ""
    frontmatter = content[4:end]
    match = re.search(r"^name:\s*(.+)$", frontmatter, flags=re.MULTILINE)
    return match.group(1).strip() if match else ""


def _safe_skill_dir_name(name: str) -> str:
    if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", name):
        raise ValueError(f"unsafe skill folder name: {name!r}")
    return name


def write_skill_markdown(*, content: str, skill_name: str, write_root: Path) -> Path:
    safe_name = _safe_skill_dir_name(skill_name)
    skill_dir = write_root / safe_name
    skill_dir.mkdir(parents=True, exist_ok=True)
    target = skill_dir / "SKILL.md"
    target.write_text(content, encoding="utf-8")
    return target


def register_skill_in_pack_metadata(
    *,
    write_root: Path,
    skill_name: str,
    category_id: str = DEFAULT_INGEST_CATEGORY,
) -> None:
    """Append a newly ingested skill to pack metadata when it is not already registered."""

    metadata_path = write_root / PACK_METADATA_FILENAME
    if not metadata_path.is_file():
        raise FileNotFoundError(f"Pack metadata not found at {metadata_path}")

    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    categories = metadata.get("categories")
    if not isinstance(categories, list):
        raise ValueError("Pack metadata is missing a categories list.")

    for category in categories:
        if not isinstance(category, dict):
            continue
        if str(category.get("id", "")).strip() != category_id:
            continue
        skills = category.get("skills")
        if not isinstance(skills, list):
            skills = []
        if skill_name not in skills:
            skills.append(skill_name)
        category["skills"] = skills
        metadata_path.write_text(
            json.dumps(metadata, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
        return

    raise ValueError(f"Pack metadata has no category with id {category_id!r}.")


def _trust_dict_from_path(path: Path) -> tuple[TrustReport, dict[str, object]]:
    report = validate_skill_trust_file(str(path))
    trust = {
        "passed": report.passed,
        "layers": report.to_dict()["layers"],
    }
    return report, trust


def _promotion_for_skill(records: Mapping[str, object], skill_name: str) -> str:
    skills = records.get("skills")
    if not isinstance(skills, list):
        return "unknown"
    for skill in skills:
        if isinstance(skill, dict) and skill.get("name") == skill_name:
            value = skill.get("promotion_status")
            return value if isinstance(value, str) else "unknown"
    return "unknown"


def append_audit_record(record: dict[str, object]) -> None:
    _AUDIT_LOG.appendleft(record)


def list_recent_ingests(limit: int = 20) -> list[dict[str, object]]:
    return list(_AUDIT_LOG)[: max(1, limit)]


def run_admin_skill_ingest(
    *,
    content: str,
    actor: str,
    skills_root: Path,
    config: AdminIngestConfig | None = None,
    neo4j_loader: Any | None = None,
) -> AdminIngestResult:
    """Write a trusted SKILL.md and rebuild the in-memory graph plan."""

    skill_name = _extract_skill_name(content)
    if not skill_name:
        return AdminIngestResult(
            outcome="rejected",
            skill_name="",
            skill_id="",
            promotion_status="rejected",
            trust_hash="",
            trust={"passed": False, "layers": {}},
            written_path="",
            persisted=False,
            message="Missing frontmatter name.",
            actor=actor,
        )

    with tempfile.NamedTemporaryFile(
        mode="w",
        encoding="utf-8",
        suffix=".md",
        delete=False,
    ) as temp_file:
        temp_file.write(content)
        temp_path = Path(temp_file.name)

    try:
        report, trust = _trust_dict_from_path(temp_path)
        digest = trust_report_hash(report)
        if not report.passed:
            result = AdminIngestResult(
                outcome="rejected",
                skill_name=skill_name,
                skill_id=f"skill:{skill_name}",
                promotion_status="rejected",
                trust_hash=digest,
                trust=trust,
                written_path="",
                persisted=False,
                message="Trust gates failed; skill was not written.",
                actor=actor,
            )
            append_audit_record(
                {
                    "timestamp": datetime.now(UTC).isoformat(),
                    "actor": actor,
                    "skill_name": skill_name,
                    "outcome": "rejected",
                    "trust_hash": digest,
                }
            )
            return result

        written_path = write_skill_markdown(
            content=content,
            skill_name=skill_name,
            write_root=skills_root,
        )
        register_skill_in_pack_metadata(write_root=skills_root, skill_name=skill_name)
        records = extract_skills_graph.extract_skills_graph_records(skills_root)
        validate_skills_graph.validate_graph_records(records)
        promotion_status = _promotion_for_skill(records, skill_name)

        if neo4j_loader is not None:
            neo4j_loader(records)

        plan = embed_skill_chunks.build_embedded_repository_load_plan(skills_root)
        _ = plan  # caller reloads MCP server plan from skills_root

        result = AdminIngestResult(
            outcome="success",
            skill_name=skill_name,
            skill_id=f"skill:{skill_name}",
            promotion_status=promotion_status,
            trust_hash=digest,
            trust=trust,
            written_path=str(written_path),
            persisted=True,
            message="Skill ingested; graph plan can be reloaded from repository.",
            actor=actor,
        )
        append_audit_record(
            {
                "timestamp": datetime.now(UTC).isoformat(),
                "actor": actor,
                "skill_name": skill_name,
                "outcome": "success",
                "trust_hash": digest,
                "written_path": str(written_path),
                "promotion_status": promotion_status,
            }
        )
        return result
    finally:
        temp_path.unlink(missing_ok=True)


def build_repository_plan(skills_root: Path) -> load_skills_neo4j.LoadPlan:
    return embed_skill_chunks.build_embedded_repository_load_plan(skills_root)
