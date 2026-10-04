# Getting started

**English** | [简体中文](GETTING-STARTED.zh-CN.md)

Roleward Job Hunting is a portable Agent Skill. This guide documents the
**currently fully verified Alpha path**: a dedicated local Codex workspace.
The core package is designed for compatible Agent Skills hosts, but this guide
does not claim second-host acceptance.

Bring a resume, career notes or one job you want to evaluate. You do not need to
prepare a full profile before beginning.

## Set up once

Clone or download [the repository](https://github.com/zhenglimindesign-ing/roleward-job-hunting),
then open its `roleward-job-hunting` folder as a local Codex project. If you want
Codex to clone it, ask in an existing local workspace:

```text
Clone https://github.com/zhenglimindesign-ing/roleward-job-hunting into a local folder.
Preserve any existing files and tell me the resulting path.
```

Open that folder, attach your source material, and say:

```text
Read SKILL.md and use Roleward Job Hunting.
Help me get started from these materials and what I want next.
```

For a direct Job/JD, ask whether it is worth pursuing. Roleward should use
existing candidate context and ask only for missing information that changes the
decision. Reply language follows yours.

## Review what matters

Before a broad Scan, Roleward needs your career background, current direction,
geography and authorization state. `Not sure` is valid. It should show a concise
Structured Context Review, distinguishing source claims, confirmed truth and
inference. Correct consequential mistakes in conversation; there is no
requirement to confirm every row or fill a profile form.

After you choose to pursue a role, review its Positioning Brief before requesting
application materials. For resume tailoring, attach or identify the base resume
you want to use. It should remain the baseline, with important career facts and
proof preserved. File generation uses an optional
[local runtime](RESUME-RUNTIME.md) that the current host can inspect and prepare;
a draft alone is not a delivered DOCX/PDF.

## Save and continue

Your private inputs, history and materials live in Git-ignored workspace areas:

| Location | Contents |
| --- | --- |
| `sources/` | Resumes and source notes |
| `state/roleward-state.json` | Structured context, opportunities and history |
| `application-files/` | Prepared application materials and export records |

Do not commit these files. Local state is not a cloud backup and does not sync
with Roleward Web, job sites or your inbox. If persistence is unavailable,
Roleward must say that continuity is limited to the current conversation.

For a new conversation, open the same workspace and say:

```text
Read SKILL.md and use Roleward Job Hunting.
Continue from my saved context and the last opportunity we worked on.
```

Roleward should load existing state before asking you to rebuild your background.
If it cannot find your history, check the workspace before initializing a new one.

## Run a Precision Scan

The current Public Alpha uses a **manual trigger**:

```text
Find a small set of roles genuinely worth my attention this week.
Use only the geography and constraints we already confirmed.
Do not pad the list if nothing is good enough.
```

Roleward should search, verify where possible, deduplicate, apply confirmed hard
constraints and return a deliberately small result set. Zero is valid.

The underlying Scan contract supports `manual | scheduled`, but a production
scheduler is not shipped in this Public Alpha.

## Requirements and updates

The currently verified path uses Codex with local files and Python 3.11+ for
persistence helpers. Fresh Scan needs current web/search access. Ordinary state
helpers use the standard library; PyYAML is only a contributor-validator
dependency. Resume rendering has separate optional requirements described above.

The package itself follows the open Agent Skills shape and is not intended to be
Codex-specific. Claude and other compatible hosts remain portability targets;
their exact file/search/persistence behavior must be accepted separately before
Roleward claims support for that host.

The documented Alpha setup is the dedicated workspace. Global installation and
automatic updating are not supported. Before a manual code update, inspect local
changes and back up private runtime areas; a code commit is not a backup of
Git-ignored career data. Preserve and reconcile local changes, update only the
code, then load state and check that history remains available.

## When something goes wrong

If the host only explains Roleward, ask it to read SKILL.md and use the workflow.
Without web access, provide the JD; do not expect a verified fresh Scan. Without
document dependencies, ask for a draft and an honest account of undelivered
files. Treat scores as orientation, not probabilities. Submit sanitized feedback
through [GitHub Issues](https://github.com/zhenglimindesign-ing/roleward-job-hunting/issues).

See [Usage](USAGE.md) and [Alpha status](ALPHA-STATUS.md).
