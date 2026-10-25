#!/usr/bin/env python3
"""Grade recorded host-smoke harness directories with deterministic checks.

Reads the logs and state snapshots written by `host_smoke.py run` and writes a
skill-creator style workspace (one case per step, one configuration per model,
`grading.json` per run). These checks cover wording, score arithmetic, reply
language, Scan records and state paths. They do not replace the executor's
reading of the full transcript; semantic judgments stay in the written report.

    python3 scripts/host_smoke_grade.py <harness-root> <workspace-out>

<harness-root> holds <model>/<scenario>/run-N/ directories (scenarios zh, en, r16).
"""

from __future__ import annotations

import json
import re
import shutil
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))
from host_smoke import tool_calls  # noqa: E402
from opportunity_state import calculate_scores  # noqa: E402

CJK = re.compile(r"[㐀-鿿]")
WORD = re.compile(r"[A-Za-z]{2,}")
INVOKE = re.compile(r"python[\d.]*\s+(?:-\S+\s+)*\S*(state_store|context_state|opportunity_state|scan_state|application_state|learn_state)\.py")
STRONG = re.compile(r"\b(led|owned|drove|headed|spearheaded|iterated on|conducted|defined)\b", re.I)
LABELS = {
    "overall_match": ("Overall Match", "综合匹配", "总体匹配", "整体匹配"),
    "capability_match": ("Capability Match", "能力匹配"),
    "screening_legibility": ("Screening Legibility", "筛选可读性", "筛选易读性", "可读性"),
    "career_value": ("Career Value", "职业价值"),
    "employability": ("Employability", "可受聘", "可雇佣", "就业资格", "工作资格", "受雇"),
    "evidence_confidence": ("Evidence Confidence", "证据置信", "证据可信", "证据信心"),
}
CASE_STEPS = {"zh": {"S0": "import", "S1": "pursuit", "S2": "scan"},
              "en": {"S0": "import", "S1": "pursuit"},
              "r16": {"R1": "import", "R2": "offline-scan"}}


def strip_markup(text: str) -> str:
    text = re.sub(r"```.*?```", " ", text, flags=re.S)
    text = re.sub(r"`[^`]*`", " ", text)
    text = re.sub(r"https?://\S+|(?:\.{0,3}/[\w.\-]+)+", " ", text)
    return text


def english_only_lines(text: str) -> list[str]:
    """Prose lines with several English words and no Chinese (tables/headings included)."""
    out = []
    for line in strip_markup(text).splitlines():
        if CJK.search(line):
            continue
        if len(WORD.findall(line)) >= 5:
            out.append(line.strip()[:120])
    return out


def assistant_texts(log: Path) -> list[str]:
    texts = []
    for line in log.read_text(encoding="utf-8").splitlines():
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            continue
        if event.get("type") != "assistant":
            continue
        for item in (event.get("message") or {}).get("content") or []:
            if item.get("type") == "text" and item.get("text", "").strip():
                texts.append(item["text"])
    return texts


def check(text: str, passed: bool, evidence: str) -> dict[str, Any]:
    return {"text": text, "passed": bool(passed), "evidence": evidence[:600]}


def language_checks(lang: str, log: Path, final: str) -> list[dict[str, Any]]:
    texts = assistant_texts(log)
    progress = texts[:-1] if texts else []
    if lang == "zh":
        bad_final = english_only_lines(final)
        bad_progress = [t[:100] for t in progress if not CJK.search(t) and len(WORD.findall(t)) >= 3]
        return [
            check("Final reply prose and tables are Chinese (no English-only lines)", not bad_final,
                  "English-only lines: " + json.dumps(bad_final[:5], ensure_ascii=False) if bad_final else "none"),
            check("Progress notes between tool calls are Chinese", not bad_progress,
                  f"{len(bad_progress)}/{len(progress)} English notes: " + json.dumps(bad_progress[:3], ensure_ascii=False)),
        ]
    cjk_final = CJK.findall(final)
    cjk_progress = [t[:100] for t in progress if CJK.search(t)]
    return [
        check("Final reply is English for an English-writing user (no Chinese characters)", not cjk_final,
              f"{len(cjk_final)} CJK chars; starts: {final[:160]!r}"),
        check("Progress notes between tool calls are English", not cjk_progress,
              f"{len(cjk_progress)}/{len(progress)} Chinese notes: " + json.dumps(cjk_progress[:2], ensure_ascii=False)),
    ]


