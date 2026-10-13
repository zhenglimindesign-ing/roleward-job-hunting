#!/usr/bin/env python3
"""Summarize resume pairwise review as an extension of the existing Alpha eval."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from eval_runner import validate_fixture

DIMENSIONS = ("relevance", "strongest_proof", "fidelity", "information_preservation",
              "screening_legibility", "natural_writing", "submission_readiness")


def evaluate(fixture: dict, review: dict) -> dict:
    errors = validate_fixture(fixture, Path("resume acceptance set"))
    if fixture.get("kind") != "resume_acceptance_set":
        errors.append("Expected the existing runner's resume_acceptance_set fixture")
    expected = {row["case_id"] for row in fixture.get("input", {}).get("cases", [])}
    rows = review.get("cases", [])
    ids = [row.get("case_id") for row in rows]
    if set(ids) != expected or len(ids) != len(expected):
        errors.append("Review must cover every case exactly once")
    if review.get("reviewer_type") not in ("human", "independent_model", "coordinator"):
        errors.append("Declare reviewer_type; model/coordinator review is not human acceptance")
    for row in rows:
        if row.get("preferred") not in ("base", "tailored", "tie") or not row.get("reason"):
            errors.append(f"{row.get('case_id')}: provide pairwise preference and reason")
        if not isinstance(row.get("hard_failures"), list) or type(row.get("no_consequential_regression")) is not bool:
            errors.append(f"{row.get('case_id')}: provide explicit failure and regression judgments")
        if not all(row.get("dimensions", {}).get(key) in ("improved", "same", "worse") for key in DIMENSIONS):
            errors.append(f"{row.get('case_id')}: review every quality dimension")
        for key in ("base_ir_sha256", "tailored_ir_sha256"):
            value = row.get(key)
            if not isinstance(value, str) or len(value) != 64:
                errors.append(f"{row.get('case_id')}: {key} must identify the reviewed content")
    failures = sum(len(row.get("hard_failures", [])) for row in rows)
    preferred = sum(row.get("preferred") == "tailored" for row in rows)
    no_regression = all(row.get("no_consequential_regression") is True for row in rows)
    return {"review_complete": not errors, "reviewer_type": review.get("reviewer_type"),
            "cases": len(rows), "hard_failure_count": failures, "tailored_preferred": preferred,
            "proposed_target_met": not errors and not failures and no_regression and preferred >= fixture["expected"]["tailored_preference_minimum"],
            "criterion_status": "proposed_pending_pm", "product_semantically_accepted": False,
            "human_acceptance_completed": review.get("reviewer_type") == "human" and not errors,
            "errors": errors}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--fixture", type=Path, default=Path("fixtures/resume/acceptance-set-v0.json"))
    parser.add_argument("--review", type=Path, required=True)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    result = evaluate(json.loads(args.fixture.read_text()), json.loads(args.review.read_text()))
    if args.output:
        args.output.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))
    return 0 if result["review_complete"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
