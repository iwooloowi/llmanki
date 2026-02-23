from __future__ import annotations

from telegram import Update
from telegram.ext import ContextTypes

from llmanki.bot import messages
from llmanki.storage.repositories import UserRepository
from llmanki.utils.rate_limit import get_rate_limit_status


def _user_id(update: Update) -> int:
    if not update.effective_user:
        raise RuntimeError("Missing user")
    return update.effective_user.id


def _require_message(update: Update):
    if not update.message:
        raise RuntimeError("Missing message")
    return update.message


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_repo: UserRepository = context.application.bot_data["user_repo"]
    user = user_repo.get(_user_id(update))
    message = _require_message(update)
    if user.deck_name:
        await message.reply_text("Send a word.")
    else:
        await message.reply_text(messages.welcome())


async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    message = _require_message(update)
    await message.reply_text(
        "Send a word to generate definition and example. "
        "Use /setdeck to change deck. Use /status to see usage."
    )


async def setdeck(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    message = _require_message(update)
    await message.reply_text(messages.ask_deck())


async def status(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_repo: UserRepository = context.application.bot_data["user_repo"]
    settings = context.application.bot_data["settings"]
    user = user_repo.get(_user_id(update))

    status_info = get_rate_limit_status(
        user,
        daily_quota=settings.daily_quota,
        cooldown_seconds=settings.cooldown_seconds,
    )
    message = _require_message(update)
    await message.reply_text(
        messages.status(user.deck_name, status_info.daily_remaining, status_info.cooldown_remaining)
    )
