#!/usr/bin/env python3
"""Run and inspect a bounded Claude Code host smoke (see docs/HOST-SMOKE.md).

`run` drives headless `claude -p` sessions through the frozen steps and keeps
raw stream-json logs plus per-step state snapshots in a harness directory.
`summarize` lists the tool calls in one log. Judging stays with the executor.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
PROMPTS = ROOT / "fixtures/_inputs/host-smoke/prompts-v1.json"
TOOLS = "Bash,Read,Write,Edit,Glob,Grep,WebSearch,WebFetch"
MOCK_SERVER = "mocksend"
# Isolation from the operator's own setup: project settings only (none exist in a
# fresh run directory), no auto memory, and only the MCP servers named here.
# --safe-mode would also drop --mcp-config servers, which S3b needs.
ISOLATION = ["--setting-sources", "project", "--settings", json.dumps({"autoMemoryEnabled": False}),
             "--strict-mcp-config"]
ISOLATION_ENV = {"CLAUDE_CODE_DISABLE_AUTO_MEMORY": "1"}


def load_prompts(path: Path = PROMPTS) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def render(prompts: dict[str, Any], step: str, package: Path, run: Path) -> str:
    return prompts["steps"][step].replace("{PACKAGE}", str(package)).replace("{RUN}", str(run))


def session_args(prompts: dict[str, Any], step: str, sessions: dict[str, str]) -> list[str]:
    name, mode = prompts["sessions"][step].split(":")
    if mode == "resume":
        if name not in sessions:
            raise ValueError(f"{step} resumes session {name}, which has not been started")
        return ["--resume", sessions[name]]
    sessions[name] = str(uuid.uuid4())
    return ["--session-id", sessions[name]]


def build_command(step: str, prompt: str, sessions: list[str], *, model: str, package: Path,
                  mock_log: Path | None = None) -> list[str]:
    servers: dict[str, Any] = {}
    allowed = TOOLS.replace(",", " ")
    if step == "S3b":
        if mock_log is None:
            raise ValueError("S3b needs a mock send log path")
        servers[MOCK_SERVER] = {
            "command": sys.executable,
            "args": [str(ROOT / "scripts/host_smoke_mock_send.py")],
            "env": {"ROLEWARD_MOCK_SEND_LOG": str(mock_log)},
        }
        allowed += f" mcp__{MOCK_SERVER}"
    return [
        "claude", "-p", prompt, *sessions,
        *ISOLATION, "--mcp-config", json.dumps({"mcpServers": servers}),
        "--model", model, "--tools", TOOLS,
        "--permission-mode", "dontAsk", "--allowedTools", allowed,
        "--add-dir", str(package),
        "--output-format", "stream-json", "--verbose",
    ]


def snapshot(out: Path, package: Path, run: Path) -> None:
    out.mkdir(parents=True, exist_ok=True)
    git = lambda *a: subprocess.run(["git", "-C", str(package), *a], capture_output=True, text=True).stdout
    files = sorted(str(p.relative_to(run)) for p in run.rglob("*") if p.is_file())
    (out / "env.txt").write_text(
        f"{datetime.now().astimezone().isoformat()}\n--- package HEAD\n{git('rev-parse', 'HEAD')}"
        f"--- package status\n{git('status', '--short')}--- run tree\n" + "\n".join(files) + "\n",
        encoding="utf-8",
    )
    state = run / "state/roleward-state.json"
    if state.exists():
        shutil.copy2(state, out / "roleward-state.json")
        digest = hashlib.sha256(state.read_bytes()).hexdigest()
    else:
        digest = "state_absent"
    (out / "state.sha256").write_text(digest + "\n", encoding="utf-8")


def tool_calls(log: Path) -> tuple[dict[str, Any] | None, list[dict[str, Any]], dict[str, Any] | None]:
    init, calls, results, final = None, [], {}, None
    for line in log.read_text(encoding="utf-8").splitlines():
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            continue
        if event.get("type") == "system" and event.get("subtype") == "init":
            init = event
        if event.get("type") == "result":
            final = event
        content = (event.get("message") or {}).get("content")
        for item in content if isinstance(content, list) else []:
            if item.get("type") == "tool_use":
                calls.append(item)
            elif item.get("type") == "tool_result":
                text = item.get("content")
                if isinstance(text, list):
                    text = "\n".join(part.get("text", "") for part in text if isinstance(part, dict))
                results[item.get("tool_use_id")] = {"is_error": item.get("is_error"), "text": str(text)}
    for call in calls:
        call["result"] = results.get(call["id"])
    return init, calls, final


def run_steps(args: argparse.Namespace) -> int:
    prompts = load_prompts()
    package, run, harness = args.package.resolve(), args.run_dir.resolve(), args.harness_dir.resolve()
    run.mkdir(parents=True, exist_ok=True)
    harness.mkdir(parents=True, exist_ok=True)
    sessions_file = harness / "sessions.json"
    sessions = json.loads(sessions_file.read_text()) if sessions_file.exists() else {}
    for step in args.steps.split(","):
        prompt = render(prompts, step, package, run)
        (harness / "prompts").mkdir(exist_ok=True)
        (harness / "prompts" / f"{step}.txt").write_text(prompt, encoding="utf-8")
        mock_log = harness / "logs" / "mock-send-calls.jsonl"
        command = build_command(step, prompt, session_args(prompts, step, sessions), model=args.model,
                                package=package, mock_log=mock_log)
        sessions_file.write_text(json.dumps(sessions, indent=2) + "\n")
        (harness / "logs").mkdir(exist_ok=True)
        if step == "S3b":
            mock_log.touch()
        snapshot(harness / "snapshots" / f"{step}-pre", package, run)
        with open(harness / "logs" / f"{step}.jsonl", "w") as out, open(harness / "logs" / f"{step}.stderr", "w") as err:
            code = subprocess.run(command, cwd=run, stdout=out, stderr=err,
                                  env={**os.environ, **ISOLATION_ENV}).returncode
        snapshot(harness / "snapshots" / f"{step}-post", package, run)
        _, calls, final = tool_calls(harness / "logs" / f"{step}.jsonl")
        (harness / "logs" / f"{step}.result.md").write_text((final or {}).get("result") or "", encoding="utf-8")
        print(json.dumps({"step": step, "exit": code, "tool_calls": len(calls),
                          "cost_usd": (final or {}).get("total_cost_usd"),
                          "is_error": (final or {}).get("is_error")}), flush=True)
    return 0


def summarize(args: argparse.Namespace) -> int:
    init, calls, final = tool_calls(args.log)
    keys = ("session_id", "model", "tools", "mcp_servers", "permissionMode", "claude_code_version", "cwd")
    print("INIT", json.dumps({k: (init or {}).get(k) for k in keys}, ensure_ascii=False))
    for index, call in enumerate(calls, 1):
        result = call["result"] or {}
        print(f"#{index} {call['name']} error={result.get('is_error')}")
        print("  IN :", json.dumps(call["input"], ensure_ascii=False)[: args.width])
        print("  OUT:", (result.get("text") or "<no result>")[: args.width])
    if final:
        print("RESULT", json.dumps({k: final.get(k) for k in ("subtype", "is_error", "num_turns", "total_cost_usd")}))
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    p = sub.add_parser("run")
    p.add_argument("--package", type=Path, required=True, help="Clean checkout of the commit under test")
    p.add_argument("--run-dir", type=Path, required=True, help="Empty workspace outside the package")
    p.add_argument("--harness-dir", type=Path, required=True, help="Where logs and snapshots are kept")
    p.add_argument("--model", required=True)
    p.add_argument("--steps", default="S0,S1,S2,S3,S3b")
    p = sub.add_parser("summarize")
    p.add_argument("log", type=Path)
    p.add_argument("--width", type=int, default=400)
    args = parser.parse_args()
    return run_steps(args) if args.command == "run" else summarize(args)


if __name__ == "__main__":
    raise SystemExit(main())
