# Default resume template

Use `standard` for ordinary Alpha resume generation. The first release has one
default layout; no template-choice wizard is required. A user-provided visual
template or explicit styling instruction takes precedence. A source resume used
for career facts does not by itself require copying its visual layout.

## Design and execution

`assets/resume-standard-v1.json` is the shared design source for both renderers in
`scripts/resume_renderers.py`. Use those renderers rather than improvising a new
layout. The template uses an A4 single column, a left-aligned 24 pt name,
10.5 pt body with 14 pt leading, blue section navigation and light section rules.
Employers are dark bold; roles and dates are secondary; work topics are regular
blue; bullets hang under a consistent text edge. Empty sections are omitted by
the content preparation step. No avatar, skill bars or narrative layout tables
are needed. The template is a display rule, not a substitute for relevant writing.

Arial is used when its regular/bold pair is present. Otherwise use bundled Noto
Sans. Do not download or redistribute proprietary fonts. Both exports choose the
same family. Export metadata records template ID, version, configuration hash,
font family and fallback use. DOCX retains named editable paragraph styles.
Page breaks may vary by office editor, so matching design parameters do not prove
identical pagination. Inspect both current exports on the actual host.

## Content mapping

Keep the existing `resume_ir.v1` provenance and source coverage. The optional
`ResumeLine.layout` field selects presentation only: `headline`, `company`,
`role`, `date`, `intro`, `topic`, `body`, `bullet`, `skill`, `degree`, or `school`.
`auto` keeps older IR compatible. Do not add a display-only factual string.

- Put at most one `headline` in a section's `lines`; it renders once below the
  name and above contacts. Its facts/wording still require source grounding.
- In each entry's `header_lines`, keep employer/degree first; mark the date line
  `date` to align it right, and mark role/school lines explicitly. All text must
  be exact baseline facts/fragments, with stable fact IDs and source references.
  Do not guess metadata by splitting arbitrary prose or change a career date.
- Within `bullet_lines`, use a `metadata` line with layout `topic` for a work
  heading, a `body` line with layout `intro` for context, and ordinary `bullet`
  lines for evidence. Their IDs and evidence bindings remain intact.
- For skills, `skill` presents an existing label before a colon in bold. It does
  not invent or strengthen qualifications.

## Reflow and delivery

Start without manual breaks. Review actual content density, heading association
and export page count. When a long entry needs a deliberate break, set its
`break_before_line_id` to a later whole bullet after at least one bullet in that
topic. Both renderers then repeat the unchanged entry metadata and latest topic
with a continuation marker. Never hardcode a break from an example into all CVs.
Do not strand an employer or topic heading, clip content, or reduce body type to
force two pages. If source content needs editing, preserve the existing evidence
and Positioning requirements.

The fictional input `fixtures/resume/standard-template-v1.json` is a full-length
layout example, not real career evidence or a semantic-quality acceptance set.
Normal outward materials still use `scripts/resume_artifacts.py` and the reviewed
Positioning gate. A successful render is not submission readiness or proof that
the wording is useful for the target job.
