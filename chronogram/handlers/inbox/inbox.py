from aiogram.types import CallbackQuery
from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import InlineKeyboardMarkup
from ...database import requests as db_req
from ...database.requests import TimeCapsuleDatabaseActions as TC
from ...database.schema import ChronogramUser
from ...utils import get_default_close_button, perform_state_clear
from ...middlewares import L10N
from .inbox_menu import (InboxCallback, start_inbox_menu, process_selection, inbox_pic,
                         start_inbox_caption)


inbox_router = Router(name='inbox_router')


@inbox_router.message(Command('inbox'))
async def command_inbox(message: Message, state: FSMContext, l10n: L10N):
    await perform_state_clear(state=state, uid=message.from_user.id)
    user_lang = await db_req.get_user_attr(tg_uid=message.from_user.id, col=ChronogramUser.language)
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[await get_default_close_button(user_lang)]])
    received_messages = await TC.get_received_timecapsules(tg_uid=message.from_user.id)
    if not received_messages:
        await message.answer(text=await start_inbox_caption(message.from_user.id, empty=True, l10n=l10n),
                             reply_markup=keyboard)
        await message.delete()
        return
    data = InboxCallback(action='INITIAL', user_id=message.chat.id)

    await message.answer_photo(photo=inbox_pic,
                               caption=await start_inbox_caption(message.from_user.id, l10n=l10n),
                               reply_markup=await start_inbox_menu(data, l10n=l10n))
    await message.delete()


@inbox_router.callback_query(InboxCallback.filter())
async def process_inbox_callback(callback_query: CallbackQuery, callback_data: InboxCallback, l10n: L10N):
    await process_selection(callback_query, callback_data, l10n=l10n)