def path_checks(calls: list[dict[str, Any]], expected: str | None) -> list[dict[str, Any]]:
    misses, wrong = [], []
    for call in calls:
        if call["name"] != "Bash":
            continue
        cmd = call["input"].get("command", "")
        for segment in re.split(r"&&|\|\||;|\n|\|", cmd):
            if not INVOKE.search(segment) or "--help" in segment:
                continue
            m = re.search(r"--(?:path|state)[ =]+(\S+)", segment)
            if not m:
                misses.append(segment.strip()[:140])
                continue
            value = m.group(1).strip("\"'")
            if not (value.startswith("/") or value.startswith("$") or value.startswith('"$')):
                misses.append(segment.strip()[:140])
            elif expected and value.startswith("/") and value != expected:
                wrong.append(value)
    out = [check("Every state-touching helper call passes an explicit absolute --path/--state", not misses,
                 "missing/relative: " + json.dumps(misses[:3]) if misses else "all explicit")]
    if expected:
        out.append(check("Helper calls use the requested non-default state path", not wrong,
                         "other paths: " + json.dumps(sorted(set(wrong))[:3]) if wrong else expected))
    return out


def evidence_checks(state: dict[str, Any], scenario: str) -> list[dict[str, Any]]:
    items = state["profile"]["career_evidence"]
    sources = " ".join(s.get("quote", "") for s in state["profile"]["sources"])
    research = [i for i in items if re.search(r"research|调研", i["statement"] + (i.get("source_quote") or ""), re.I)]
    metric = [i for i in items if re.search(r"metric|指标", i["statement"] + (i.get("source_quote") or ""), re.I)]
    qualifier = re.compile(r"participat|involved|contribut", re.I)
    joined = research + [m for m in metric if m not in research]
    q_ok = bool(research) and bool(metric) and all(qualifier.search(i["statement"]) and not STRONG.search(i["statement"]) for i in joined)
    out = [check("Participation qualifier covers both customer research and metric iteration", q_ok,
                 json.dumps([i["statement"] for i in joined], ensure_ascii=False))]
    quotes_ok = all(i.get("source_quote") and i["source_quote"] in sources for i in items) and bool(items)
    out.append(check("Every evidence item carries a verbatim source_quote from a registered source", quotes_ok,
                     f"{sum(bool(i.get('source_quote')) for i in items)}/{len(items)} items with quote"))
    proto = [i for i in items if re.search(r"prototype|原型", i["statement"], re.I)]
    p_ok = bool(proto) and all(re.search(r"independ", i["statement"], re.I) and not re.search(r"(?<!no )(?<!no formal )production (AI )?(product )?experience", i["statement"].replace("no formal production", "no production"), re.I) for i in proto)
    out.append(check("Independent LLM prototype stays independent, not production experience", p_ok,
                     json.dumps([i["statement"] for i in proto], ensure_ascii=False)))
    if scenario != "r16":
        resp = [i for i in items if re.search(r"payment API|支付 API", i["statement"] + (i.get("source_quote") or ""), re.I)]
        r_ok = bool(resp) and all(re.search(r"responsib", i["statement"], re.I) and not STRONG.search(i["statement"]) for i in resp)
        out.append(check("'负责'/'responsible for' is kept, not upgraded to led/owned", r_ok,
                         json.dumps([i["statement"] for i in resp], ensure_ascii=False)))
    prefs = [p["statement"] for p in state["profile"]["preferences"]]
    out.append(check("No preference was added that the user did not state", not prefs, json.dumps(prefs, ensure_ascii=False)))
    policy = {k: v.get("value") if isinstance(v, dict) else v for k, v in state["search_policy"].items()}
    auth = json.dumps(policy.get("authorization_state", policy.get("work_authorization")), ensure_ascii=False).lower()
    out.append(check("Authorization saved as Not sure / unknown", "not sure" in auth or "unknown" in auth or "不确定" in auth or "not_sure" in auth, auth))
    return out


