# Getting Started with Roleward Job Hunting

Roleward Job Hunting is a Codex-first Alpha for running a more deliberate job search: understand your real background, find fewer but better opportunities, decide what is worth pursuing, position yourself truthfully, and learn from outcomes.

This guide covers the current recommended Alpha setup.

## Before you start

You will get the most value if you have at least one of the following:

- a current resume or CV;
- a LinkedIn/profile export;
- career notes or an existing AI career-context summary;
- a clear description of what you want next.

You do **not** need all of them. Roleward should use what already exists before asking you to fill gaps.

Current Alpha requirements:

- Codex with local file access;
- Python 3.11+ for local persistence and helper scripts;
- web/search access in the host if you want a fresh live job scan.

## Recommended Alpha setup: dedicated Codex workspace

The current recommended path is to use the public repository itself as a dedicated local job-search workspace.

### Step 1 — get the repository locally

Repository:

`https://github.com/zhenglimindesign-ing/roleward-job-hunting`

You can clone/download it yourself, or ask Codex to clone it in an existing local workspace:

```text
Clone https://github.com/zhenglimindesign-ing/roleward-job-hunting into a local folder for me.
Do not modify the repository after cloning. Tell me the final folder path.
```

Then open the resulting `roleward-job-hunting` folder as the current project in Codex.

### Step 2 — start Roleward

For a first setup with an existing resume:

```text
Read SKILL.md and use Roleward Job Hunting.

Here is my resume. Help me set up my career context and current job-search direction.
Use the material I already gave you before asking questions.
Show me the important facts, assumptions, conflicts and missing items that matter for my next action.
```

If your resume is already saved locally, you can place it under `sources/` and point Codex to the file.

If you do not have a useful resume ready:

```text
Read SKILL.md and use Roleward Job Hunting.

I want to set up my job search, but I do not have a clean career summary ready.
Ask only the questions needed to establish my Career Anchor, Direction, Geography and Authorization state.
```

### Step 3 — review your context

Roleward should not create an opaque profile and immediately start making decisions.

Before the first broad Scan, review at least:

- **Career Anchor** — your actual experience and strongest evidence;
- **Direction** — the role families, capabilities or transition you want next;
- **Geography** — approved locations / remote scope;
- **Authorization state** — for example `No sponsorship`, `Sponsorship required`, `Depends`, or `Not sure`.

Roleward distinguishes:

- **Source Material** — what a CV, file or external source says;
- **Confirmed Truth** — what you explicitly confirm about yourself;
- **Inferred Signal** — a bounded hypothesis that must not silently become a hard fact.

If something consequential is wrong, correct it directly in conversation. Roleward should preserve the correction and supersede the earlier state rather than rewriting history.

## Three useful ways to begin

### A. Start from your career context

```text
Here is my resume and a short note about what I want next.
Help me build a grounded Roleward career context and tell me what you still need before a first Scan.
```

Best when you want Roleward to become a persistent job-search companion.

### B. Evaluate one job immediately

```text
Should I pursue this role?
<job URL or pasted JD>
```

Roleward should analyze the job using whatever candidate context already exists. If a missing user-owned fact could materially change the decision, it may ask for that fact.

### C. Run a Precision Scan

```text
Find a small set of roles genuinely worth my attention this week.
Use only my confirmed geography and constraints.
Do not pad the list if nothing is good enough.
```

The intended result is a **small shortlist or zero**, not a long feed of plausible jobs.

## Local state and privacy

When this repository is used as the dedicated Alpha workspace, the helper scripts expect these local runtime areas:

- `state/roleward-state.json` — structured current state;
- `sources/` — private source material such as resumes and AI-context exports;
- `application-files/` — generated application artifacts when persisted locally.

These runtime files are excluded by the repository's `.gitignore`.

Important:

- do not commit your resume, private career context, application history or local state;
- do not edit `state/roleward-state.json` manually unless you understand the schema;
- prefer correcting your context conversationally so provenance and supersession can be preserved;
- if you intentionally want a hard reset, back up your local state first rather than casually deleting history.

Roleward Alpha has no required production backend. Your local state is not automatically synced to the Roleward web product.

## What happens after you choose Pursue?

Roleward should not jump directly to resume rewriting.

The intended sequence is:

1. Job is assessed as `Pursue` (or you explicitly choose to pursue it).
2. Roleward creates a **Positioning Brief**.
3. You review/correct the positioning.
4. Only then does Roleward generate the outward materials you actually need:
   - tailored resume / CV;
   - cover letter when useful;
   - 0–3 credible contacts;
   - connection note / InMail draft.

This Human Review step exists to keep downstream materials grounded in how you actually want to present your career.

## Updating your search later

You can change your direction or constraints conversationally:

```text
Update my search direction: UAE is still primary, but I now also want to consider Netherlands roles if sponsorship is available.
Do not change my existing Career Anchor.
```

or:

```text
I no longer want to prioritize this role family. Treat that as a confirmed preference change, not a conclusion from previous rejections.
```

Roleward should preserve prior state/history and apply the new confirmed state going forward.

## Recording outcomes

Examples:

```text
I applied to this role today. Mark it as Applied.
```

```text
I was rejected after the recruiter screen. They did not give a reason.
Update the outcome, but do not infer why I was rejected.
```

```text
They explicitly said they need deeper enterprise AI deployment experience.
Record that as the confirmed rejection reason and tell me what — if anything — Roleward should learn from it.
```

One outcome should not become a permanent market rule.

## Updating Roleward itself

If you cloned the repository, update the local code from the latest `main` before a new test or after a documented release.

Because reusable Codex user-level installation is still being product-smoke-tested, the dedicated repository-workspace flow remains the recommended Alpha setup for now.

## Troubleshooting

### Codex is explaining Roleward instead of using it

Say explicitly:

```text
Read SKILL.md and use the Roleward Job Hunting workflow for this task. Do not summarize the Skill to me unless needed.
```

### Roleward keeps asking things already in my resume

Tell it:

```text
Use existing source material before asking me questions. Ask only for missing information that materially changes the current decision.
```

Repeated unnecessary questions are a product-quality issue worth reporting.

### A live Scan cannot verify current jobs

The host needs current web/search access. Without it, Roleward can still analyze a JD you provide, but it should not claim it performed a fresh Scan or verified current sponsorship/live-link status.

### The numbers move between runs

Treat the displayed scores as orientation signals, not probabilities. The primary output is the recommendation (`Pursue`, `Verify first`, `Pass`) plus the evidence and reasoning behind it.

### I want Roleward available across all Codex projects

Codex supports reusable user-level Skills, but Roleward's public one-step install/update experience is still being validated. The current Alpha docs intentionally recommend the dedicated workspace path until that flow is smoke-tested end to end.

## Next

See [Usage Guide](USAGE.md) for concrete workflows and prompts.
