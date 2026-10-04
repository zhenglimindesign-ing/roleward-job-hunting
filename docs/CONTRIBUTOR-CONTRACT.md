# Public contributor contract

This map summarizes the shipped Roleward contract for contributors. It does not
add a judgment rule or approve an acceptance target. Use the linked public
policies for implementation details and [Alpha status](ALPHA-STATUS.md) for
current evidence limits. If these sources appear to conflict, report the
conflict before changing behavior. Private roadmap and career data are not
needed to understand or reproduce the public contract.

## Behavior to preserve

| Area | Shipped expectation | Public source |
| --- | --- | --- |
| Routing | Use the smallest relevant workflow; a supplied JD can enter Pursuit directly | [SKILL](../SKILL.md) |
| Career evidence | Source material, confirmed user truth and inference remain distinct; existing context precedes consequential questions | [Context](../references/context-policy.md) |
| Discovery | Confirmed hard constraints hold; a small shortlist or zero is valid; never widen scope to fill a quota | [Search](../references/search-policy.md) |
| Pursuit | Recommend Pursue / Verify first / Pass; a score does not mechanically decide; unknown is not negative evidence | [Pursuit](../references/pursuit-policy.md), [scores](../references/score-policy.md) |
| Verification | A Verify first plan needs an actionable, material pre-application check; interview-only checks belong during the process | [Pursuit](../references/pursuit-policy.md) |
| Positioning | Preserve explicit user review before outward application artifacts | [Positioning](../references/positioning-policy.md) |
| Resume | Preserve consequential facts and strongest relevant proof; separate independent work from employment/production; bind output to current reviewed inputs | [Resume](../references/resume-policy.md) |
| Continuity | User decisions stay separate from system recommendations; snapshots and history remain bound to their actual sources; verify saves | [State](../references/state-policy.md), [schema](../schemas/roleward-state-v0.schema.json) |
| Learning | One rejection is an observation; its cause may be unknown; inferred preferences need confirmation before becoming persistent truth | [Learn](../references/learn-policy.md) |
| Tools and action | State capability limits truthfully; no automatic application submission or professional message sending | [Tool boundary](../references/tool-boundary.md), [SKILL](../SKILL.md) |

The sources above describe existing expectations. An observed failure is useful
evidence; this table is not a claim that every model run satisfies them.

## Validation by change

| Change | Minimum useful evidence |
| --- | --- |
| Documentation or translation | Check links and code/path references; keep supported scope, approval meaning and English/Chinese claims aligned |
| Deterministic helper | Reproduce the bug, run the affected smoke check, and cover the meaningful invariant; reuse unchanged evidence |
| Resume path | Inspect actual affected DOCX/PDF outputs plus source/positioning fidelity; file existence and fact IDs do not establish semantic truth |
| Skill instruction or decision policy | Show the motivating case and affected tradeoff; obtain product approval for changed semantics; validate meaningful behavior with label-separated inputs when needed |
| Host, installation or update | Exercise the real path on that host and preserve private state; format compatibility alone does not prove support |
| Fixture or evaluation tooling | Distinguish structural checks, executable controls and independent model output; preserve case versions and historical results |

Python 3.11+ and PyYAML 6.0.3 are used for package validation:

```sh
python -B scripts/validate_skill.py
```

Select affected checks from [the existing CI workflow](../.github/workflows/skill-checks.yml).
Resume export checks additionally need the [optional runtime](RESUME-RUNTIME.md).
The [fixture guide](../fixtures/README.md) explains label separation, immutable
generated output and the limits of automated scoring. Run the complete existing
suite when the change affects multiple workflow boundaries; a docs-only change
does not need a new semantic run.

## Changes that need an explicit owner decision

New workflows or integrations, score interpretation, hard constraints,
Pursuit/verification semantics, persisted state contracts, external action,
accepted labels or thresholds, and supported-host/release claims need a scope
discussion before implementation. A contributor's proposed expectation does
not automatically change any of them. Preserve the current HOLD and other open
gates until the product owner explicitly disposes of them.

Public contribution review can use these public sources. Maintainers reconcile
accepted changes with private product records; contributors are not required
to access or publish those records. See [contribution guide](../CONTRIBUTING.md).