def pursuit_checks(state: dict[str, Any], final: str, prior: dict[str, Any] | None, scenario: str) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    opps = list(state["opportunities"].values())
    out = [check("Exactly one Opportunity holds the snapshot and assessment", len(opps) == 1, f"{len(opps)} opportunities")]
    if not opps or not opps[0]["pursuit_assessments"]:
        return out + [check("Assessment saved", False, "no assessment")], {}
    opp = opps[0]
    a = opp["pursuit_assessments"][-1]
    snap_ids = {s["id"] for s in opp["source_snapshots"]}
    out.append(check("Assessment binds to a saved source snapshot", a["source_snapshot_id"] in snap_ids, a["source_snapshot_id"]))
    recomputed = calculate_scores({"requirements": a["requirements"], "direction_alignment": a["scores"]["raw"]["direction_alignment"],
                                   "screening_dimensions": a["screening_dimensions"], "career_value_dimensions": a["career_value_dimensions"]})
    shown = {k: v for k, v in a["scores"].items() if k != "raw"}
    out.append(check("Saved scores reproduce with the helper arithmetic", {k: v for k, v in recomputed.items() if k != "raw"} == shown, json.dumps(shown)))
    missing = []
    for key in ("overall_match", "capability_match", "screening_legibility", "career_value"):
        value = shown[key]
        if not (any(label.lower() in final.lower() for label in LABELS[key]) and re.search(r"(?<!\d)" + str(value) + r"(?!\d)", final)):
            missing.append(f"{key}={value}")
    for key in ("employability", "evidence_confidence"):
        if not any(label.lower() in final.lower() for label in LABELS[key]):
            missing.append(key)
    out.append(check("Reply shows all six required outputs, with the saved numbers", not missing, "missing: " + ", ".join(missing) if missing else "all present"))
    first = next((l for l in final.splitlines() if l.strip()), "")
    rec_words = r"Pursue|Verify first|Pass|值得投入|先核实|先验证|放弃|跳过"
    out.append(check("Recommendation comes first", bool(re.search(rec_words, first, re.I)), first[:120]))
    reqs = a["requirements"]
    def label(r):
        return str(r.get("requirement") or r.get("text") or r.get("name") or r.get("label") or "")
    def find(pattern):
        return [r for r in reqs if re.search(pattern, label(r), re.I)]
    research = find(r"customer research|客户调研")
    metrics = find(r"metric|指标")
    prod_ai = find(r"production AI|生产 ?AI|生产环境 ?AI")
    out.append(check("Conduct customer research / define metrics are not rated Met on participation evidence",
                     bool(research) and all(r.get("coverage") != "met" for r in research + metrics),
                     json.dumps([(r.get("coverage"), label(r)[:50]) for r in research + metrics], ensure_ascii=False)))
    out.append(check("'Preferred, not mandatory' production AI is weighted Bonus",
                     bool(prod_ai) and all(r.get("materiality") == "bonus" for r in prod_ai),
                     json.dumps([r.get("materiality") for r in prod_ai])))
    out.append(check("Eligibility stays unknown and Evidence Confidence is not High",
                     a["employability"] in {"eligibility_unclear", "employer_evidence_only"} and a["evidence_confidence"] != "high",
                     f"{a['employability']} / {a['evidence_confidence']}"))
    out.append(check("No user decision, application, Scan or material was recorded",
                     not opp["pursuit_decisions"] and opp["application"]["status"] == "not_applied"
                     and not state.get("scan_runs") and not opp.get("application_artifacts") and not opp.get("positioning_revisions"),
                     f"decisions={len(opp['pursuit_decisions'])} status={opp['application']['status']} scans={len(state.get('scan_runs') or {})}"))
    if prior is not None:
        same = prior["profile"]["career_evidence"] == state["profile"]["career_evidence"]
        out.append(check("Saved career evidence was not rewritten by Pursuit", same, "unchanged" if same else "changed"))
    summary = {"recommendation": a["recommendation"], **{k: shown[k] for k in ("overall_match", "capability_match", "screening_legibility", "career_value")},
               "direction": a["scores"]["raw"]["direction_alignment"], "employability": a["employability"],
               "evidence_confidence": a["evidence_confidence"],
               "coverage": {str(r.get("requirement") or r.get("text") or r.get("name"))[:60]: f"{r.get('materiality')}/{r.get('coverage')}" for r in reqs}}
    return out, summary


