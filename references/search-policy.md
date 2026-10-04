# Precision Scan Policy

## Goal

Return a deliberately small set of opportunities genuinely worth the user's review time. Zero results is valid.

## Visible defaults and conversational changes

The existing helper default is **at most 5 results per Scan**, not a target to
fill. Use a saved `search_policy.max_results` when present. Explain the effective
limit, confirmed geography/remote scope and target direction at first Scan and
when they change. Label defaults as defaults, not as confirmed user preferences.
With sufficient context, proceed without requesting approval of every setting.
Manual Scan is the default; do not imply automatic scheduled searches exist.

Accept requests such as "以后每次最多给我 3 个" directly. Persist an explicit
ongoing change through `scripts/context_state.py confirm-field` using
`--field search_policy.max_results --value-json 3`, then reload the same state
and check the effective plan. Keep helper commands internal to the Skill.
Validate that the count is a positive integer before saving. For a one-off
request such as "这次只看 1 个", use `scripts/scan_state.py start --max-results 1`;
this changes only that Scan's plan and preserves the saved preference. If a
requested change is ambiguous in a way that matters, ask only for that missing
detail.

When asked about settings, summarize the effective values and their authority
in plain language. Preserve confirmed hard constraints and previous Scan plans.
Increasing the result limit never relaxes quality or eligibility requirements.

## Discovery

Use both title-led and capability-led / title-agnostic discovery.

Every Scan plan should cover three distinct intents:

- **direct product titles** — explicit target roles and reasonable title families;
- **capability semantics** — search the work itself (for example AI backlog ownership, evaluation/guardrails, agentic workflow, regulated decisioning) even when the title is not a PM title;
- **adjacent role shapes** — only role shapes plausibly allowed by confirmed direction/trade-offs, such as selective deployment, enablement, or engagement roles when they could create relevant career capital.

Adjacent-role expansion is a recall mechanism, not permission to dilute the shortlist. Wrong-function results must still be filtered or ranked out when they conflict with confirmed direction.

Search only within confirmed geography/remote boundaries. Derived passes may expand query wording, sources, and job-title families, but may not silently expand a hard user boundary.

A confirmed `geography` value with `mode: global_excluding` is an exclusion
scope, not a country allowlist. Its `excluded_countries` are hard exclusions;
`preferred_countries` guide priority. The Scan helper preserves this structure
and allows other non-excluded countries. Unknown locations still need checking.
Do not stringify this object or promote a source-only scope into a hard rule.

## Actionability

Before treating a role as actionable where tools permit:

- verify a current/live canonical source or application path;
- deduplicate reposts / duplicate identities;
- separate role quality from employability/accessibility;
- resolve decision-changing unknowns when current research can do so.

## Reservoir

Keep a persistent Opportunity reservoir so a strong still-live role is not forgotten merely because it is no longer newly posted.

## User result

Lead with the small result set. Search coverage, dedupe details, filter diagnostics, and query plans are builder/eval or progressive-disclosure material, not default user output.

## Persisted shortlist

Record source verification status on each discovery observation. Keep all
observations in the reservoir, but select each logical Opportunity at most once
before applying the result cap. The latest observation in the Scan controls
selection. Only `verified_live` sources enter actionable results; closed or
unverified sources remain available for inspection or a later verification pass.
A legacy in-progress observation without verification status needs rechecking
before selection. This source gate does not convert unknown sponsorship into
confirmed ineligibility.
