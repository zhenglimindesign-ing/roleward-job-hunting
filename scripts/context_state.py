#!/usr/bin/env python3
"""Deterministic context/state operations for Roleward Job Hunting Alpha."""

from __future__ import annotations

import argparse
import hashlib
import json
import uuid
from pathlib import Path
from typing import Any

from state_store import load_state, save_state, utc_now

AUTH_SOURCE = "source_material"
AUTH_CONFIRMED = "confirmed_truth"
AUTH_INFERRED = "inferred_signal"
ALLOWED_AUTHORITIES = {AUTH_SOURCE, AUTH_CONFIRMED, AUTH_INFERRED}


def _id(prefix: str) -> str:
    return f"{prefix}-{uuid.uuid4().hex[:12]}"


def _ensure_extensions(state: dict[str, Any]) -> None:
    state.setdefault("field_history", [])
    state.setdefault("pending_conflicts", [])
    state.setdefault("audit_log", [])


def _audit(state: dict[str, Any], event: str, **details: Any) -> None:
    _ensure_extensions(state)
    state["audit_log"].append({"event": event, "at": utc_now(), **details})


def add_source(state: dict[str, Any], *, source_type: str, label: str, local_path: str | None) -> str:
    _ensure_extensions(state)
    source_id = _id("src")
    record: dict[str, Any] = {
        "id": source_id,
        "type": source_type,
        "label": label,
        "observed_at": utc_now(),
    }
    if local_path:
        path = Path(local_path)
        record["local_path"] = str(path)
        if path.exists() and path.is_file():
            record["sha256"] = hashlib.sha256(path.read_bytes()).hexdigest()
            record["size_bytes"] = path.stat().st_size
    state["profile"]["sources"].append(record)
    _audit(state, "source_added", source_id=source_id, source_type=source_type, label=label)
    return source_id


def _field_record(value: Any, authority: str, source_ids: list[str]) -> dict[str, Any]:
    if authority not in ALLOWED_AUTHORITIES:
        raise ValueError(f"Unsupported authority: {authority}")
    return {
        "value": value,
        "authority": authority,
        "source_ids": source_ids,
        "updated_at": utc_now(),
    }


def _same_value(a: Any, b: Any) -> bool:
    return json.dumps(a, sort_keys=True, ensure_ascii=False) == json.dumps(b, sort_keys=True, ensure_ascii=False)


def set_field(
    state: dict[str, Any],
    container: dict[str, Any],
    field: str,
    value: Any,
    *,
    authority: str,
    source_ids: list[str],
    field_path: str,
) -> str:
    _ensure_extensions(state)
    incoming = _field_record(value, authority, source_ids)
    current = container.get(field)
    if current is None:
        container[field] = incoming
        _audit(state, "field_set", field=field_path, authority=authority)
        return "set"

    if not isinstance(current, dict) or "value" not in current:
        state["field_history"].append({"field": field_path, "superseded": current, "at": utc_now()})
        container[field] = incoming
        _audit(state, "field_normalized", field=field_path, authority=authority)
        return "replaced_legacy"

    if _same_value(current.get("value"), value):
        merged = list(dict.fromkeys([*(current.get("source_ids") or []), *source_ids]))
        current["source_ids"] = merged
        if authority == AUTH_CONFIRMED and current.get("authority") != AUTH_CONFIRMED:
            current["authority"] = AUTH_CONFIRMED
            current["updated_at"] = utc_now()
            _audit(state, "field_confirmed", field=field_path)
            return "confirmed"
        _audit(state, "field_supported", field=field_path, authority=authority)
        return "supported"

    current_authority = current.get("authority")
    if current_authority == AUTH_CONFIRMED and authority != AUTH_CONFIRMED:
        conflict = {
            "id": _id("conflict"),
            "field": field_path,
            "current": current,
            "incoming": incoming,
            "status": "needs_user_review",
            "created_at": utc_now(),
        }
        state["pending_conflicts"].append(conflict)
        _audit(state, "conflict_recorded", field=field_path, conflict_id=conflict["id"])
        return "conflict"

    state["field_history"].append({"field": field_path, "superseded": current, "at": utc_now()})
    container[field] = incoming
    _audit(state, "field_superseded", field=field_path, authority=authority)
    return "superseded"


