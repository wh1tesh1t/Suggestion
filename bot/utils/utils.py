import operator

from functools import partial

from hydrogram.enums import ChatMemberStatus
from hydrogram.types import (
    CallbackQuery,
    ChatPrivileges,
    Message,
)

async def check_perms(
    message: CallbackQuery | Message,
    permissions: ChatPrivileges | None = None,
    complain_missing_perms: bool = True,
    s=None,
) -> bool:
    if isinstance(message, CallbackQuery):
        sender = partial(message.answer, show_alert=True)
        chat = message.message.chat
    else:
        sender = message.reply_text
        chat = message.chat
    # TODO: Cache all admin permissions in db.
    user = await chat.get_member(message.from_user.id)
    if user.status == ChatMemberStatus.OWNER:
        return True

    # No permissions specified, accept being an admin.
    if not permissions and user.status == ChatMemberStatus.ADMINISTRATOR:
        return True
    if user.status != ChatMemberStatus.ADMINISTRATOR:
        if complain_missing_perms:
            await sender(s("admins_no_admin_error"))
        return False

    missing_perms = [
        perm
        for perm, value in permissions.__dict__.items()
        if value and not getattr(user.privileges, perm)
    ]

    if not missing_perms:
        return True
    if complain_missing_perms:
        await sender(s("admins_no_permission_error").format(permissions=", ".join(missing_perms)))
    return False

class BotCommands:
    def __init__(self):
        self.commands = {}

    def add_command(
        self,
        command: str,
        category: str,
        aliases: list | None = None,
    ):
        description_key = f"cmd_{command}_description"

        if self.commands.get(category) is None:
            self.commands[category] = []
        self.commands[category].append({
            "command": command,
            "description_key": description_key,
            "aliases": aliases or [],
        })

    def get_commands_message(self, s, category: str | None = None):
        # TODO: Add pagination support.
        if category is None:
            cmds_list = []
            for subcategory in self.commands:
                cmds_list += self.commands[subcategory]
        else:
            cmds_list = self.commands[category]

        res = (
            s("cmds_list_category_title").format(category=s(f"cmds_category_{category}")) + "\n\n"
        )

        cmds_list.sort(key=operator.itemgetter("command"))

        for cmd in cmds_list:
            res += f"<b>/{cmd['command']}</b> - <i>{s(cmd['description_key'])}</i>\n"

        return res

commands = BotCommands()
