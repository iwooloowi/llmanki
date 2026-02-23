from __future__ import annotations

from telegram import InlineKeyboardButton, InlineKeyboardMarkup


APPROVE = "approve"
REGENERATE = "regenerate"
OTHER_MEANING = "other_meaning"
CANCEL = "cancel"


def approval_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("Approve", callback_data=APPROVE)],
            [InlineKeyboardButton("Regenerate", callback_data=REGENERATE)],
            [InlineKeyboardButton("Other meaning", callback_data=OTHER_MEANING)],
            [InlineKeyboardButton("Cancel", callback_data=CANCEL)],
        ]
    )
