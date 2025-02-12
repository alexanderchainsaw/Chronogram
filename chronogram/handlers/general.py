from aiogram.filters import Command
from aiogram import Router
from aiogram.types import Message
from datetime import datetime, timedelta
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import InlineKeyboardMarkup
from ..database.schema import ChronogramUser
from ..middlewares import L10N
from ..database import requests as db_req
from ..utils import get_default_close_button, perform_state_clear


general_router = Router(name="general_router")


@general_router.message(Command("start"))
async def command_start(message: Message, state: FSMContext, l10n: L10N):
    await perform_state_clear(state=state, uid=message.from_user.id)
    utc_offset = await db_req.get_user_attr(
        tg_uid=message.from_user.id, col=ChronogramUser.utc_offset_minutes
    )
    await message.answer(
        text=l10n.data["/start"].format(
            {"ru": "🇷🇺", "en": "🇬🇧"}[l10n.lang],
            (datetime.utcnow() + timedelta(minutes=utc_offset)).strftime(
                "%H:%M %d.%m.%Y"
            ),
        )
    )
    await message.delete()


@general_router.message(Command("about"))
async def command_about(message: Message, state: FSMContext, l10n: L10N):
    await perform_state_clear(state=state, uid=message.from_user.id)
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[[await get_default_close_button(l10n.lang)]]
    )
    await message.answer(text=l10n.data["/about"], reply_markup=keyboard)
    await message.delete()


@general_router.message(Command("help"))
async def command_help(message: Message, state: FSMContext, l10n: L10N):
    await perform_state_clear(state=state, uid=message.from_user.id)
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[[await get_default_close_button(l10n.lang)]]
    )
    await message.answer(text=l10n.data["/help"], reply_markup=keyboard)
    await message.delete()
