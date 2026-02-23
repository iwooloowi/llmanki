from __future__ import annotations

from enum import IntEnum
from typing import Optional

from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler

from llmanki.bot import keyboards, messages
from llmanki.domain.card_builder import build_basic_cards
from llmanki.storage.repositories import PendingRepository, UserRepository
from llmanki.utils.rate_limit import check_and_update
from llmanki.workflows.create_cards import format_preview


class State(IntEnum):
    ASK_DECK = 1
    AWAIT_WORD = 2
    AWAIT_APPROVAL = 3


def _user_id(update: Update) -> int:
    if not update.effective_user:
        raise RuntimeError("Missing user")
    return update.effective_user.id


async def on_deck(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_repo: UserRepository = context.application.bot_data["user_repo"]
    deck_manager = context.application.bot_data["deck_manager"]

    deck_name = (update.message.text or "").strip()
    if not deck_name:
        await update.message.reply_text(messages.ask_deck())
        return State.ASK_DECK

    exists = await deck_manager.ensure_deck(deck_name)
    if not exists:
        await update.message.reply_text(messages.deck_not_found(deck_name))
        return State.ASK_DECK

    user_repo.set_deck(_user_id(update), deck_name)
    await update.message.reply_text(messages.deck_set(deck_name))
    return State.AWAIT_WORD


async def on_word(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_repo: UserRepository = context.application.bot_data["user_repo"]
    pending_repo: PendingRepository = context.application.bot_data["pending_repo"]
    generator = context.application.bot_data["example_generator"]
    settings = context.application.bot_data["settings"]

    user = user_repo.get(_user_id(update))
    if not user.deck_name:
        await update.message.reply_text(messages.ask_deck())
        return State.ASK_DECK

    word = (update.message.text or "").strip()
    if not word:
        return State.AWAIT_WORD

    rl = check_and_update(
        user,
        daily_quota=settings.daily_quota,
        cooldown_seconds=settings.cooldown_seconds,
    )
    if not rl.allowed:
        if rl.reason == "cooldown" and rl.retry_after is not None:
            await update.message.reply_text(messages.cooldown(rl.retry_after))
        elif rl.reason == "quota":
            await update.message.reply_text(messages.quota_exceeded())
        return State.AWAIT_WORD

    user_repo.update_usage(user.user_id, daily_count=rl.daily_count, last_request_ts=rl.last_request_ts)

    await update.message.reply_text(messages.generating())
    gen = await generator.generate(word)
    pending_repo.upsert(user.user_id, gen, regen_count=0, meaning_hint=None)

    await update.message.reply_text(
        f"{messages.preview_header()}\n\n{format_preview(gen)}",
        reply_markup=keyboards.approval_keyboard(),
    )
    return State.AWAIT_APPROVAL


async def _regenerate(update: Update, context: ContextTypes.DEFAULT_TYPE, meaning_hint: Optional[str]) -> int:
    pending_repo: PendingRepository = context.application.bot_data["pending_repo"]
    generator = context.application.bot_data["example_generator"]
    settings = context.application.bot_data["settings"]

    user_id = _user_id(update)
    pending = pending_repo.get(user_id)
    if not pending:
        await update.callback_query.answer()
        await update.callback_query.edit_message_text(messages.no_pending())
        return State.AWAIT_WORD

    if pending.regen_count >= settings.max_regenerations:
        await update.callback_query.answer()
        await update.callback_query.edit_message_text(messages.regen_limit_reached())
        return State.AWAIT_APPROVAL

    await update.callback_query.answer()
    gen = await generator.generate(pending.generation.word, meaning_hint=meaning_hint)
    pending_repo.upsert(
        user_id,
        gen,
        regen_count=pending.regen_count + 1,
        meaning_hint=meaning_hint,
    )

    await update.callback_query.edit_message_text(
        f"{messages.preview_header()}\n\n{format_preview(gen)}",
        reply_markup=keyboards.approval_keyboard(),
    )
    return State.AWAIT_APPROVAL


async def on_regenerate(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    return await _regenerate(update, context, meaning_hint=None)


async def on_other_meaning(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    return await _regenerate(update, context, meaning_hint="Use a different meaning from before.")


async def on_approve(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_repo: UserRepository = context.application.bot_data["user_repo"]
    pending_repo: PendingRepository = context.application.bot_data["pending_repo"]
    deck_manager = context.application.bot_data["deck_manager"]

    user_id = _user_id(update)
    pending = pending_repo.get(user_id)
    if not pending:
        await update.callback_query.answer()
        await update.callback_query.edit_message_text(messages.no_pending())
        return State.AWAIT_WORD

    user = user_repo.get(user_id)
    if not user.deck_name:
        await update.callback_query.answer()
        await update.callback_query.edit_message_text(messages.ask_deck())
        return State.ASK_DECK

    cards = build_basic_cards(pending.generation)
    await deck_manager.add_cards(user.deck_name, cards)
    await deck_manager.sync()
    pending_repo.clear(user_id)

    await update.callback_query.answer()
    await update.callback_query.edit_message_text(messages.approved())
    return State.AWAIT_WORD


async def on_cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    pending_repo: PendingRepository = context.application.bot_data["pending_repo"]
    pending_repo.clear(_user_id(update))
    await update.callback_query.answer()
    await update.callback_query.edit_message_text(messages.cancelled())
    return State.AWAIT_WORD
