# Roleward Job Hunting

**A precision-first AI job hunting skill for deciding where your effort is actually worth spending.**

Roleward learns your real career context, helps you find or evaluate opportunities, decides which ones are worth pursuing, and turns that decision into truthful positioning and application materials.

It is designed to help you apply **better, not more**.

> **Alpha · Codex-first.** The current recommended Alpha experience is to use this repository as a dedicated local Codex job-search workspace. Reusable user-level Skill installation is still being product-smoke-tested.

## Why Roleward?

General AI can rewrite a resume or summarize a job description. Roleward is designed around a harder question:

> **Is this opportunity actually worth pursuing for me?**

It keeps several things separate that are easy to blur together:

- what you can actually do;
- how legible your hire case is to a recruiter;
- whether the role advances your current direction;
- whether location, sponsorship or another constraint makes it actionable;
- what is known versus inferred;
- what one rejection means — and what it does **not** mean.

The core loop is:

**Understand Me → Precision Scan → Pursuit → Position → Human Review → Application Pack → Track → Learn**

## Who is this for?

Roleward Alpha is most useful for job seekers who:

- already use AI or Codex as part of their job search;
- have a non-trivial career history that cannot be reduced to keyword matching;
- are changing direction, function, industry, geography, or all of the above;
- want a smaller set of genuinely worthwhile opportunities rather than a long list;
- care about truthful positioning and want AI outputs grounded in real career evidence;
- are willing to review important assumptions instead of fully automating the application process.

It is **not** designed for mass application, automatic LinkedIn outreach, fabricated resume matching, or guaranteed interview predictions.

## What can I do with it?

| I want to… | Roleward helps me… |
| --- | --- |
| **Set up my career context** | Turn a resume, career notes, or existing AI context into a structured, reviewable career profile |
| **Find worthwhile opportunities** | Search broadly, then return a deliberately small shortlist — or zero when nothing is good enough |
| **Evaluate one job** | Decide `Pursue`, `Verify first`, or `Pass` using capability, screening legibility, career value and employability |
| **Figure out my positioning** | Build a Positioning Brief before rewriting outward materials |
| **Prepare an application** | Tailor a resume, cover letter, contact shortlist, or outreach draft after positioning is reviewed |
| **Learn from outcomes** | Track applications and use confirmed outcomes conservatively without turning one rejection into a permanent rule |

## Quick start — Codex Alpha

### 1. Get this repository onto your computer

Clone or download this repository, then open the `roleward-job-hunting` folder as a local project in the Codex app.

If you prefer not to use the terminal, you can ask Codex in an existing local workspace to clone this repository for you:

```text
Clone https://github.com/zhenglimindesign-ing/roleward-job-hunting into a local folder for me.
Do not modify the repository after cloning. Tell me the final folder path.
```

Then open that folder in Codex.

### 2. Start with one prompt

If you already have a resume:

```text
Read SKILL.md and use Roleward Job Hunting.

Here is my resume. Help me set up my career context and current job-search direction.
Do not ask me for information you can already infer safely from the material; show me the important facts, assumptions and missing items to review.
```

If you want to evaluate a job immediately:

```text
Read SKILL.md and use Roleward Job Hunting.

Should I pursue this role?
<job URL or paste the JD>
```

Roleward will route both requests into the same underlying workflow.

### 3. Review your context before trusting downstream decisions

For a first Scan, Roleward needs only enough context to understand:

- your **Career Anchor** — what you have actually done;
- your **Direction** — where you are trying to go now;
- your **Geography** — where you want/can work;
- your **Authorization state** — for example, no sponsorship needed, sponsorship required, depends, or not sure.

It should show a **Structured Context Review** rather than forcing you through a long form.

### 4. Try a real task

```text
Find a small set of roles genuinely worth my attention this week.
Focus only on the geographies and constraints we already confirmed.
```

or:

```text
I want to pursue this role.
Before rewriting my resume, help me decide how I should position my background.
```

See [Getting Started](docs/GETTING-STARTED.md) for setup, local state and privacy, and [Usage Guide](docs/USAGE.md) for more workflows and example prompts.

## What does a Pursuit decision look like?

A typical job-level result is intentionally decision-first:

```text
PURSUE

Overall Match        80
Capability Match     75
Screening Legibility 65
Career Value         90

Why it may be worth your time
Your enterprise B2B product and regulated-system background creates a credible bridge into the role.

Main concern
The JD asks for formal production-AI experience that your current evidence does not fully demonstrate.

Verify during the process
How strictly the team treats that requirement.
```

The exact numbers are **orientation signals, not probabilities**. The recommendation and reasoning matter more than a 5–10 point score difference.

## What Roleward will not do

Roleward should not:

- automatically submit applications;
- automatically send LinkedIn or professional messages;
- invent experience or upgrade independent projects into formal production experience;
- silently widen your geography or other hard constraints just to return more jobs;
- treat an unknown sponsorship fact as a rejection;
- treat one rejection as proof that an entire role family is wrong for you;
- claim a calibrated interview probability in the current Alpha.

## Local state and privacy

The Alpha is designed around local structured files.

When you use this repository as the dedicated workspace:

- default structured state: `state/roleward-state.json`;
- private source material such as CVs or AI-context exports: `sources/`;
- generated application artifacts: `application-files/`.

Real user files under these runtime directories are ignored by Git. **Do not commit your resume, career context, application history or local state to this public repository.**

See [Getting Started](docs/GETTING-STARTED.md#local-state-and-privacy) for details.

## Current Alpha boundaries

- Primary tested host: **Codex**.
- Local file access and Python 3.11+ are required for structured persistence/helpers.
- Current live discovery depends on the host having web/search access.
- Manual Precision Scan is sufficient for Alpha; production-grade scheduled scanning is not yet part of this public Alpha.
- Reusable user-level Codex Skill installation/update flow is still being verified; the dedicated repository-workspace flow above is the current recommended path.
- Scores are secondary decision aids and may vary between runs; Roleward is evaluated primarily on recommendation quality, evidence credibility and decision usefulness.
- No Roleward production backend is required for the current Alpha.

## For contributors and builders

The user-facing entrypoint is `SKILL.md`. Supporting implementation lives in:

- `references/` — focused workflow policies;
- `scripts/` — deterministic state and workflow helpers;
- `schemas/` — local state schema;
- `fixtures/` — public synthetic/de-identified eval fixtures;
- `state/`, `sources/`, `application-files/` — Git-ignored local runtime areas.

Bootstrap checks:

```bash
python3 scripts/validate_skill.py
python3 scripts/smoke_context.py
python3 scripts/smoke_opportunity.py
python3 scripts/smoke_scan.py
python3 scripts/smoke_application.py
python3 scripts/smoke_learn.py
python3 scripts/smoke_eval.py
python3 scripts/eval_runner.py
```

Internal product and eval authority lives in the private canonical Roleward repository. This public repository is the distributable implementation surface.

## License

TBD. No open-source license is implied until one is explicitly added.
