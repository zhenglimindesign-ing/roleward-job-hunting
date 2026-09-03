# Score Policy

Scores are assessment signals, not real-world outcome probabilities. Display in the nearest 5-point increment.

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

## Direction Alignment

Internal component. Measures alignment with the user's confirmed current search/career direction. It excludes employability and longer-term career value.

## Overall Match

`70% Capability Match + 30% Direction Alignment`

Orientation only. Does not mechanically determine Pursuit.

## Screening Legibility

Question: How easily can a recruiter understand a credible reason to screen this candidate using real evidence and reasonable truthful positioning?

Evaluate inherent truthful hire-case legibility after reasonable tailoring, not the accidental wording/layout quality of an untailored base CV.

Four 0–4 dimensions:

1. Direct professional evidence
2. Role/seniority continuity
3. Domain/product-surface continuity
4. Inference burden / credibility gaps

Convert the 16-point total to 0–100, then display nearest 5.

## Career Value

Question: If obtained, how valuable is this role for the direction the user is trying to build over the next several years?

Four 0–4 dimensions:

1. Direction gain
2. Capability/ownership compounding
3. Market signal / future legibility
4. Optionality vs reset cost

Convert to 0–100, then display nearest 5. Prestige alone cannot drive a high score.

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
