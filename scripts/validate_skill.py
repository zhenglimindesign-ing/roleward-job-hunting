#!/usr/bin/env python3
"""Dependency-light validator for the Roleward Agent Skill bootstrap."""

from __future__ import annotations

import re
import sys
from pathlib import Path

try:
    import yaml
except ImportError:  # pragma: no cover
    yaml = None

NAME_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")


def validate(root: Path) -> list[str]:
    errors: list[str] = []
    skill = root / "SKILL.md"
    if not skill.exists():
        return ["SKILL.md is missing"]

    text = skill.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        return ["SKILL.md must start with YAML frontmatter"]
    try:
        _, frontmatter, body = text.split("---", 2)
    except ValueError:
        return ["SKILL.md frontmatter is not terminated"]

    if yaml is None:
        errors.append("PyYAML is unavailable; frontmatter cannot be parsed")
        return errors
    meta = yaml.safe_load(frontmatter) or {}
    name = meta.get("name")
    description = meta.get("description")
    compatibility = meta.get("compatibility")

    if not isinstance(name, str) or not NAME_RE.fullmatch(name):
        errors.append("name must contain lowercase letters/numbers/hyphens only")
    elif name != root.name:
        errors.append(f"name {name!r} must match directory name {root.name!r}")
    if not isinstance(description, str) or not (1 <= len(description) <= 1024):
        errors.append("description must be 1-1024 characters")
    if compatibility is not None and (not isinstance(compatibility, str) or len(compatibility) > 500):
        errors.append("compatibility must be <=500 characters when present")
    if body.count("\n") + 1 > 500:
        errors.append("SKILL.md body exceeds the recommended 500-line limit")

    required = [
        "references/context-policy.md",
        "references/state-policy.md",
        "references/search-policy.md",
        "references/pursuit-policy.md",
        "references/score-policy.md",
        "references/positioning-policy.md",
        "references/learn-policy.md",
        "references/tool-boundary.md",
        "schemas/roleward-state-v0.schema.json",
        "scripts/state_store.py",
        "scripts/context_state.py",
        "scripts/opportunity_state.py",
        "scripts/scan_state.py",
        "scripts/application_state.py",
        "scripts/learn_state.py",
        "scripts/eval_runner.py",
    ]
    for relative in required:
        if not (root / relative).exists():
            errors.append(f"required bootstrap file missing: {relative}")
    return errors


def main() -> int:
    root = Path(sys.argv[1] if len(sys.argv) > 1 else ".").resolve()
    errors = validate(root)
    if errors:
        print("INVALID")
        for error in errors:
            print(f"- {error}")
        return 1
    print(f"VALID: {root}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
