# Resume fidelity, relevance and delivery

Read this policy when preparing a tailored resume. Positioning Review remains
the only mandatory Application Prep gate. The checks below are the agent's work;
they do not add a user wizard or another mandatory approval.

## Baseline and authority

When a usable base resume exists, use it as the artifact baseline. Preserve its
career, employer/title/date facts, qualifications and strongest relevant proof.
Career Evidence verifies and supports that baseline; it is not blanket permission
to regenerate the candidate's history. A resume claim remains Source Material
unless the user has confirmed it. If it conflicts with confirmed current truth,
surface the consequential conflict and use the user's correction.

Tailor primarily through selection, emphasis, ordering, compression and wording.
Use reviewed Positioning and the exact Job requirements to explain material
omissions or structural changes. Prefer light edits when the base is already
strong. Older evidence can be the strongest evidence; recent AI keywords do not
outweigh demonstrated professional capability. Keep independent/selected project
work distinct from formal employment and production/customer experience.

Never invent or upgrade employers, titles, dates, metrics, qualifications,
seniority, ownership or production status. Do not flatten a complex career into
generic JD language. Consequential evidence must survive with its meaning intact.

## Source transfer

Preserve the source file and its SHA-256. Extract readable text, then map a
structured baseline back to the extracted lines. Inspect reading order, role
boundaries, dates and qualifications against the original. Resolve extraction
loss before tailoring; a successful extraction command does not prove fidelity.

`scripts/resume_source.py` supports text-layer PDF (up to 20 pages / 4 MB),
paragraph-based DOCX, and UTF-8 TXT/Markdown. Table-based DOCX, complex layouts,
scanned or protected PDFs may need the host's existing ingestion tools. Do not
silently introduce OCR or claim unsupported input has been read correctly.

Use the portable `resume_ir.v1` structure in `scripts/resume_ir.py`. Map every source line to provenance facts, including section labels; facts
may be exact fragments of a combined contact line. Map rendered content to
those facts and retain complete source coverage. Keep baseline entry headers verbatim. Every rewritten/generated
line cites supporting baseline fact IDs. Authorized supplements cite active
Career Evidence that is either confirmed truth or traceable source material
explicitly included in the current reviewed Positioning. Retain its authority
in the export manifest; review does not convert a source claim into verified
truth. Supplements belong to the matching existing role/project and
must not silently add a new career entry. Cross-role supplements require manual
reconciliation before this helper path. Do not authorize a supplement merely
because an evidence ID exists.

If no usable base exists, explain that a newly assembled resume is a draft from
confirmed evidence, not a tailored copy. The baseline export helper does not
cover that fallback. Complete the bounded drafting task without fabricating
history or claiming submission readiness.

## One Alpha structure and template

Use one conservative single-column template: candidate/contact header; optional
summary; professional experience; separate independent/selected projects when
relevant; education; skills; languages/confirmed qualifications when relevant.
Omit irrelevant empty sections. Within experience use reverse chronology;
emphasize older proof through bullet selection or a truthful summary rather than
changing dates. A reviewed positioning reason can change section order while
preserving section semantics. Do not redesign the layout for each generation.

For a long employment entry covering distinct work areas, preserve or add a
small set of source-grounded topic headings so a reader can scan its scope.
Keep the original role and chronology; topics do not create new career entries.
Compress wording without flattening meaningful work areas into a single long
bullet list. Use the template's existing `topic` style for these headings.

The default is the `standard` template in [resume template](resume-template.md):
A4 portrait, left-aligned name, blue navigation, separate employer/role/date
hierarchy and hanging bullets. Its shared parameters are in
`assets/resume-standard-v1.json`. Arial is preferred when available; the bundled
OFL Noto Sans is the recorded fallback. PDF embeds the selected font; DOCX specifies
the same family but an editor may substitute it. Keep readable 10.5 pt body text.
Aim for one or two pages through relevant content editing and reviewed reflow,
never by shrinking type to force a page count. Honor an explicit user template
or style; do not open a template picker for ordinary default generation.
Exact source-PDF layout preservation and a full resume editor remain outside Alpha.

## Export and binding

Deliver both editable DOCX and PDF when the runtime supports them. Read
[resume runtime](../docs/RESUME-RUNTIME.md) before using the helper. Bind the
tailored IR to the current reviewed Positioning revision and Job source snapshot.
The helper checks baseline identity, source coverage, entry headers, protected
proof, numeric claims, output text coverage and PDF page count, then records
both files through the existing Application state helper. It does not validate
the meaning of a cited claim or its consistency with Positioning.

Before delivery inspect the actual latest PDF and a rendered DOCX: no lost
content, clipping, overlap, orphaned headings, broken entry association or
incorrect contact links. DOCX/PDF pagination can differ by editor; inspect both.
Save the structured revision and export manifest locally. Regeneration creates
a new revision; a changed Job/Positioning must not reuse stale materials.
Prepared files do not mean an application was submitted.

## Quality assessment

Treat unsupported consequential claims, fact drift, project-to-production
upgrades, contradictions with reviewed Positioning and protected-proof loss as
hard failures. Structural automation can identify some of them; semantic review
must examine relevance, fidelity, strongest proof, information preservation,
screening legibility and natural writing. Evidence references alone are not a
truth or quality score.

Compare Base and Tailored: if only one could be submitted, which would the
reviewer choose, and why? The proposed five-case Alpha target is zero hard
failures, Tailored preferred in at least four cases, and the remaining case no
worse in a consequential way. This is a proposed extension of the canonical
Positioning/Application eval, pending PM acceptance; it is not a population claim.
