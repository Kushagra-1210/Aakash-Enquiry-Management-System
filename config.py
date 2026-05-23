"""Load configuration from environment variables."""

import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent / ".env")

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "").strip()
GOOGLE_SHEET_ID = os.getenv("GOOGLE_SHEET_ID", "").strip()
AAKASH_GROUP_ID = os.getenv("AAKASH_GROUP_ID", "").strip()
FATHER_CHAT_ID = os.getenv("FATHER_CHAT_ID", "").strip()

TEXT_MODEL = "llama-3.3-70b-versatile"
IMAGE_MODEL = "meta-llama/llama-4-scout-17b-16e-instruct"

GOOGLE_CREDENTIALS_FILE = os.getenv(
    "GOOGLE_CREDENTIALS_FILE",
    str(Path(__file__).resolve().parent / "credentials.json"),
).strip()

SHEET_COLUMNS = [
    "Date",
    "Student Name",
    "Parent Name",
    "Student Phone",
    "Parent Phone",
    "Class & Course",
    "Gender & DOB",
    "School",
    "Address",
    "Lead Source",
    "Counseling Notes",
    "Follow Up",
    "N/A",
]

LEAD_SOURCES = [
    "Fresh Walk In",
    "Reference",
    "School Contact",
    "Banner",
    "Social Media",
    "Online",
    "Telecaller",
    "Other",
]

# Substrings (lowercase) mapped to canonical lead source after AI parse
LEAD_SOURCE_ALIASES: dict[str, str] = {
    "walk in": "Fresh Walk In",
    "walk-in": "Fresh Walk In",
    "walkin": "Fresh Walk In",
    "reference": "Reference",
    "referred": "Reference",
    "school contact": "School Contact",
    "school visit": "School Contact",
    "banner": "Banner",
    "hoarding": "Banner",
    "social media": "Social Media",
    "instagram": "Social Media",
    "facebook": "Social Media",
    "youtube": "Social Media",
    "whatsapp status": "Social Media",
    "online": "Online",
    "website": "Online",
    "google": "Online",
    "telecaller": "Telecaller",
    "tele caller": "Telecaller",
    "telecalling": "Telecaller",
    "tele call": "Telecaller",
    "outbound call": "Telecaller",
    "calling team": "Telecaller",
}
