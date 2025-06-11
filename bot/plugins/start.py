from hydrogram import Client, filters
from hydrogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
)

from bot.utils import commands
from bot.utils.localization import Strings, use_chat_lang

from bot.utils.logger import loggerprint

from bot.database.global_ban import check_ban


from hydrogram.enums import ParseMode

# Using a low priority group so deeplinks will run before this and stop the propagation.
@Client.on_message(filters.command("start") & filters.private, group=2)
@Client.on_callback_query(filters.regex("^start_back$"))
@use_chat_lang
@check_ban
@loggerprint
async def start_pvt(c: Client, m: Message | CallbackQuery, s: Strings):
    if isinstance(m, CallbackQuery):
        msg = m.message
        send = msg.edit_text
    else:
        msg = m
        send = msg.reply_text

    await send(s("start_msg"), parse_mode=ParseMode.MARKDOWN)
