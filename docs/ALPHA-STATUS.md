# Alpha status

As of 2026-10-02, this **Alpha implementation** combines the previously verified
local integrity fixes with the public conversation and bilingual updates.
This integration does not declare semantic acceptance or create a formal
versioned release.

## First Alpha scope

Codex with local files: Understand Me, manual Precision Scan or a supplied JD,
Pursuit, a reviewed Positioning Brief, requested application materials, and
Track/Learn. Use the dedicated repository workspace described in
[Getting Started](GETTING-STARTED.md).

Manual review of consequential personal facts and positioning remains part of
the workflow. Applications and professional messages require the user's action.
Scheduled scanning, backend synchronization, hiring-probability predictions and
an automatic user-level installation/update flow are outside this Alpha scope.

## What the technical checks establish

The bootstrap commands in the [README](../README.md#for-contributors-and-builders)
check package structure, local state helpers and synthetic fixtures.
`smoke_journey.py` exercises the complete deterministic CLI lifecycle in separate
processes and an isolated workspace. It simulates user approval and outcomes.

The application regressions cover immutable input snapshots, job-source changes,
review gates and saved-file hashes. The scan regressions cover deduplication,
live-link status handling and preservation of excluded discovery observations.
Evidence-ID validation verifies references, not whether a model's prose is true.
These checks do not establish live search quality or personal usefulness.

## Remaining acceptance gates

| Gate | Current evidence | Next step |
| --- | --- | --- |
| Pursuit recommendation stability | Held: a controlled repeat missed the existing real-case threshold | Resolve remote-country uncertainty and combined core-experience gaps, then freeze any policy revision before a new independent evaluation |
| Score interpretation | Arithmetic replays; requirement grouping and ratings can change scores by 10–20 points | Review grouping/rating anchors; keep scores secondary and avoid probability claims |
| Personal use and useful materials | One personal workflow has reached reviewed positioning and prepared resume files; synthetic helpers also cover persistence | Gather broader user feedback; prepared files do not prove an application was submitted or that hiring outcomes improved |
| Live Search precision | Personal live scans have occurred; aggregate worth-review precision has not been established | Evaluate a bounded scan before claiming measured discovery quality |
| Codex installation and updates | The prior local package was discovered and updated, with private-data preservation checked; this combined package has not replaced it | Reuse prior evidence and check release-specific changes; do not claim a universal one-step installer |
| Other runtime environments | No second-environment acceptance is established | Validate an environment before advertising support for it |
| Publication | Public Alpha implementation; license still TBD | Confirm the exact branch/commit before sharing; an Alpha announcement does not certify the formal semantic gates |

The earlier recommendation to accept Pursuit with residuals predates the
controlled repeat. It must not be read as current acceptance. Frozen benchmark
labels and historical outputs remain unchanged; passing deterministic tests does
not remove the semantic hold.

## Feedback

Report problems in [GitHub Issues](https://github.com/zhenglimindesign-ing/roleward-job-hunting/issues).
Share a sanitized request, expected result, actual result and version when
available. Do not include resumes, private career details or saved state.
