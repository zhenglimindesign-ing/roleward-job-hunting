# Everyday requests

**English** | [简体中文](USAGE.zh-CN.md)

After [setup](GETTING-STARTED.md), use ordinary language. Roleward should carry
context forward and propose the next useful step without making you manage stages.

| Your request | Expected result |
| --- | --- |
| “Here is my resume and what I want next.” | Structured context review using existing sources; only consequential questions |
| “Find a few worthwhile roles this week.” | Bounded live Scan within confirmed policy; zero results is valid |
| “Should I pursue this Job?” | Pursue / Verify first / Pass, supporting evidence, material gaps and a concrete verification plan when needed |
| “Help me position myself for this role.” | Positioning Brief with strongest proof and truthful boundaries for your review |
| “Tailor this base resume for the reviewed positioning.” | More relevant resume that preserves career facts and important proof; editable DOCX and PDF when supported |
| “Prepare a cover letter / contact shortlist / connection note.” | Only requested materials; zero to three credible contacts, never invented context |
| “I applied today.” | Recorded application with a verified save receipt |
| “I was rejected; no reason was given.” | Recorded outcome; rejection cause remains unknown |
| “Continue from last time.” | Existing state loaded before continuing |

## Run a Scan

The current Public Alpha Scan is manually triggered:

```text
Find a small set of roles genuinely worth my attention this week.
Use my confirmed geography and constraints. Do not pad the list.
```

The Skill's Scan contract is trigger-agnostic and can later be invoked by a
scheduler, but production scheduled scanning is not currently shipped. Do not
expect background monitoring unless the host and a later Roleward release
explicitly provide it.

## Change a preference without rebuilding your history

```text
Keep UAE as my primary market. Also consider Netherlands roles when sponsorship
is available. Preserve my career evidence and earlier applications.
```

```text
For future scans, show at most three roles. This time, show only one.
```

The ongoing limit is saved; a one-time limit applies only to that Scan. Your
explicit direction outranks inferred preferences. One rejection or Pass reason
must not become a permanent market rule.

## Prepare a resume

```text
Use this base resume and our reviewed positioning for the job.
Keep the strongest relevant proof, even if it is older. Keep independent work
clearly separate from formal production experience. Give me editable DOCX and PDF.
```

Roleward should select and emphasize evidence rather than reconstruct your
career from scratch. Review the exported files before submission: career facts,
content, contacts and page breaks matter. Files are local and tied to the Job
source and Positioning revision. If either changes, prepare a new revision.
A prepared resume is not a submitted application.

## Track outcomes conservatively

```text
They explicitly said they require deeper production AI ownership.
Record that reason, and explain what this single outcome can reasonably tell us.
```

Confirmed feedback can support learning. Unconfirmed causes remain hypotheses;
Roleward must not rewrite your goals from them. It does not monitor your inbox or
submit applications/send messages for you.

## Capability limits

Without current web access, provide a Job/JD for analysis. Without persistence,
continuity is limited to the conversation. Without the optional document runtime,
Roleward must identify undelivered file formats. The package is portable by
design, but host-specific support is claimed only after that host is accepted.
See [Alpha status](ALPHA-STATUS.md) and [Resume runtime](RESUME-RUNTIME.md).
