from functools import wraps
from hydrogram.types import Message, CallbackQuery

LOGGER_TEXT_LIMIT = 100

def loggerprint(func):
    @wraps(func)
    async def loggerw(client, update, *args, **kwargs):
        user_id = update.from_user.id if update.from_user else "N/A"
        username = update.from_user.username if update.from_user and update.from_user.username else "N/A"
        user_full_name = update.from_user.full_name if update.from_user else "N/A"

        chat_id = "N/A"
        chat_type = "UNKNOWN"
        oinfo = ""

        if isinstance(update, Message):
            chat_id = update.chat.id
            chat_type = update.chat.type.name if update.chat.type else "UNKNOWN"
            content = update.text if update.text else (update.caption if update.caption else "[No Text/Caption]")
            oinfo = f"{content}"

        elif isinstance(update, CallbackQuery):
            if update.message:
                chat_id = update.message.chat.id
                chat_type = update.message.chat.type.name if update.message.chat.type else "UNKNOWN"

            callback_data = update.data if update.data else "[No Data]"
            oinfo = f"{callback_data} => "

            if update.message and (update.message.text or update.message.caption):
                original_msg_text = update.message.text or update.message.caption
                oinfo += f"{original_msg_text[:LOGGER_TEXT_LIMIT]}"

        else:
            oinfo = f"UNKNOWN UPDATE TYPE: {type(update).__name__}"

        logger_text = (
            f"\033[31m[BotLog]\033[36m Func [{func.__name__}] "
            f"Chat [{chat_type}] | ID [{chat_id}] "
            f"User [{user_full_name}, @{username}, {user_id}]\n"
            f"\033[31m[Other]\033[36m {oinfo}\033[0m\n"
        )

        print(logger_text)

        return await func(client, update, *args, **kwargs)
    return loggerw
