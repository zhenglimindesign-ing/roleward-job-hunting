# Roleward Job Hunting

**English** | [简体中文](README.zh-CN.md)

**Decide which opportunities deserve your attention, then position yourself truthfully.**

[Roleward](https://roleward.liminzheng.com/) is an AI career workbench.
**Roleward Job Hunting** is its open-source, portable Agent Skill for job hunting.

It helps you invest limited job-search effort in a small number of opportunities
genuinely worth pursuing. It looks at both:

- **where you have been** — your real experience, evidence, strengths and gaps;
- **where you want to go next** — your current direction, career value and trade-offs.

The goal is to help you apply **better, not more**.

> **Alpha · portable by design, Codex-verified today.** The Skill follows the
> open Agent Skills shape rather than a Codex-specific instruction format. The
> currently fully verified Alpha setup is a dedicated local Codex workspace.
> Claude and other compatible hosts remain portability targets, but second-host
> acceptance has not yet been completed. See [Alpha status](docs/ALPHA-STATUS.md).

## Why Roleward?

A lot of AI job-search tooling starts after you already have a JD:

**JD → fit score → rewritten resume → apply**

Roleward starts one decision earlier:

> **Is this opportunity actually worth my time?**

A role can match your past and still be a poor next move. A role can also be a
stretch and still be worth pursuing.

Roleward therefore keeps several questions separate:

- **Capability Match:** what does your real evidence demonstrate?
- **Screening Legibility:** can a recruiter understand a credible hire case?
- **Career Value:** does the role move you toward where you want to go next?
- **Employability:** do location, sponsorship or other structural constraints
  make the opportunity actionable?
- **Evidence Confidence:** what is known, inferred or still uncertain?

The primary decision is **Pursue / Verify first / Pass**. Scores are secondary
orientation signals, not interview probabilities.

## What Roleward takes off your plate

Job hunting is expensive because the same work repeats:

**find roles → screen them → research unknowns → decide whether to apply →
work out your positioning → tailor materials → track outcomes → adjust the next search**

Roleward is designed to carry much of that research, synthesis and preparation
so that your attention stays on the decisions that actually need you.

| Stage | Roleward handles | You mainly do |
| --- | --- | --- |
| **Set up your context** | Extract and structure useful career evidence, current direction, geography and authorization from your resume, notes or existing AI context | Provide existing material and correct consequential mistakes |
| **Find opportunities** | Search current sources, verify links where possible, deduplicate, apply confirmed constraints and return a deliberately small shortlist | Trigger a Scan when you want one and decide which opportunities deserve attention |
| **Fit / Pursuit analysis** | Compare the role with your capability, screening legibility, career value and employability; research decision-changing unknowns when tools can resolve them | Review the reasoning and make the final Pursue / Verify first / Pass decision |
| **Position yourself** | Select the strongest truthful proof, surface credibility gaps and draft a Positioning Brief | Confirm or correct how you want to present your background |
| **Prepare an Application Pack** | Prepare the requested Tailored Resume, Cover Letter, 0–3 credible contacts and outreach draft; resume output uses a stable fixed template | Review the final material and decide whether to submit or send it |
| **Track and learn** | Keep opportunity, application and outcome history connected and use confirmed feedback conservatively | Tell Roleward what actually happened and correct bad inferences |

After the initial setup, you should not need to explain your entire career again
for every new job. The same structured context carries into later Searches,
Pursuit decisions, positioning and materials.

### Manual Scan now; scheduled Scan later

The current Public Alpha supports **manually triggered Precision Scan**:

```text
Find a small set of roles genuinely worth my attention this week.
Use only the geography and constraints we already confirmed.
Do not pad the list if nothing is good enough.
```

Roleward handles the search, verification, deduplication, filtering and first-pass
judgment rather than handing you a long feed of links.

The Scan workflow is trigger-agnostic and already models `manual | scheduled`,
so a future scheduler can invoke the same workflow. **Production scheduled
scanning is not shipped in this Public Alpha.**

## Who is it for?

Roleward Alpha is most useful if you:

- already use AI in your job search;
- have a career history that cannot be reduced to keyword matching;
- are changing function, industry, seniority, geography or professional direction;
- want to spend more time on fewer, higher-value opportunities;
- care about truthful positioning rather than maximum JD keyword overlap;
- want AI assistance without handing over consequential career decisions.

It is probably not the right tool if your main goal is mass application,
automatic submission, automatic LinkedIn outreach, fabricated matching or a
guaranteed interview-probability score.

## Quick start — current verified Alpha path

The fully verified setup today is a dedicated local Codex workspace.

1. Clone or download [this repository](https://github.com/zhenglimindesign-ing/roleward-job-hunting).
2. Open the resulting `roleward-job-hunting` folder as a local Codex project.
3. Attach a resume, career notes or a Job/JD and say:

```text
Read SKILL.md and use Roleward Job Hunting.
Help me get started from the material I attached and what I want next.
Use what is already there, then ask only what matters for my next step.
```

For a direct opportunity:

```text
Read SKILL.md and use Roleward Job Hunting.

Should I pursue this role?
<job URL or pasted JD>
```

A first Scan needs enough context to understand your actual career background,
current direction, geography and authorization state; `Not sure` is valid.

You can write in any language. Roleward should reply in the language you use;
persisted schema fields stay in canonical English.

See [Getting Started](docs/GETTING-STARTED.md) for setup and privacy, and
[Usage](docs/USAGE.md) for everyday requests.

## Decide first, then prepare the application

A typical opportunity result should lead with the decision and reasoning rather
than a wall of requirements:

```text
PURSUE

Why it may be worth your time
Your enterprise B2B and regulated-product background creates a credible bridge
into the role, while the role also moves you toward your current AI-product direction.

Main concern
The JD asks for deeper formal production-AI experience than your current evidence
clearly demonstrates.

Verify during the process
How strictly the team treats that requirement versus adjacent enterprise-product
experience.
```

If you decide to pursue, Roleward creates a **Positioning Brief** before outward
materials. It should cover the hiring case, strongest proof, what to emphasize,
what to de-emphasize, credibility gaps and the recommended narrative.

You review or correct that positioning first. Then Roleward prepares only the
materials you actually need.

## Resume tailoring is not resume reconstruction

When a usable base resume exists, Roleward treats it as the **artifact baseline**.

Tailoring should mainly change:

- selection;
- emphasis;
- ordering;
- compression;
- wording.

Career Evidence and reviewed Positioning help choose and verify content; they
are not permission to rebuild your career history from scratch.

The current resume path preserves consequential facts and strong proof, keeps
independent work distinct from formal production experience, and renders through
one fixed Roleward template. When the optional local document runtime is
available, the Skill delivers editable **DOCX + PDF** and checks the actual files.
It does not attempt to reproduce arbitrary source-PDF layouts.

See [Resume runtime](docs/RESUME-RUNTIME.md).

## Human review is part of the product

Human Review is intentional, not a missing automation feature.

You should review:

- consequential imported assumptions about your career;
- whether an opportunity is worth pursuing;
- positioning before outward materials;
- the final resume or message before it leaves your workspace.

Roleward does **not** submit applications or send professional messages on your
behalf. AI reduces search, synthesis and preparation work; final career judgment
and external action remain yours.

## Local files and continuity

Your dedicated workspace stores:

- private source material in `sources/`;
- structured state in `state/roleward-state.json`;
- prepared materials in `application-files/`.

These runtime areas are Git-ignored. Do not publish real resumes, private career
context, application history or local state.

A new conversation can continue from the same saved state. Local files are not a
cloud backup, and the Skill does not synchronize with Roleward Web, job sites or
your inbox.

## What is still Alpha?

The package is portable by design, but **Codex is the only host with the complete
verified Alpha path today**. Do not read that as a Codex-only product claim:
Claude and other compatible hosts remain intended portability targets, but a
second-host acceptance has not yet been completed.

Other open gates include:

- Pursuit recommendation stability remains on **HOLD** pending PM adjudication;
- aggregate live-search worth-review precision is not yet accepted;
- resume artifact machinery is implemented, but the proposed human quality gate
  still needs PM acceptance;
- an independent first-user usefulness check remains open;
- production scheduled Scan, universal installation/update, backend sync and
  automatic external actions are not part of this Alpha.

Technical checks do not establish semantic recommendation quality or real hiring
outcomes. See [Alpha status](docs/ALPHA-STATUS.md).

## Feedback

If Roleward recommends an obviously poor opportunity, misses an important reason
to pursue one, asks for information already present, inflates career evidence,
produces a worse tailored resume, or learns too much from one outcome, please
open a [GitHub Issue](https://github.com/zhenglimindesign-ing/roleward-job-hunting/issues).

Share only sanitized prompts, expectations, actual behavior and version/commit
information. Do not post private resumes or local state.

## For contributors and builders

Contributions are welcome. Start with the [contribution guide](CONTRIBUTING.md)
and [public contributor contract](docs/CONTRIBUTOR-CONTRACT.md). Documentation
and reproducible fixes can go directly to a PR; propose new workflows or
judgment changes in an Issue first. Synthetic behavior cases and useful
disagreements are especially helpful. Never publish private career data.

Use Python 3.11+ and PyYAML 6.0.3 for package validation. Optional document
checks also need `requirements-resume.txt`.

```sh
python -B scripts/validate_skill.py
python -B scripts/eval_runner.py
python -B scripts/smoke_journey.py
python -B scripts/smoke_resume.py
```

The workflow in `.github/workflows/skill-checks.yml` lists the complete
regression suite. Synthetic fixtures do not prove model quality or real
application outcomes.

Internal product and evaluation authority remains in the private Roleward
repository; this public repository is the distributable implementation surface.

## License

[MIT](LICENSE). Packaged Noto Sans fonts retain their
[SIL OFL terms](assets/fonts/OFL.txt).
