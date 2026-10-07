# State and History Policy

Schema id: `roleward.job-hunting.state.v0`.

## Core logical objects

- Source Material
- Career Evidence
- Current Direction
- Search Policy
- Constraints & Preferences
- Decision Observations / Inferred Signals
- Opportunity
- Opportunity Source Snapshot
- Pursuit Assessment
- Pursuit Decision
- Positioning Revision
- Application Artifact Revision
- Application & Outcome
- Learned Signal

## Invariants

1. Current state may be superseded; history is not rewritten.
2. User-owned truth, source evidence, inference, and learned signals remain distinct.
3. One Opportunity spans discovery through outcome.
4. Provenance travels with claims and generated artifacts.
5. Unknown is a valid state.
6. Consequential conflicts are surfaced, not silently resolved.

## Update rules

### Workspace, continuity and visible receipts

Resolve one absolute state path for the current job-search workspace and reuse it
across helper calls (`--path` for `state_store.py`, `--state` for workflow helpers).
Pass it explicitly even when the working directory currently makes the CLI
default point to that file. Use it for Scan start/log/ingest/finalize and all
readback calls too; a working-directory change must not select another history.
The default is `state/roleward-state.json` inside that workspace, not inside the
shared installed Skill package. Check the established workspace before creating
an empty state. If the user expects existing history and its location cannot be
resolved from available context, ask for the workspace; do not claim it is empty.

For a genuinely new workspace, `state_store.py show` returns `state_missing`
with exit code 2 and does not create a file. After checking the workspace and
establishing that this is a new history, use `state_store.py init`, then reload
it. Never treat an invalid or inaccessible existing file as a missing history.
Ordinary users ask in natural language; the host operates these helpers.

Extraction and assessment JSON use the public contracts in `context_state.py`
and `opportunity_state.py`, with the state shape in
`schemas/roleward-state-v0.schema.json`. Read those contracts when preparing a
payload; CLI flag help alone does not define their fields. Do not infer field
names or require the user to construct JSON.

At first use or on request, explain briefly: explicit reports of applications
and outcomes are saved locally; continuity requires access to the same state;
external job sites and inboxes are not automatically synchronized. Give the
resolved location when explaining storage. A new conversation can reuse this
record, but it does not inherit the full conversation or imply cloud backup.

For each meaningful write:

1. Resolve the exact opportunity/field and the user's intent before writing.
   A clear report of an action already taken is enough to record it. An intention
   to apply, approval of positioning or a completed CV is not an application.
2. Use the existing helper, check success, reload the same file and verify the
   relevant field or event. Return a concise receipt only for verified writes,
   for example "已记录：A 公司的产品经理岗位已投递。" Do not dump IDs or JSON.
3. If saving or readback fails, say the change has not been verified as saved;
   retain the update in the current conversation, identify the blocker and
   retry only after checking current state. Do not create a duplicate event
   merely because a previous write's result was uncertain.

Before repeating an identical status report, inspect the existing current status
and history; acknowledge an already-recorded event instead of appending it again.
For a correction, preserve earlier history and append the corrected current
status. Helper `created_at` timestamps are recording times, not evidence of the
actual application/interview date.

For "查看投递记录" or a return to the workflow, read the saved state and show
company, role, current status and relevant recorded progress in plain language.
Distinguish reviewed opportunities from submitted applications. Derive the next
step from actual decisions, positioning reviews and artifacts; do not guess
missing approvals, reasons, dates or external results. If persistence is
unavailable, clearly scope continuity to the current conversation.

### Explicit user correction

Update current user-owned state immediately when clear. Preserve the previous state when it explains prior outputs.

### New CV / AI Context / profile import

Diff against existing state. Do not blanket overwrite. Consequential contradictions require review.

### Job source change

Preserve immutable source observations. A materially changed posting becomes a new current snapshot and may mark existing assessments/materials stale.

### Generated analysis/materials

Create revisions. Never rewrite historical output in place when provenance matters.

### Time-sensitive facts

Revalidate only when plausibly stale and consequential. Never expire a value into `false`.
