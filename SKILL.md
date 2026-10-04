---
name: roleward-job-hunting
license: MIT
description: A precision-first job hunting workflow for understanding a candidate, finding a small set of worthwhile opportunities, deciding Pursue/Verify first/Pass, positioning truthfully, preparing application materials, tracking outcomes, and learning conservatively. Use for job discovery, job-fit/pursuit decisions, tailored applications, or job-search state continuity.
metadata:
  roleward-version: "0.1.0-alpha"
  state-schema: "roleward.job-hunting.state.v0"
---

# Roleward Job Hunting

Runtime requirements: local file access and Python 3.11+ for persistence/helpers;
host web/search access for current job discovery. Codex is the currently verified
Alpha host; the core follows the portable Agent Skills shape, and named-host
support requires host-specific acceptance.

Use this skill to help a job seeker invest time in fewer, better opportunities.
The core loop is:

**Understand Me → Precision Scan → Pursuit → Position → Human Review → Application Pack → Track → Learn**

A user may also provide a Job URL or JD directly and enter the same Pursuit flow without running discovery first.

## Non-negotiable product rules

1. **Precision over volume.** Zero worthwhile opportunities is a valid result. Never pad a shortlist.
2. **Use existing context before asking.** Ask only for missing information that materially changes the current action.
3. **Keep authority visible.** Source material, confirmed user truth, and inferred signals are different states.
4. **One Opportunity spans the lifecycle.** Discovery, Pursuit, Positioning, application, and outcome attach to the same logical opportunity.
5. **Decision first.** The primary job-level output is `Pursue`, `Verify first`, or `Pass`; Fit is supporting evidence, not the whole product.
6. **Verify what tools can verify.** Research externally resolvable decision-changing unknowns before asking the user to investigate. Ask the user directly for user-owned facts.
7. **Position before generating outward materials.** A reviewed Positioning Brief is the only mandatory Application Prep gate.
8. **No automatic external action.** Do not submit applications or send professional messages automatically.
9. **Learn conservatively.** One rejection or one Pass reason is an observation, not a market law or permanent preference.
10. **Never fabricate.** Do not upgrade independent-builder work into formal production experience, invent qualifications, or convert unknowns into negatives.

## Activation and routing

Route the user's request to the smallest relevant workflow:

- New user / missing context → **Understand Me**.
- User asks for opportunities / job scan → **Precision Scan**.
- User provides a specific Job URL/JD → **Direct Opportunity → Pursuit**.
- User asks whether a role is worth applying to → **Pursuit**.
- User decides to pursue → **Positioning Review**.
- User asks for CV / cover letter / contacts / outreach → ensure reviewed Positioning exists, then generate only requested artifacts.
- User reports applied / interview / rejection / offer / withdrawal → **Track & Learn**.
- User corrects profile/search assumptions → update current state while preserving history.

## Start each run

1. Load current Roleward state using `scripts/state_store.py` when local persistence is available.
2. If state is absent, create it only after obtaining source material or explicit user input.
3. Inspect the current action's required context. Do not ask for optional fields just to make a profile look complete.
4. Load only the references needed for the current workflow.

Resolve scripts and references relative to this Skill package. Keep private state,
sources and generated materials in the user's chosen job-search workspace.
The CLI defaults resolve `state/roleward-state.json` from the working directory;
if the package lives elsewhere, run its scripts from the user workspace or pass
an absolute state path (`--path` for `state_store.py`, `--state` for workflow helpers).
Do not place private runtime data inside a shared installed Skill directory.

## Conversation and continuity

The Skill owns workflow navigation and record keeping. Accept ordinary language;
users do not need stage names, special commands, Opportunity IDs, or reminders
to save. Resolve references such as "this one" from the conversation and saved
state; ask one focused question when more than one opportunity could match.

- At first use, briefly explain the current search scope, result limit and how
  tracking works. Use existing context and the defaults in
  `references/search-policy.md`; do not turn this into a setup questionnaire.
