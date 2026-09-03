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

ALLOWED_KINDS = {
    "context",
    "opportunity",
    "search_pool",
    "learn_sequence",
    "state_roundtrip",
    "portable_profile_set",
}


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
    if payload.get("kind") == "portable_profile_set":
        profiles = (payload.get("input") or {}).get("profiles")
        if not isinstance(profiles, list) or not profiles:
            errors.append(f"{path}: portable_profile_set requires non-empty input.profiles")
        else:
            for profile in profiles:
                if not profile.get("profile_id") or not isinstance(profile.get("jobs"), list) or len(profile["jobs"]) < 2:
                    errors.append(f"{path}: each portable profile needs profile_id and at least two jobs")
    return errors


def _context_ready(input_payload: dict[str, Any]) -> bool:
    return all(bool(input_payload.get(key)) for key in ("career_anchor", "direction", "geography", "authorization_state"))


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

    if kind == "portable_profile_set":
        profiles = payload["input"]["profiles"]
        actual_profiles = len(profiles)
        actual_jobs = sum(len(profile["jobs"]) for profile in profiles)
        if expected.get("profile_count") != actual_profiles:
            errors.append(f"{fixture_id}: profile_count expected {expected.get('profile_count')} got {actual_profiles}")
        if expected.get("job_count") != actual_jobs:
            errors.append(f"{fixture_id}: job_count expected {expected.get('job_count')} got {actual_jobs}")
        return errors

    # Search pools and Learn sequences need host/model or sequence-specific runners.
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
            if payload["kind"] in {"context", "opportunity", "state_roundtrip", "portable_profile_set"}:
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
