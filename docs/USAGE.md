# Roleward Job Hunting Usage Guide

This guide explains what to ask Roleward, what it should return, and how the main workflows connect.

Roleward is not organized around a menu of features. The same persistent career context should support the whole loop:

**Understand Me → Precision Scan → Pursuit → Position → Human Review → Application Pack → Track → Learn**

You can enter that loop at different points depending on what you need now.

## 1. Set up or update my career context

Use when:

- you are starting Roleward for the first time;
- your resume or profile changed;
- your job-search direction changed;
- Roleward is reasoning from a stale or incorrect assumption.

Example:

```text
Here is my resume and a short career note.
Help me set up my Roleward career context.
Use what is already present before asking me questions, and show me the consequential facts and assumptions to review.
```

What to expect:

- a structured Career Anchor rather than a generic biography;
- current Direction;
- Geography / remote scope;
- Authorization state;
- important evidence and gaps;
- consequential conflicts or missing facts only.

Roleward should distinguish sourced facts, user-confirmed truth and inference.

### Update one thing without rebuilding everything

```text
My current direction has changed. I still want senior product roles, but AI is no longer a hard requirement.
Update the confirmed direction without rewriting my career evidence.
```

or:

```text
You inferred that I prefer product ownership over deployment-heavy roles. I have not confirmed that preference.
Remove it as a confirmed preference and keep it only as an unconfirmed hypothesis if there is supporting evidence.
```

## 2. Find worthwhile opportunities — Precision Scan

Use when you want Roleward to discover current opportunities rather than evaluate a job you already found.

Example:

```text
Find a small set of opportunities genuinely worth my attention this week.
Use my confirmed search policy and current geography.
Do not widen constraints or pad the list just to return more jobs.
```

More specific:

```text
Scan for senior AI/product roles in the UAE and the remote EMEA scope we already confirmed.
Search by both titles and relevant capabilities, including adjacent role shapes when the work is genuinely relevant.
Return only the roles worth reviewing.
```

What to expect:

- a deliberately small shortlist, or zero;
- current/canonical job sources when available;
- live-link verification where the host can do it;
- hard constraints applied separately from soft fit;
- adjacent titles only when their actual work is relevant;
- opportunities persisted into the local reservoir when persistence is available.

What not to expect:

- 50 loosely related jobs;
- silent widening from UAE to worldwide;
- assuming an employer sponsors because it is international;
- filling the shortlist with weaker results because the requested count was not reached.

## 3. Evaluate one job — Direct Opportunity / Pursuit

Use when you already have a job URL or JD.

Example:

```text
Should I pursue this role?
<job URL>
```

or:

```text
Evaluate this JD for me and tell me whether it deserves my time.
<pasted JD>
```

The primary output should be one of:

- **Pursue** — worth entering the process;
- **Verify first** — a decision-changing fact can realistically be checked before entering the process;
- **Pass** — not worth pursuing under the current confirmed context.

Supporting signals may include:

- Overall Match;
- Capability Match;
- Screening Legibility;
- Career Value;
- Employability;
- Evidence Confidence.

These are not interview probabilities.

### How to read the dimensions

**Capability Match** asks: can you plausibly do the material work based on demonstrated evidence?

**Screening Legibility** asks: can a recruiter understand a truthful hire case without requiring excessive inference?

**Career Value** asks: if you got the job, would it meaningfully help your current direction, ownership, future market signal or optionality?

**Employability** keeps sponsorship, work authorization, location and other structural access questions separate from fit.

### Verify first should be actionable

Good:

```text
VERIFY FIRST
The role is strong on fit and career value, but role-level UK sponsorship is required and currently unknown.
Check the exact requisition or ask recruiting a specific eligibility question before investing further.
```

Not good:

```text
VERIFY FIRST
Find out whether you would really have product influence after joining.
```

If a question can only be learned through interviews, Roleward should normally say `Pursue` and mark it as **verify during process**, not block the initial decision.

## 4. Compare several opportunities

Use when you already have multiple roles competing for attention.

Example:

```text
Compare these three opportunities using my current Roleward context.
Tell me which ones deserve attention first and why.
Do not rank them only by Overall Match.

<job 1>
<job 2>
<job 3>
```

A useful comparison should distinguish:

- present-day hiring credibility;
- career-direction upside;
- structural accessibility;
- meaningful trade-offs;
- decision-changing unknowns.

A role with a slightly lower score may still deserve more attention if the hire case and career value are stronger.

## 5. Decide how to position myself