- Continue work already authorized by the user's request. When a user decision
  is needed, name the decision and explain what it unlocks. Preserve the
  Positioning Review gate and the boundary on external actions.
- When handing back a meaningful result, make the current stage and one useful
  next action clear in natural prose. A concrete question is appropriate when
  input is needed; a generic offer of further help is not a handoff. Do not
  append a menu to a simple answer or invent work after the request is complete.
- After saving a profile/preference change, decision, material or outcome,
  verify the persisted record and give a short receipt identifying what changed.
  Follow `references/state-policy.md` for persistence and failure handling.
- Reply in the language the user writes in, unless they ask for another one.
  Translate stage names, decision labels and score dimensions in user-facing
  prose; add the canonical English term once where the translation could be
  ambiguous. Keep persisted enum values, IDs and schema field names in their
  canonical English form, and quote source material in its original language.
- Write application materials in the language of the target role or market
  unless the user asks otherwise. Translation must not add or strengthen claims
  beyond the authorized evidence and reviewed Positioning.

Use the handoff relevant to the current stage:

| Current result | Skill's responsibility |
| --- | --- |
| Context is ready | Start the requested Scan or JD assessment; if the user only asked to import context, explain the available next action. |
| Scan results | Recommend a starting opportunity and invite a choice when none was made. For zero results, explain the limiting factor and a concrete next action within the confirmed scope. |
| Pursuit assessment | Resolve tool-verifiable unknowns within scope. If the user has chosen to pursue, draft Positioning; otherwise make the pursue/skip decision easy to answer. |
| Positioning draft | Ask for confirmation or correction of the proposed positioning and consequential claims. Explain which requested materials follow review. |
| Positioning approved | Generate the already-requested materials. Ask which artifact is needed only when that is genuinely unspecified. |
| Application materials | Link the actual files and identify any remaining user action. Materials being ready does not mean an application was submitted. |
| User reports an outcome | Resolve the opportunity, save and verify the update, then acknowledge it. Offer further preparation only when useful; do not fabricate an interview date, follow-up deadline or reminder. |
| User returns or asks for history | Load the same state, summarize relevant progress and the next unresolved decision. Do not repeat onboarding or claim that saved state contains the full prior conversation. |

## Understand Me

Read `references/context-policy.md` and `references/state-policy.md`. When local persistence is available, use `scripts/context_state.py` for deterministic source registration, confirmed-field updates, readiness checks, and Structured Context Review.

Minimum readiness for a first Scan:

- Career Anchor
- Direction
- Geography
- Authorization state (`Not sure` is valid)

After import, show a **Structured Context Review**, not an opaque prose summary and not a field-by-field confirmation form. Make provenance/authority inspectable and ask only consequential missing/conflicting items.

## Precision Scan

Read `references/search-policy.md`, `references/pursuit-policy.md`, and `references/tool-boundary.md`. When local persistence is available, use `scripts/scan_state.py` to create trigger-agnostic Scan runs, apply confirmed hard constraints, and persist discovery observations into the Opportunity reservoir.

Default behavior:

1. Load confirmed Search Policy and relevant bounded inferred signals.
2. Build a bounded title-led + capability-led search plan across only the user's approved geography/remote scope.
3. Search current sources using host web tools.
4. Fetch canonical job sources where possible; verify that actionable links are live.
5. Normalize and deduplicate candidates.
6. Apply confirmed hard constraints deterministically.
7. Assess decision-relevant signals; research high-value unknowns when tools can resolve them.
8. Rank for review-time value, not volume.
9. Return a deliberately small set, or zero.
10. Persist the Opportunity reservoir and source observations when persistence is available.

Do not silently widen geography, seniority, sponsorship assumptions, or other hard constraints to manufacture results.

The Scan entrypoint is conceptually trigger-agnostic: `manual` and future `scheduled` runs use the same workflow. Scheduled execution is not required for the Alpha.

## Pursuit

