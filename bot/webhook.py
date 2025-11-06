from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

import logfire
from aiogram.types import Update
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware

from .bot import bot, bot_shutdown, bot_startup, dispatcher
from .config import WEBHOOK_BASE_URL


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncGenerator[None]:
    async with bot_startup():
        await bot.set_webhook(f"{WEBHOOK_BASE_URL}/webhook", drop_pending_updates=True)

    yield

    async with bot_shutdown():
        await bot.delete_webhook(drop_pending_updates=True)


app = FastAPI(title="Look Telegram Bot", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)
logfire.instrument_fastapi(app)


@app.post("/webhook", status_code=status.HTTP_200_OK)
async def webhook(request: Request) -> None:
    update = Update(**await request.json())
    await dispatcher.feed_update(bot, update)