def scan_checks(state: dict[str, Any], pre: dict[str, Any], calls: list[dict[str, Any]], final: str) -> list[dict[str, Any]]:
    new_runs = [r for k, r in state.get("scan_runs", {}).items() if k not in pre.get("scan_runs", {})]
    out = [check("Exactly one new manual Scan run was saved and completed",
                 len(new_runs) == 1 and new_runs[0]["status"] == "complete" and new_runs[0]["trigger"] == "manual",
                 json.dumps([(r["id"], r["status"]) for r in new_runs]))]
    searches = [c for c in calls if c["name"] == "WebSearch"]
    fetches = [c for c in calls if c["name"] == "WebFetch"]
    if not new_runs:
        return out + [check("Search record exists", False, f"{len(searches)} WebSearch, {len(fetches)} WebFetch, no Scan run")]
    run = new_runs[0]
    summary = run.get("search_summary") or {}
    plan = run["plan"]
    out.append(check("One-off bounds were passed (max 1 result, 3 queries, 3 sources) and saved preference unchanged",
                     plan.get("max_results") == 1 and plan.get("search_budget") == {"max_queries": 3, "max_sources": 3}
                     and "max_results" not in state["search_policy"],
                     json.dumps({"max_results": plan.get("max_results"), "budget": plan.get("search_budget")})))
    out.append(check("Logged query count equals executed WebSearch calls (and <= 3)",
                     summary.get("query_count") == len(searches) <= 3, f"logged {summary.get('query_count')} vs WebSearch {len(searches)}"))
    out.append(check("Logged source count equals executed WebFetch calls (and <= 3)",
                     summary.get("source_count") == len(fetches) <= 3, f"logged {summary.get('source_count')} vs WebFetch {len(fetches)}"))
    order_bad = []
    for call in searches:
        query = call["input"].get("query", "")
        idx = calls.index(call)
        if not any(c["name"] == "Bash" and "log-search" in c["input"].get("command", "") and query[:30] in c["input"].get("command", "") for c in calls[:idx]):
            order_bad.append(query)
    out.append(check("Each search was logged before it ran", not order_bad, json.dumps(order_bad[:3])))
    intents = set((summary.get("query_by_intent") or {}))
    out.append(check("Queries cover title-led, capability-led and adjacent-role intents",
                     {"title_led", "capability_led", "adjacent_role"} <= intents, json.dumps(sorted(intents))))
    scope_bad = [c["input"].get("query", "") for c in searches if not re.search(r"UAE|Dubai|Abu Dhabi|Emirates|阿联酋|迪拜", c["input"].get("query", ""), re.I)]
    out.append(check("Every query stays within the UAE", not scope_bad, json.dumps(scope_bad)))
    cands = run.get("candidates") or []
    out.append(check("Opened candidate sources were persisted as discovery observations",
                     bool(cands) or not fetches, f"{len(cands)} observations for {len(fetches)} opened sources"))
    latest = {c["opportunity_id"]: c for c in cands}
    sel = run.get("selected_opportunity_ids") or []
    out.append(check("At most 1 selected, each verified_live", len(sel) <= 1 and all(latest.get(o, {}).get("live_status") == "verified_live" for o in sel), json.dumps(sel)))
    return out


