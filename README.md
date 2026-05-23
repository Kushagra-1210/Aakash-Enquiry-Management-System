# Aakash Enquiry Management System (AEMS)

AI-powered enquiry management system for Aakash Institute — converts unstructured counselor notes and handwritten forms into structured Google Sheets data, with instant team notifications via Telegram.

---

## Overview

Counselors at coaching institutes spend significant time on manual data entry after every student enquiry. AEMS eliminates this entirely. A counselor sends enquiry details (typed notes, Hinglish, or a photo of the registration form) to a Telegram bot. The AI parses it, shows a structured preview for confirmation, saves it to Google Sheets, and notifies the internal team — all in under 30 seconds.

---

## How It Works

```
Counselor sends text/photo → Telegram Bot
        ↓
AI parses and structures the data (Groq + Llama)
        ↓
Counselor reviews and confirms the preview
        ↓
Data saved to Google Sheets
        ↓
Internal team notified via Telegram group
```

---

## AI Models

| Model | Role |
|-------|------|
| `llama-3.3-70b-versatile` | Parses text-based enquiry notes |
| `meta-llama/llama-4-scout-17b-16e-instruct` | Extracts data from handwritten form photos |

The vision model handles handwritten Indian registration forms — including mixed Hindi/English fields, date/DOB disambiguation, and partial handwriting — with high accuracy.

---

## Features

- **Multimodal Input** — Accepts typed notes, Hinglish, photos of forms, or a combination
- **Zero Hallucination Policy** — Missing fields stay blank; the model never guesses
- **Confirmation Step** — Structured preview shown before any data is written
- **Smart Lead Source Detection** — Automatically classifies Walk In, Reference, Banner, Social Media, etc.
- **Header-Safe Sheet Writing** — Reads column headers dynamically; survives sheet restructuring
- **Access Control** — Bot responds only to the authorized Telegram user
- **Team Notifications** — Formatted enquiry summary posted to internal group on every save
- **24/7 Deployment** — Hosted on Railway; runs continuously without any local machine

---

## Data Captured Per Enquiry

| Field | Description |
|-------|-------------|
| Date | Enquiry/visit date |
| Student Name | Full name |
| Parent Name | Father/guardian name |
| Student Phone | Student contact number |
| Parent Phone | Parent contact number |
| Class & Course | e.g. `11 \| Medical (NEET)` |
| Gender & DOB | e.g. `Male \| 14 Oct 2010` |
| School | Current school name |
| Address | Residential address |
| Lead Source | Walk In / Reference / Banner / Social Media / Online / Telecaller |
| Counseling Notes | Fees, scholarships, discounts, remarks |
| Follow Up | Next follow-up date or action |
| N/A | Any useful detail that doesn't fit other columns |

---

## Tech Stack

| Tool | Purpose |
|------|---------|
| Python | Core language |
| python-telegram-bot | Bot framework |
| Groq API | LLM inference (free tier) |
| Google Sheets API | Data storage via gspread |
| Railway | 24/7 cloud hosting |
| GitHub | Version control |

**Total monthly infrastructure cost: ₹0**

---

## Project Structure

```
AEMS/
├── main.py          — Bot logic, session management, message handlers
├── config.py        — Environment variable loading and constants
├── parser.py        — Groq AI parsing for text and images
├── sheets.py        — Google Sheets integration
├── notifier.py      — Telegram group notification formatter
├── test.py          — Parser testing (mock and live modes)
├── requirements.txt — Dependencies
└── .gitignore       — Excludes credentials and secrets
```

---

## Setup

### 1. Clone the repository
```bash
git clone https://github.com/Kushagra-1210/Aakash-Data-Management-Project.git
cd Aakash-Data-Management-Project
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure environment variables
Create a `.env` file in the project root:
```env
TELEGRAM_BOT_TOKEN=your_token
GROQ_API_KEY=your_groq_key
GOOGLE_SHEET_ID=your_sheet_id
AAKASH_GROUP_ID=your_group_id
FATHER_CHAT_ID=your_authorized_chat_id
```

### 4. Add Google credentials
Download the service account JSON from Google Cloud Console and place it as `credentials.json` in the project root. For cloud deployment, set the `GOOGLE_CREDENTIALS_JSON` environment variable with the full JSON contents instead.

### 5. Run locally
```bash
python main.py
```

---

## Testing

```bash
# Mock test — no API keys required
python test.py

# Live test — uses real Groq API
python test.py --live
```

---

## Deployment (Railway)

1. Push repository to GitHub
2. Create a new project on [Railway](https://railway.app) and connect the repo
3. Add all environment variables from `.env` in the Railway dashboard
4. Add `GOOGLE_CREDENTIALS_JSON` with the full contents of `credentials.json`
5. Deploy — Railway runs the bot continuously

---

## Security

- `credentials.json` and `.env` are excluded from version control via `.gitignore`
- Bot enforces single-user access control via Telegram chat ID
- Google Sheet access is scoped to the service account only
- No student data is stored outside the organization's own Google Sheet

---

## Built By

**Kushagra Bansal**  
B.Tech CSE, Shiv Nadar University  
[GitHub](https://github.com/Kushagra-1210) · [LinkedIn](https://www.linkedin.com/in/kushagra-kb1210)