from datetime import datetime, timezone
from io import BytesIO
from pathlib import Path
from xml.sax.saxutils import escape
from zipfile import ZIP_DEFLATED, ZipFile, ZipInfo

from docx import Document
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.opc.constants import RELATIONSHIP_TYPE as RT
from urllib.parse import urlparse
from docx.enum.text import WD_LINE_SPACING
from docx.shared import Inches, Pt
from reportlab.lib.colors import HexColor
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import LETTER
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from reportlab.platypus import (
    KeepTogether,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
)

from resume_ir import ResumeIR


RENDER_VERSION = "fixed-ats-skill-v1"
_ASSET_DIR = Path(__file__).resolve().parents[1] / "assets" / "fonts"
_REGULAR_FONT = _ASSET_DIR / "NotoSans-Regular.ttf"
_BOLD_FONT = _ASSET_DIR / "NotoSans-Bold.ttf"
_FONT_READY = False


def _register_fonts() -> None:
    global _FONT_READY
    if _FONT_READY:
        return
    pdfmetrics.registerFont(TTFont("RolewardNoto", str(_REGULAR_FONT)))
    pdfmetrics.registerFont(TTFont("RolewardNoto-Bold", str(_BOLD_FONT)))
    _FONT_READY = True


class _InvariantCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        kwargs["invariant"] = 1
        kwargs["pageCompression"] = 1
        super().__init__(*args, **kwargs)
        self.setAuthor("Roleward")
        self.setCreator("Roleward Tailored Resume")
        self.setSubject("ATS-safe tailored resume")


def _pdf_styles():
    styles = getSampleStyleSheet()
    return {
        "name": ParagraphStyle(
            "ResumeName",
            parent=styles["Normal"],
            fontName="RolewardNoto-Bold",
            fontSize=17,
            leading=20,
            alignment=TA_CENTER,
            spaceAfter=4,
        ),
        "contact": ParagraphStyle(
            "ResumeContact",
            parent=styles["Normal"],
            fontName="RolewardNoto",
            fontSize=8.5,
            leading=10.5,
            alignment=TA_CENTER,
            textColor=HexColor("#333333"),
            spaceAfter=2,
        ),
        "section": ParagraphStyle(
            "ResumeSection",
            parent=styles["Heading2"],
            fontName="RolewardNoto-Bold",
            fontSize=12,
            leading=15,
            textColor=HexColor("#111111"),
            spaceBefore=8,
            spaceAfter=4,
            keepWithNext=True,
            borderWidth=0,
        ),
        "entry": ParagraphStyle(
            "ResumeEntry",
            parent=styles["Normal"],
            fontName="RolewardNoto-Bold",
            fontSize=10.5,
            leading=13.5,
            spaceAfter=2,
            keepWithNext=True,
        ),
        "body": ParagraphStyle(
            "ResumeBody",
            parent=styles["Normal"],
            fontName="RolewardNoto",
            fontSize=10.5,
            leading=13.5,
            spaceAfter=2,
        ),
        "bullet": ParagraphStyle(
            "ResumeBullet",
            parent=styles["Normal"],
            fontName="RolewardNoto",
            fontSize=10.5,
            leading=13.5,
            leftIndent=11,
            firstLineIndent=-7,
            bulletIndent=0,
            spaceAfter=2,
        ),
    }


def _contact_link(contact) -> str | None:
    if contact.kind == "email":
        value = contact.text.removeprefix("mailto:")
        return "mailto:" + value if "@" in value and not any(c.isspace() for c in value) else None
    if contact.kind == "link":
        value = contact.text
        return value if urlparse(value).scheme in ("https", "http") and urlparse(value).netloc else None
    return None


def _contact_html(contact) -> str:
    target = _contact_link(contact)
    return f'<link href="{escape(target, {chr(34): "&quot;"})}">{escape(contact.text)}</link>' if target else escape(contact.text)


def render_pdf(resume_ir: ResumeIR) -> bytes:
    _register_fonts()
    buffer = BytesIO()
    document = SimpleDocTemplate(
        buffer,
        pagesize=LETTER,
        rightMargin=0.62 * inch,
        leftMargin=0.62 * inch,
        topMargin=0.52 * inch,
        bottomMargin=0.52 * inch,
        title=f"{resume_ir.header.name} Resume",
        author="Roleward",
    )
    styles = _pdf_styles()
    story = [
        Paragraph(escape(resume_ir.header.name), styles["name"]),
        Paragraph(
            "  |  ".join(_contact_html(contact) for contact in resume_ir.header.contacts),
            styles["contact"],
        ),
        Spacer(1, 3),
    ]
    for section in resume_ir.sections:
        story.append(Paragraph(escape(section.title.upper()), styles["section"]))
        for line in section.lines:
            story.append(Paragraph(escape(line.text), styles["body"]))
        for entry in section.entries:
            headers = [
                Paragraph(escape(line.text), styles["entry"])
                for line in entry.header_lines
            ]
            bullets = [
                Paragraph(
                    escape(line.text),
                    styles["bullet"],
                    bulletText="•",
                )
                for line in entry.bullet_lines
            ]
            if bullets:
                story.append(KeepTogether([*headers, bullets[0]]))
                story.extend(bullets[1:])
            else:
                story.extend(headers)
    document.build(story, canvasmaker=_InvariantCanvas)
    return buffer.getvalue()


