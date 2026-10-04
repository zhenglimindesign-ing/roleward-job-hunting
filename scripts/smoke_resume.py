#!/usr/bin/env python3
"""Targeted synthetic regressions for baseline fidelity and actual resume files."""
from copy import deepcopy
from io import BytesIO
import json
from pathlib import Path
import tempfile
import unittest
from zipfile import ZipFile

from application_state import record_positioning_draft, review_positioning
from opportunity_state import upsert_opportunity
from resume_artifacts import export_resume, validate_resume
from resume_ir import ResumeIR
from resume_renderers import render_docx, render_pdf
from resume_source import extract_source


class ResumeTests(unittest.TestCase):
    def setUp(self):
        self.root = Path(__file__).resolve().parents[1]
        self.case = json.loads((self.root / "fixtures/_inputs/resume/R03/input.json").read_text())
        self.base = ResumeIR.model_validate(self.case["base"])
        self.tail = self.base.model_copy(deep=True)
        self.tail.source_kind = "tailored_resume"
        self.tail.provenance.strategy_revision_id = self.case["reviewed_positioning_id"]
        self.source = self.root / "fixtures/_inputs/resume/R03/base.txt"

    def check(self):
        return validate_resume(self.base, self.tail, self.case["state"], self.case["opportunity_id"], self.source, self.case["protected_line_ids"])

    def test_unchanged_strong_baseline_is_valid(self):
        self.assertTrue(self.check()["source_coverage_complete"])

    def test_source_coverage_cannot_silently_drop_a_line(self):
        self.base.provenance.facts.pop()
        with self.assertRaisesRegex(ValueError, "omitted source content"):
            self.check()

    def test_contact_drift_is_rejected(self):
        self.tail.header.contacts[0].text = "wrong@example.com"
        with self.assertRaisesRegex(ValueError, "contact"):
            self.check()

    def test_unused_fact_registry_cannot_hide_baseline_loss(self):
        self.base.sections[2].entries[0].bullet_lines.pop(1)
        with self.assertRaisesRegex(ValueError, "omitted source content"):
            self.check()

    def test_combined_contact_line_can_map_exact_fragments(self):
        from hashlib import sha256
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / "base.txt"
            lines = self.source.read_text().splitlines()
            lines[1] = lines[1] + " | " + lines[2]
            del lines[2]
            source.write_text("\n".join(lines) + "\n")
            for fact in self.base.provenance.facts:
                index = int(fact.source_id.split("-")[1])
                if index == 3:
                    fact.source_id = "source-2"
                elif index > 3:
                    fact.source_id = f"source-{index - 1}"
            self.base.provenance.source_content_hash = sha256(source.read_bytes()).hexdigest()
            self.tail.provenance.source_content_hash = self.base.provenance.source_content_hash
            self.source = source
            self.assertTrue(self.check()["source_coverage_complete"])

    def test_employer_title_date_drift_is_rejected(self):
        self.tail.sections[2].entries[0].header_lines[0].text += " Senior AI Leader"
        with self.assertRaisesRegex(ValueError, "Employer/title/date"):
            self.check()

    def test_older_protected_proof_cannot_disappear(self):
        self.tail.sections[2].entries[0].bullet_lines.pop(0)
        with self.assertRaisesRegex(ValueError, "Protected"):
            self.check()

    def test_independent_work_cannot_move_into_experience(self):
        self.tail.sections[2].entries.append(self.tail.sections[1].entries.pop())
        with self.assertRaisesRegex(ValueError, "Independent/project"):
            self.check()

    def test_numeric_claim_requires_referenced_support(self):
        line = self.tail.sections[2].entries[0].bullet_lines[1]
        line.text = "Reduced onboarding time by 95%."
        with self.assertRaisesRegex(ValueError, "Unsupported numeric"):
            self.check()

    def test_changed_claim_cannot_use_an_unknown_reference(self):
        self.tail.sections[0].lines[0].text = "Enterprise platform product manager."
        self.tail.sections[0].lines[0].evidence_refs = ["unknown"]
        with self.assertRaisesRegex(ValueError, "authorized grounding"):
            self.check()

    def test_old_positioning_cannot_export(self):
        state = self.case["state"]
        draft = record_positioning_draft(state, self.case["opportunity_id"], {"thesis": "new angle"})
        review_positioning(state, self.case["opportunity_id"], draft["id"])
        with self.assertRaisesRegex(ValueError, "current reviewed Positioning"):
            self.check()

    def test_job_change_invalidates_previous_review(self):
        upsert_opportunity(self.case["state"], {"company": "Example Hiring Team", "title": "Enterprise Platform Product Manager", "url": "https://example.com/jobs/r03", "text": "Materially changed job requirements"})
        with self.assertRaisesRegex(ValueError, "current job source"):
            self.check()

    def test_both_files_are_deterministic_and_links_survive(self):
        self.assertEqual(render_docx(self.tail), render_docx(self.tail))
        self.assertEqual(render_pdf(self.tail), render_pdf(self.tail))
        with ZipFile(BytesIO(render_docx(self.tail))) as package:
            xml = package.read("word/document.xml")
            self.assertNotIn(b"<w:tbl", xml)
            self.assertNotIn(b"<w:drawing", xml)
            rels = package.read("word/_rels/document.xml.rels")
            self.assertIn(b"mailto:taylor.chen@example.com", rels)
        from pdfminer.pdfpage import PDFPage
        from pdfminer.pdftypes import resolve1
        links = [resolve1(resolve1(a).get("A", {})).get("URI", b"").decode()
                 for page in PDFPage.get_pages(BytesIO(render_pdf(self.tail)))
                 for a in resolve1(page.annots or [])]
        self.assertIn("mailto:taylor.chen@example.com", links)

    def test_export_records_two_files_and_idempotent_repeat(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = export_resume(self.base, self.tail, self.case["state"], self.case["opportunity_id"], self.source, Path(tmp), self.case["protected_line_ids"])
            repeated = export_resume(self.base, self.tail, self.case["state"], self.case["opportunity_id"], self.source, Path(tmp), self.case["protected_line_ids"])
            self.assertEqual(result, repeated)
            self.assertEqual(len(self.case["state"]["opportunities"][self.case["opportunity_id"]]["application_artifacts"]), 2)
            self.assertTrue(result["semantic_review_required"])

    def test_pdf_and_docx_sources_reopen(self):
        with tempfile.TemporaryDirectory() as tmp:
            for fmt, renderer in (("pdf", render_pdf), ("docx", render_docx)):
                path = Path(tmp) / ("source." + fmt)
                path.write_bytes(renderer(self.tail))
                self.assertTrue(extract_source(path)["lines"])


if __name__ == "__main__":
    unittest.main()
