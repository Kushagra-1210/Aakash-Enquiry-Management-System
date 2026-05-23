"""Groq AI parsing for enquiry text and images."""

from __future__ import annotations

import base64
import json
import re
from datetime import datetime
from typing import Any

from groq import Groq

import config

FIELDS = config.SHEET_COLUMNS


def _system_prompt() -> str:
    lead_list = ", ".join(config.LEAD_SOURCES)
    return f"""You extract Aakash Institute student enquiry data from counselor notes.
Input may be Hindi, English, or Hinglish (text and/or registration form images).

Return ONLY a single JSON object with exactly these keys (use empty string "" if unknown — NEVER guess):
Date, Student Name, Parent Name, Student Phone, Parent Phone, Class & Course, Gender & DOB, School, Address, Lead Source, Counseling Notes, Follow Up, N/A

Rules:
- Lead Source: detect from context only. Use exactly one of: {lead_list}. Empty if unclear.
  Hints:
  • Fresh Walk In — direct center visit, walk-in, bina appointment aaya
  • Reference — kisi student/parent/staff ne refer kiya
  • School Contact — school visit, principal, school program
  • Banner — banner, hoarding, mall/outdoor ad
  • Social Media — Instagram, Facebook, YouTube, WhatsApp status
  • Online — website, Google, online form, digital ad
  • Telecaller — telecaller/telecalling team ki call, outbound call, caller se enquiry aayi
  • Other — source clear hai par upar ki list me nahi aata
- Class & Course format examples: "9 | Foundation", "FS | First Step", "11 | Medical (NEET)", "12 | Engineering (JEE)"
- Aakash courses: Foundation, Medical (NEET), Engineering (JEE), Integrated, First Step, Achiever
- Gender & DOB format: "Male | 14 Oct 2010" (or Female | date)
- Counseling Notes: fees discussed, scholarships, discounts, special remarks
- N/A: any useful detail that does not fit other columns
- Date: use enquiry/visit date if mentioned, else today's date in format "21 May 2026"
- Phone numbers: digits only or as written on form
- No markdown, no explanation, only valid JSON"""


def _image_system_prompt() -> str:
    lead_list = ", ".join(config.LEAD_SOURCES)
    return f"""You are an expert at reading handwritten Indian coaching institute enquiry forms, just like a highly experienced human data entry operator. You have perfect understanding of form layouts, handwriting variations, and context.

You are reading a PHOTO of an Aakash Institute enquiry/registration form. Input may be Hindi, English, or Hinglish.

Return ONLY a single JSON object with exactly these keys (use empty string "" if unknown — NEVER guess):
Date, Student Name, Parent Name, Student Phone, Parent Phone, Class & Course, Gender & DOB, School, Address, Lead Source, Counseling Notes, Follow Up, N/A

Key intelligence rules:

FORM STRUCTURE UNDERSTANDING:
- Forms have multiple sections: header info, student details, parent details, academic details, visit details
- The DATE at the very top of the form (near Sr.No) is always the ENQUIRY DATE — put in "Date". Never confuse it with DOB
- DOB appears inside student details section, usually written as "D.O.B", "Date of Birth", "DOB" followed by a date — put in "Gender & DOB" with gender, never in "Date"
- Always read the field LABEL on the left to understand what the value on the right means

HANDWRITING INTELLIGENCE:
- Read handwriting contextually — if a number appears next to "Mobile" it is a phone number even if hard to read
- Common handwriting confusions to handle: 1/7, 0/6, 5/S, 4/9, 8/3 — use context to pick the right one
- Names may have initials before them like "f Sonam" — the initial is a title/prefix, actual name is "Sonam"
- Superscript letters like "9th" mean class 9, "10th" means class 10
- Partially filled or messy fields — extract whatever is readable
- Gender M = Male, F = Female — format "Gender & DOB" as "Male | 20 June 2012"

FIELD MAPPING FOR AAKASH FORMS:
- First Name + Last Name combined = Student Name
- Mobile Number / Student Mobile = Student Phone
- Father Mobile / Parent Mobile / Father's Mobile No = Parent Phone
- Father Name / Father's Name = Parent Name
- Class Studying In / Class Going To / Current Class = extract the class number
- Stream = part of course (Medical=NEET, Engineering=JEE, Foundation=class 6-10) — format "Class & Course" as "9 | Foundation" or "11 | Medical (NEET)" when stream is clear
- School Name / School = School
- Address / Residential Address = Address
- Visit Type "First Time Visit" checked = Lead Source "Fresh Walk In"
- Visit Type "Second Time Visit" checked = Lead Source "Reference"
- IACST / Scholarship Test score = put in Counseling Notes
- Lead Source (if not from Visit Type): use exactly one of: {lead_list}. Empty if unclear

CONTEXT AWARENESS:
- If DOB says "20 June 2012" and enquiry date says "17/5" — enquiry date is 17 May current year, DOB is 20 June 2012
- If class is 9th and DOB is 2012 — this makes sense, do not swap them
- Indian phone numbers are always 10 digits starting with 6/7/8/9
- Indian names follow patterns — use this to separate first/last names correctly
- Dates in India are usually DD/MM/YYYY format unless written in full like "20 June 2012"

EMPTY FIELDS:
- If a field is blank or has just a dash, return empty string
- Never invent or guess data that is not visible
- If handwriting is completely illegible for a field, return empty string

OUTPUT:
- Return only valid JSON with the standard keys listed above
- No explanation, no markdown, no extra text
- Cross-verify extracted data makes logical sense before returning
- Put any detail that does not fit other columns in "N/A\""""


