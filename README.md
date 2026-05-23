# 🚀 Aakash Data Management Project (ADMP)
> *Because writing on paper is so 2005.*

---

## 🤯 What Is This?

A **zero-cost, fully automated, AI-powered enquiry management system** built for Aakash Institute — where a counselor just *talks* to a Telegram bot in casual Hinglish, and the entire data entry, storage, and team notification happens **automatically.**

No app. No form. No manual typing. Just chat.

---

## ⚡ The Magic in 10 Seconds

```
Father types casually on Telegram
          ↓
AI reads it (even if it's messy Hinglish)
          ↓
Structured data appears in Google Sheets
          ↓
Team gets notified instantly
          ↓
You close your laptop and go home
```

---

## 🧠 The Brain

| Model | Job |
|-------|-----|
| `llama-3.3-70b-versatile` | Reads text messages |
| `meta-llama/llama-4-scout-17b-16e-instruct` | Reads handwritten forms from photos |

Yes. It reads **handwriting.** From a photo. Taken on a phone. In bad lighting. And still gets it right.

---

## 🏗️ Project Structure

```
ADMP/
├── main.py          — The boss. Controls everything.
├── config.py        — Keeps secrets safe
├── parser.py        — The AI brain
├── sheets.py        — Talks to Google Sheets
├── notifier.py      — Pings the team
├── test.py          — Makes sure nothing is broken
├── credentials.json — Google's ID card (keep private!)
├── .env             — All the secret keys (NEVER share)
├── requirements.txt — All the tools needed
└── .gitignore       — Hides the secrets from GitHub
```

---

## 🎯 Features That Slap

- ✅ **Hinglish Support** — Type like you talk. AI understands.
- ✅ **Photo + Text** — Send a photo of the form AND add extra details in text. Bot merges both.
- ✅ **Never Guesses** — Missing info stays blank. No fake data. Ever.
- ✅ **Confirmation Step** — Father sees a preview before anything gets saved.
- ✅ **Smart Lead Detection** — Automatically figures out if it's a Walk In, Reference, Banner, etc.
- ✅ **Header-Safe Sheets** — Add/delete/reorder columns in the sheet anytime. Bot never breaks.
- ✅ **24/7 on Railway** — Runs forever. Even when the laptop is off.
- ✅ **Father-Only Access** — Unauthorized users get blocked instantly.
- ✅ **Team Notifications** — Internal Telegram group gets a beautiful formatted message every time.

---

## 📋 Data Captured Per Enquiry

```
📅 Date
👤 Student Name
👨‍👩‍👧 Parent Name
📞 Student Phone
📞 Parent Phone
📚 Class & Course
🎂 Gender & DOB
🏫 School
📍 Address
🔍 Lead Source
📝 Counseling Notes
⏰ Follow Up
⚠️  N/A (anything unrecognized)
```

---

## 🔔 What the Team Sees

Every enquiry triggers this in the internal group:

```
🆕 New Enquiry — 23 May 2026

👤 Student: Sonam Kakkar
👨‍👩‍👧 Parent: —
📞 Student Phone: 9958793545
📞 Parent Phone: —
📚 Class & Course: 9 | Foundation
🎂 Gender & DOB: Male | 20 Jun 2012
🏫 School: Matrikiran School
📍 Address: —
🔍 Lead Source: Fresh Walk In
📝 Notes: First time visit. Interested in Foundation.
⏰ Follow Up: 25 May 2026
```

Clean. Instant. No effort.

---

## 🛠️ Tech Stack

| Tool | Purpose | Cost |
|------|---------|------|
| Python | Core language | ₹0 |
| python-telegram-bot | Bot framework | ₹0 |
| Groq API | AI engine | ₹0 |
| Google Sheets API | Database | ₹0 |
| Railway | 24/7 hosting | ₹0 |
| GitHub | Version control | ₹0 |

### 💰 Total Monthly Cost: ₹0

---

## 🚀 Setup in 5 Steps

### 1. Clone the repo
```bash
git clone https://github.com/yourusername/Aakash-Data-Management-Project.git
cd Aakash-Data-Management-Project
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Fill in `.env`
```env
TELEGRAM_BOT_TOKEN=your_token
GROQ_API_KEY=your_groq_key
GOOGLE_SHEET_ID=your_sheet_id
AAKASH_GROUP_ID=your_group_id
FATHER_CHAT_ID=your_father_id
```

### 4. Add `credentials.json`
Download from Google Cloud service account and place in project root.

### 5. Run
```bash
python main.py
```

---

## 🧪 Testing

Test the AI parser without Telegram or Sheets:
```bash
# Mock test (no API key needed)
python test.py

# Live Groq test
python test.py --live
```

---

## 🔒 Security

- `.env` and `credentials.json` are in `.gitignore` — never pushed to GitHub
- Bot only responds to one authorized Telegram user
- Google Sheet access limited to service account only
- No student data stored anywhere except your own Google Sheet

---

## 🌐 Deploy 24/7 (Free)

1. Push to GitHub
2. Connect repo to **Railway.app**
3. Add environment variables in Railway dashboard
4. Deploy — runs forever

Your laptop can be off. In another city. Doesn't matter.

---

## 🗺️ Roadmap

- [ ] WhatsApp support
- [ ] Monthly analytics auto-report
- [ ] Follow-up reminder system
- [ ] Multi-branch support
- [ ] Management dashboard

---

## 👨‍💻 Built By

**Kushagra Bansal**
Built with 0 budget, 100% automation, and the energy of someone who never wants to do manual data entry again.

---

> *"The best automation is the one your father can use without any training."*

---

⭐ Star this repo if it saved you from spreadsheet hell.
