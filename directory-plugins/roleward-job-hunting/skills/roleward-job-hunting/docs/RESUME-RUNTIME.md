# Resume files and local runtime

The normal state/workflow helpers remain standard-library Python. Resume file
generation is optional and uses the dependencies pinned in
[`requirements-resume.txt`](../requirements-resume.txt): `python-docx`, ReportLab,
Pydantic and `pdfminer.six`. These are local rendering/parsing libraries; no
Roleward backend, paid generation API or office application is required to create
DOCX/PDF. A compatible Word/LibreOffice renderer is needed to verify DOCX layout.

Use a compatible runtime already available in the host. For a standalone setup,
ask Codex to prepare an isolated environment and install the pinned requirements
after inspecting existing dependencies. Do not change a shared environment or
install a full office stack silently. The host should do this preparation; users
do not need to operate the helper CLI during ordinary job hunting.

The portable path is:

1. Extract the selected source with `scripts/resume_source.py`.
2. Build `parsed_resume` IR whose fact map covers all extracted source lines;
   verify source transfer against the original.
3. Tailor the IR against reviewed Positioning and current Job requirements,
   retaining entry IDs/headers and linking changed lines to supporting facts.
4. Mark consequential baseline proof as protected line IDs. Supply supplement
   IDs only when explicitly authorized and role-matched.
5. Export both files with `scripts/resume_artifacts.py` and inspect them.

Example for agents/builders, from the dedicated workspace:

```sh
python scripts/resume_source.py sources/base.txt --output sources/base-extracted.json
python scripts/resume_artifacts.py \
  --state state/roleward-state.json --opportunity-id OPPORTUNITY_ID \
  --source sources/base.txt --base sources/base-ir.json \
  --tailored application-files/tailored-ir.json \
  --protected-line-id BASE_PROOF_ID --output-dir application-files
```

The structured schema can be inspected with
`ResumeIR.model_json_schema()` in `scripts/resume_ir.py`. Fact IDs in a baseline
are local source identities, not automatically confirmed Career Evidence IDs.
Each provenance fact records the matching extraction line ID in `source_id`.
Fact text must match the source line or an unambiguous exact fragment of it.
All meaningful source text must be covered by facts actually represented in
the baseline (plus section labels); copying unused facts into provenance does
not satisfy coverage. Baseline header/body lines reference those fact IDs. `strategy_revision_id` in the tailored provenance
must equal the existing reviewed Positioning revision ID.

Exports retain source/IR hashes, Job source snapshot, Positioning revision,
renderer version, template/configuration identity, actual font selection and
per-file hashes. Repeating a reconciled identical export
does not append duplicate artifact records. If an export/save is interrupted,
preserve the files and inspect state before retrying. The helper intentionally
fails on unresolved coverage, changed career headers, stale positioning,
unauthorized supplements, lost export text or more than two PDF pages.

Sources, IR, state and exports belong under the workspace's Git-ignored
`sources/`, `state/` and `application-files/`. Public fixtures contain invented
candidates only. Never add a real resume or private benchmark to the package.

The built-in `standard` design is specified in
[`references/resume-template.md`](../references/resume-template.md) and
`assets/resume-standard-v1.json`. Optional presentation fields preserve older
ResumeIR inputs while supporting separate role/date/topic hierarchy and reviewed
page breaks. The template does not connect to Web storage or user accounts.
OFL fallback font redistribution terms are in `assets/fonts/OFL.txt`.
