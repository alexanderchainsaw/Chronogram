import aiogram.exceptions
from aiogram.filters import Command
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.utils.keyboard import InlineKeyboardMarkup, InlineKeyboardButton
from ..database import requests as db_req
from ..utils import get_default_close_button, perform_state_clear
from ..middlewares import L10N

from config import config

delete_router = Router(name='delete_router')


class DeleteEverything(StatesGroup):
    awaiting_confirmation = State()


@delete_router.message(Command('delete_everything'))
async def cmd_delete_everything(message: Message, state: FSMContext, l10n: L10N):
    await perform_state_clear(state=state, uid=message.from_user.id)
    cancel = InlineKeyboardButton(text=l10n.data['buttons']['cancel'], callback_data='cancel_delete_everything')
    prompt_message_id = (await message.answer(text=l10n.data['/delete_everything']['init'],
                                              reply_markup=InlineKeyboardMarkup(
        inline_keyboard=[[cancel]]))).message_id
    await state.set_state(DeleteEverything.awaiting_confirmation)
    await state.update_data(prompt_message_id=prompt_message_id)
    await message.delete()


@delete_router.message(DeleteEverything.awaiting_confirmation)
async def confirm_delete_everything(message: Message, state: FSMContext, l10n: L10N):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[await get_default_close_button(l10n.lang)]])
    if message.text != l10n.data['/delete_everything']['confirmation_message']:
        await message.answer(text=l10n.data['/delete_everything']['confirmation_message_invalid'],
                             reply_markup=keyboard)
    else:
        await db_req.TimeCapsuleDatabaseActions.delete_everything(tg_uid=message.from_user.id)
        await message.answer(text=l10n.data['/delete_everything']['success'],
                             reply_markup=keyboard)
    try:
        data = await state.get_data()
        await config.BOT.delete_message(chat_id=message.from_user.id, message_id=data['prompt_message_id'])
    except (aiogram.exceptions.TelegramBadRequest, KeyError) as e:
        config.LOGGER.warning(f"Error on delete_everything (delete prompt message), error: {e}")
    await state.clear()
    await message.delete()


@delete_router.callback_query(F.data == "cancel_delete_everything")
async def cancel_delete_everything(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.delete()
