# Score Policy

Scores are assessment signals, not real-world outcome probabilities. Display in the nearest 5-point increment.

Use `scripts/opportunity_state.py` for the display rounding as well as arithmetic.
Its exact halfway values use ties to even: 62.5 displays as 60, and 82.5 as 80.
Retain unrounded components when calculating Overall Match.

## Capability Match

Question: How completely does demonstrated evidence cover the material capability/scope requirements of the exact role?

Requirement materiality weights:

- Core / required: 3
- Important / strongly preferred: 1
- Bonus / optional: 0.25

Coverage values:

- Met: 1.0
- Partial: 0.5
- Missing: 0
- Unscored: excluded from capability denominator

Formula:

`sum(materiality_weight * coverage_value) / sum(materiality_weight) * 100`

Only capability-assessable requirements participate.

Split the JD into atomic requirements before scoring. Declared exposure does
not establish depth, ownership, tenure, or seniority. Do not mark an entire
compound requirement Met when only part is supported. Missing job facts are
not candidate gaps; hard eligibility belongs to Employability.

Match the requirement's verb and scope. When the JD asks the candidate to own,
lead, conduct, define or deliver work, evidence of participation, support,
contribution or exposure is Partial unless it shows the candidate did that
work. Read the evidence's `source_quote`, when present, rather than only its
normalized statement.

Take materiality from the JD's own wording. Required, must-have and minimum
items are Core. Strongly preferred items are Important. Preferred, nice-to-have,
plus or bonus items are Bonus, including a preference related to a main
responsibility: score that responsibility as its own requirement instead of
raising the preference's weight. A JD stating that a preferred item is not
mandatory confirms Bonus.

## Direction Alignment

Internal component. Measures alignment with the user's confirmed current search/career direction. It excludes employability and longer-term career value.

## Overall Match

`70% Capability Match + 30% Direction Alignment`

Orientation only. Does not mechanically determine Pursuit.

## Screening Legibility

Question: How easily can a recruiter understand a credible reason to screen this candidate using real evidence and reasonable truthful positioning?

Evaluate inherent truthful hire-case legibility after reasonable tailoring, not the accidental wording/layout quality of an untailored base CV.

Four 0–4 dimensions:

1. Direct professional evidence: 0 no credible core hire case; 1 remote
   adjacency; 2 meaningful adjacent professional evidence; 3 strong direct
   continuity; 4 obvious direct continuity.
2. Role/seniority continuity: 0 structural mismatch/reset; 1 several inferential
   jumps; 2 one meaningful jump; 3 mostly legible continuity; 4 immediately legible.
3. Domain/product-surface continuity: 0 missing core domain/surface; 1 weak
   analogy; 2 credible adjacent transfer; 3 strong continuity; 4 direct match.
4. Inference burden / credibility gaps: 0 unsupported equivalence; 1 several
   major gaps; 2 one major or several moderate gaps; 3 limited manageable gaps;
   4 no meaningful inferential leap.

Convert the 16-point total to 0–100, then display nearest 5.

## Career Value

Question: If obtained, how valuable is this role for the direction the user is trying to build over the next several years?

Four 0–4 dimensions:

1. Direction gain
2. Capability/ownership compounding
3. Market signal / future legibility
4. Optionality vs reset cost

Convert to 0–100, then display nearest 5. Prestige alone cannot drive a high score.

Retain the atomic requirement ratings, Direction input, and four component
ratings for Screening Legibility and Career Value in evaluation/state records.
Keep brief evidence-based explanations alongside evaluation results.
Use `scripts/opportunity_state.py`
for arithmetic. These details are progressive disclosure, not extra default
user-facing scores. Displayed totals alone cannot explain repeat-score drift.

## Employability

Categorical, evidence-backed. Working states:

- Eligible now
- Role-level sponsorship/international hiring confirmed
- Employer-level evidence only / verify role
- Eligibility unclear
- Ineligible now
- Structural blocker

## Evidence Confidence

Categorical: High / Medium / Low. Reflects source reliability, data sufficiency, and unresolved inputs, not match quality.

## Deferred

Screening Call Probability is unavailable until calibrated on sufficient comparable outcomes.
