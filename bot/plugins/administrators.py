import os
from hydrogram import Client, filters
from hydrogram.types import Message

from sqlite3 import IntegrityError, OperationalError

from config import SUPER_ADMIN, DATABASE_PATH

from bot.utils import commands
from bot.utils.localization import Strings, use_chat_lang
from bot.database.administrators import (
    user_add_to_admin,
    user_remove_from_admin,
    is_user_admin,
)
from bot.database.global_ban import (
    user_add_to_ban,
    user_remove_from_ban,
    is_user_banned,
    check_ban,
)

async def get_admin_id(user_id):
    if user_id == SUPER_ADMIN:
        return SUPER_ADMIN
    elif await is_user_admin(user_id):
        return await is_user_admin(user_id)
    else:
        return None

@Client.on_message(filters.command("feedback") & filters.user(SUPER_ADMIN))
@use_chat_lang
async def feedbackcmd(c: Client, m: Message, s: Strings):
    args = m.text.split(maxsplit=2)

    if len(args) < 3:
        return await m.reply_text(s("feedback_example"))

    try:
        user_id = int(args[1])
        fmsg = args[2]
        user = await c.get_users(user_id)
        username = user.username if user.username else "noname"

        await c.send_message(chat_id=user_id, text=fmsg)
        await m.reply_text(s("feedback_sent_success").format(name=username, id=user_id))
    except Exception as e:
        await m.reply_text(s("feedback_sent_fail").format(id=user_id))

@Client.on_message(filters.command("me"))
@use_chat_lang
@check_ban
async def sudos(c: Client, m: Message , s: Strings):
    admin = await get_admin_id(m.from_user.id)

    if admin is None:
        return await m.reply_text(s("you_not_admin"))

    await m.reply_text(s("you_admin"))


@Client.on_message(
    filters.command("backup")
    & filters.user(SUPER_ADMIN)
    & ~filters.forwarded
    & ~filters.group
    & ~filters.via_bot
)
async def backupcmd(c: Client, m: Message):
    await m.reply_document(DATABASE_PATH)


@Client.on_message(filters.command("sql") & filters.user(SUPER_ADMIN))
@use_chat_lang
async def execsql(c: Client, m: Message, s: Strings):
    command = m.text.split(maxsplit=1)[1]

    try:
        ex = await conn.execute(command)
    except (IntegrityError, OperationalError) as e:
        await m.reply_text(s("sql_error").format(classname=e.__class__.__name__, error=e))
        return

    ret = await ex.fetchall()
    await conn.commit()

    if not ret:
        await m.reply_text(s("sql_executed"))
        return

    res = "|".join([name[0] for name in ex.description]) + "\n"
    res += "\n".join(["|".join(str(s) for s in items) for items in ret])

    if len(res) < 3500:
        await m.reply_text(f"<code>{res}</code>")
        return

    bio = io.BytesIO()
    bio.name = "output.txt"

    bio.write(res.encode())

    await m.reply_document(bio)


@Client.on_message(filters.command("add_admin") & filters.user(SUPER_ADMIN))
@use_chat_lang
async def add_admin(c: Client, m: Message, s: Strings):
    if len(m.command) < 2:
        await m.reply(s("give_me_user_id"))
        return

    user_id = m.command[1]

    admin = await is_user_banned(user_id)

    if admin:
        await m.reply(s("already_added_admin"))
        return

    try:
        user = await c.get_users(user_id)
        username = user.username if user.username else "noname"

        await user_add_to_admin(user_id)
        await m.reply(s("user_added_to_admin").format(name=username, id=user_id))
    except Exception as e:
        await m.reply(f"Error: {str(e)}")


@Client.on_message(filters.command("del_admin") & filters.user(SUPER_ADMIN))
@use_chat_lang
async def del_admin(c: Client, m: Message, s: Strings):
    if len(m.command) < 2:
        await m.reply(s("give_me_user_id"))
        return

    user_id = m.command[1]

    try:
        admin = await is_user_admin(user_id)

        if admin:
            user = await c.get_users(user_id)
            username = user.username if user.username else "noname"

            await user_remove_from_admin(user_id)
            await m.reply(s("user_removed_from_admin").format(name=username, id=user_id))
        else:
            await m.reply(s("admin_not_found").format(id=user_id))
    except Exception as e:
        await m.reply(f"Error: {str(e)}")


@Client.on_message(filters.command("ban_user"))
@use_chat_lang
@check_ban
async def global_ban_user(c: Client, m: Message, s: Strings):
    caller_id = m.from_user.id
    admin = await get_admin_id(caller_id)

    if admin is None:
        return await m.reply_text(s("you_not_admin"))

    if len(m.command) < 2:
        await m.reply(s("give_me_user_id"))
        return

    user_id = m.command[1]

    try:
        target_user_id = int(user_id)
    except ValueError:
        return await m.reply(s("invalid_user_id"))

    if caller_id == SUPER_ADMIN:
        if target_user_id == SUPER_ADMIN:
            return await m.reply(s("you_cannot_ban_self"))
    else:
        if not await is_user_admin(caller_id):
            return await m.reply(s("you_not_admin"))

        if target_user_id == SUPER_ADMIN:
            return await m.reply(s("you_cannot_ban_superadmin"))

        if await is_user_admin(target_user_id):
            return await m.reply(s("you_cannot_ban_admin"))

        if target_user_id == caller_id:
            return await m.reply(s("you_cannot_ban_self"))

    banned_user = await is_user_banned(target_user_id)
    if banned_user:
        await m.reply(s("alredy_banned"))
        return

    try:
        user = await c.get_users(target_user_id)
        username = user.username if user.username else "noname"

        await user_add_to_ban(target_user_id)
        await m.reply(s("user_banned").format(name=username, id=target_user_id))
    except Exception as e:
        await m.reply(f"Error: {str(e)}")


@Client.on_message(filters.command("unban_user"))
@use_chat_lang
@check_ban
async def global_unban_user(c: Client, m: Message, s: Strings):
    caller_id = m.from_user.id
    admin = await get_admin_id(caller_id)

    if admin is None:
        return await m.reply_text(s("you_not_admin"))

    if len(m.command) < 2:
        await m.reply(s("give_me_user_id"))
        return

    user_id = m.command[1]

    try:
        target_user_id = int(user_id)
    except ValueError:
        return await m.reply(s("invalid_user_id"))


    if caller_id == SUPER_ADMIN:
        pass
    else:
        if not await is_user_admin(caller_id):
            return await m.reply(s("you_not_admin"))

        if target_user_id == SUPER_ADMIN:
            return

        if await is_user_admin(target_user_id):
            return await m.reply(s("you_cannot_unban_admin"))

        if target_user_id == caller_id:
            return

    banned_user = await is_user_banned(target_user_id)
    if not banned_user:
        return await m.reply(s("user_notfound").format(id=target_user_id))

    try:
        user = await c.get_users(target_user_id)
        username = user.username if user.username else "noname"

        await user_remove_from_ban(target_user_id)
        await m.reply(s("user_unbanned").format(name=username, id=target_user_id))
    except Exception as e:
        await m.reply(f"Error: {str(e)}")


commands.add_command("me", "admin")
commands.add_command("ban_user", "admin")
commands.add_command("unban_user", "admin")
