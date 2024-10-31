from aiogram.types import CallbackQuery
from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from chronogram.settings_menu_models import SettingsCallback
from aiogram.fsm.context import FSMContext
from chronogram.handlers.settings.settings_menu import (process_selection, start_settings_menu,
                                                        get_init_settings_msg)
from chronogram.handlers.settings.utc_picker import process_utc_picker, UtcPickerCallback
from chronogram.utils import perform_state_clear
from chronogram.middlewares import L10N

settings_router = Router(name='settings_router')


@settings_router.message(Command('settings'))
async def command_settings(message: Message, state: FSMContext, l10n: L10N):
    await perform_state_clear(state=state, uid=message.from_user.id)
    await message.answer(text=await get_init_settings_msg(message.from_user.id, l10n=l10n),
                         reply_markup=await start_settings_menu(
        tg_uid=message.from_user.id, l10n=l10n))
    await message.delete()


@settings_router.callback_query(UtcPickerCallback.filter())
async def process_utc_picker_callback(callback_query: CallbackQuery, callback_data: UtcPickerCallback, l10n: L10N):
    await process_utc_picker(callback_query, callback_data, l10n=l10n)


@settings_router.callback_query(SettingsCallback.filter())
async def process_settings_callback(callback_query: CallbackQuery, callback_data: SettingsCallback, l10n: L10N):
    await process_selection(callback_query, callback_data, l10n=l10n)