Use after Roleward recommends `Pursue`, or when you independently decide to pursue a role.

Example:

```text
I want to pursue this role.
Before rewriting my resume, create the Positioning Brief you recommend.
```

What to expect:

- positioning thesis;
- strongest proof points;
- what to emphasize;
- what to de-emphasize;
- credibility gaps;
- recommended narrative.

This is the only mandatory Application Prep review gate.

### Correct the positioning before generating materials

```text
I agree with the proof points, but I do not want to position myself as an AI-native PM.
Use enterprise product + applied AI transition as the narrative instead.
Update the Positioning Brief before generating anything outward-facing.
```

Roleward should preserve the revised positioning and use that version downstream.

## 6. Prepare application materials

After Positioning Review, ask only for what you need.

### Tailored resume / CV

```text
Use the reviewed Positioning Brief to tailor my resume for this role.
Keep every factual claim grounded in my confirmed career evidence.
Do not exaggerate independent AI work into formal production experience.
```

### Cover letter

```text
Does this application benefit from a cover letter?
If yes, draft a concise one using the reviewed positioning. If not, tell me to skip it.
```

### Contacts

```text
Find up to three credible people who may be useful to contact for this role.
Zero is acceptable if no one is clearly relevant.
```

### Outreach

```text
Draft a short LinkedIn connection note for the best contact.
Do not imply that we know each other or that they referred me.
```

Roleward should not automatically submit an application or send a professional message.

## 7. Track an application

Examples:

```text
I submitted this application today. Mark it as Applied.
```

```text
I have a recruiter screen next Tuesday. Update this opportunity to Screening.
```

```text
I withdrew because the compensation was below my confirmed floor.
Record the outcome and reason separately.
```

The system recommendation and your actual decision are separate. You can pursue a role Roleward passed, or skip one Roleward recommended, without rewriting the historical assessment.

## 8. Learn from outcomes without overfitting

### Unknown rejection reason

```text
I was rejected. They gave no reason.
Record Rejected, but keep the reason unknown.
```

Roleward should not invent a cause from the JD or your profile.

### Confirmed rejection reason

```text
The recruiter explicitly said they need deeper enterprise AI deployment experience.
Record that exact reason and tell me whether it is one observation or part of a broader pattern.
```

Learning should progress conservatively:

- **Weak Observation** — one piece of evidence;
- **Emerging Pattern** — repeated independent evidence;
- **Confirmed Signal** — explicitly confirmed user truth / appropriately promoted state.

One rejection must not automatically:

- exclude an entire role family;
- become a permanent preference;
- override confirmed direction;
- turn an inference into a factual outward claim.

## 9. Correct Roleward when it gets something wrong

You are expected to intervene when a consequential assumption is wrong.

Examples:

```text
That is not correct. I did own wallet product work directly; update the confirmed evidence and keep the old source history.
```

```text
Do not treat "delivery-heavy" as a negative preference. I am open to those roles when the actual work and career value make sense.
```

```text
You are over-weighting my future direction and under-weighting realistic current fit. Re-evaluate this role using the confirmed context without turning Direction into a hard constraint.
```

Roleward should supersede current state without erasing prior evidence/history.

## 10. Useful prompt patterns

### Start my job search

```text
Read SKILL.md and use Roleward Job Hunting.
Help me set up my current job search from the material I provide.
```

### Find roles

```text
Find a small set of roles genuinely worth my attention this week.
Precision over volume. Zero is acceptable.
```

### Evaluate a role

```text
Should I pursue this job?
<URL>
```

### Compare roles

```text
Which of these opportunities deserve my attention first, and what is the trade-off in each?
```

### Position me

```text
I want to pursue this one. Build the Positioning Brief before changing my resume.
```

### Tailor my application

```text
Use the reviewed positioning to tailor only the application materials I actually need.
```

### Record feedback

```text
Here is the recruiter feedback. Record only what is explicitly confirmed and tell me what Roleward should — and should not — learn from it.
```

## 11. Current Alpha caveats

- Codex is the primary tested host.
- A fresh Precision Scan requires a host with web/search access.
- Local structured persistence requires file access and Python 3.11+.
- Scheduled production scanning is not yet part of the public Alpha.
- Reusable user-level Codex Skill installation is still being product-smoke-tested; use the repository as a dedicated workspace for the current recommended Alpha flow.
- Recommendation quality is more important than exact numeric score repeatability.
- No calibrated Screening Call Probability is available.

For first-time setup and privacy, see [Getting Started](GETTING-STARTED.md).
