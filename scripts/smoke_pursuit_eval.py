#!/usr/bin/env python3
"""Regression checks for assessment persistence and honest eval boundaries."""

import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
from copy import deepcopy
from pathlib import Path

from opportunity_state import record_assessment
from pursuit_eval import evaluate, portable_cases
from state_store import empty_state, load_state, save_state

ROOT = Path(__file__).resolve().parents[1]


def plan(when="before_application"):
    return {"target": "Role-level sponsorship", "when": when,
            "method": "Check the employer's role-specific hiring information."}


def output(case_id):
    return {"case_id": case_id, "recommendation": "pursue",
            "overall_match": 80, "capability_match": 80,
            "screening_legibility": 75, "career_value": 85,
            "employability": "eligibility_unclear", "evidence_confidence": "medium",
            "core_hiring_reason": "Synthetic evaluator control, not a host judgment.",
            "major_support": [], "major_gaps": [], "decision_unknowns": [],
            "verification_plan": []}


class PursuitRegression(unittest.TestCase):
    def setUp(self):
        self.payload = json.loads((ROOT / "fixtures/_inputs/direct-opportunity-assessment.json").read_text())
        self.fixture = json.loads((ROOT / "fixtures/portable/profile-set-v0.json").read_text())
        self.labels = {"cases": [{"case_id": f"case-{n}", "pursuit_label": "pursue"} for n in range(12)]}
        self.outputs = {"run": {"variant": "synthetic_control", "run_id": "unit-test",
                                "model_or_host": "none; synthetic test", "created_at": "2026-09-06T00:00:00Z"},
                        "cases": [output(row["case_id"]) for row in self.labels["cases"]]}

    def test_verified_plan_and_components_survive_reload_and_input_mutation(self):
        state = empty_state()
        self.payload.update(recommendation="verify_first", verification_plan=[plan()])
        result = record_assessment(state, self.payload)
        frozen = deepcopy(result["assessment"])
        self.payload["verification_plan"][0]["target"] = "Rewritten input"
        self.payload["requirements"][0]["coverage"] = "missing"
        self.payload["screening_dimensions"][0] = 0
        self.payload["career_value_dimensions"][0] = 0
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "state.json"
            save_state(path, state)
            loaded = load_state(path)
        self.assertEqual(loaded["opportunities"][result["opportunity_id"]]["pursuit_assessments"][0], frozen)
        self.assertEqual(frozen["verification_plan"], [plan()])
        self.assertEqual(frozen["screening_dimensions"], [3, 3, 2, 3])
        self.assertEqual(frozen["career_value_dimensions"], [4, 3, 3, 2])

    def test_invalid_verification_never_mutates_state(self):
        for plans in ([], None, "Ask recruiter", [plan("during_process")],
                      [{**plan(), "method": " "}], [{**plan(), "when": []}], ["bad"]):
            with self.subTest(plans=plans):
                state = empty_state()
                before = deepcopy(state)
                self.payload.update(recommendation="verify_first", verification_plan=plans)
                with self.assertRaises(ValueError):
                    record_assessment(state, self.payload)
                self.assertEqual(state, before)

    def test_invalid_score_does_not_add_an_opportunity(self):
        state = empty_state()
        before = deepcopy(state)
        self.payload["screening_dimensions"] = [5, 3, 2, 3]
        with self.assertRaises(ValueError):
            record_assessment(state, self.payload)
        self.assertEqual(state, before)

    def test_pursue_allows_process_checks_but_not_pre_application_gate(self):
        self.payload["verification_plan"] = [plan("during_process")]
        record_assessment(empty_state(), self.payload)
        self.payload["verification_plan"] = [plan()]
        with self.assertRaises(ValueError):
            record_assessment(empty_state(), self.payload)

    def test_legacy_pursue_payload_remains_valid(self):
        record = record_assessment(empty_state(), self.payload)["assessment"]
        self.assertEqual(record["verification_plan"], [])

    def test_exact_85_percent_boundary(self):
        self.outputs["cases"][0]["recommendation"] = "pass"
        self.assertTrue(evaluate(self.labels, self.outputs)["passes_automated_gate"])
        self.outputs["cases"][1]["recommendation"] = "pass"
        result = evaluate(self.labels, self.outputs)
        self.assertFalse(result["passes_automated_gate"])
        self.assertEqual(result["exact_matches"], 10)

    def test_missing_case_is_not_removed_from_denominator(self):
        self.outputs["cases"] = self.outputs["cases"][:1]
        result = evaluate(self.labels, self.outputs)
        self.assertEqual(result["expected_cases"], 12)
        self.assertEqual(result["recommendation_agreement"], round(1 / 12, 4))
        self.assertFalse(result["passes_automated_gate"])
        self.assertEqual(len(result["errors"]), 11)

    def test_duplicate_empty_and_extra_cases_fail(self):
        for target in ("labels", "outputs"):
            for kind in ("duplicate", "empty"):
                with self.subTest(target=target, kind=kind):
                    labels, outputs = deepcopy(self.labels), deepcopy(self.outputs)
                    payload = labels if target == "labels" else outputs
                    payload["cases"] = payload["cases"] + [payload["cases"][0]] if kind == "duplicate" else []
                    with self.assertRaises(ValueError):
                        evaluate(labels, outputs)
        self.outputs["cases"].append(output("unexpected"))
        self.assertFalse(evaluate(self.labels, self.outputs)["passes_automated_gate"])

    def test_scores_do_not_truncate_fractions_or_accept_booleans(self):
        for value in (True, False, 80.5, float("nan"), float("inf"), -5, 105, 10 ** 999, "80"):
            with self.subTest(value=value):
                self.outputs["cases"][0]["capability_match"] = value
                self.assertFalse(evaluate(self.labels, self.outputs)["passes_automated_gate"])

    def test_verify_first_format_is_necessary_but_not_semantic_acceptance(self):
        self.labels["cases"][0]["pursuit_label"] = "verify_first"
        self.outputs["cases"][0]["recommendation"] = "verify_first"
        self.assertFalse(evaluate(self.labels, self.outputs)["passes_automated_gate"])
        self.outputs["cases"][0]["verification_plan"] = [plan()]
        result = evaluate(self.labels, self.outputs)
        self.assertTrue(result["passes_automated_gate"])
        self.assertTrue(result["semantic_review_required"])

    def test_missing_output_contract_fields_fail(self):
        for field in ("employability", "core_hiring_reason", "evidence_confidence", "major_support",
                      "major_gaps", "decision_unknowns", "verification_plan"):
            outputs = deepcopy(self.outputs)
            del outputs["cases"][0][field]
            self.assertFalse(evaluate(self.labels, outputs)["passes_automated_gate"], field)

    def test_portable_export_excludes_labels_and_annotations(self):
        self.fixture["input"]["profiles"][0]["private_annotation"] = "label hint"
        self.fixture["input"]["profiles"][0]["jobs"][0]["future_label"] = "label hint"
        cases = portable_cases(self.fixture)
        self.assertEqual(len(cases), 10)
        for case in cases:
            self.assertEqual(set(case), {"case_id", "profile_id", "candidate", "job"})
            self.assertEqual(set(case["job"]), {"title", "summary"})
            self.assertEqual(set(case["candidate"]), {"career_anchor", "direction", "geography", "authorization_state"})

    def test_portable_revision_preserves_frozen_inputs_and_labels(self):
        original = (ROOT / "fixtures/portable/profile-set-v0.json").read_bytes()
        original_hash = hashlib.sha256(original).hexdigest()
        self.assertEqual(original_hash, "3cb2f4852c25d65c779a6ffae2443afbe4877e12cf66156860e6e37e0d6d48cd")
        revised = json.loads((ROOT / "fixtures/portable/profile-set-v1.json").read_text())
        self.assertEqual(revised["revision"]["parent_sha256"], original_hash)
        self.assertEqual(revised["revision"]["supersedes"], self.fixture["id"])
        first = {c["case_id"]: c for c in portable_cases(self.fixture)}
        second = {c["case_id"]: c for c in portable_cases(revised)}
        self.assertEqual(set(first), set(second))
        self.assertEqual([key for key in first if first[key] != second[key]], ["P2-J1"])
        self.assertEqual(first["P2-J1"]["candidate"], second["P2-J1"]["candidate"])
        self.assertIn("explicitly offers visa/work-permit sponsorship", second["P2-J1"]["job"]["summary"])
        self.assertEqual(first["P3-J2"], second["P3-J2"])
        # Apart from version metadata and that one job summary, the freeze is identical.
        revised.pop("revision")
        revised["id"] = self.fixture["id"]
        revised["input"]["profiles"][1]["jobs"][0]["summary"] = first["P2-J1"]["job"]["summary"]
        self.assertEqual(revised, self.fixture)

    def test_default_portable_export_uses_current_version_without_label_metadata(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "inputs.json"
            result = subprocess.run(
                [sys.executable, "-B", str(ROOT / "scripts/pursuit_eval.py"),
                 "prepare-portable", "--out", str(path)],
                cwd=ROOT, capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            exported = json.loads(path.read_text())
        source = (ROOT / "fixtures/portable/profile-set-v1.json").read_bytes()
        self.assertEqual(exported["source_sha256"], hashlib.sha256(source).hexdigest())
        self.assertEqual(set(exported), {"source_sha256", "cases"})
        self.assertEqual(exported["cases"], portable_cases(json.loads(source)))
        for case in exported["cases"]:
            self.assertEqual(set(case), {"case_id", "profile_id", "candidate", "job"})
            self.assertEqual(set(case["job"]), {"title", "summary"})

    def test_invalid_portable_fixtures_fail_before_export(self):
        mutations = [
            lambda f: f.update(input=[]),
            lambda f: f["input"]["profiles"].append(None),
            lambda f: f["input"]["profiles"].append(deepcopy(f["input"]["profiles"][0])),
            lambda f: f["input"]["profiles"][0]["jobs"][1].update(job_id="P1-J1"),
            lambda f: f["input"]["profiles"][0]["jobs"][0].update(expected_pursuit=[]),
            lambda f: f["input"]["profiles"][0].update(geography=[]),
            lambda f: f["expected"].update(job_count=999),
        ]
        for index, mutation in enumerate(mutations):
            fixture = deepcopy(self.fixture)
            mutation(fixture)
            with self.subTest(index=index), self.assertRaises(ValueError):
                portable_cases(fixture)

    def test_portable_label_scoring_does_not_claim_model_execution(self):
        # Deliberately label-derived controls test the scorer, not the Skill.
        cases = []
        for profile in self.fixture["input"]["profiles"]:
            for job in profile["jobs"]:
                case = output(job["job_id"])
                case["recommendation"] = job["expected_pursuit"]
                if case["recommendation"] == "verify_first":
                    case["verification_plan"] = [plan()]
                cases.append(case)
        self.outputs["cases"] = cases
        result = evaluate(self.fixture, self.outputs)
        self.assertEqual(result["exact_matches"], 10)
        self.assertTrue(result["semantic_review_required"])

    def test_cli_failure_exit_and_no_overwrite(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "inputs.json"
            cmd = [sys.executable, "-B", str(ROOT / "scripts/pursuit_eval.py"),
                   "prepare-portable", "--fixture", str(ROOT / "fixtures/portable/profile-set-v0.json"),
                   "--out", str(path)]
            first = subprocess.run(cmd, capture_output=True, text=True)
            self.assertEqual(first.returncode, 0, first.stdout + first.stderr)
            saved = path.read_bytes()
            second = subprocess.run(cmd, capture_output=True, text=True)
            self.assertNotEqual(second.returncode, 0)
            self.assertEqual(path.read_bytes(), saved)
            labels = Path(td) / "labels.json"
            outputs = Path(td) / "outputs.json"
            labels.write_text(json.dumps(self.labels))
            self.outputs["cases"] = self.outputs["cases"][:1]
            outputs.write_text(json.dumps(self.outputs))
            result = subprocess.run([sys.executable, "-B", str(ROOT / "scripts/pursuit_eval.py"),
                                     "evaluate", "--labels", str(labels), "--outputs", str(outputs)],
                                    capture_output=True, text=True)
            self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
            self.assertFalse(json.loads(result.stdout)["passes_automated_gate"])

    def test_empty_fixture_directory_fails(self):
        with tempfile.TemporaryDirectory() as td:
            result = subprocess.run([sys.executable, "-B", str(ROOT / "scripts/eval_runner.py"),
                                     "--fixtures", td], capture_output=True, text=True)
            self.assertEqual(result.returncode, 1)


if __name__ == "__main__":
    unittest.main()
