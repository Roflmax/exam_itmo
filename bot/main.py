"""
Telegram bot entry point for gym application.

Initializes the bot, dispatcher, and starts polling.
"""

import asyncio
import logging
import os
import sys

from aiogram import Bot, Dispatcher

from .handlers import router

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


async def main() -> None:
    """Initialize and start the bot."""
    # Load token from environment variable
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token:
        logger.error("TELEGRAM_BOT_TOKEN environment variable is not set")
        sys.exit(1)

    # Initialize bot and dispatcher
    bot = Bot(token=token)
    dp = Dispatcher()

    # Register router from handlers
    dp.include_router(router)

    logger.info("Starting gym bot...")

    # Start polling
    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())