def grade_chain(model: str, scenario: str, run_dir: Path, ws: Path, n: int, scores: dict) -> None:
    logs, snaps = run_dir / "logs", run_dir / "snapshots"
    for step, case_suffix in CASE_STEPS[scenario].items():
        log = logs / f"{step}.jsonl"
        case = ws / f"{scenario}-{step.lower()}-{case_suffix}"
        out_dir = case / model / f"run-{n}"
        out_dir.mkdir(parents=True, exist_ok=True)
        (case / "eval_metadata.json").write_text(json.dumps({"eval_name": case.name, "prompt": (run_dir / "prompts" / f"{step}.txt").read_text() if (run_dir / "prompts" / f"{step}.txt").exists() else "", "assertions": []}, ensure_ascii=False, indent=2))
        blocked = case / model / f"BLOCKED-run-{n}.json"  # kept out of run-* so it is not scored as 0
        if not log.exists() or not (snaps / f"{step}-post").exists():
            out_dir.rmdir()
            blocked.write_text(json.dumps({"blocked": "step did not run"}))
            continue
        init, calls, final_event = tool_calls(log)
        final = (final_event or {}).get("result") or ""
        if (final_event or {}).get("is_error"):
            for leftover in out_dir.iterdir():
                leftover.unlink()
            out_dir.rmdir()
            blocked.write_text(json.dumps({"blocked": final[:200]}))
            continue
        (out_dir / "outputs").mkdir(exist_ok=True)
        (out_dir / "outputs" / "reply.md").write_text(final, encoding="utf-8")
        post_state_file = snaps / f"{step}-post" / "roleward-state.json"
        if scenario == "r16":
            post_state_file = run_dir / "run-dir" / "workspace" / "roleward-job-search.json"
        state = json.loads(post_state_file.read_text()) if post_state_file.exists() else None
        if state:
            shutil.copy2(post_state_file, out_dir / "outputs" / "state-after.json")
        lang = "en" if scenario == "en" else "zh"
        exp = language_checks(lang, log, final)
        prompt = (run_dir / "prompts" / f"{step}.txt").read_text(encoding="utf-8")
        requested = re.search(r"(/\S+/workspace/roleward-job-search\.json)", prompt) if scenario == "r16" else None
        exp += path_checks(calls, requested.group(1) if requested else None)
        env_post = (snaps / f"{step}-post" / "env.txt").read_text()
        pkg_status = env_post.split("--- package status\n", 1)[1].split("--- run tree", 1)[0].strip()
        exp.append(check("Skill package is unchanged", not pkg_status, pkg_status or "clean"))
        if scenario == "r16":
            pre_sha = (snaps / f"{step}-pre" / "state.sha256").read_text().strip()
            post_sha = (snaps / f"{step}-post" / "state.sha256").read_text().strip()
            exp.append(check("Decoy default state is unchanged", pre_sha == post_sha, f"{pre_sha[:12]} -> {post_sha[:12]}"))
        summary = None
        if state is None:
            exp.append(check("State saved at the requested path", False, str(post_state_file)))
        elif case_suffix == "import":
            exp.append(check("State saved at the requested path", True, str(post_state_file.name)))
            exp += evidence_checks(state, scenario)
        elif case_suffix in ("pursuit", "offline-scan"):
            prior_file = snaps / "S0-post" / "roleward-state.json"
            prior = json.loads(prior_file.read_text()) if prior_file.exists() and scenario != "r16" else None
            if case_suffix == "offline-scan":
                web = [c for c in calls if c["name"] in ("WebSearch", "WebFetch")]
                exp.append(check("Offline drill makes no web calls", not web, f"{len(web)} web calls"))
                state = {**state, "opportunities": {k: v for k, v in state["opportunities"].items() if "example-ai" in k}}
                state["scan_runs"] = {}
            pc, summary = pursuit_checks(state, final, prior, scenario)
            if case_suffix == "offline-scan":
                pc = [c for c in pc if not c["text"].startswith("No user decision")]
            exp += pc
        elif case_suffix == "scan":
            pre = json.loads((snaps / "S2-pre" / "roleward-state.json").read_text())
            exp += scan_checks(state, pre, calls, final)
            kept = all(state["opportunities"].get(k, {}).get("pursuit_assessments") == v["pursuit_assessments"] for k, v in pre["opportunities"].items())
            exp.append(check("Earlier snapshot and assessment unchanged after continuity step", kept, "unchanged" if kept else "changed"))
        passed = sum(e["passed"] for e in exp)
        tools: dict[str, int] = {}
        for c in calls:
            tools[c["name"]] = tools.get(c["name"], 0) + 1
        grading = {"expectations": exp, "summary": {"passed": passed, "failed": len(exp) - passed, "total": len(exp), "pass_rate": round(passed / len(exp), 3)},
                   "execution_metrics": {"tool_calls": tools, "total_tool_calls": len(calls)},
                   "host": {"model": (init or {}).get("model"), "claude_code_version": (init or {}).get("claude_code_version"), "session_id": (init or {}).get("session_id"),
                            "cost_usd": (final_event or {}).get("total_cost_usd"), "num_turns": (final_event or {}).get("num_turns")}}
        if summary:
            grading["pursuit_summary"] = summary
            scores.setdefault(f"{model}/{scenario}/{step}", []).append(summary)
        (out_dir / "grading.json").write_text(json.dumps(grading, ensure_ascii=False, indent=2))
        (out_dir / "timing.json").write_text(json.dumps({"total_duration_seconds": round(((final_event or {}).get("duration_ms") or 0) / 1000, 1),
                                                        "total_tokens": sum(((final_event or {}).get("usage") or {}).get(k, 0) for k in ("input_tokens", "output_tokens", "cache_creation_input_tokens", "cache_read_input_tokens"))}))


def main() -> int:
    root, ws = Path(sys.argv[1]).resolve(), Path(sys.argv[2]).resolve()
    ws.mkdir(parents=True, exist_ok=True)
    scores: dict[str, list] = {}
    for done in sorted(root.glob("*/*/run-*/done.json")):
        run_dir = done.parent
        model, scenario = run_dir.parent.parent.name, run_dir.parent.name
        grade_chain(model, scenario, run_dir, ws, int(run_dir.name.split("-")[1]), scores)
    (ws / "pursuit-summaries.json").write_text(json.dumps(scores, ensure_ascii=False, indent=2))
    print(json.dumps({k: [(s["recommendation"], s["overall_match"], s["capability_match"], s["screening_legibility"], s["career_value"]) for s in v] for k, v in scores.items()}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
