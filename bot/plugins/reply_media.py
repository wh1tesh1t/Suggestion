import os
from hydrogram import Client, filters, types
from hydrogram.types import Message

from config import FORWARDING_CHAT, MAX_FILE_SIZE_BYTES, MEDIA_CAPTION_LIMIT, TEXT_MESSAGE_LIMIT

from bot.utils.localization import Strings, use_chat_lang
from bot.database.global_ban import check_ban
from bot.utils import commands

from bot.utils.logger import loggerprint

@Client.on_message(filters.command(["suggestpost","sp","r"]))
@use_chat_lang
@check_ban
@loggerprint
async def sendmedia(c: Client, m: types.Message, s: Strings):
    user = m.from_user
    user_name = user.username or user.first_name
    user_id = user.id

    text = ""
    if m.text:
        parts = m.text.split(maxsplit=1)
        if len(parts) > 1:
            text = parts[1]
    elif m.caption:
        parts = m.caption.split(maxsplit=1)
        if len(parts) > 1:
            text = parts[1]

    has_media = any(
        getattr(m, attr, None) is not None for attr in [
            'audio', 'photo', 'animation', 'document', 'video', 'voice'
        ]
    )

    if not has_media and not text:
        await m.reply_text(s("suggestpost_example"))
        return

    caption_content = s("suggestpost_info").format(user_name=user_name, user_id=user_id)
    if text:
        caption_content += s("suggestpost_text").format(text=text)

    media_types = {
        'audio': c.send_audio,
        'photo': c.send_photo,
        'animation': c.send_animation,
        'document': c.send_document,
        'video': c.send_video,
        'voice': c.send_voice
    }

    for attr, send_func in media_types.items():
        media = getattr(m, attr, None)
        if media:
            if media.file_size and media.file_size > MAX_FILE_SIZE_BYTES:
                await m.reply_text(s("suggestpost_file_too_large").format(limit_mb=MAX_FILE_SIZE_BYTES / (1024*1024)))
                return

            final_media_caption = caption_content
            if len(final_media_caption) > MEDIA_CAPTION_LIMIT:
                final_media_caption = final_media_caption[:MEDIA_CAPTION_LIMIT]

            file = await c.download_media(media)
            await send_func(
                chat_id=FORWARDING_CHAT,
                **{attr: file},
                caption=final_media_caption
            )
            await m.reply_text(s("suggestpost_sended"))
            os.remove(file)
            break
    else:
        final_text_message = caption_content
        if len(final_text_message) > TEXT_MESSAGE_LIMIT:
            final_text_message = final_text_message[:TEXT_MESSAGE_LIMIT]

        await c.send_message(
            chat_id=FORWARDING_CHAT,
            text=final_text_message
        )
        await m.reply_text(s("suggestpost_sended"))

commands.add_command("suggestpost", "general")
