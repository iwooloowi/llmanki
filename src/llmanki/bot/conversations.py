from __future__ import annotations

from enum import IntEnum
from typing import Optional

from telegram import Update
from telegram.ext import ContextTypes

from llmanki.bot import keyboards, messages
from llmanki.domain.card_builder import build_basic_cards
from llmanki.services.anki_connect import AnkiConnectError
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


def _require_message(update: Update):
    if not update.message:
        raise RuntimeError("Missing message")
    return update.message


def _require_callback(update: Update):
    if not update.callback_query:
        raise RuntimeError("Missing callback query")
    return update.callback_query


async def on_setdeck(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    message = _require_message(update)
    await message.reply_text(messages.ask_deck())
    return State.ASK_DECK


async def on_deck(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_repo: UserRepository = context.application.bot_data["user_repo"]
    deck_manager = context.application.bot_data["deck_manager"]

    message = _require_message(update)
    deck_name = (message.text or "").strip()
    if not deck_name:
        await message.reply_text(messages.ask_deck())
        return State.ASK_DECK

    try:
        exists = await deck_manager.ensure_deck(deck_name)
    except AnkiConnectError:
        await message.reply_text(messages.anki_unavailable())
        return State.ASK_DECK
    if not exists:
        await message.reply_text(messages.deck_not_found(deck_name))
        return State.ASK_DECK

    user_repo.set_deck(_user_id(update), deck_name)
    await message.reply_text(messages.deck_set(deck_name))
    return State.AWAIT_WORD


async def on_word(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_repo: UserRepository = context.application.bot_data["user_repo"]
    pending_repo: PendingRepository = context.application.bot_data["pending_repo"]
    generator = context.application.bot_data["example_generator"]
    settings = context.application.bot_data["settings"]

    message = _require_message(update)
    user = user_repo.get(_user_id(update))
    if not user.deck_name:
        await message.reply_text(messages.ask_deck())
        return State.ASK_DECK

    word = (message.text or "").strip()
    if not word:
        return State.AWAIT_WORD

    rl = check_and_update(
        user,
        daily_quota=settings.daily_quota,
        cooldown_seconds=settings.cooldown_seconds,
    )
    if not rl.allowed:
        if rl.reason == "cooldown" and rl.retry_after is not None:
            await message.reply_text(messages.cooldown(rl.retry_after))
        elif rl.reason == "quota":
            await message.reply_text(messages.quota_exceeded())
        return State.AWAIT_WORD

    user_repo.update_usage(
        user.user_id, daily_count=rl.daily_count, last_request_ts=rl.last_request_ts
    )

    await message.reply_text(messages.generating())
    try:
        gen = await generator.generate(word)
    except Exception:
        await message.reply_text(messages.generation_failed())
        return State.AWAIT_WORD
    pending_repo.upsert(user.user_id, gen, regen_count=0, meaning_hint=None)

    await message.reply_text(
        f"{messages.preview_header()}\n\n{format_preview(gen)}",
        reply_markup=keyboards.approval_keyboard(),
    )
    return State.AWAIT_APPROVAL


async def _regenerate(
    update: Update, context: ContextTypes.DEFAULT_TYPE, meaning_hint: Optional[str]
) -> int:
    pending_repo: PendingRepository = context.application.bot_data["pending_repo"]
    generator = context.application.bot_data["example_generator"]
    settings = context.application.bot_data["settings"]

    user_id = _user_id(update)
    callback = _require_callback(update)
    pending = pending_repo.get(user_id)
    if not pending:
        await callback.answer()
        await callback.edit_message_text(messages.no_pending())
        return State.AWAIT_WORD

    if pending.regen_count >= settings.max_regenerations:
        await callback.answer()
        await callback.edit_message_text(messages.regen_limit_reached())
        return State.AWAIT_APPROVAL

    await callback.answer()
    gen = await generator.generate(pending.generation.word, meaning_hint=meaning_hint)
    pending_repo.upsert(
        user_id,
        gen,
        regen_count=pending.regen_count + 1,
        meaning_hint=meaning_hint,
    )

    await callback.edit_message_text(
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
    callback = _require_callback(update)
    pending = pending_repo.get(user_id)
    if not pending:
        await callback.answer()
        await callback.edit_message_text(messages.no_pending())
        return State.AWAIT_WORD

    user = user_repo.get(user_id)
    if not user.deck_name:
        await callback.answer()
        await callback.edit_message_text(messages.ask_deck())
        return State.ASK_DECK

    cards = build_basic_cards(pending.generation)
    try:
        await deck_manager.add_cards(user.deck_name, cards)
        await deck_manager.sync()
    except AnkiConnectError:
        await callback.answer()
        await callback.edit_message_text(
            messages.anki_unavailable(),
            reply_markup=keyboards.approval_keyboard(),
        )
        return State.AWAIT_APPROVAL
    pending_repo.clear(user_id)

    await callback.answer()
    await callback.edit_message_text(messages.approved())
    return State.AWAIT_WORD


async def on_cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    pending_repo: PendingRepository = context.application.bot_data["pending_repo"]
    pending_repo.clear(_user_id(update))
    callback = _require_callback(update)
    await callback.answer()
    await callback.edit_message_text(messages.cancelled())
    return State.AWAIT_WORD