def _set_run_font(run, *, bold: bool = False, size: float = 10.5) -> None:
    run.font.name = "Noto Sans"
    run.font.size = Pt(size)
    run.bold = bold


def _add_docx_paragraph(
    document: Document,
    text: str,
    *,
    bold: bool = False,
    size: float = 10.5,
    before: float = 0,
    after: float = 2,
    keep_with_next: bool = False,
):
    paragraph = document.add_paragraph()
    paragraph.paragraph_format.space_before = Pt(before)
    paragraph.paragraph_format.space_after = Pt(after)
    paragraph.paragraph_format.line_spacing_rule = WD_LINE_SPACING.SINGLE
    paragraph.paragraph_format.keep_with_next = keep_with_next
    run = paragraph.add_run(text)
    _set_run_font(run, bold=bold, size=size)
    return paragraph


def _normalized_docx(document: Document) -> bytes:
    raw = BytesIO()
    document.save(raw)
    output = BytesIO()
    with ZipFile(BytesIO(raw.getvalue()), "r") as source:
        with ZipFile(output, "w", ZIP_DEFLATED, compresslevel=9) as target:
            for name in sorted(source.namelist()):
                info = ZipInfo(name, date_time=(1980, 1, 1, 0, 0, 0))
                info.compress_type = ZIP_DEFLATED
                info.external_attr = 0o600 << 16
                target.writestr(info, source.read(name))
    return output.getvalue()


def render_docx(resume_ir: ResumeIR) -> bytes:
    document = Document()
    section = document.sections[0]
    section.page_width = Inches(8.5)
    section.page_height = Inches(11)
    section.top_margin = Inches(0.52)
    section.bottom_margin = Inches(0.52)
    section.left_margin = Inches(0.62)
    section.right_margin = Inches(0.62)

    fixed_time = datetime(2000, 1, 1, tzinfo=timezone.utc)
    document.core_properties.author = "Roleward"
    document.core_properties.last_modified_by = "Roleward"
    document.core_properties.title = f"{resume_ir.header.name} Resume"
    document.core_properties.subject = "ATS-safe tailored resume"
    document.core_properties.created = fixed_time
    document.core_properties.modified = fixed_time
    document.core_properties.revision = 1

    name = _add_docx_paragraph(
        document,
        resume_ir.header.name,
        bold=True,
        size=17,
        after=2,
    )
    name.alignment = 1
    contacts = _add_docx_paragraph(
        document,
        "",
        size=8.5,
        after=4,
    )
    contacts.alignment = 1
    for index, contact in enumerate(resume_ir.header.contacts):
        if index:
            _set_run_font(contacts.add_run("  |  "), size=8.5)
        target = _contact_link(contact)
        if target:
            link = OxmlElement("w:hyperlink")
            link.set(qn("r:id"), contacts.part.relate_to(target, RT.HYPERLINK, is_external=True))
            run = OxmlElement("w:r")
            props = OxmlElement("w:rPr")
            fonts = OxmlElement("w:rFonts")
            fonts.set(qn("w:ascii"), "Noto Sans"); fonts.set(qn("w:hAnsi"), "Noto Sans")
            props.append(fonts)
            size = OxmlElement("w:sz"); size.set(qn("w:val"), "17"); props.append(size)
            run.append(props)
            text = OxmlElement("w:t"); text.text = contact.text; run.append(text)
            link.append(run); contacts._p.append(link)
        else:
            _set_run_font(contacts.add_run(contact.text), size=8.5)

    for resume_section in resume_ir.sections:
        heading = _add_docx_paragraph(
            document,
            resume_section.title.upper(),
            bold=True,
            size=12,
            before=6,
            after=3,
            keep_with_next=True,
        )
        heading.paragraph_format.keep_together = True
        for line in resume_section.lines:
            _add_docx_paragraph(document, line.text)
        for entry in resume_section.entries:
            for line in entry.header_lines:
                _add_docx_paragraph(
                    document,
                    line.text,
                    bold=True,
                    size=10.5,
                    keep_with_next=True,
                )
            for line in entry.bullet_lines:
                paragraph = _add_docx_paragraph(document, f"• {line.text}")
                paragraph.paragraph_format.left_indent = Inches(0.16)
                paragraph.paragraph_format.first_line_indent = Inches(-0.11)

    return _normalized_docx(document)


def render_resume(resume_ir: ResumeIR, export_format: str) -> tuple[bytes, str]:
    if export_format == "pdf":
        return render_pdf(resume_ir), "application/pdf"
    if export_format == "docx":
        return (
            render_docx(resume_ir),
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        )
    raise ValueError("Unsupported Resume export format.")
