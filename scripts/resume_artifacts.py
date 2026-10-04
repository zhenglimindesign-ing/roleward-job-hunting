#!/usr/bin/env python3
"""Validate resume invariants, render DOCX/PDF, and bind files to existing reviewed state.

Reference checks and protected text checks are not semantic acceptance.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path

from application_state import _reviewed_positioning, record_artifact
from resume_ir import ResumeIR, iter_lines, sha256_json
from resume_renderers import RENDER_VERSION, render_docx, render_pdf, template_metadata
from resume_source import extract_source
from state_store import load_state, save_state


def _numbers(text: str) -> set[str]:
    return set(re.findall(r"\d+(?:[.,]\d+)*(?:%|[xX])?", text))


def _all_lines(ir: ResumeIR) -> dict:
    lines = list(iter_lines(ir))
    ids = [line.id for line in lines]
    if len(ids) != len(set(ids)):
        raise ValueError("Resume line IDs must be unique")
    return {line.id: line for line in lines}


def validate_resume(base: ResumeIR, tailored: ResumeIR, state: dict, opportunity_id: str,
                    source: Path, protected_line_ids: list[str],
                    authorized_supplement_ids: list[str] | None = None) -> dict:
    opp = state["opportunities"][opportunity_id]
    reviewed = _reviewed_positioning(opp)
    if base.source_kind != "parsed_resume" or tailored.source_kind != "tailored_resume":
        raise ValueError("Expected parsed baseline and tailored ResumeIR")
    extracted = extract_source(source)
    if base.provenance.source_content_hash != extracted["source_sha256"]:
        raise ValueError("Base Resume source hash mismatch")
    if (tailored.provenance.source_content_hash != base.provenance.source_content_hash
            or tailored.provenance.source_file_id != base.provenance.source_file_id):
        raise ValueError("Tailored Resume must retain the selected Base Resume identity")
    if tailored.provenance.strategy_revision_id != reviewed["id"]:
        raise ValueError("Tailored Resume must bind to the current reviewed Positioning")
    if base.header != tailored.header:
        raise ValueError("Candidate name or contact facts changed")
    before, after = _all_lines(base), _all_lines(tailored)
    source_lines = {line["id"]: line["text"] for line in extracted["lines"]}
    facts = {fact.id: fact for fact in base.provenance.facts}
    if len(facts) != len(base.provenance.facts):
        raise ValueError("Base Resume fact IDs must be unique")
    # A fact can be an exact fragment of a combined contact/source line.
    # Coverage is measured from content actually represented by the baseline,
    # not from unused facts merely copied into its provenance registry.
    rendered_fact_ids = {base.header.name_source_line_id,
                         *[c.source_line_id for c in base.header.contacts], *before}
    coverage = {line_id: set() for line_id in source_lines}
    for fact in facts.values():
        source_text = source_lines.get(fact.source_id, "")
        start = source_text.find(fact.text)
        if fact.source_kind != "resume" or not fact.text or start < 0:
            raise ValueError(f"Base fact {fact.id} does not match an extracted source line")
        if fact.id not in rendered_fact_ids and fact.fact_kind != "section_title":
            raise ValueError(f"Base Resume omitted source content represented by fact {fact.id}")
        if fact.text != source_text and source_text.find(fact.text, start + 1) >= 0:
            raise ValueError("Ambiguous source fragment; retain the full source line")
        coverage[fact.source_id].update(range(start, start + len(fact.text)))
    if any(any(char.isalnum() and index not in coverage[line_id]
               for index, char in enumerate(text)) for line_id, text in source_lines.items()):
        raise ValueError("Base Resume mapping omitted source content; resolve coverage before tailoring")
    header_refs = [(base.header.name_source_line_id, base.header.name)]
    header_refs += [(contact.source_line_id, contact.text) for contact in base.header.contacts]
    for line_id, text in header_refs:
        if line_id not in facts or facts[line_id].text != text:
            raise ValueError("Base name/contact must map to source facts")
    for line in before.values():
        if line.id not in facts or facts[line.id].text != line.text:
            raise ValueError(f"Base content {line.id} does not match its source fact")
    base_entries = {entry.id: entry for section in base.sections for entry in section.entries}
    tail_entries = {entry.id: entry for section in tailored.sections for entry in section.entries}
    if len(base_entries) != sum(len(s.entries) for s in base.sections) or len(tail_entries) != sum(len(s.entries) for s in tailored.sections):
        raise ValueError("Resume entry IDs must be unique")
    if set(base_entries) != set(tail_entries):
        raise ValueError("Career entries cannot disappear or be invented during baseline tailoring")
    for entry_id, entry in base_entries.items():
        if entry.header_lines != tail_entries[entry_id].header_lines:
            raise ValueError("Employer/title/date or entry header changed")
    old_sections = {section.id: section.kind for section in base.sections}
    if len(old_sections) != len(base.sections) or len({s.id for s in tailored.sections}) != len(tailored.sections):
        raise ValueError("Resume section IDs must be unique")
    for section in tailored.sections:
        if section.id not in old_sections or section.kind != old_sections[section.id]:
            raise ValueError("Section semantics must retain the selected baseline")
    for section in base.sections:
        for entry in section.entries:
            owner = next(s.kind for s in tailored.sections if any(e.id == entry.id for e in s.entries))
            if owner != section.kind:
                raise ValueError("Independent/project work cannot become formal experience")
    for line_id in protected_line_ids:
        if line_id not in before or line_id not in after or before[line_id].text != after[line_id].text:
            raise ValueError(f"Protected consequential evidence lost or distorted: {line_id}")
    evidence = {item["id"]: item for item in state["profile"].get("career_evidence", []) if item.get("active", True)}
    supplements = set(authorized_supplement_ids or [])
    for ref in supplements:
        if ref not in evidence or evidence[ref].get("authority") != "confirmed_truth":
            raise ValueError("Supplements require explicit authorization and confirmed Career Evidence")
    known = {key: fact.text for key, fact in facts.items()}
    known.update({key: evidence[key]["statement"] for key in supplements})
    used_supplements = set()
    for line in after.values():
        if line.id in before and line.text == before[line.id].text:
            continue
        if not line.evidence_refs or any(ref not in known for ref in line.evidence_refs):
            raise ValueError(f"Changed/generated line {line.id} lacks authorized grounding")
        support = " ".join(known[ref] for ref in line.evidence_refs)
        if not _numbers(line.text).issubset(_numbers(support)):
            raise ValueError(f"Unsupported numeric/date/metric claim in {line.id}")
        used_supplements.update(set(line.evidence_refs) & supplements)
    return {"positioning_revision_id": reviewed["id"], "source_snapshot_id": reviewed["source_snapshot_id"],
            "base_source_sha256": extracted["source_sha256"], "base_ir_sha256": sha256_json(base),
            "tailored_ir_sha256": sha256_json(tailored), "protected_line_ids": protected_line_ids,
            "supplement_evidence_ids": sorted(used_supplements), "source_coverage_complete": True,
            "semantic_review_required": True}


def export_resume(base: ResumeIR, tailored: ResumeIR, state: dict, opportunity_id: str,
                  source: Path, output: Path, protected_line_ids: list[str],
                  authorized_supplement_ids: list[str] | None = None) -> dict:
    binding = validate_resume(base, tailored, state, opportunity_id, source,
                              protected_line_ids, authorized_supplement_ids)
    files = {"docx": render_docx(tailored), "pdf": render_pdf(tailored)}
    # Check both exports before creating any artifact records.
    from io import BytesIO
    from zipfile import ZipFile
    import xml.etree.ElementTree as ET
    from pdfminer.high_level import extract_text
    from pdfminer.pdfpage import PDFPage
    with ZipFile(BytesIO(files["docx"])) as package:
        root = ET.fromstring(package.read("word/document.xml"))
        docx_text = " ".join(node.text or "" for node in root.iter("{http://schemas.openxmlformats.org/wordprocessingml/2006/main}t"))
    pdf_text = extract_text(BytesIO(files["pdf"]))
    normalize = lambda text: " ".join(text.split())
    expected = [tailored.header.name, *[c.text for c in tailored.header.contacts],
                *[s.title.upper() for s in tailored.sections], *[line.text for line in iter_lines(tailored)]]
    for text in expected:
        if normalize(text) not in normalize(pdf_text) or normalize(text) not in normalize(docx_text):
            raise ValueError("An exported file lost intended Resume content")
    page_count = len(list(PDFPage.get_pages(BytesIO(files["pdf"]))))
    if page_count > 2:
        raise ValueError("Resume exceeds two readable pages; compress content rather than shrinking type")
    bundle_id = binding["tailored_ir_sha256"][:16]
    output = output.resolve()
    output.mkdir(parents=True, exist_ok=True)
    paths = {fmt: output / f"resume-{bundle_id}.{fmt}" for fmt in files}
    manifest_path = output / f"resume-{bundle_id}.json"
    for fmt, path in paths.items():
        if path.exists() and path.read_bytes() != files[fmt]:
            raise ValueError("Refusing to overwrite an existing differing artifact")
    if manifest_path.exists():
        existing = json.loads(manifest_path.read_text())
        if all(p.exists() and hashlib.sha256(p.read_bytes()).hexdigest() == existing["files"][fmt]["sha256"] for fmt, p in paths.items()):
            ids = {a["id"] for a in state["opportunities"][opportunity_id].get("application_artifacts", [])}
            if all(row["artifact_id"] in ids for row in existing["files"].values()) and all(existing.get(k) == v for k, v in binding.items()):
                return existing
        raise ValueError("Existing export cannot be reconciled safely; preserve it and use a new output folder")
    result = {**binding, **template_metadata(), "render_version": RENDER_VERSION, "pdf_pages": page_count,
              "visual_review_required": True, "files": {}}
    for fmt, data in files.items():
        paths[fmt].write_bytes(data)
    for fmt, path in paths.items():
        artifact = record_artifact(state, opportunity_id, "resume", {
            "local_path": str(path), "claims": [],
            "metadata": {**binding, **template_metadata(), "format": fmt, "render_version": RENDER_VERSION}})
        result["files"][fmt] = {"path": str(path), "sha256": artifact["sha256"], "artifact_id": artifact["id"]}
    manifest_path.write_text(json.dumps(result, indent=2) + "\n")
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--state", type=Path, default=Path("state/roleward-state.json"))
    parser.add_argument("--opportunity-id", required=True)
    parser.add_argument("--base", type=Path, required=True)
    parser.add_argument("--tailored", type=Path, required=True)
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, default=Path("application-files"))
    parser.add_argument("--protected-line-id", action="append", default=[])
    parser.add_argument("--authorized-supplement-id", action="append", default=[])
    args = parser.parse_args()
    state = load_state(args.state)
    result = export_resume(ResumeIR.model_validate_json(args.base.read_text()),
                           ResumeIR.model_validate_json(args.tailored.read_text()), state,
                           args.opportunity_id, args.source, args.output_dir, args.protected_line_id,
                           args.authorized_supplement_id)
    save_state(args.state, state)
    reloaded = load_state(args.state)
    ids = {a["id"] for a in reloaded["opportunities"][args.opportunity_id]["application_artifacts"]}
    if not all(row["artifact_id"] in ids for row in result["files"].values()):
        raise ValueError("Saved Resume artifact records did not survive readback")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