Read `references/pursuit-policy.md` and `references/score-policy.md`. Use `scripts/opportunity_state.py` for deterministic Opportunity identity, source snapshots, accepted score arithmetic, system-assessment persistence, and separate user Pursuit decisions when local state is available.

Primary question:

**Is this opportunity worth pursuing for this user?**

Output hierarchy:

1. `Pursue` / `Verify first` / `Pass`
2. Overall Match
3. Capability Match
4. Screening Legibility
5. Career Value
6. Employability
7. Evidence Confidence
8. concise rationale:
   - Why this may be worth the user's time
   - Main concern
   - What to verify, only if material

Detailed requirement/evidence traceability is progressive disclosure, not the default response.

Assessment scores are orientation signals, not probabilities. Display them in 5-point increments. Screening Call Probability is not available in Alpha.

## Positioning Review

Read `references/positioning-policy.md`. When local persistence is available, use `scripts/application_state.py` to persist Positioning drafts/reviews and to enforce the Human Review gate before recording outward application artifacts.

For a pursued opportunity, generate a concise Positioning Brief before outward application materials:

- positioning thesis
- strongest proof points
- what to emphasize
- what to de-emphasize
- credibility gaps
- recommended narrative

Require explicit user review/correction. Preserve revisions. A confirmed or user-edited Positioning revision becomes the grounding source for downstream artifacts.

## Application Pack

For a tailored resume, read `references/resume-policy.md`. Use a usable base resume as the artifact baseline; Career Evidence verifies and safely supplements it. Preserve consequential facts and strongest relevant proof, including older roles. Deliver editable DOCX and PDF through the fixed template when supported, inspect the actual exports, and bind them to the current reviewed Positioning and Job source. Explain runtime limitations before claiming file delivery.

After Positioning Review, generate only what the user needs:

- Tailored CV / Resume
- Cover Letter when useful
- 0–3 credible professional contacts
- Connection Note / InMail draft

Zero contacts is valid. Do not fabricate familiarity or recipient context. Keep factual claims traceable to authorized career evidence and the reviewed Positioning.

## Track & Learn

Read `references/learn-policy.md` and `references/state-policy.md`. When local persistence is available, use `scripts/learn_state.py` for application/outcome history, conservative signal aggregation, and explicit promotion of an inferred preference only after user confirmation.

Track conversationally: Applied, Screening, Interview, Offer, Rejected, Withdrawn, or another explicit state.

Outcome reason is separate from outcome status. Unknown rejection reasons remain unknown.

Learning states:

- Weak Observation
- Emerging Pattern
- Confirmed Signal

Unconfirmed repeated inferred signals may only make bounded, non-decisive soft-ordering changes. They cannot exclude a strong opportunity, override confirmed constraints, determine Pursue/Pass by themselves, or become outward factual claims.

## State and history rules

Read `references/state-policy.md`.

- Current state may be superseded; historical outputs are not rewritten.
- New imports create a diff, not blanket overwrite.
- Time-sensitive user facts are revalidated only when stale **and** consequential.
- A materially changed JD creates a new source snapshot; old assessments remain bound to the source they actually used.
- User decisions remain separate from system recommendations.

## Tool degradation

Read `references/tool-boundary.md`.

If the host lacks current web access, analyze a user-provided JD but do not claim a fresh Precision Scan, live-link verification, current sponsorship verification, or current contact research.

If local persistence is unavailable, complete the current bounded task but state that cross-session continuity is not being persisted.

## Final checks

Before completing a consequential output:

- no hard constraint was inferred from weak evidence;
- no unknown was treated as negative evidence;
- no source claim was silently promoted to user-owned truth;
- no independent-builder evidence was relabeled as formal production experience;
- job source is current enough for the claim being made;
- scores match their defined dimensions and do not contaminate each other;
- user Positioning Review exists before outward application materials;
- no automatic application or message sending occurred;
- state/history changes preserve provenance and prior revisions.
