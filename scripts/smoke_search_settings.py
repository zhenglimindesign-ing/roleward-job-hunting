#!/usr/bin/env python3
"""Fresh-process checks for saved settings, one-off caps and state continuity."""

import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main():
    work = ROOT / "work"
    work.mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="search-settings-", dir=work) as td:
        workspace = Path(td)
        state_path = workspace / "state" / "roleward-state.json"

        def run(script, *args, expected=0, parse=True):
            flag = "--path" if script == "state_store.py" else "--state"
            result = subprocess.run(
                [sys.executable, "-B", str(ROOT / "scripts" / script),
                 flag, str(state_path), *args],
                cwd=workspace, capture_output=True, text=True,
            )
            assert result.returncode == expected, (script, args, result.stdout, result.stderr)
            return json.loads(result.stdout) if parse and expected == 0 else result.stdout

        def state():
            return run("state_store.py", "show")

        def set_limit(value):
            run("context_state.py", "confirm-field", "--field", "search_policy.max_results",
                "--value-json", json.dumps(value), parse=False)

        run("state_store.py", "init", parse=False)
        default = run("scan_state.py", "start")
        assert default["plan"]["max_results"] == 5
        assert "max_results" not in state()["search_policy"]
        set_limit(3)
        saved = run("scan_state.py", "start")
        assert saved["plan"]["max_results"] == 3
        assert state()["search_policy"]["max_results"]["authority"] == "confirmed_truth"
        once = run("scan_state.py", "start", "--max-results", "1")
        assert once["plan"]["max_results"] == 1
        assert run("scan_state.py", "start")["plan"]["max_results"] == 3
        assert state()["search_policy"]["max_results"]["value"] == 3

        candidates = {"candidates": [
            {"job": {"company": f"Synthetic {i}", "title": "Product Manager",
                     "url": f"https://example.invalid/jobs/{i}", "text": f"Synthetic role {i}",
                     "live_status": "verified_live"},
             "facts": {"geographies": ["Germany"], "employability": "eligible_now"},
             "disposition": "worth_review"}
            for i in range(6)
        ]}
        payload = workspace / "candidates.json"
        payload.write_text(json.dumps(candidates))
        # Later settings changes must not rewrite existing Scan plans.
        set_limit(2)
        for scan, expected in [(default, 5), (saved, 3), (once, 1)]:
            run("scan_state.py", "ingest", "--scan-id", scan["id"], "--input", str(payload))
            finished = run("scan_state.py", "finalize", "--scan-id", scan["id"])
            assert len(finished["selected_opportunity_ids"]) == expected
        assert run("scan_state.py", "start")["plan"]["max_results"] == 2
        assert any(row["field"] == "search_policy.max_results" and
                   row["superseded"]["value"] == 3 for row in state()["field_history"])

        for value, exit_code in [("0", 1), ("-1", 1), ("1.5", 2)]:
            before = state_path.read_bytes()
            run("scan_state.py", "start", "--max-results", value, expected=exit_code, parse=False)
            assert state_path.read_bytes() == before
        # Legacy malformed saved values must fail without silently choosing a cap.
        for value in [0, -1, True, 1.5, "many"]:
            set_limit(value)
            before = state_path.read_bytes()
            run("scan_state.py", "start", expected=1, parse=False)
            assert state_path.read_bytes() == before
        set_limit(2)
        run("state_store.py", "validate", parse=False)
    print("Search settings passed: default 5, persisted edits, one-off override, frozen plans, invalid-value isolation")


if __name__ == "__main__":
    main()