def add_career_evidence(
    state: dict[str, Any], *, domain: str, statement: str, authority: str, source_ids: list[str]
) -> str:
    record = {
        "id": _id("evidence"),
        "domain": domain,
        "statement": statement,
        "authority": authority,
        "source_ids": source_ids,
        "active": True,
        "created_at": utc_now(),
    }
    state["profile"]["career_evidence"].append(record)
    _audit(state, "career_evidence_added", evidence_id=record["id"], domain=domain, authority=authority)
    return record["id"]


def add_list_signal(
    state: dict[str, Any], *, target: str, statement: str, authority: str, source_ids: list[str]
) -> str:
    if target not in {"constraints", "preferences"}:
        raise ValueError("target must be constraints or preferences")
    record = {
        "id": _id("constraint" if target == "constraints" else "preference"),
        "statement": statement,
        "authority": authority,
        "source_ids": source_ids,
        "active": True,
        "created_at": utc_now(),
    }
    state["profile"][target].append(record)
    _audit(state, f"{target[:-1]}_added", item_id=record["id"], authority=authority)
    return record["id"]


def apply_extraction(state: dict[str, Any], payload: dict[str, Any], authority: str) -> dict[str, Any]:
    source_id = payload.get("source_id")
    source_ids = [source_id] if isinstance(source_id, str) and source_id else []
    results: dict[str, Any] = {"career_evidence": [], "fields": {}, "constraints": [], "preferences": []}

    for item in payload.get("career_evidence", []):
        results["career_evidence"].append(
            add_career_evidence(
                state,
                domain=str(item.get("domain", "other")),
                statement=str(item["statement"]),
                authority=authority,
                source_ids=source_ids,
            )
        )

    for field, value in (payload.get("direction") or {}).items():
        results["fields"][f"profile.direction.{field}"] = set_field(
            state,
            state["profile"]["direction"],
            field,
            value,
            authority=authority,
            source_ids=source_ids,
            field_path=f"profile.direction.{field}",
        )

    for field, value in (payload.get("search_policy") or {}).items():
        results["fields"][f"search_policy.{field}"] = set_field(
            state,
            state["search_policy"],
            field,
            value,
            authority=authority,
            source_ids=source_ids,
            field_path=f"search_policy.{field}",
        )

    for statement in payload.get("constraints", []):
        results["constraints"].append(
            add_list_signal(state, target="constraints", statement=str(statement), authority=authority, source_ids=source_ids)
        )
    for statement in payload.get("preferences", []):
        results["preferences"].append(
            add_list_signal(state, target="preferences", statement=str(statement), authority=authority, source_ids=source_ids)
        )
    return results


def _field_value(container: dict[str, Any], key: str) -> Any:
    value = container.get(key)
    if isinstance(value, dict) and "value" in value:
        return value["value"]
    return value


def readiness(state: dict[str, Any]) -> dict[str, Any]:
    career_anchor = bool(state["profile"]["career_evidence"] or state["profile"]["sources"])
    direction = any(
        _field_value(state["profile"]["direction"], key)
        for key in ("target_roles", "capability_direction", "target_direction")
    )
    geography = any(
        _field_value(state["search_policy"], key)
        for key in ("geography", "geographies", "locations", "remote_scope")
    )
    authorization = any(
        key in state["search_policy"]
        and _field_value(state["search_policy"], key) is not None
        for key in ("authorization_state", "work_authorization", "sponsorship_state")
    )
    checks = {
        "career_anchor": bool(career_anchor),
        "direction": bool(direction),
        "geography": bool(geography),
        "authorization_state": bool(authorization),
    }
    return {"ready": all(checks.values()), "checks": checks, "missing": [k for k, ok in checks.items() if not ok]}


def _status(record: Any) -> str:
    if isinstance(record, dict):
        authority = record.get("authority")
        if authority == AUTH_CONFIRMED:
            return "Confirmed"
        if authority == AUTH_SOURCE:
            return "Source-backed"
        if authority == AUTH_INFERRED:
            return "Inferred"
    return "Unknown"


