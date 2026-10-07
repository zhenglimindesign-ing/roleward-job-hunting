# Eval Fixtures

Public repository fixtures must be synthetic or de-identified unless a specific real source is explicitly authorized for publication.

## Public portable layer

`portable/profile-set-v1.json` is the current five-profile, ten-job synthetic
set. `portable/profile-set-v0.json` remains the unchanged historical freeze.
Both cover:

- direct enterprise-AI match;
- career transition with independent AI evidence;
- sponsorship-dependent candidate;
- senior candidate facing scope reset;
- sparse/uncertain context.

These cases freeze expected Pursuit/edge semantics so the Skill cannot be tuned only to the design user's background. Model/host-backed execution is added separately from deterministic fixture validation.

The PM-approved v1 revision (2026-09-06) adds explicit role-level visa/work-permit
sponsorship to P2-J1. Its Pursue label is unchanged: this case tests the career
transition bridge without conflating an unknown sponsorship condition.
P3-J2 still tests employer-only evidence and role-level sponsorship verification.
All candidate facts, case identities, other job inputs, and expected labels are
unchanged. The version metadata records the parent ID and SHA-256.

Use v1 for new runs and pass `--fixture fixtures/portable/profile-set-v0.json`
from the repository root only when preparing a historical v0 run. Never compare
the changed P2-J1 input as an identical-input repeat.
The fixture runner checks both versioned sets structurally; that is not twenty
independent jobs or two model executions.

### Prepare and evaluate portable host runs

The fixture contains answer labels and stress annotations. A session that has
read it cannot generate independent blind acceptance evidence for these jobs.
Prepare inputs with an explicit evidence allowlist:

```bash
mkdir -p work/portable-run
python3 scripts/pursuit_eval.py prepare-portable \
  --fixture fixtures/portable/profile-set-v1.json \
  --out work/portable-run/inputs.json
```

The command exports all five profiles and ten jobs without `expected_pursuit`,
`stress`, or fixture expectations. It refuses to overwrite an existing file.
Copy only the exported inputs and the Skill/runtime files needed for generation
into a fresh isolated host workspace; exclude this fixtures directory, labels,
prior outputs, and scoring reports. Label removal from a file does not clear
labels already seen by a running session. Record the input and Skill hashes and
actual host/runtime metadata; do not infer the effective model from defaults.

Have the host assess each `case_id` once using only supplied candidate/job
evidence. Unknown job details remain unknown. For historical benchmarks, retain
the decision-time scope. Return a JSON object with `run` metadata (`variant`,
`run_id`, `model_or_host`, `created_at`) and a `cases` array. Each case contains:

- `case_id`, `recommendation` (`pursue`, `verify_first`, or `pass`);
- `overall_match`, `capability_match`, `screening_legibility`, `career_value`
  as numeric 0–100 values in 5-point increments;
- non-empty `employability` and `core_hiring_reason` text;
- `evidence_confidence` (`high`, `medium`, or `low`);
- string arrays `major_support`, `major_gaps`, `decision_unknowns`;
- `verification_plan`, an array of `{target, method, when}` objects, with
  `when` equal to `before_application` or `during_process`.

Retain score inputs and rationale separately for arithmetic/drift review; these
are not validated by the output scorer. Preserve the generated file unchanged.
Only after generation, score in the evaluation workspace:

```bash
python3 scripts/pursuit_eval.py evaluate \
  --labels fixtures/portable/profile-set-v1.json \
  --outputs work/portable-run/outputs.json
```

The same scorer accepts private frozen labels shaped as a `cases` array of
`{case_id, pursuit_label}` objects, without copying them into the public package.
Missing cases stay in the agreement denominator; duplicate or unexpected cases,
invalid score increments, missing required fields, and invalid verification
timing fail automated acceptance. Exit status is nonzero on validation failure
or agreement below 85%. Numeric agreement and structural validity are reported
separately. Even a passing automated gate requires semantic review of factual
grounding, materiality, and whether verification methods are actually feasible.

Before comparing repeat runs, verify candidate inputs, each job input, Skill
content, and known runtime settings. Exclude changed-input cases from unchanged
input stability metrics. A label-aware test or handcrafted expected-output
control verifies tooling only; it is not a blind run, baseline comparison, or
evidence that the Skill improved.

## Issue #16 behavior regression

`_inputs/residual-observations-v0.json` contains new synthetic, label-free
requests for the four execution residuals. In a fresh host workspace, substitute
one absolute, non-default `{state_path}` outside the Skill package. Run the
`import` request once, then the `scan` request in a fresh process using the same
workspace. Start helpers from a different directory containing a valid decoy
default state. Keep inputs, actual user-facing messages, helper argv and state
readback; do not rescue an interrupted import or rerun to obtain a pass.

Review separately after generation: the participation qualifier must cover
both research and metric iteration in saved evidence and replies; all reply
prose, progress/receipts and table labels must be Chinese (original JD quotes
and canonical terms added once are allowed); the authorized import must save
without a second permission question; every helper must explicitly reuse the
same absolute state path and leave the decoy unchanged. Ownership-type research
and metrics requirements remain Partial unless other evidence establishes the
work. Do not assert Important versus Bonus for the production-AI preference:
that is the pending policy decision in #16.

`smoke_search_settings.py` exercises the cross-directory path/readback invariant
in CI. It verifies helpers, not model argv choices. The other three checks need
actual host outputs and semantic review; deterministic CI does not prove them
or establish Claude Code support. The motivating observations and prior runs
remain unchanged.

## Private real layer

The accepted Alpha benchmark also requires, in the private Roleward repository:

- 12–15 real/de-identified Opportunity cases;
- 3 frozen Search pools;
- Positioning/Application labels derived from Pursue cases;
- Learn sequences, repeat-stability and baseline comparisons.

Private real-user benchmark material must not be copied into this public repo.

## Resume acceptance extension

`resume/acceptance-set-v0.json` adds five invented candidate/job requests to the
existing Alpha eval runner. Inputs under `_inputs/resume/` include source text,
baseline IR and explicitly simulated reviewed Positioning/state. They cover
direct fit, transition, older strongest proof, a production credibility gap and
an already-strong baseline. Do not treat simulated approval as real user review.

The normal runner checks fixture structure; it does not generate tailored content
or judge quality. Use an isolated generation context with only raw inputs and the
frozen Skill. Review the actual Base/Tailored files separately, including the
pairwise submission question. `scripts/resume_eval.py` summarizes a complete
review while retaining reviewer type and the proposed criterion's PM-pending
status. Semantic failures cannot be cleared by passing `smoke_resume.py`.
