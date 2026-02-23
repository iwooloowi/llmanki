from __future__ import annotations

from telegram import Update
from telegram.ext import ContextTypes

from llmanki.bot import messages
from llmanki.storage.repositories import UserRepository


def _user_id(update: Update) -> int:
    if not update.effective_user:
        raise RuntimeError("Missing user")
    return update.effective_user.id


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_repo: UserRepository = context.application.bot_data["user_repo"]
    user = user_repo.get(_user_id(update))
    if user.deck_name:
        await update.message.reply_text("Send a word.")
    else:
        await update.message.reply_text(messages.welcome())


async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "Send a word to generate definition and example. Use /setdeck to change deck."
    )


async def setdeck(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(messages.ask_deck())
