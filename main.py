"""Aakash Institute enquiry Telegram bot."""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from enum import Enum

from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

import config
import notifier
import parser
import sheets

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)


class SessionState(str, Enum):
    COLLECTING = "collecting"
    AWAITING_CONFIRM = "awaiting_confirm"


@dataclass
class UserSession:
    state: SessionState = SessionState.COLLECTING
    text_parts: list[str] = field(default_factory=list)
    images: list[tuple[bytes, str]] = field(default_factory=list)
    pending_record: dict[str, str] | None = None


def _is_father(chat_id: int) -> bool:
    return str(chat_id) == config.FATHER_CHAT_ID


def _get_session(context: ContextTypes.DEFAULT_TYPE, chat_id: int) -> UserSession:
    sessions: dict[int, UserSession] = context.application.bot_data.setdefault(
        "sessions", {}
    )
    if chat_id not in sessions:
        sessions[chat_id] = UserSession()
    return sessions[chat_id]


def _reset_session(session: UserSession) -> None:
    session.state = SessionState.COLLECTING
    session.text_parts = []
    session.images = []
    session.pending_record = None


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.effective_chat or not update.message:
        return
    if not _is_father(update.effective_chat.id):
        await update.message.reply_text(
            "This bot is for authorized Aakash counseling staff only."
        )
        return
    _reset_session(_get_session(context, update.effective_chat.id))
    await update.message.reply_text(
        "Send enquiry details (text and/or photos). "
        "When finished, type *Done*.",
        parse_mode="Markdown",
    )


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.effective_chat or not update.message:
        return

    chat_id = update.effective_chat.id
    if not _is_father(chat_id):
        await update.message.reply_text("You are not authorized to use this bot.")
        return

    session = _get_session(context, chat_id)

    if session.state == SessionState.AWAITING_CONFIRM:
        await _handle_confirmation(update, context, session)
        return

    text = (update.message.text or update.message.caption or "").strip()

    if text.lower() == "done":
        await _process_done(update, context, session)
        return

    if update.message.photo:
        try:
            photo = update.message.photo[-1]
            file = await context.bot.get_file(photo.file_id)
            image_bytes = bytes(await file.download_as_bytearray())
            session.images.append((image_bytes, "image/jpeg"))
        except Exception as exc:
            logger.exception("Failed to download photo")
            await update.message.reply_text(
                f"Could not download the photo. Please try again.\n({exc})"
            )
            return

    if text and text.lower() != "done":
        session.text_parts.append(text)

    if not text and not update.message.photo:
        await update.message.reply_text(
            "Send text or a photo, then type *Done* when finished.",
            parse_mode="Markdown",
        )
        return

    await update.message.reply_text("Added. Send more or type *Done*.", parse_mode="Markdown")


async def _process_done(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    session: UserSession,
) -> None:
    if not session.text_parts and not session.images:
        await update.message.reply_text(
            "Nothing to process yet. Send text or photos first."
        )
        return

    await update.message.reply_text("Processing with AI… please wait.")

    try:
        record = parser.parse_enquiry(session.text_parts, session.images)
    except Exception as exc:
        logger.exception("Parsing failed")
        await update.message.reply_text(
            f"Sorry, AI parsing failed. Please try again.\nError: {exc}"
        )
        return

    session.pending_record = record
    session.state = SessionState.AWAITING_CONFIRM

    await update.message.reply_text(
        parser.format_preview(record),
        parse_mode="Markdown",
    )


async def _handle_confirmation(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    session: UserSession,
) -> None:
    if not update.message:
        return

    reply = (update.message.text or "").strip().upper()

    if reply == "YES" and session.pending_record:
        record = session.pending_record
        await update.message.reply_text("Saving enquiry…")

        try:
            sheets.append_enquiry(record)
        except Exception as exc:
            logger.exception("Sheets save failed")
            await update.message.reply_text(
                f"Could not save to Google Sheet.\nError: {exc}"
            )
            return

        try:
            await notifier.send_group_notification(context.bot, record)
        except Exception as exc:
            logger.exception("Group notification failed")
            await update.message.reply_text(
                "Saved to sheet, but group notification failed.\n"
                f"Error: {exc}"
            )
            _reset_session(session)
            return

        _reset_session(session)
        await update.message.reply_text(
            "✅ Enquiry saved and team notified. Send the next enquiry anytime."
        )
        return

    await update.message.reply_text(
        "Cancelled. Send corrected text/photos, then type *Done* again.",
        parse_mode="Markdown",
    )
    session.state = SessionState.COLLECTING
    session.pending_record = None


def _validate_config() -> list[str]:
    missing = []
    for name, value in [
        ("TELEGRAM_BOT_TOKEN", config.TELEGRAM_BOT_TOKEN),
        ("GROQ_API_KEY", config.GROQ_API_KEY),
        ("GOOGLE_SHEET_ID", config.GOOGLE_SHEET_ID),
        ("AAKASH_GROUP_ID", config.AAKASH_GROUP_ID),
        ("FATHER_CHAT_ID", config.FATHER_CHAT_ID),
    ]:
        if not value:
            missing.append(name)
    return missing


def main() -> None:
    missing = _validate_config()
    if missing:
        raise SystemExit(f"Missing required .env values: {', '.join(missing)}")

    app = (
        Application.builder()
        .token(config.TELEGRAM_BOT_TOKEN)
        .build()
    )

    app.add_handler(CommandHandler("start", start))
    app.add_handler(
        MessageHandler(
            filters.ChatType.PRIVATE & (filters.TEXT | filters.PHOTO),
            handle_message,
        )
    )

    logger.info("Aakash enquiry bot started")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
