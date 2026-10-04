import hashlib
import json
import re
from typing import Any, Literal

from pydantic import BaseModel, Field


RESUME_IR_SCHEMA_VERSION = "resume_ir.v1"


class ResumeContact(BaseModel):
    kind: Literal["email", "phone", "location", "link", "other"]
    text: str = Field(min_length=1)
    source_line_id: str


class ResumeHeader(BaseModel):
    name: str = Field(min_length=1)
    name_source_line_id: str
    contacts: list[ResumeContact] = Field(default_factory=list)


class ResumeLine(BaseModel):
    id: str
    text: str = Field(min_length=1)
    kind: Literal["body", "bullet", "metadata"] = "body"
    source_page: int = Field(ge=1, le=20)
    source_bbox: tuple[float, float, float, float] | None = None
    evidence_refs: list[str] = Field(default_factory=list)


class ResumeEntry(BaseModel):
    id: str
    header_lines: list[ResumeLine] = Field(default_factory=list)
    bullet_lines: list[ResumeLine] = Field(default_factory=list)


class ResumeSection(BaseModel):
    id: str
    title: str = Field(min_length=1)
    kind: Literal[
        "summary",
        "experience",
        "education",
        "skills",
        "projects",
        "certifications",
        "languages",
        "volunteer",
        "custom",
    ]
    entries: list[ResumeEntry] = Field(default_factory=list)
    lines: list[ResumeLine] = Field(default_factory=list)


class ResumeFact(BaseModel):
    id: str
    text: str = Field(min_length=1)
    fact_kind: Literal[
        "name",
        "contact",
        "section_title",
        "entry_header",
        "bullet",
        "body",
        "career_vault_supplement",
        "derived_career_fact",
    ]
    source_kind: Literal["resume", "career_vault", "derived"]
    source_id: str
    source_page: int | None = None


class ResumeProvenance(BaseModel):
    source_file_id: str
    source_content_hash: str
    parser_version: str
    parse_id: str | None = None
    strategy_revision_id: str | None = None
    facts: list[ResumeFact] = Field(default_factory=list)


class ResumeIR(BaseModel):
    schema_version: Literal["resume_ir.v1"] = RESUME_IR_SCHEMA_VERSION
    source_kind: Literal["parsed_resume", "tailored_resume"]
    header: ResumeHeader
    sections: list[ResumeSection] = Field(min_length=1)
    provenance: ResumeProvenance
    warnings: list[str] = Field(default_factory=list)


def canonical_json(value: BaseModel | dict[str, Any]) -> str:
    payload = value.model_dump(mode="json") if isinstance(value, BaseModel) else value
    return json.dumps(
        payload,
        ensure_ascii=False,
        separators=(",", ":"),
        sort_keys=True,
    )


def sha256_json(value: BaseModel | dict[str, Any]) -> str:
    return hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()


def stable_id(prefix: str, *parts: object) -> str:
    raw = "\x1f".join(str(part) for part in parts)
    digest = hashlib.sha256(raw.encode("utf-8")).hexdigest()[:16]
    return f"{prefix}_{digest}"


def normalized_match_key(value: str | None) -> str:
    if not value:
        return ""
    return re.sub(r"[^a-z0-9]+", " ", value.casefold()).strip()


def iter_lines(resume_ir: ResumeIR):
    for section in resume_ir.sections:
        yield from section.lines
        for entry in section.entries:
            yield from entry.header_lines
            yield from entry.bullet_lines


def line_map(resume_ir: ResumeIR) -> dict[str, ResumeLine]:
    return {line.id: line for line in iter_lines(resume_ir)}
