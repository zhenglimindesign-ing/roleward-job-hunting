#!/usr/bin/env python3
"""Offline Pursuit output checks and label-free portable input preparation.

This tool never generates model judgments or establishes semantic acceptance.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
from typing import Any

from opportunity_state import RECOMMENDATIONS, verification_errors

SCORE_FIELDS = ("overall_match", "capability_match", "screening_legibility", "career_value")
PROFILE_FIELDS = ("career_anchor", "direction", "geography", "authorization_state")


def portable_cases(fixture: dict[str, Any]) -> list[dict[str, Any]]:
    """Explicitly allowlist evidence fields; never copy labels or stress hints."""
    from eval_runner import run_fixture, validate_fixture

    errors = validate_fixture(fixture, Path("portable fixture"))
    if fixture.get("kind") != "portable_profile_set":
        errors.append("Expected portable_profile_set")
    if errors:
        raise ValueError("; ".join(errors))
    errors = run_fixture(fixture)
    if errors:
        raise ValueError("; ".join(errors))
    return [
        {
            "case_id": job["job_id"],
            "profile_id": profile["profile_id"],
            "candidate": {key: profile[key] for key in PROFILE_FIELDS},
            "job": {key: job[key] for key in ("title", "summary")},
        }
        for profile in fixture["input"]["profiles"]
        for job in profile["jobs"]
    ]


def index_cases(payload: Any, name: str) -> dict[str, dict[str, Any]]:
    rows = payload.get("cases") if isinstance(payload, dict) else payload
    if not isinstance(rows, list) or not rows:
        raise ValueError(f"{name}: expected a non-empty cases array")
    indexed = {}
    for row in rows:
        if not isinstance(row, dict):
            raise ValueError(f"{name}: each case must be an object")
        case_id = row.get("case_id")
        if not isinstance(case_id, str) or not case_id.strip():
            raise ValueError(f"{name}: non-empty case_id is required")
        if case_id in indexed:
            raise ValueError(f"{name}: duplicate case_id {case_id}")
        indexed[case_id] = row
    return indexed


def label_cases(labels: Any) -> dict[str, dict[str, Any]]:
    if isinstance(labels, dict) and labels.get("kind") == "portable_profile_set":
        portable_cases(labels)  # Validate the complete fixture before scoring.
        labels = {"cases": [
            {"case_id": job["job_id"], "pursuit_label": job["expected_pursuit"]}
            for profile in labels["input"]["profiles"] for job in profile["jobs"]
        ]}
    truth = index_cases(labels, "labels")
    for case_id, row in truth.items():
        if row.get("pursuit_label") not in tuple(RECOMMENDATIONS):
            raise ValueError(f"{case_id}: invalid pursuit_label")
    return truth


def output_errors(case: dict[str, Any]) -> list[str]:
    errors = []
    recommendation = case.get("recommendation")
    if recommendation not in tuple(RECOMMENDATIONS):
        errors.append("invalid recommendation")
    for field in SCORE_FIELDS:
        value = case.get(field)
        if (type(value) not in (int, float) or not 0 <= value <= 100
                or not math.isfinite(value) or value % 5 != 0):
            errors.append(f"{field} must be a finite 0-100 number in 5-point increments")
    for field in ("employability", "core_hiring_reason"):
        if not isinstance(case.get(field), str) or not case[field].strip():
            errors.append(f"{field} must be non-empty text")
    if case.get("evidence_confidence") not in ("high", "medium", "low"):
        errors.append("evidence_confidence must be high, medium, or low")
    for field in ("major_support", "major_gaps", "decision_unknowns"):
        value = case.get(field)
        if not isinstance(value, list) or any(not isinstance(v, str) or not v.strip() for v in value):
            errors.append(f"{field} must be an array of non-empty strings")
    errors.extend(verification_errors(recommendation, case.get("verification_plan")))
    return errors


def evaluate(labels: Any, outputs: Any) -> dict[str, Any]:
    truth = label_cases(labels)
    pred = index_cases(outputs, "outputs")
    errors = []
    run = outputs.get("run") if isinstance(outputs, dict) else None
    if not isinstance(run, dict) or any(
        not isinstance(run.get(key), str) or not run[key].strip()
        for key in ("variant", "run_id", "model_or_host", "created_at")
    ):
        errors.append("run requires non-empty variant, run_id, model_or_host, and created_at")
    for case_id in sorted(set(truth) - set(pred)):
        errors.append(f"{case_id}: missing output")
    for case_id in sorted(set(pred) - set(truth)):
        errors.append(f"{case_id}: unexpected output")
    for case_id, case in pred.items():
        errors.extend(f"{case_id}: {error}" for error in output_errors(case))
    rows = [
        {"case_id": case_id, "gold": gold["pursuit_label"],
         "pred": pred.get(case_id, {}).get("recommendation"),
         "match": pred.get(case_id, {}).get("recommendation") == gold["pursuit_label"]}
        for case_id, gold in truth.items()
    ]
    exact = sum(row["match"] for row in rows)
    agreement = exact / len(truth)
    return {
        "expected_cases": len(truth), "provided_cases": len(pred),
        "exact_matches": exact, "recommendation_agreement": round(agreement, 4),
        "meets_85pct_numeric_gate": agreement >= 0.85,
        "passes_structural_checks": not errors,
        "passes_automated_gate": agreement >= 0.85 and not errors,
        "semantic_review_required": True,
        "errors": errors, "case_results": rows,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    prepare = sub.add_parser("prepare-portable")
    prepare.add_argument("--fixture", default="fixtures/portable/profile-set-v1.json")
    prepare.add_argument("--out", required=True)
    score = sub.add_parser("evaluate")
    score.add_argument("--labels", required=True)
    score.add_argument("--outputs", required=True)
    args = parser.parse_args()
    try:
        if args.command == "prepare-portable":
            source = Path(args.fixture).read_bytes()
            result = {"source_sha256": hashlib.sha256(source).hexdigest(),
                      "cases": portable_cases(json.loads(source))}
            with Path(args.out).open("x", encoding="utf-8") as handle:
                json.dump(result, handle, ensure_ascii=False, indent=2)
                handle.write("\n")
            print(f"Prepared {len(result['cases'])} label-free cases: {args.out}")
            return 0
        result = evaluate(json.loads(Path(args.labels).read_text(encoding="utf-8")),
                          json.loads(Path(args.outputs).read_text(encoding="utf-8")))
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0 if result["passes_automated_gate"] else 1
    except (OSError, ValueError, TypeError) as exc:
        print(json.dumps({"error": str(exc)}))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
