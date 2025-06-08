from hydrogram import Client, filters
from hydrogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
)

from bot.utils import commands
from bot.utils.localization import Strings, use_chat_lang

from bot.database.global_ban import check_ban


from hydrogram.enums import ParseMode

# Using a low priority group so deeplinks will run before this and stop the propagation.
@Client.on_message(filters.command("menu") & filters.private, group=2)
@Client.on_callback_query(filters.regex("^menu_back$"))
@use_chat_lang
@check_ban
async def menu_pr(c: Client, m: Message | CallbackQuery, s: Strings):
    if isinstance(m, CallbackQuery):
        msg = m.message
        send = msg.edit_text
    else:
        msg = m
        send = msg.reply_text

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(s("menu_commands_btn"), callback_data="commands"),
            ],
            [
                InlineKeyboardButton(s("menu_language_btn"), callback_data="chlang"),
            ],
        ]
    )
    await send(s("menu_msg"), reply_markup=keyboard, parse_mode=ParseMode.MARKDOWN)


@Client.on_message(filters.command("menu") & filters.group, group=2)
@use_chat_lang
@check_ban
async def menu_gr(c: Client, m: Message | CallbackQuery, s: Strings):
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    s("menu_start_chat"),
                    url=f"https://t.me/{c.me.username}?start=start",
                )
            ]
        ]
    )
    await m.reply_text(s("menu_msg"), reply_markup=keyboard, parse_mode=ParseMode.MARKDOWN)

commands.add_command("menu", "info")
