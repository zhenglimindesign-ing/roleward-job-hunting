# Context and Onboarding Policy

## First-class inputs

- AI Context Import
- CV / Resume
- professional-profile content when available
- short manual summary as fallback

## First Scan minimum

Only four groups are required:

1. Career Anchor
2. Direction
3. Geography
4. Authorization state

`Not sure` is a valid authorization state. Profile completeness is not a gate.

## Structured Context Review

Group the user's current state into a small number of readable areas, typically:

- Career Background
- Current Direction
- Geography & Mobility
- relevant Preferences / Trade-offs

Expose enough status/provenance to distinguish:

- confirmed current truth
- source-backed/imported claim
- inferred signal
- missing information that needs an answer

Do not require confirmation of every row. Ask only when a missing/conflicting item materially affects the next action.

## Authority

- CV/profile/context imports are Source Material first.
- Explicit user statements/corrections can update Confirmed Truth.
- Preferences inferred from behavior remain Inferred Signals until confirmed.
- Legal/work-authorization truth must come from the user or an authoritative current source appropriate to that fact; never infer it from behavior.

## Evidence wording

Normalizing or translating a career statement must not change the degree of
involvement, ownership, scope, certainty or recency. Keep qualifiers such as
participated in, supported, contributed to, responsible for, exposure to,
independent and prototype; "participated in customer research" must not become
"experience with customer research" or "led customer research", and
"responsible for" must not become "led". Restating saved evidence follows the
same rule.

When the user states career facts in conversation, register the statement with
`context_state.py add-source --quote` in its original language. Attach the exact
supporting excerpt to each consequential evidence item as `source_quote`; the
helper rejects an excerpt that does not appear verbatim in the source. The
Structured Context Review shows that wording beside the normalized statement.
