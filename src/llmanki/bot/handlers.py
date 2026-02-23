from __future__ import annotations

from telegram import Update
from telegram.ext import CallbackQueryHandler, CommandHandler, ConversationHandler, MessageHandler, filters

from llmanki.bot import commands, conversations, keyboards


def build_handlers() -> list:
    convo = ConversationHandler(
        entry_points=[MessageHandler(filters.TEXT & ~filters.COMMAND, conversations.on_word)],
        states={
            conversations.State.ASK_DECK: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, conversations.on_deck)
            ],
            conversations.State.AWAIT_WORD: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, conversations.on_word)
            ],
            conversations.State.AWAIT_APPROVAL: [
                CallbackQueryHandler(conversations.on_approve, pattern=f"^{keyboards.APPROVE}$"),
                CallbackQueryHandler(
                    conversations.on_regenerate, pattern=f"^{keyboards.REGENERATE}$"
                ),
                CallbackQueryHandler(
                    conversations.on_other_meaning, pattern=f"^{keyboards.OTHER_MEANING}$"
                ),
                CallbackQueryHandler(conversations.on_cancel, pattern=f"^{keyboards.CANCEL}$"),
            ],
        },
        fallbacks=[CommandHandler("setdeck", commands.setdeck)],
    )

    return [
        CommandHandler("start", commands.start),
        CommandHandler("help", commands.help_cmd),
        CommandHandler("setdeck", commands.setdeck),
        convo,
    ]