def review_markdown(state: dict[str, Any]) -> str:
    lines = ["# Structured Context Review", ""]
    sections = [
        ("Current Direction", state["profile"]["direction"]),
        ("Search Policy", state["search_policy"]),
    ]
    lines.extend(["## Career Background", "", "| Evidence | Status |", "|---|---|"])
    for item in state["profile"]["career_evidence"]:
        lines.append(f"| {item.get('statement','')} | {_status(item)} |")
    if not state["profile"]["career_evidence"]:
        lines.append("| No structured career evidence yet | Missing |")
    lines.append("")

    for title, fields in sections:
        lines.extend([f"## {title}", "", "| Item | Value | Status |", "|---|---|---|"])
        if fields:
            for key, record in fields.items():
                value = record.get("value") if isinstance(record, dict) and "value" in record else record
                rendered = json.dumps(value, ensure_ascii=False) if isinstance(value, (list, dict)) else str(value)
                lines.append(f"| {key} | {rendered} | {_status(record)} |")
        else:
            lines.append("| — | Not specified | Optional / missing |")
        lines.append("")

    lines.extend(["## Preferences / Trade-offs", "", "| Preference | Status |", "|---|---|"])
    for item in state["profile"]["preferences"]:
        if item.get("active", True):
            lines.append(f"| {item.get('statement','')} | {_status(item)} |")
    if not state["profile"]["preferences"]:
        lines.append("| No current preference signals | Optional |")
    lines.append("")

    ready = readiness(state)
    lines.append(f"**First Scan ready:** {'Yes' if ready['ready'] else 'No'}")
    if ready["missing"]:
        lines.append(f"**Consequential missing:** {', '.join(ready['missing'])}")
    if state.get("pending_conflicts"):
        open_conflicts = [c for c in state["pending_conflicts"] if c.get("status") == "needs_user_review"]
        if open_conflicts:
            lines.append(f"**Needs review:** {len(open_conflicts)} consequential conflict(s)")
    return "\n".join(lines) + "\n"


def resolve_container(state: dict[str, Any], path: str) -> tuple[dict[str, Any], str]:
    parts = path.split(".")
    if parts[:2] == ["profile", "direction"] and len(parts) == 3:
        return state["profile"]["direction"], parts[2]
    if parts[0] == "search_policy" and len(parts) == 2:
        return state["search_policy"], parts[1]
    raise ValueError("Supported field paths: profile.direction.<field> or search_policy.<field>")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--state", default="state/roleward-state.json")
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("add-source")
    p.add_argument("--type", required=True)
    p.add_argument("--label", required=True)
    p.add_argument("--path")

    p = sub.add_parser("apply-extraction")
    p.add_argument("--input", required=True)
    p.add_argument("--authority", choices=sorted(ALLOWED_AUTHORITIES), default=AUTH_SOURCE)

    p = sub.add_parser("confirm-field")
    p.add_argument("--field", required=True)
    p.add_argument("--value-json", required=True)

    sub.add_parser("readiness")
    sub.add_parser("review")

    args = parser.parse_args()
    state_path = Path(args.state)
    state = load_state(state_path)

    if args.command == "add-source":
        source_id = add_source(state, source_type=args.type, label=args.label, local_path=args.path)
        save_state(state_path, state)
        print(source_id)
        return 0

    if args.command == "apply-extraction":
        payload = json.loads(Path(args.input).read_text(encoding="utf-8"))
        result = apply_extraction(state, payload, args.authority)
        save_state(state_path, state)
        print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
        return 0

    if args.command == "confirm-field":
        container, key = resolve_container(state, args.field)
        value = json.loads(args.value_json)
        result = set_field(
            state,
            container,
            key,
            value,
            authority=AUTH_CONFIRMED,
            source_ids=[],
            field_path=args.field,
        )
        save_state(state_path, state)
        print(result)
        return 0

    if args.command == "readiness":
        print(json.dumps(readiness(state), ensure_ascii=False, indent=2, sort_keys=True))
        return 0

    if args.command == "review":
        print(review_markdown(state), end="")
        return 0

    raise AssertionError(args.command)


if __name__ == "__main__":
    raise SystemExit(main())
