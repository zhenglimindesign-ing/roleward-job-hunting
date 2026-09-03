#!/usr/bin/env python3
"""Deterministic Scan run, hard-constraint, and Opportunity-reservoir helpers."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

from opportunity_state import upsert_opportunity
from state_store import load_state, save_state, utc_now

TRIGGERS = {"manual", "scheduled"}
REVIEW_DISPOSITIONS = {"worth_review", "verify_first", "screened_out"}
DEFAULT_MAX_RESULTS = 5


def _unwrap(value: Any) -> Any:
    if isinstance(value, dict) and "value" in value:
        return value["value"]
    return value


def _list(value: Any) -> list[str]:
    value = _unwrap(value)
    if value is None:
        return []
    if isinstance(value, str):
        return [value]
    if isinstance(value, list):
        return [str(item) for item in value if str(item).strip()]
    return [str(value)]


def _confirmed_list(container: dict[str, Any], key: str) -> list[str]:
    value = container.get(key)
    if isinstance(value, dict) and value.get("authority") != "confirmed_truth":
        return []
    return _list(value)


def _first_list(container: dict[str, Any], keys: tuple[str, ...]) -> list[str]:
    for key in keys:
        values = _list(container.get(key))
        if values:
            return values
    return []


def build_search_plan(state: dict[str, Any]) -> dict[str, Any]:
    direction = state["profile"]["direction"]
    policy = state["search_policy"]
    role_terms = _first_list(direction, ("target_roles", "capability_direction", "target_direction"))
    geographies = _first_list(policy, ("geographies", "geography", "locations", "remote_scope"))
    seniority = _first_list(policy, ("seniority", "seniority_range")) or _first_list(direction, ("seniority",))
    authorization_state = None
    for key in ("authorization_state", "work_authorization", "sponsorship_state"):
        if key in policy:
            authorization_state = _unwrap(policy[key])
            break
    return {
        "role_terms": role_terms,
        "geographies": geographies,
        "seniority": seniority,
        "authorization_state": authorization_state,
        "excluded_companies": _confirmed_list(policy, "excluded_companies"),
        "max_results": int(_unwrap(policy.get("max_results")) or DEFAULT_MAX_RESULTS),
        "coverage_modes": ["title_led", "capability_led"],
    }


def start_scan(state: dict[str, Any], trigger: str) -> dict[str, Any]:
    if trigger not in TRIGGERS:
        raise ValueError(f"trigger must be one of {sorted(TRIGGERS)}")
    state.setdefault("scan_runs", {})
    plan = build_search_plan(state)
    seed = json.dumps({"plan": plan, "at": utc_now()}, sort_keys=True).encode("utf-8")
    run_id = f"scan-{hashlib.sha256(seed).hexdigest()[:12]}"
    state["scan_runs"][run_id] = {
        "id": run_id,
        "trigger": trigger,
        "status": "running",
        "started_at": utc_now(),
        "plan": plan,
        "candidates": [],
        "selected_opportunity_ids": [],
    }
    state.setdefault("audit_log", []).append({"event": "scan_started", "scan_id": run_id, "trigger": trigger, "at": utc_now()})
    return state["scan_runs"][run_id]


def hard_constraint_check(state: dict[str, Any], candidate: dict[str, Any]) -> dict[str, Any]:
    """Reject only when a structured, confirmed hard conflict is explicit.

    Unknown or missing candidate facts remain verification needs rather than
    negative evidence.
    """
    plan = build_search_plan(state)
    facts = candidate.get("facts") or {}
    job = candidate.get("job") or {}
    violations: list[str] = []
    needs_verification: list[str] = []

    excluded_companies = {item.casefold() for item in plan["excluded_companies"]}
    company = str(job.get("company") or "").strip()
    if company and company.casefold() in excluded_companies:
        violations.append("excluded_company")

    approved_geographies = {item.casefold() for item in plan["geographies"]}
    candidate_geographies = {item.casefold() for item in _list(facts.get("geographies"))}
    remote_allowed = bool(facts.get("remote_matches_policy"))
    if approved_geographies:
        if candidate_geographies:
            if not (approved_geographies & candidate_geographies) and not remote_allowed:
                violations.append("outside_confirmed_geography")
        else:
            needs_verification.append("geography")

    employability = str(facts.get("employability") or "").strip().lower()
    if employability in {"ineligible_now", "structural_blocker"}:
        violations.append("employability_blocker")
    elif not employability or employability in {"eligibility_unclear", "employer_evidence_only"}:
        needs_verification.append("employability")

    return {
        "passes": not violations,
        "violations": violations,
        "needs_verification": sorted(set(needs_verification)),
    }


def ingest_candidates(state: dict[str, Any], scan_id: str, candidates: list[dict[str, Any]]) -> dict[str, Any]:
    state.setdefault("scan_runs", {})
    if scan_id not in state["scan_runs"]:
        raise KeyError(f"Unknown scan id: {scan_id}")
    run = state["scan_runs"][scan_id]
    if run.get("status") != "running":
        raise ValueError("Can only ingest candidates into a running scan")

    persisted: list[dict[str, Any]] = []
    for candidate in candidates:
        check = hard_constraint_check(state, candidate)
        requested = str(candidate.get("disposition") or "verify_first")
        if requested not in REVIEW_DISPOSITIONS:
            raise ValueError(f"Unsupported disposition: {requested}")
        disposition = "screened_out" if not check["passes"] else requested
        opp_id, snap_id = upsert_opportunity(state, candidate["job"])
        discovery = {
            "scan_id": scan_id,
            "source_snapshot_id": snap_id,
            "disposition": disposition,
            "reasons": candidate.get("reasons") or [],
            "hard_constraint_check": check,
            "observed_at": utc_now(),
        }
        opportunity = state["opportunities"][opp_id]
        opportunity.setdefault("discovery_observations", []).append(discovery)
        persisted.append({"opportunity_id": opp_id, **discovery})
    run["candidates"].extend(persisted)
    run["updated_at"] = utc_now()
    return {"scan_id": scan_id, "candidates": persisted}


def finalize_scan(state: dict[str, Any], scan_id: str) -> dict[str, Any]:
    run = state["scan_runs"][scan_id]
    max_results = int(run["plan"].get("max_results") or DEFAULT_MAX_RESULTS)
    selected = [
        item["opportunity_id"]
        for item in run["candidates"]
        if item["disposition"] in {"worth_review", "verify_first"}
    ][:max_results]
    run["selected_opportunity_ids"] = selected
    run["status"] = "complete"
    run["completed_at"] = utc_now()
    state.setdefault("audit_log", []).append({"event": "scan_completed", "scan_id": scan_id, "selected_count": len(selected), "at": utc_now()})
    return run


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--state", default="state/roleward-state.json")
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("start")
    p.add_argument("--trigger", choices=sorted(TRIGGERS), default="manual")

    p = sub.add_parser("ingest")
    p.add_argument("--scan-id", required=True)
    p.add_argument("--input", required=True)

    p = sub.add_parser("finalize")
    p.add_argument("--scan-id", required=True)

    args = parser.parse_args()
    path = Path(args.state)
    state = load_state(path)

    if args.command == "start":
        result = start_scan(state, args.trigger)
    elif args.command == "ingest":
        payload = json.loads(Path(args.input).read_text(encoding="utf-8"))
        result = ingest_candidates(state, args.scan_id, payload["candidates"])
    else:
        result = finalize_scan(state, args.scan_id)

    save_state(path, state)
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
