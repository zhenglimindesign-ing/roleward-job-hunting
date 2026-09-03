#!/usr/bin/env python3
"""Deterministic application tracking and conservative Learn helpers."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

from context_state import AUTH_CONFIRMED, add_list_signal
from state_store import load_state, save_state, utc_now

APPLICATION_STATUSES = {
    "not_applied",
    "applied",
    "screening",
    "interview",
    "offer",
    "rejected",
    "withdrawn",
}
REASON_AUTHORITIES = {"confirmed", "unknown"}


def _id(prefix: str, seed: str) -> str:
    return f"{prefix}-{hashlib.sha256((seed + utc_now()).encode()).hexdigest()[:12]}"


def _opportunity(state: dict[str, Any], opportunity_id: str) -> dict[str, Any]:
    try:
        return state["opportunities"][opportunity_id]
    except KeyError as exc:
        raise KeyError(f"Unknown opportunity: {opportunity_id}") from exc


def record_application_status(state: dict[str, Any], opportunity_id: str, status: str) -> dict[str, Any]:
    normalized = status.lower()
    if normalized not in APPLICATION_STATUSES:
        raise ValueError(f"status must be one of {sorted(APPLICATION_STATUSES)}")
    opp = _opportunity(state, opportunity_id)
    app = opp.setdefault("application", {"status": "not_applied", "status_history": [], "outcomes": []})
    app.setdefault("status_history", [])
    record = {
        "id": _id("status", opportunity_id + normalized),
        "status": normalized,
        "created_at": utc_now(),
    }
    app["status_history"].append(record)
    app["status"] = normalized
    state.setdefault("audit_log", []).append({"event": "application_status_recorded", "opportunity_id": opportunity_id, "status": normalized, "at": utc_now()})
    return record


def _upsert_learned_signal(state: dict[str, Any], key: str, statement: str, evidence_id: str) -> dict[str, Any]:
    signals = state["signals"]["learned_signals"]
    signal = next((item for item in signals if item.get("key") == key and item.get("active", True)), None)
    if signal is None:
        signal = {
            "id": _id("learned", key),
            "key": key,
            "statement": statement,
            "evidence_ids": [],
            "strength": "weak_observation",
            "active": True,
            "created_at": utc_now(),
        }
        signals.append(signal)
    if evidence_id not in signal["evidence_ids"]:
        signal["evidence_ids"].append(evidence_id)
    count = len(signal["evidence_ids"])
    signal["strength"] = "emerging_pattern" if count >= 2 else "weak_observation"
    signal["updated_at"] = utc_now()
    return signal


def record_outcome(
    state: dict[str, Any],
    opportunity_id: str,
    *,
    status: str,
    reason: str | None,
    reason_authority: str,
    signal_key: str | None = None,
) -> dict[str, Any]:
    normalized = status.lower()
    if normalized not in APPLICATION_STATUSES:
        raise ValueError(f"status must be one of {sorted(APPLICATION_STATUSES)}")
    if reason_authority not in REASON_AUTHORITIES:
        raise ValueError(f"reason_authority must be one of {sorted(REASON_AUTHORITIES)}")
    if reason_authority == "unknown" and reason:
        raise ValueError("unknown outcome reason must not contain a causal reason")
    if reason_authority == "confirmed" and not reason:
        raise ValueError("confirmed outcome reason requires reason text")

    opp = _opportunity(state, opportunity_id)
    record_application_status(state, opportunity_id, normalized)
    app = opp.setdefault("application", {"status": normalized, "status_history": [], "outcomes": []})
    outcome = {
        "id": _id("outcome", opportunity_id + normalized),
        "status": normalized,
        "reason": reason,
        "reason_authority": reason_authority,
        "created_at": utc_now(),
    }
    app.setdefault("outcomes", []).append(outcome)

    if reason_authority == "confirmed" and signal_key:
        outcome["learned_signal_id"] = _upsert_learned_signal(
            state,
            signal_key,
            statement=reason or signal_key,
            evidence_id=outcome["id"],
        )["id"]

    state.setdefault("audit_log", []).append({"event": "application_outcome_recorded", "opportunity_id": opportunity_id, "outcome_id": outcome["id"], "at": utc_now()})
    return outcome


def record_preference_observation(
    state: dict[str, Any], opportunity_id: str, *, signal_key: str, statement: str
) -> dict[str, Any]:
    _opportunity(state, opportunity_id)
    observation = {
        "id": _id("observation", opportunity_id + signal_key),
        "opportunity_id": opportunity_id,
        "signal_key": signal_key,
        "statement": statement,
        "authority": "user_observation",
        "created_at": utc_now(),
    }
    state["signals"]["decision_observations"].append(observation)

    independent = {
        item.get("opportunity_id")
        for item in state["signals"]["decision_observations"]
        if item.get("signal_key") == signal_key and item.get("opportunity_id")
    }
    inferred = next(
        (item for item in state["signals"]["inferred_signals"] if item.get("key") == signal_key and item.get("active", True)),
        None,
    )
    if inferred is None:
        inferred = {
            "id": _id("inferred", signal_key),
            "key": signal_key,
            "statement": statement,
            "evidence_observation_ids": [],
            "status": "unconfirmed",
            "strength": "weak_observation",
            "active": True,
            "created_at": utc_now(),
        }
        state["signals"]["inferred_signals"].append(inferred)
    if observation["id"] not in inferred["evidence_observation_ids"]:
        inferred["evidence_observation_ids"].append(observation["id"])
    inferred["independent_opportunity_count"] = len(independent)
    inferred["strength"] = "emerging_pattern" if len(independent) >= 3 else "weak_observation"
    inferred["updated_at"] = utc_now()
    return {"observation": observation, "inferred_signal": inferred}


def confirm_preference(state: dict[str, Any], signal_id: str) -> dict[str, Any]:
    signal = next((item for item in state["signals"]["inferred_signals"] if item.get("id") == signal_id), None)
    if signal is None:
        raise KeyError(f"Unknown inferred signal: {signal_id}")
    preference_id = add_list_signal(
        state,
        target="preferences",
        statement=str(signal["statement"]),
        authority=AUTH_CONFIRMED,
        source_ids=[],
    )
    signal["status"] = "confirmed_by_user"
    signal["confirmed_preference_id"] = preference_id
    signal["updated_at"] = utc_now()
    return {"signal_id": signal_id, "preference_id": preference_id}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--state", default="state/roleward-state.json")
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("status")
    p.add_argument("--opportunity-id", required=True)
    p.add_argument("--status", choices=sorted(APPLICATION_STATUSES), required=True)

    p = sub.add_parser("outcome")
    p.add_argument("--opportunity-id", required=True)
    p.add_argument("--status", choices=sorted(APPLICATION_STATUSES), required=True)
    p.add_argument("--reason")
    p.add_argument("--reason-authority", choices=sorted(REASON_AUTHORITIES), required=True)
    p.add_argument("--signal-key")

    p = sub.add_parser("observe-preference")
    p.add_argument("--opportunity-id", required=True)
    p.add_argument("--signal-key", required=True)
    p.add_argument("--statement", required=True)

    p = sub.add_parser("confirm-preference")
    p.add_argument("--signal-id", required=True)

    args = parser.parse_args()
    path = Path(args.state)
    state = load_state(path)

    if args.command == "status":
        result = record_application_status(state, args.opportunity_id, args.status)
    elif args.command == "outcome":
        result = record_outcome(
            state,
            args.opportunity_id,
            status=args.status,
            reason=args.reason,
            reason_authority=args.reason_authority,
            signal_key=args.signal_key,
        )
    elif args.command == "observe-preference":
        result = record_preference_observation(
            state,
            args.opportunity_id,
            signal_key=args.signal_key,
            statement=args.statement,
        )
    else:
        result = confirm_preference(state, args.signal_id)

    save_state(path, state)
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
