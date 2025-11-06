import logging
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

import logfire
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from .config import LOGFIRE_ENVIRONMENT, LOGFIRE_SERVICE_NAME, TOKEN
from .handlers import register_handlers

bot = Bot(TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dispatcher = Dispatcher()


def setup_logfire() -> None:
    logfire.configure(
        service_name=LOGFIRE_SERVICE_NAME,
        environment=LOGFIRE_ENVIRONMENT,
        send_to_logfire="if-token-present",
        distributed_tracing=False,
        console=logfire.ConsoleOptions(min_log_level="debug"),
    )

    logging.basicConfig(
        level=logging.INFO,
        handlers=[logfire.LogfireLoggingHandler(level=logging.INFO)],
    )


@asynccontextmanager
async def bot_startup() -> AsyncGenerator[None]:
    setup_logfire()

    with logfire.span("Bot startup"):
        register_handlers(dispatcher)

        await bot.delete_webhook(drop_pending_updates=True)

        yield


@asynccontextmanager
async def bot_shutdown() -> AsyncGenerator[None]:
    with logfire.span("Bot shutdown"):
        yield


async def run_polling() -> None:
    async with bot_startup():
        pass

    await dispatcher.start_polling(bot)

    async with bot_shutdown():
        pass
