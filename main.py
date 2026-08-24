from __future__ import annotations

import asyncio
import logging

from pybot.bot import PyBot
from pybot.config import Settings
from pybot.logging_config import configure_logging


async def main() -> None:
    settings = Settings.from_env()
    configure_logging(settings.log_level)

    bot = PyBot(settings)
    async with bot:
        await bot.start(settings.discord_token)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logging.getLogger("pybot").info("Bot detenido por el usuario")