def _empty_record() -> dict[str, str]:
    return {key: "" for key in FIELDS}


def _client() -> Groq:
    if not config.GROQ_API_KEY:
        raise ValueError("GROQ_API_KEY is not set in .env")
    return Groq(api_key=config.GROQ_API_KEY)


def _extract_json(text: str) -> dict[str, Any]:
    text = text.strip()
    if not text:
        return _empty_record()

    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        match = re.search(r"\{[\s\S]*\}", text)
        if not match:
            return _empty_record()
        data = json.loads(match.group())

    return _normalize_record(data)


def _normalize_record(data: dict[str, Any]) -> dict[str, str]:
    record = _empty_record()
    for key in FIELDS:
        value = data.get(key, data.get(key.replace(" ", "_"), ""))
        if value is None:
            record[key] = ""
        else:
            record[key] = str(value).strip()

    if not record["Date"]:
        record["Date"] = datetime.now().strftime("%d %b %Y")

    record["Lead Source"] = _normalize_lead_source(record["Lead Source"])
    return record


def _normalize_lead_source(value: str) -> str:
    """Map AI output to a canonical lead source label."""
    if not value:
        return ""

    cleaned = value.strip()
    if cleaned in config.LEAD_SOURCES:
        return cleaned

    lowered = cleaned.lower()
    for alias, canonical in config.LEAD_SOURCE_ALIASES.items():
        if alias in lowered:
            return canonical

    for source in config.LEAD_SOURCES:
        if source.lower() in lowered or lowered in source.lower():
            return source

    return cleaned


def parse_text(text: str) -> dict[str, str]:
    """Parse plain text enquiry notes via Groq text model."""
    if not text.strip():
        return _empty_record()

    client = _client()
    response = client.chat.completions.create(
        model=config.TEXT_MODEL,
        messages=[
            {"role": "system", "content": _system_prompt()},
            {
                "role": "user",
                "content": f"Extract enquiry fields from this counselor input:\n\n{text}",
            },
        ],
        response_format={"type": "json_object"},
        temperature=0.1,
    )
    content = response.choices[0].message.content or "{}"
    return _extract_json(content)


def parse_image(image_bytes: bytes, mime_type: str = "image/jpeg") -> dict[str, str]:
    """Parse a registration form or photo via Groq vision model."""
    if not image_bytes:
        return _empty_record()

    b64 = base64.standard_b64encode(image_bytes).decode("utf-8")
    data_url = f"data:{mime_type};base64,{b64}"

    client = _client()
    response = client.chat.completions.create(
        model=config.IMAGE_MODEL,
        messages=[
            {"role": "system", "content": _image_system_prompt()},
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": (
                            "Extract all enquiry fields from this Aakash Institute "
                            "enquiry form image. Follow the form layout rules exactly. "
                            "Return JSON only."
                        ),
                    },
                    {"type": "image_url", "image_url": {"url": data_url}},
                ],
            },
        ],
        response_format={"type": "json_object"},
        temperature=0.1,
    )
    content = response.choices[0].message.content or "{}"
    return _extract_json(content)


def merge_parsed(*records: dict[str, str]) -> dict[str, str]:
    """Merge multiple parse results; prefer non-empty, combine notes when both differ."""
    merged = _empty_record()
    combine_keys = {"Counseling Notes", "N/A"}

    for record in records:
        for key in FIELDS:
            new_val = (record.get(key) or "").strip()
            if not new_val:
                continue
            old_val = merged[key]
            if not old_val:
                merged[key] = new_val
            elif old_val == new_val:
                continue
            elif key in combine_keys:
                merged[key] = f"{old_val}; {new_val}"
            else:
                merged[key] = new_val

    if not merged["Date"]:
        merged["Date"] = datetime.now().strftime("%d %b %Y")

    return merged


def parse_enquiry(text_parts: list[str], images: list[tuple[bytes, str]]) -> dict[str, str]:
    """Parse all text and images, then merge into one record."""
    results: list[dict[str, str]] = []

    combined_text = "\n\n".join(t.strip() for t in text_parts if t.strip())
    if combined_text:
        results.append(parse_text(combined_text))

    for image_bytes, mime_type in images:
        results.append(parse_image(image_bytes, mime_type))

    if not results:
        return _empty_record()

    return merge_parsed(*results)


def format_preview(record: dict[str, str]) -> str:
    """Human-readable preview for confirmation (MarkdownV2-safe)."""
    from telegram.helpers import escape_markdown

    lines = ["📋 *Extracted enquiry preview*\n"]
    for key in FIELDS:
        value = record.get(key, "") or "—"
        lines.append(
            f"*{escape_markdown(key, version=2)}:* "
            f"{escape_markdown(value, version=2)}"
        )
    lines.append(
        "\nReply *YES* to save, or send corrections and type *Done* again\\."
    )
    return "\n".join(lines)
