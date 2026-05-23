"""Google Sheets integration — write rows by header name."""

from __future__ import annotations

import json
import os

import gspread
from google.oauth2.service_account import Credentials

import config

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]


def _worksheet():
    if not config.GOOGLE_SHEET_ID:
        raise ValueError("GOOGLE_SHEET_ID is not set in .env")

    credentials_json = os.getenv("GOOGLE_CREDENTIALS_JSON")
    if credentials_json:
        creds = Credentials.from_service_account_info(
            json.loads(credentials_json),
            scopes=SCOPES,
        )
    else:
        creds = Credentials.from_service_account_file(
            config.GOOGLE_CREDENTIALS_FILE,
            scopes=SCOPES,
        )
    client = gspread.authorize(creds)
    spreadsheet = client.open_by_key(config.GOOGLE_SHEET_ID)
    return spreadsheet.sheet1


def _header_map(headers: list[str]) -> dict[str, int]:
    return {name.strip(): idx for idx, name in enumerate(headers) if name.strip()}


def _split_gender_dob(combined: str) -> tuple[str, str]:
    """Split 'Male | 14 Oct 2010' into gender and DOB parts."""
    if not combined:
        return "", ""
    if "|" in combined:
        gender, dob = combined.split("|", 1)
        return gender.strip(), dob.strip()
    return combined.strip(), ""


def _write_gender_dob(
    row: list[str],
    col_map: dict[str, int],
    combined: str,
) -> None:
    """Write Gender & DOB to one column or separate Gender / DOB columns."""
    if "Gender & DOB" in col_map:
        row[col_map["Gender & DOB"]] = combined
        return

    gender, dob = _split_gender_dob(combined)
    if "Gender" in col_map:
        row[col_map["Gender"]] = gender
    if "DOB" in col_map:
        row[col_map["DOB"]] = dob


def append_enquiry(record: dict[str, str]) -> None:
    """Append one enquiry row aligned to sheet headers by name."""
    sheet = _worksheet()
    headers = sheet.row_values(1)
    if not headers:
        raise ValueError(
            "Sheet row 1 must contain column headers matching config.SHEET_COLUMNS"
        )

    col_map = _header_map(headers)
    row = [""] * len(headers)

    for key in config.SHEET_COLUMNS:
        value = record.get(key, "")
        if key == "Gender & DOB":
            _write_gender_dob(row, col_map, value)
        elif key in col_map:
            row[col_map[key]] = value

    sheet.append_row(row, value_input_option="USER_ENTERED")
