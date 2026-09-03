#!/usr/bin/env python3
"""Deterministic public fixture runner for Roleward Job Hunting Alpha."""

from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path
from typing import Any

from opportunity_state import calculate_scores
from state_store import empty_state, load_state, save_state

ALLOWED_KINDS = {"context", "opportunity", "search_pool", "learn_sequence", "state_roundtrip"}


def validate_fixture(payload: Any, path: Path) -> list[str]:
    errors: list[str] = []
    if not isinstance(payload, dict):
        return [f"{path}: fixture must be an object"]
    if not isinstance(payload.get("id"), str) or not payload["id"].strip():
        errors.append(f"{path}: id is required")
    if payload.get("kind") not in ALLOWED_KINDS:
        errors.append(f"{path}: kind must be one of {sorted(ALLOWED_KINDS)}")
    if "input" not in payload:
        errors.append(f"{path}: input is required")
    if "expected" not in payload:
        errors.append(f"{path}: expected is required")
    return errors


def _context_ready(input_payload: dict[str, Any]) -> bool:
    return all(
        bool(input_payload.get(key))
        for key in ("career_anchor", "direction", "geography", "authorization_state")
    )


def run_fixture(payload: dict[str, Any]) -> list[str]:
    kind = payload["kind"]
    expected = payload["expected"]
    fixture_id = payload["id"]
    errors: list[str] = []

    if kind == "context":
        actual = _context_ready(payload["input"])
        if actual != bool(expected.get("first_scan_ready")):
            errors.append(f"{fixture_id}: first_scan_ready expected {expected.get('first_scan_ready')} got {actual}")
        return errors

    if kind == "state_roundtrip":
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "state.json"
            state = empty_state()
            save_state(path, state)
            reloaded = load_state(path)
            if expected.get("reload_equivalent") and reloaded != json.loads(path.read_text(encoding="utf-8")):
                errors.append(f"{fixture_id}: state reload is not equivalent to persisted JSON")
            if expected.get("history_preserved") and not all(key in reloaded for key in ("profile", "opportunities", "signals")):
                errors.append(f"{fixture_id}: required history containers missing after reload")
        return errors

    if kind == "opportunity":
        scores = calculate_scores(payload["input"])
        for key in ("overall_match", "capability_match", "screening_legibility", "career_value"):
            if key in expected and scores.get(key) != expected[key]:
                errors.append(f"{fixture_id}: {key} expected {expected[key]} got {scores.get(key)}")
        return errors

    # Search pools and Learn sequences need host/model or sequence-specific runners.
    # Their envelope is validated here; execution is added with those benchmark layers.
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--fixtures", default="fixtures")
    args = parser.parse_args()
    root = Path(args.fixtures)
    files = [
        path for path in sorted(root.rglob("*.json"))
        if not any(part.startswith("_") for part in path.relative_to(root).parts)
    ]
    errors: list[str] = []
    executed = 0
    for path in files:
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except Exception as exc:
            errors.append(f"{path}: invalid JSON: {exc}")
            continue
        fixture_errors = validate_fixture(payload, path)
        errors.extend(fixture_errors)
        if not fixture_errors:
            errors.extend(run_fixture(payload))
            if payload["kind"] in {"context", "opportunity", "state_roundtrip"}:
                executed += 1
    if errors:
        print(f"Fixture run failed: {len(errors)} error(s)")
        for error in errors:
            print(f"- {error}")
        return 1
    print(f"Fixture run passed: {len(files)} fixture(s), {executed} deterministic execution(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
