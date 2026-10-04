# Roleward Job Hunting

**English** | [简体中文](README.zh-CN.md)

**Decide which opportunities deserve your attention, then position yourself truthfully.**

[Roleward](https://roleward.liminzheng.com/) is an AI career workbench.
**Roleward Job Hunting** is its open-source, Codex-first job-hunting Skill.
It helps you invest limited job-search effort in a small number of worthwhile
opportunities, using both your actual career evidence and the direction you want
to pursue next. It is designed to help you apply **better, not more**.

> **Alpha · Codex-first.** Use this repository as a dedicated local Codex
> job-search workspace. Reusable global installation and automatic updating are
> not supported Alpha paths. See [Alpha status](docs/ALPHA-STATUS.md) for current
> verification limits.

## Why use it?

A keyword match cannot decide whether a job is worth your effort. Roleward keeps
five questions distinct:

- **Capability Match:** what does your evidence demonstrate?
- **Screening Legibility:** can a recruiter understand a credible hire case?
- **Career Value:** does the role advance your current direction?
- **Employability:** do location, sponsorship or other structural constraints
  make the opportunity actionable?
- **Evidence Confidence:** what is known, inferred or still uncertain?

The primary decision is **Pursue / Verify first / Pass**. Scores are secondary
orientation signals, not interview probabilities. Before writing application
materials, Roleward helps you decide how to present your background truthfully.

## Who is it for?

Job seekers who already use Codex, have a career history worth understanding,
are considering a transition or new market, and want fewer worthwhile roles.
You should be willing to correct consequential assumptions and review positioning.
It is not intended for mass applications, fabricated resume matching or guaranteed
hiring predictions.

## How the workflow works

**Understand Me → Precision Scan or a supplied Job → Pursuit → Positioning
Review → requested materials → Track and Learn**

Start with a resume, career notes or a Job/JD. Roleward uses existing information
before asking for missing facts. A Scan returns a small shortlist; **zero is a
valid result**. For a pursued role, you review a Positioning Brief before asking
for a resume, cover letter or outreach draft. Materials are prepared separately
when useful. Explicit applications and outcomes can then inform future work.

## Start in Codex

1. Clone or download [this repository](https://github.com/zhenglimindesign-ing/roleward-job-hunting).
2. Open the resulting `roleward-job-hunting` folder as a local Codex project.
3. Attach a resume or paste a Job/JD and start with:

```text
Read SKILL.md and use Roleward Job Hunting.
Help me get started with the material I attached.
Use what is already there, then ask only what matters for my next step.
```

For a direct job evaluation, replace the last two lines with:

```text
Should I pursue this role?
<job URL or pasted JD>
```

You can write in any language. Roleward should reply in your language; local
structured field names remain in English. A first Scan needs your actual career
background, current direction, geography and authorization state; `Not sure` is
valid. See [Getting Started](docs/GETTING-STARTED.md) for setup and privacy, and
[Usage](docs/USAGE.md) for everyday requests.

## Human review and your control

**Human Review is a product principle.** You correct consequential personal
facts and choose how to position yourself. Positioning Review is the only
mandatory Application Prep gate. Roleward keeps independent projects distinct
from formal production experience, preserves important proof in your base
resume, and uses one fixed template for editable DOCX and PDF when the local
runtime supports them. You remain responsible for final submission review.

Roleward does not submit applications or send professional messages. Scheduled
production scanning, interview coaching, salary negotiation and a networking
CRM are outside this Alpha.

## Local files and continuity

Your dedicated workspace stores private inputs in `sources/`, structured history
in `state/roleward-state.json`, and prepared materials in `application-files/`.
These areas are Git-ignored; do not publish them. A new conversation can continue
from the same saved state. Local files are not a cloud backup, and the Skill does
not synchronize with Roleward Web or your job sites/inbox.

## What is still Alpha?

Pursuit recommendation stability remains on hold. Live-search precision and
independent first-user usefulness have not been established. The resume quality
criterion is proposed and requires human acceptance. Codex is the only supported
Alpha host; other hosts and universal install/update paths are unvalidated.
Document generation needs an optional [local resume runtime](docs/RESUME-RUNTIME.md).
Technical checks do not establish recommendation or generated-content quality.

See [Alpha status](docs/ALPHA-STATUS.md). Report sanitized problems through
[GitHub Issues](https://github.com/zhenglimindesign-ing/roleward-job-hunting/issues).

## For contributors and builders

Use Python 3.11+ and PyYAML 6.0.3 for package validation. The optional document
checks also need `requirements-resume.txt`.

```sh
python -B scripts/validate_skill.py
python -B scripts/eval_runner.py
python -B scripts/smoke_journey.py
python -B scripts/smoke_resume.py
```

The workflow in `.github/workflows/skill-checks.yml` lists the complete regression
suite. Synthetic fixtures do not prove model quality or real application outcomes.

## License

[MIT](LICENSE). Packaged Noto Sans fonts retain their [SIL OFL terms](assets/fonts/OFL.txt).
