"""Format and send enquiry notifications to the internal Telegram group."""

from __future__ import annotations

from telegram import Bot

import config


def format_notification(record: dict[str, str]) -> str:
    """Build the group notification message."""
    date = record.get("Date", "") or "—"
    return (
        f"🆕 New Enquiry — {date}\n"
        f"👤 Student: {record.get('Student Name', '') or '—'}\n"
        f"👨‍👩‍👧 Parent: {record.get('Parent Name', '') or '—'}\n"
        f"📞 Student Phone: {record.get('Student Phone', '') or '—'}\n"
        f"📞 Parent Phone: {record.get('Parent Phone', '') or '—'}\n"
        f"📚 Class & Course: {record.get('Class & Course', '') or '—'}\n"
        f"🎂 Gender & DOB: {record.get('Gender & DOB', '') or '—'}\n"
        f"🏫 School: {record.get('School', '') or '—'}\n"
        f"📍 Address: {record.get('Address', '') or '—'}\n"
        f"🔍 Lead Source: {record.get('Lead Source', '') or '—'}\n"
        f"📝 Notes: {record.get('Counseling Notes', '') or '—'}\n"
        f"⏰ Follow Up: {record.get('Follow Up', '') or '—'}"
    )


async def send_group_notification(bot: Bot, record: dict[str, str]) -> None:
    """Post formatted enquiry to the Aakash internal group."""
    if not config.AAKASH_GROUP_ID:
        raise ValueError("AAKASH_GROUP_ID is not set in .env")

    message = format_notification(record)
    await bot.send_message(
        chat_id=int(config.AAKASH_GROUP_ID),
        text=message,
    )
