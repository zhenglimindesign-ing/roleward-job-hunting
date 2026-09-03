#!/usr/bin/env python3
"""Deterministic Positioning review and Application artifact provenance helpers."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

from state_store import load_state, save_state, utc_now

ARTIFACT_TYPES = {"resume", "cover_letter", "connection_note", "contact_shortlist"}


def _id(prefix: str, seed: str) -> str:
    return f"{prefix}-{hashlib.sha256((seed + utc_now()).encode()).hexdigest()[:12]}"


def _opportunity(state: dict[str, Any], opportunity_id: str) -> dict[str, Any]:
    try:
        return state["opportunities"][opportunity_id]
    except KeyError as exc:
        raise KeyError(f"Unknown opportunity: {opportunity_id}") from exc


def _career_evidence_ids(state: dict[str, Any]) -> set[str]:
    return {
        str(item.get("id"))
        for item in state["profile"].get("career_evidence", [])
        if item.get("id") and item.get("active", True)
    }


def record_positioning_draft(state: dict[str, Any], opportunity_id: str, content: dict[str, Any]) -> dict[str, Any]:
    opp = _opportunity(state, opportunity_id)
    revision = {
        "id": _id("positioning", opportunity_id),
        "status": "draft",
        "created_at": utc_now(),
        "source_snapshot_id": opp.get("current_snapshot_id"),
        "pursuit_assessment_id": opp.get("current_assessment_id"),
        "content": content,
    }
    opp.setdefault("positioning_revisions", []).append(revision)
    opp["current_positioning_id"] = revision["id"]
    state.setdefault("audit_log", []).append({"event": "positioning_draft_recorded", "opportunity_id": opportunity_id, "positioning_id": revision["id"], "at": utc_now()})
    return revision


def review_positioning(
    state: dict[str, Any], opportunity_id: str, revision_id: str, *, edited_content: dict[str, Any] | None = None
) -> dict[str, Any]:
    opp = _opportunity(state, opportunity_id)
    source = next((item for item in opp.get("positioning_revisions", []) if item.get("id") == revision_id), None)
    if source is None:
        raise KeyError(f"Unknown positioning revision: {revision_id}")
    reviewed = {
        "id": _id("positioning", opportunity_id + revision_id),
        "status": "reviewed",
        "created_at": utc_now(),
        "parent_revision_id": revision_id,
        "source_snapshot_id": source.get("source_snapshot_id"),
        "pursuit_assessment_id": source.get("pursuit_assessment_id"),
        "content": edited_content if edited_content is not None else source.get("content", {}),
    }
    opp["positioning_revisions"].append(reviewed)
    opp["current_positioning_id"] = reviewed["id"]
    opp["current_reviewed_positioning_id"] = reviewed["id"]
    state.setdefault("audit_log", []).append({"event": "positioning_reviewed", "opportunity_id": opportunity_id, "positioning_id": reviewed["id"], "at": utc_now()})
    return reviewed


def _reviewed_positioning(opp: dict[str, Any]) -> dict[str, Any]:
    revision_id = opp.get("current_reviewed_positioning_id")
    if not revision_id:
        raise ValueError("Application artifacts require a reviewed Positioning revision")
    revision = next((item for item in opp.get("positioning_revisions", []) if item.get("id") == revision_id), None)
    if revision is None or revision.get("status") != "reviewed":
        raise ValueError("Current reviewed Positioning revision is missing or invalid")
    return revision


def validate_claim_refs(state: dict[str, Any], claims: list[dict[str, Any]]) -> None:
    known = _career_evidence_ids(state)
    for index, claim in enumerate(claims):
        if not claim.get("factual", True):
            continue
        refs = {str(item) for item in claim.get("evidence_ids", [])}
        if not refs:
            raise ValueError(f"factual claim {index} has no evidence_ids")
        unknown = refs - known
        if unknown:
            raise ValueError(f"factual claim {index} references unknown evidence ids: {sorted(unknown)}")


def record_artifact(
    state: dict[str, Any], opportunity_id: str, artifact_type: str, payload: dict[str, Any]
) -> dict[str, Any]:
    if artifact_type not in ARTIFACT_TYPES:
        raise ValueError(f"artifact_type must be one of {sorted(ARTIFACT_TYPES)}")
    opp = _opportunity(state, opportunity_id)
    positioning = _reviewed_positioning(opp)
    claims = payload.get("claims") or []
    validate_claim_refs(state, claims)

    if artifact_type == "contact_shortlist":
        contacts = payload.get("contacts") or []
        if len(contacts) > 3:
            raise ValueError("contact shortlist may contain at most 3 contacts")

    local_path = payload.get("local_path")
    sha256 = None
    if local_path:
        path = Path(local_path)
        if path.exists() and path.is_file():
            sha256 = hashlib.sha256(path.read_bytes()).hexdigest()

    artifact = {
        "id": _id("artifact", opportunity_id + artifact_type),
        "type": artifact_type,
        "created_at": utc_now(),
        "positioning_revision_id": positioning["id"],
        "source_snapshot_id": positioning.get("source_snapshot_id"),
        "pursuit_assessment_id": positioning.get("pursuit_assessment_id"),
        "evidence_ids": sorted({str(ref) for claim in claims for ref in claim.get("evidence_ids", [])}),
        "local_path": local_path,
        "sha256": sha256,
        "metadata": payload.get("metadata") or {},
    }
    if artifact_type == "contact_shortlist":
        artifact["contacts"] = payload.get("contacts") or []
    opp.setdefault("application_artifacts", []).append(artifact)
    state.setdefault("audit_log", []).append({"event": "application_artifact_recorded", "opportunity_id": opportunity_id, "artifact_id": artifact["id"], "artifact_type": artifact_type, "at": utc_now()})
    return artifact


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--state", default="state/roleward-state.json")
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("position")
    p.add_argument("--opportunity-id", required=True)
    p.add_argument("--input", required=True)

    p = sub.add_parser("review-positioning")
    p.add_argument("--opportunity-id", required=True)
    p.add_argument("--revision-id", required=True)
    p.add_argument("--input")

    p = sub.add_parser("artifact")
    p.add_argument("--opportunity-id", required=True)
    p.add_argument("--type", choices=sorted(ARTIFACT_TYPES), required=True)
    p.add_argument("--input", required=True)

    args = parser.parse_args()
    path = Path(args.state)
    state = load_state(path)

    if args.command == "position":
        content = json.loads(Path(args.input).read_text(encoding="utf-8"))
        result = record_positioning_draft(state, args.opportunity_id, content)
    elif args.command == "review-positioning":
        content = json.loads(Path(args.input).read_text(encoding="utf-8")) if args.input else None
        result = review_positioning(state, args.opportunity_id, args.revision_id, edited_content=content)
    else:
        payload = json.loads(Path(args.input).read_text(encoding="utf-8"))
        result = record_artifact(state, args.opportunity_id, args.type, payload)

    save_state(path, state)
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
