# Health check, 2026-10-25

Bounded behavior evaluation of the released Skill plus a repository code and
security review. Commit under test: `f3bccf6` (main, v0.1.0-alpha.3).
This is evidence for one host configuration and a small number of runs. It is
not a support claim and does not change any acceptance gate in
[Alpha status](../ALPHA-STATUS.md).

**Status: partial.** The run was cut short by the weekly usage limit. Done:
Sonnet 5.5, two runs of each chain (one Scan step blocked by the limit); manual
code and security review of all helper scripts. Not done: the third Sonnet 5.5
run, every Opus 5.5 run, and the `code-review` / `security-review` skill passes
(see [Not done](#not-done)).

## Setup

| Item | Value |
| --- | --- |
| Host | Claude Code 2.1.308 (the build bundled with the Claude desktop app), headless `claude -p` via [`host_smoke.py`](../../scripts/host_smoke.py) |
| Model | `claude-sonnet-5-5` (reported by each session's init event) |
| Isolation | project settings only, auto memory off, strict MCP, `--permission-mode dontAsk`, tools `Bash,Read,Write,Edit,Glob,Grep,WebSearch,WebFetch` |
| Package | sparse clone of `f3bccf6` without `fixtures/`, `docs/HOST-SMOKE.md`, `scripts/host_smoke*.py`, `scripts/smoke_*.py` |
| Environment | the operator's environment was inherited (see finding S1). A control prompt in English got English replies both with this environment and with a stripped one, so the language results below are not caused by it. |
| Runs | 2026-10-25 12:23–12:29 +04; 13 graded steps, 1 blocked; total reported cost USD 3.21 |

Chains (each run is a fresh workspace):

- **zh** — the frozen [host-smoke-v1](../../fixtures/_inputs/host-smoke/prompts-v1.json)
  S0 import → S1 direct JD → S2 new session, continuity + live UAE Scan (bounded to 3 queries / 3 sources / 1 result).
- **en** — new [English rendering](../../fixtures/_inputs/host-smoke/prompts-v1-en.json)
  of S0 and S1 with the same facts and JD, to test that replies follow an English-writing user.
- **r16** — the issue #16 regression inputs ([residual-observations-v0](../../fixtures/_inputs/residual-observations-v0.json),
  [host rendering](../../fixtures/_inputs/host-smoke/residual-16-v0.json)): import to a
  non-default path with a valid decoy default state in the working directory, then an
  offline two-job screen in a new session.

Grading: [`host_smoke_grade.py`](../../scripts/host_smoke_grade.py) applies 36
deterministic checks to the logs and state snapshots and writes a skill-creator
workspace (`grading.json` per run, `benchmark.json`, static review page). The
reviewer then read every reply and the relevant tool calls; judgments that the
script cannot make are stated as such below. Raw logs, snapshots and the review
page are kept locally under the Git-ignored `work/health-check/` of the
evaluation checkout and are not published (they contain operator environment
values, see S1).

## Results by focus area

Pass rate over all checks: **93% ± 5%** (13 step runs). Per case:

| Case | run-1 | run-2 |
| --- | --- | --- |
| zh S0 import | 10/11 | 11/11 |
| zh S1 direct JD → Pursuit | 13/14 | 13/14 |
| zh S2 continuity + Scan | 13/14 | blocked (usage limit) |
| en S0 import | 10/11 | 11/11 |
| en S1 direct JD → Pursuit | 13/14 | 14/14 |
| r16 import (non-default path, decoy) | 10/12 | 11/12 |
| r16 offline screen + assessment | 14/15 | 13/15 |

### 1. Wording and qualifiers — held in every run

All 6 import runs kept the involvement level in saved evidence and replies:

- `参与过客户调研与产品指标迭代` → "Participated in customer research and
  product-metric iteration" (zh, r16); "Was involved in customer research and
  product-metric iteration" (en). No run split the clause or used a stronger verb.
- `负责` / "responsible for" stayed "Responsible for"; never "led" or "owned".
- The LLM prototype stayed "independently built … no formal production AI product experience".
- Every evidence item carried a verbatim `source_quote`; no preference was invented.
- In all 6 Pursuit assessments, "conduct customer research" and "define
  (evaluation) metrics" were rated Partial, never Met, and the "preferred, not
  mandatory" production-AI item was weighted Bonus (the #19 rule).

### 2. Score and recommendation consistency — arithmetic stable, recommendation not

Saved scores reproduced with the helper in all runs. Displayed scores matched
the saved values. Recommendations and scores for the **same facts and JD**:

| Chain | Recommendation | Overall | Capability | Screening | Career value |
| --- | --- | --- | --- | --- | --- |
| zh S1 run-1 | Pursue | 85 | 80 | 75 | 80 |
| zh S1 run-2 | Pursue | 90 | 85 | 80 | 80 |
| en S1 run-1 | Verify first | 80 | 75 | 75 | 75 |
| en S1 run-2 | Verify first | 80 | 80 | 75 | 80 |
| r16 R2 run-1 | Pursue | 65 | 50 | 50 | 75 |
| r16 R2 run-2 | Verify first | 60 | 50 | 50 | 70 |

- The Pursue/Verify first split is the timing boundary already recorded in
  Alpha status: whether the user's own "Not sure" work authorization and unknown
  sponsorship justify a pre-application check. The Chinese runs put it during
  the process; the English runs made it a pre-application gate. Two runs per
  language cannot show whether the language matters.
- Drift comes from requirement grouping and coverage, not arithmetic. Example:
  "own enterprise payment API / onboarding / compliance approvals" was Met in
  zh (from "负责") and Partial in en run-1 (from "responsible for"), and "define
  evaluation metrics" was Core in some runs and Important in others.

### 3. Reply language — two problems

- **English users received Chinese replies (new).** en run-1 answered both S0 and
  S1 in Chinese, including the sentence "你用英文写的,所以我用英文回复。" ("You
  wrote in English, so I reply in English"), with Chinese table headings. en run-2
  was entirely English. The control prompt without the Skill answered in English,
  so the likely cause is the Skill text: the only concrete language example in
  `SKILL.md` is the Chinese receipt `"已保存并核对。" rather than "State persisted
  and verified."`. This is a hypothesis; it has not been tested with a revised
  example.
- **English progress notes in Chinese runs (issue #16 item 3, still present).**
  7 of 9 Chinese-language step runs had English notes between tool calls, for
  example "Now read back from disk." and "Let me start by reading the skill
  package's rules." Final Chinese replies were Chinese except one English line
  in r16 run-1 ("Readback matches and the file validates.").

### 4. Scan record completeness — one failure, partly a helper problem

zh S2 run-1 logged exactly 3 queries and 3 opened sources before running them
(matching the 3 WebSearch and 3 WebFetch calls), covered all three intents,
stayed in the UAE, passed the one-off bounds without changing the saved
preference and reported counts from `search_summary`. Zero results was
returned honestly (no source verified live). But **no discovery observation
was saved**: its `ingest` payload was a bare list instead of `{"candidates": [...]}`,
the helper failed with a `KeyError` traceback, and `finalize` in the same shell
command still ran, so the completed Scan could no longer take observations. The
reply disclosed this. The ingest payload shape is documented nowhere except the
code (`state-policy.md` names only the extraction and assessment contracts).
Fixed in this branch (C2). The second Scan run was blocked by the usage limit.

### 5. State path, continuity and boundaries — held

Every state-touching helper call in all 13 runs passed an explicit absolute
path; r16 runs used the requested non-default path and left the decoy default
state byte-identical. S2 restated the saved profile and the earlier assessment
from disk without re-initializing, and did not call the assessed role applied.
No run recorded a user decision or application, modified the package, or asked
for an extra confirmation before an authorized save. S3/S3b (external action)
were not run in this round.

## Code review

Manual review of all helper and evaluation scripts (`scripts/*.py`), schema and
CI. Deterministic suite: all 15 CI checks pass locally (Python 3.13.9, pinned
resume runtime), before and after the fixes.

| ID | Finding | Evidence | Disposition |
| --- | --- | --- | --- |
| C1 | `learn_state.confirm_preference` appends a second confirmed preference when the same signal is confirmed again | repro: two calls → 2 preferences | **Fixed**; `smoke_learn.py` asserts idempotency |
| C2 | `scan_state.py ingest` crashes with `KeyError` on a payload without `candidates`; the shape is undocumented | zh S2 run-1 lost all observations | **Fixed**: exit 2 with the expected shape, nothing saved; shape in `ingest --help`; `smoke_search_settings.py` covers it |
| C3 | `hard_constraint_check` matches geography names exactly: with saved scope `UAE`, a job in `Dubai`, `Dubai, UAE` or `United Arab Emirates` is a hard violation and is screened out | repro in report session | **Partly fixed**: `ingest --help` now says to use the saved names. A normalization or alias rule is an owner decision (hard-constraint semantics) |
| C4 | Learned-signal strength counts outcomes, not independent opportunities: two confirmed reasons on one opportunity make an `emerging_pattern` | repro: one opportunity, two outcomes | Owner decision; learn-policy requires repeated *independent* observations |
| C5 | Chinese resumes cannot be exported: the bundled/selected fonts (Arial, Noto Sans Latin) have no CJK glyphs; the export check then fails with the generic "An exported file lost intended Resume content" | rendered PDF text extracts as `\x00` | Owner decision (bundle a CJK font and its licence, or document the limit) |
| C6 | Opportunity identity uses the URL when present, else company+title, so a role first seen as a pasted JD and later via a Scan URL gets two Opportunities | code reading | Report only |
| C7 | A source snapshot's digest ignores `live_status` and location, so re-observing the same text with a new live status keeps the old snapshot status (discovery observations do record it) | code reading | Report only |
| C8 | `opportunity_state` accepts any `employability` / `evidence_confidence` string and `True` as a 0–4 dimension; `resume_ir.normalized_match_key` is unused and ASCII-only | code reading | Report only (low) |

## Security and personal-data review

| ID | Finding | Disposition |
| --- | --- | --- |
| S1 | `host_smoke.py` passed the operator's whole environment to the session under test, whose S0 prompt asks it to record its environment; logs keep tool results. In en run-2 the model ran an environment listing and the local log captured the operator's account e-mail, account UUID and parent-session variables. | **Fixed**: the session now gets an allowlist (`HOME`, `PATH`, locale, shell basics and CLI auth variables). Affected logs stay in the Git-ignored local `work/`; do not publish them. |
| S2 | State writes use `mkstemp` + `os.replace`, so the state file is mode 0600. Resume exports, the export manifest and extracted sources are written with the default umask (typically 0644). | Report only (local multi-user exposure) |
| S3 | Renderers escape all text for ReportLab and limit links to http(s)/mailto; DOCX hyperlinks are external relationships only. No markup or local-file injection path found. | No action |
| S4 | Resume parsing bounds input (4 MB, 20 PDF pages, no table DOCX). | No action |
| S5 | `.gitignore` excludes `state/`, `sources/`, `application-files/`, `work/`, `outputs/`; public fixtures contain only invented candidates (scan for e-mail/phone patterns found only dates and IDs). | No action |
| S6 | CI uses pinned action SHAs, `contents: read` and `persist-credentials: false`. | No action |
| S7 | The host smoke runs the model with `dontAsk` and Bash; it is not sandboxed beyond the run directory convention. | Documented limit; run only with synthetic data on a machine you control |

## Changes in this branch

- `scripts/host_smoke.py`: `--prompts` option; allowlisted session environment (S1).
- `scripts/host_smoke_grade.py`: new deterministic grader for harness directories.
- `fixtures/_inputs/host-smoke/prompts-v1-en.json`, `residual-16-v0.json`: new prompt sets (inputs unchanged in substance).
- `scripts/scan_state.py`: ingest payload validation and documented shape (C2, C3 note).
- `scripts/learn_state.py`: idempotent preference confirmation (C1).
- Tests: `smoke_learn.py`, `smoke_search_settings.py`, `smoke_host_smoke.py`.

`SKILL.md`, policies and scoring rules are unchanged.

## Decisions for the owner

1. **English-language replies (§3).** Replace or pair the Chinese-only receipt
   example in `SKILL.md` with a neutral rule, then rerun en S0/S1 at least three
   times to confirm. This is wording, not policy, but it touches the Skill text.
2. **Geography matching (C3).** Keep exact names (host must normalize, now
   documented) or add country aliases/city containment in the helper.
3. **Learned-signal independence (C4).** Count distinct opportunities, as
   `record_preference_observation` already does?
4. **Chinese resume export (C5).** Bundle a CJK font or document the limit.
5. **Recommendation stability (§2).** Whether the user's own "Not sure"
   authorization is a pre-application check is still judgment-sensitive.

## Not done

- Sonnet 5.5 run-3 of every chain and run-2 of zh S2; all Opus 5.5 runs; S3/S3b.
  Resume them with `scratchpad`-style package clone and
  `python3 scripts/host_smoke.py run … --prompts <set> --steps <steps>`, then
  `python3 scripts/host_smoke_grade.py <harness-root> <workspace>`.
- The `code-review` (high, whole repository) and `security-review` skill passes;
  the tables above are from a manual review.
- The language hypothesis in §3 is untested.
