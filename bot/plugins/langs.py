from __future__ import annotations

from itertools import zip_longest

from hydrogram import Client, filters
from hydrogram.enums import ChatType
from hydrogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
)

from bot.database.localization import set_db_lang
from bot.utils.decorators import require_admin
from bot.utils.localization import Strings, langdict, use_chat_lang

from bot.utils.logger import loggerprint

from bot.database.global_ban import check_ban

def gen_langs_kb():
    return [
        [
            InlineKeyboardButton(
                f"{langdict[lang]['_meta_language_flag']} {langdict[lang]['_meta_language_name']}",
                callback_data=f"set_lang {lang}",
            )
            for lang in langs
            if lang
        ]
        for langs in zip_longest(*[iter(langdict)] * 2)
    ]


@Client.on_callback_query(filters.regex("^chlang$"))
@Client.on_message(filters.command(["setchatlang", "setlang"]) & filters.group)
@require_admin(allow_in_private=True)
@use_chat_lang
@check_ban
@loggerprint
async def chlang(c: Client, m: CallbackQuery | Message, s: Strings):
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            *gen_langs_kb(),
            [InlineKeyboardButton(s("general_back_btn"), callback_data="menu_back")],
        ]
    )

    if isinstance(m, CallbackQuery):
        msg = m.message
        sender = msg.edit_text
    else:
        msg = m
        sender = msg.reply_text

    res = (
        s("language_changer_private")
        if msg.chat.type == ChatType.PRIVATE
        else s("language_changer_chat")
    )

    await sender(res, reply_markup=keyboard)


@Client.on_callback_query(filters.regex("^set_lang "))
@require_admin(allow_in_private=True)
@check_ban
@loggerprint
async def set_chat_lang(c: Client, m: CallbackQuery):
    lang = m.data.split()[1]
    await set_db_lang(m.message.chat.id, m.message.chat.type, lang)

    await set_chat_lang_edit(c, m)


@use_chat_lang
@check_ban
@loggerprint
async def set_chat_lang_edit(c: Client, m: CallbackQuery, s: Strings):
    if m.message.chat.type == ChatType.PRIVATE:
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        s("general_back_btn"),
                        callback_data="start_back",
                    )
                ]
            ]
        )
    else:
        keyboard = None
    await m.message.edit_text(s("language_changed_successfully"), reply_markup=keyboard)
