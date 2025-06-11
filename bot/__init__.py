import logging
import time

import hydrogram
from hydrogram import Client
from hydrogram.enums import ParseMode
from hydrogram.errors import BadRequest
from hydrogram.raw.all import layer

from config import (
    API_HASH,
    API_ID,
    FORWARDING_CHAT,
    TOKEN,
    WORKERS
)

from subprocess import run

logger = logging.getLogger(__name__)


class Bot(Client):
    def __init__(self):
        name = self.__class__.__name__.lower()

        super().__init__(
            name=name,
            app_version=f"BotBot",
            api_id=API_ID,
            api_hash=API_HASH,
            bot_token=TOKEN,
            parse_mode=ParseMode.HTML,
            workers=WORKERS,
            plugins={"root": "bot.plugins"},
            sleep_threshold=180,
        )

    async def start(self):
        await super().start()

        self.start_time = time.time()

        logger.info(
            "Bot running with Hydrogram v%s (Layer %s) started on @%s.",
            hydrogram.__version__,
            layer,
            self.me.username,
        )

        start_message = (
            "<b>Suggestion Bot started!</b>\n\n"
        )

        try:
            await self.send_message(chat_id=FORWARDING_CHAT, text=start_message)
        except BadRequest:
            logger.warning("Unable to send message to FORWARDING_CHAT.")

    async def stop(self):
        await super().stop()
        logger.warning("Bot stopped!")
