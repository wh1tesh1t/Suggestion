import os
import random

from .core import database

conn = database.get_conn()

async def user_add_to_ban(user_id: int):
    await conn.execute('INSERT INTO banned_users (user_id) VALUES (?)', (user_id,))
    await conn.commit()

async def user_remove_from_ban(user_id: int):
    await conn.execute('DELETE FROM banned_users WHERE user_id = ?', (user_id,))
    await conn.commit()

async def is_user_banned(user_id: int) -> bool:
    async with conn.execute('SELECT user_id FROM banned_users WHERE user_id = ?', (user_id,)) as cursor:
        return await cursor.fetchone() is not None

async def group_add_to_ban(group_id: int):
    await conn.execute('INSERT INTO banned_groups (group_id) VALUES (?)', (group_id,))
    await conn.commit()

async def group_remove_from_ban(group_id: int):
    await conn.execute('DELETE FROM banned_groups WHERE group_id = ?', (group_id,))
    await conn.commit()

async def is_group_banned(group_id: int) -> bool:
    async with conn.execute('SELECT group_id FROM banned_groups WHERE group_id = ?', (group_id,)) as cursor:
        return await cursor.fetchone() is not None

def check_ban(func):
    async def wrapper(client, message, *args, **kwargs):
        if message.from_user:
            # Ignore banned user
            if await is_user_banned(message.from_user.id):
                return
        return await func(client, message, *args, **kwargs)

    return wrapper
