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
