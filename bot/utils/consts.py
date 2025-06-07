from collections.abc import Iterable

from hydrogram.enums import ChatMemberStatus, ChatType

GROUP_TYPES: Iterable[ChatType] = (ChatType.GROUP, ChatType.SUPERGROUP)

ADMIN_STATUSES: Iterable[ChatMemberStatus] = (
    ChatMemberStatus.OWNER,
    ChatMemberStatus.ADMINISTRATOR,
)
