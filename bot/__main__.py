import asyncio
import logging
import platform
import sys

from hydrogram import idle

from bot import Bot
from bot.database import database

logging.basicConfig(
    level=logging.INFO,
    format="%(name)s.%(funcName)s | %(levelname)s | %(message)s",
    datefmt="[%X]",
)

# To avoid some annoying log
logging.getLogger("hydrogram.syncer").setLevel(logging.WARNING)
logging.getLogger("hydrogram.client").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)

try:
    import uvloop

    uvloop.install()
except ImportError:
    logger.warning("uvloop is not installed and therefore will be disabled.")


async def main():
    bot = Bot()

    try:
        # start the bot
        await database.connect()
        await bot.start()

        await idle()
    except KeyboardInterrupt:
        # exit gracefully
        logger.warning("Forced stop… Bye!")
    finally:
        # close https connections and the DB if open
        await bot.stop()
        if database.is_connected:
            await database.close()


if __name__ == "__main__":
    # open new asyncio event loop
    event_policy = asyncio.get_event_loop_policy()
    event_loop = event_policy.new_event_loop()
    asyncio.set_event_loop(event_loop)

    # start the bot
    event_loop.run_until_complete(main())

    # close asyncio event loop
    event_loop.close()
