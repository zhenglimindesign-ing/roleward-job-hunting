#!/usr/bin/env python3
"""Minimal local persistence helper for Roleward Job Hunting Alpha."""

from __future__ import annotations

import argparse
import json
import os
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

SCHEMA_VERSION = "roleward.job-hunting.state.v0"


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def empty_state() -> dict[str, Any]:
    now = utc_now()
    return {
        "schema_version": SCHEMA_VERSION,
        "profile": {
            "career_evidence": [],
            "direction": {},
            "constraints": [],
            "preferences": [],
            "sources": [],
        },
        "search_policy": {},
        "opportunities": {},
        "signals": {
            "decision_observations": [],
            "inferred_signals": [],
            "learned_signals": [],
        },
        "created_at": now,
        "updated_at": now,
    }


def validate_state(state: Any) -> list[str]:
    errors: list[str] = []
    if not isinstance(state, dict):
        return ["state must be a JSON object"]
    if state.get("schema_version") != SCHEMA_VERSION:
        errors.append(f"schema_version must be {SCHEMA_VERSION!r}")
    for key, expected in (
        ("profile", dict),
        ("search_policy", dict),
        ("opportunities", dict),
        ("signals", dict),
    ):
        if not isinstance(state.get(key), expected):
            errors.append(f"{key} must be a {expected.__name__}")
    if not isinstance(state.get("updated_at"), str):
        errors.append("updated_at must be a string")
    profile = state.get("profile") if isinstance(state.get("profile"), dict) else {}
    for key, expected in (
        ("career_evidence", list),
        ("direction", dict),
        ("constraints", list),
        ("preferences", list),
        ("sources", list),
    ):
        if not isinstance(profile.get(key), expected):
            errors.append(f"profile.{key} must be a {expected.__name__}")
    signals = state.get("signals") if isinstance(state.get("signals"), dict) else {}
    for key in ("decision_observations", "inferred_signals", "learned_signals"):
        if not isinstance(signals.get(key), list):
            errors.append(f"signals.{key} must be a list")
    return errors


def load_state(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(path)
    state = json.loads(path.read_text(encoding="utf-8"))
    errors = validate_state(state)
    if errors:
        raise ValueError("Invalid Roleward state:\n- " + "\n- ".join(errors))
    return state


def save_state(path: Path, state: dict[str, Any]) -> None:
    state = dict(state)
    state["updated_at"] = utc_now()
    errors = validate_state(state)
    if errors:
        raise ValueError("Refusing to save invalid Roleward state:\n- " + "\n- ".join(errors))
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temp_name = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            json.dump(state, handle, ensure_ascii=False, indent=2, sort_keys=True)
            handle.write("\n")
        os.replace(temp_name, path)
    except Exception:
        try:
            os.unlink(temp_name)
        except FileNotFoundError:
            pass
        raise


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=["init", "validate", "show"])
    parser.add_argument("--path", default="state/roleward-state.json")
    args = parser.parse_args()
    path = Path(args.path)

    if args.command == "init":
        if path.exists():
            print(f"State already exists: {path}")
            return 2
        save_state(path, empty_state())
        print(f"Initialized {path}")
        return 0

    state = load_state(path)
    if args.command == "validate":
        print(f"Valid {SCHEMA_VERSION}: {path}")
    else:
        print(json.dumps(state, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
