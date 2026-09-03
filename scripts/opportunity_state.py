#!/usr/bin/env python3
"""Deterministic Opportunity identity, source snapshot and score persistence."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path
from typing import Any
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

from state_store import load_state, save_state, utc_now

MATERIALITY = {"core": 3.0, "important": 1.0, "bonus": 0.25}
COVERAGE = {"met": 1.0, "partial": 0.5, "missing": 0.0}
RECOMMENDATIONS = {"pursue", "verify_first", "pass"}
TRACKING_PREFIXES = ("utm_",)
TRACKING_KEYS = {"ref", "source", "trk", "trackingId", "gh_src"}


def round5(value: float) -> int:
    return int(5 * round(value / 5.0))


def normalize_url(url: str | None) -> str | None:
    if not url:
        return None
    parts = urlsplit(url.strip())
    query = [
        (k, v)
        for k, v in parse_qsl(parts.query, keep_blank_values=True)
        if k not in TRACKING_KEYS and not any(k.startswith(prefix) for prefix in TRACKING_PREFIXES)
    ]
    path = re.sub(r"/+", "/", parts.path or "/").rstrip("/") or "/"
    return urlunsplit((parts.scheme.lower(), parts.netloc.lower(), path, urlencode(query), ""))


def slug(text: str) -> str:
    value = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
    return value[:60] or "unknown"


def opportunity_identity(company: str, title: str, url: str | None) -> str:
    canonical = normalize_url(url)
    seed = canonical or f"{company.strip().lower()}|{title.strip().lower()}"
    digest = hashlib.sha256(seed.encode("utf-8")).hexdigest()[:12]
    return f"opp-{slug(company)[:24]}-{slug(title)[:30]}-{digest}"


def snapshot(job: dict[str, Any]) -> dict[str, Any]:
    source_text = str(job.get("text") or "")
    canonical = normalize_url(job.get("url"))
    digest_seed = json.dumps({"canonical_url": canonical, "title": job.get("title"), "company": job.get("company"), "source_text": source_text}, sort_keys=True, ensure_ascii=False)
    digest = hashlib.sha256(digest_seed.encode("utf-8")).hexdigest()
    return {
        "id": f"snap-{digest[:16]}",
        "observed_at": utc_now(),
        "canonical_url": canonical,
        "title": job.get("title"),
        "company": job.get("company"),
        "location": job.get("location"),
        "source_sha256": digest,
        "source_text": source_text,
        "live_status": job.get("live_status", "unknown"),
    }


def capability_raw(requirements: list[dict[str, Any]]) -> float:
    numerator = 0.0
    denominator = 0.0
    for req in requirements:
        materiality = str(req.get("materiality", "")).lower()
        coverage = str(req.get("coverage", "")).lower()
        if coverage == "unscored":
            continue
        if materiality not in MATERIALITY:
            raise ValueError(f"Unsupported materiality: {materiality}")
        if coverage not in COVERAGE:
            raise ValueError(f"Unsupported coverage: {coverage}")
        weight = MATERIALITY[materiality]
        denominator += weight
        numerator += weight * COVERAGE[coverage]
    if denominator == 0:
        raise ValueError("Capability score needs at least one assessable requirement")
    return numerator / denominator * 100.0


def dimension_score(values: list[int], name: str) -> float:
    if len(values) != 4:
        raise ValueError(f"{name} requires exactly four dimensions")
    if any((not isinstance(v, int)) or v < 0 or v > 4 for v in values):
        raise ValueError(f"{name} dimensions must be integers 0-4")
    return sum(values) / 16.0 * 100.0


def calculate_scores(payload: dict[str, Any]) -> dict[str, Any]:
    capability = capability_raw(payload.get("requirements", []))
    direction = float(payload["direction_alignment"])
    if not 0 <= direction <= 100:
        raise ValueError("direction_alignment must be 0-100")
    screening = dimension_score(payload["screening_dimensions"], "screening")
    career = dimension_score(payload["career_value_dimensions"], "career_value")
    overall = capability * 0.70 + direction * 0.30
    return {
        "overall_match": round5(overall),
        "capability_match": round5(capability),
        "direction_alignment_internal": round5(direction),
        "screening_legibility": round5(screening),
        "career_value": round5(career),
        "raw": {
            "overall_match": overall,
            "capability_match": capability,
            "direction_alignment": direction,
            "screening_legibility": screening,
            "career_value": career,
        },
    }


def upsert_opportunity(state: dict[str, Any], job: dict[str, Any]) -> tuple[str, str]:
    company = str(job.get("company") or "Unknown company")
    title = str(job.get("title") or "Unknown role")
    opp_id = opportunity_identity(company, title, job.get("url"))
    snap = snapshot(job)
    opportunity = state["opportunities"].setdefault(
        opp_id,
        {
            "id": opp_id,
            "company": company,
            "title": title,
            "canonical_url": normalize_url(job.get("url")),
            "source_snapshots": [],
            "pursuit_assessments": [],
            "pursuit_decisions": [],
            "positioning_revisions": [],
            "application_artifacts": [],
            "application": {"status": "not_applied", "outcomes": []},
            "created_at": utc_now(),
        },
    )
    existing = {item.get("source_sha256") for item in opportunity["source_snapshots"]}
    if snap["source_sha256"] not in existing:
        opportunity["source_snapshots"].append(snap)
    opportunity["current_snapshot_id"] = snap["id"]
    opportunity["updated_at"] = utc_now()
    return opp_id, snap["id"]


def record_assessment(state: dict[str, Any], payload: dict[str, Any]) -> dict[str, Any]:
    recommendation = str(payload["recommendation"]).lower()
    if recommendation not in RECOMMENDATIONS:
        raise ValueError(f"recommendation must be one of {sorted(RECOMMENDATIONS)}")
    opp_id, snap_id = upsert_opportunity(state, payload["job"])
    scores = calculate_scores(payload)
    assessment = {
        "id": f"assessment-{hashlib.sha256((opp_id + snap_id + utc_now()).encode()).hexdigest()[:12]}",
        "created_at": utc_now(),
        "source_snapshot_id": snap_id,
        "recommendation": recommendation,
        "scores": scores,
        "employability": payload.get("employability", "eligibility_unclear"),
        "evidence_confidence": payload.get("evidence_confidence", "low"),
        "core_hiring_reason": payload.get("core_hiring_reason"),
        "why_worth_time": payload.get("why_worth_time"),
        "main_concern": payload.get("main_concern"),
        "what_to_verify": payload.get("what_to_verify"),
        "requirements": payload.get("requirements", []),
    }
    state["opportunities"][opp_id]["pursuit_assessments"].append(assessment)
    state["opportunities"][opp_id]["current_assessment_id"] = assessment["id"]
    state.setdefault("audit_log", []).append({"event": "pursuit_assessment_recorded", "opportunity_id": opp_id, "assessment_id": assessment["id"], "at": utc_now()})
    return {"opportunity_id": opp_id, "snapshot_id": snap_id, "assessment": assessment}


def record_decision(state: dict[str, Any], opportunity_id: str, decision: str, reason: str | None = None) -> dict[str, Any]:
    normalized = decision.lower()
    if normalized not in RECOMMENDATIONS:
        raise ValueError(f"decision must be one of {sorted(RECOMMENDATIONS)}")
    if opportunity_id not in state["opportunities"]:
        raise KeyError(f"Unknown opportunity: {opportunity_id}")
    record = {
        "id": f"decision-{hashlib.sha256((opportunity_id + normalized + utc_now()).encode()).hexdigest()[:12]}",
        "decision": normalized,
        "reason": reason,
        "created_at": utc_now(),
    }
    state["opportunities"][opportunity_id]["pursuit_decisions"].append(record)
    state["opportunities"][opportunity_id]["current_decision_id"] = record["id"]
    if reason:
        state["signals"]["decision_observations"].append({
            "id": f"observation-{record['id'].split('-', 1)[1]}",
            "opportunity_id": opportunity_id,
            "statement": reason,
            "authority": "user_observation",
            "created_at": utc_now(),
        })
    state.setdefault("audit_log", []).append({"event": "pursuit_decision_recorded", "opportunity_id": opportunity_id, "decision_id": record["id"], "at": utc_now()})
    return record


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--state", default="state/roleward-state.json")
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("assess")
    p.add_argument("--input", required=True)

    p = sub.add_parser("identity")
    p.add_argument("--company", required=True)
    p.add_argument("--title", required=True)
    p.add_argument("--url")

    p = sub.add_parser("decision")
    p.add_argument("--opportunity-id", required=True)
    p.add_argument("--decision", choices=sorted(RECOMMENDATIONS), required=True)
    p.add_argument("--reason")

    args = parser.parse_args()
    if args.command == "identity":
        print(opportunity_identity(args.company, args.title, args.url))
        return 0

    state_path = Path(args.state)
    state = load_state(state_path)
    if args.command == "decision":
        result = record_decision(state, args.opportunity_id, args.decision, args.reason)
    else:
        payload = json.loads(Path(args.input).read_text(encoding="utf-8"))
        result = record_assessment(state, payload)
    save_state(state_path, state)
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
