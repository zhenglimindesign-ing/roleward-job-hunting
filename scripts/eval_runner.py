#!/usr/bin/env python3
"""Small deterministic fixture runner; model-backed eval execution is added later."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

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
    for path in files:
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except Exception as exc:
            errors.append(f"{path}: invalid JSON: {exc}")
            continue
        errors.extend(validate_fixture(payload, path))
    if errors:
        print(f"Fixture validation failed: {len(errors)} error(s)")
        for error in errors:
            print(f"- {error}")
        return 1
    print(f"Fixture validation passed: {len(files)} fixture(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
