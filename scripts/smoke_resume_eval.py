#!/usr/bin/env python3
"""Test review completeness and proposed-gate boundaries without claiming acceptance."""
from copy import deepcopy
import json
from pathlib import Path

from resume_eval import DIMENSIONS, evaluate

fixture = json.loads((Path(__file__).resolve().parents[1] / "fixtures/resume/acceptance-set-v0.json").read_text())
review = {"reviewer_type": "independent_model", "cases": [
    {"case_id": row["case_id"], "preferred": "tailored" if i < 4 else "tie",
     "reason": "Synthetic test judgment", "hard_failures": [],
     "no_consequential_regression": True, "dimensions": {key: "same" for key in DIMENSIONS},
     "base_ir_sha256": "0" * 64, "tailored_ir_sha256": "1" * 64}
    for i, row in enumerate(fixture["input"]["cases"])]}
result = evaluate(fixture, review)
assert result["proposed_target_met"] and not result["product_semantically_accepted"]
assert not result["human_acceptance_completed"]
missing = deepcopy(review); missing["cases"].pop()
assert not evaluate(fixture, missing)["review_complete"]
failure = deepcopy(review); failure["cases"][0]["hard_failures"] = ["unsupported consequential claim"]
assert not evaluate(fixture, failure)["proposed_target_met"]
worse = deepcopy(review); worse["cases"][-1]["no_consequential_regression"] = False
assert not evaluate(fixture, worse)["proposed_target_met"]
duplicate = deepcopy(review); duplicate["cases"][-1]["case_id"] = duplicate["cases"][0]["case_id"]
assert not evaluate(fixture, duplicate)["review_complete"]
print("Resume review completeness and proposed-gate boundary checks passed (5 checks; synthetic judgments).")
