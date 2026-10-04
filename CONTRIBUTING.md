# Contributing to Roleward

**English** | [简体中文](CONTRIBUTING.zh-CN.md)

Contribute a reproducible problem, a useful case, or a focused improvement.
For behavior changes, consult the [public contributor contract](docs/CONTRIBUTOR-CONTRACT.md)
and [current Alpha limits](docs/ALPHA-STATUS.md). Simple documentation fixes
can go directly to a PR. Private product documents and real career records
are not required to contribute.

## Choose a contribution

| Contribution | Start here | Who decides |
| --- | --- | --- |
| Typo, translation, focused documentation repair, reproducible bug | Submit a small PR directly | Maintainer reviews and merges |
| Synthetic behavior case or host observation | Open a behavior-case issue with inputs and evidence | Maintainer assesses relevance and any proposed expectation |
| New feature, integration, decision rule, score meaning, or state contract | Open an improvement issue before implementation | Product owner decides scope and semantics; maintainer reviews implementation |
| Acceptance labels, thresholds, supported-host claims, or release claims | Discuss the proposed change explicitly | Product owner approves; historical evidence stays intact |

Anyone can propose a change. Contributors work in their own fork or branch;
opening a PR does not grant write access or authorize release. Architecture,
product direction and consequential judgment rules remain owner decisions.

## Prepare a focused change

1. Describe the observed problem and the smallest useful result. For a feature
   or policy proposal, wait for scope agreement before building it.
2. Fork the repository, make a branch, and keep the diff focused. Preserve user
   files and unrelated work. Keep private runtime content from `state/`,
   `sources/` and `application-files/`, and local `work/` or `outputs/`, out of
   submitted content. Tracked placeholder READMEs may receive documentation fixes.
3. Check the affected behavior. Follow the relevant validation row in the
   [contract](docs/CONTRIBUTOR-CONTRACT.md#validation-by-change).
4. Open a PR using the template. Show the before/after result, affected rules,
   checks actually run, and what remains unverified. Maintainers may request
   changes or decline a proposal that does not fit the current scope.

AI-assisted contributions are welcome. The contributor remains responsible
for the diff, its sources and the reported checks. Explain the problem rather
than submitting a large bundle of generic instructions or unrelated cleanup.

## Contribute behavior evidence

Use the behavior-case issue template. Give only the minimum synthetic or
explicitly authorized, sanitized input needed to explain the result. Record
the Skill commit, host and model when observed; write `unknown` when unavailable.
Separate the actual output from your interpretation and proposed alternative.

An alternative recommendation is a proposal, not an accepted label. Cases may
have legitimate value tradeoffs or incomplete evidence. A maintainer can keep
a disagreement open rather than manufacture one correct answer. Keep raw inputs
separate from expected answers when an independent evaluation is warranted.
Do not revise historical labels or regenerate outputs merely to improve a pass
rate. See [fixture guidance](fixtures/README.md).

## Protect career data and contributor credit

Do not post full resumes, source exports, contact details, credentials, or saved
state. Removing a person's name alone may leave identifiable career history.
Prefer fictional examples. Publish third-party text only when you have the
necessary rights; a job URL and a minimal permitted excerpt may be sufficient.

Keep authorship when continuing someone else's work; coordinate on an active PR
before replacing it. Merged work retains Git/PR attribution, including a
co-author attribution when appropriate.

Original project material uses the [MIT license](LICENSE); packaged fonts retain
their [OFL terms](assets/fonts/OFL.txt). Identify the source and license of added
material and make sure you can contribute it under the applicable terms.
Private user material does not become project-licensed by being used locally.

## Maintainer review

Maintainers review scope, public-contract consistency, data boundaries and the
relevant evidence before merging. Existing GitHub CI checks package and
deterministic regressions. Passing CI alone cannot approve a changed Pursuit
judgment, prove prose fidelity, validate another host, or remove Alpha HOLD.
Branch-protection settings and repository permissions are managed separately;
this guide does not change them or promise a response deadline.
