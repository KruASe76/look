# ruff: noqa: RUF001

__all__ = ["register_handlers"]

from aiogram import Dispatcher, Router
from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
    WebAppInfo,
)

from .config import FRONTEND_URL

GREETING_MESSAGE_TEXT = (
    "Привет! Я Look.\nЗа пару минут покажу, какие вещи созданы для тебя.\nГотов?"
)
GREETING_BUTTON_TEXT = "🚀 Начать"

router = Router()


@router.message()
async def greeting(message: Message) -> None:
    await message.answer(
        text=GREETING_MESSAGE_TEXT,
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text=GREETING_BUTTON_TEXT,
                        web_app=WebAppInfo(url=FRONTEND_URL),
                    )
                ]
            ]
        ),
    )


def register_handlers(dispatcher: Dispatcher) -> None:
    dispatcher.include_router(router)
