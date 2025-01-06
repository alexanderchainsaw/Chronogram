import aiogram.exceptions
from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.utils.keyboard import InlineKeyboardMarkup
from chronogram.middlewares import L10N
from chronogram.utils import get_default_close_button

common_router = Router(name='common_router')


@common_router.callback_query(F.data == 'default_close_menu')
async def common_close_menu(callback: CallbackQuery, l10n: L10N):
    try:
        await callback.message.delete()
    except aiogram.exceptions.TelegramBadRequest:
        await callback.answer(l10n.data['cant_delete_msg'])
        await callback.message.delete_reply_markup()


@common_router.message()
async def default_response(message: Message, l10n: L10N):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[await get_default_close_button(l10n.lang)]])
    await message.answer(l10n.data['default_response'], reply_markup=keyboard)
