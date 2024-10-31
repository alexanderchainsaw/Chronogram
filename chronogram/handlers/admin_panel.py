from aiogram.filters import Command
from aiogram.filters import BaseFilter
import chronogram.database.requests as db_req
from aiogram import Router
from aiogram.types import Message
from aiogram.utils.keyboard import InlineKeyboardMarkup
from chronogram.utils import get_default_close_button, perform_state_clear
from aiogram.fsm.context import FSMContext
from config import config

admin_router = Router(name='admin_router')


class AdminFilter(BaseFilter):
    def __init__(self) -> None:
        self.admin_ids = [int(x) for x in config.ADMIN_IDS]

    async def __call__(self, message: Message) -> bool:
        return message.chat.id in self.admin_ids


@admin_router.message(AdminFilter(), Command('admin'))
async def get_admin_instructions(message: Message, state: FSMContext):
    await perform_state_clear(state=state, uid=message.from_user.id)
    await message.answer(text='<b>Admin commands:</b>\n\n'
                              '• /admin_stats - stats\n'
                              '• /admin_message *user_tg_id* *message_text*\n'
                              '• /forcerefund *user_tg_id* *transaction_id*\n'
                              '• /gift_sub *user_tg_id* *months*')
    await message.delete()


@admin_router.message(AdminFilter(), Command('admin_stats'))
async def get_app_stats(message: Message, state: FSMContext):
    await perform_state_clear(state=state, uid=message.from_user.id)
    data = await db_req.get_stats()
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[await get_default_close_button('en')]])
    await message.answer(f'• Total users: {data[0]}\n'
                         f'• Subscriptions bought: {data[1]}\n'
                         f'• Subscriptions active: {data[2]}\n', reply_markup=keyboard)
    await message.delete()


@admin_router.message(AdminFilter(), Command('admin_message'))
async def admin_message(message: Message, state: FSMContext):
    await perform_state_clear(state=state, uid=message.from_user.id)
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[await get_default_close_button('en')]])
    if len(message.text.split(maxsplit=2)) != 3:
        await message.answer("Usage:\n<code>/admin_message *user_tg_id* *message text*</code>", reply_markup=keyboard)
        return
    _, user_id, message_text = message.text.split(maxsplit=2)
    await config.BOT.send_message(chat_id=int(user_id), text=message_text)
    await message.answer('Message sent.', reply_markup=keyboard)
    await message.delete()


@admin_router.message(AdminFilter(), Command('forcerefund'))
async def forceful_refund(message: Message, state: FSMContext):
    await perform_state_clear(state=state, uid=message.from_user.id)
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[await get_default_close_button('en')]])
    if len(message.text.split()) != 3:
        await message.answer("Usage:\n<code>/forcerefund *user_tg_id* *transaction_id*</code>", reply_markup=keyboard)
        return
    _, user_id, transaction_id = message.text.split()
    match await db_req.process_refund(tg_uid=int(user_id), telegram_payment_charge_id=transaction_id):
        case 'INVALID_PAY_ID':
            await message.answer('Invalid transaction id', reply_markup=keyboard)
            return
        case 'REFUNDED':
            await message.answer('Already refunded', reply_markup=keyboard)
        case 'SUCCESS':
            await config.BOT.refund_star_payment(user_id=int(user_id), telegram_payment_charge_id=transaction_id)
            await message.answer('Refunded!', reply_markup=keyboard)
    await message.delete()


@admin_router.message(AdminFilter(), Command('gift_sub'))
async def gift_subscription(message: Message, state: FSMContext):
    await perform_state_clear(state=state, uid=message.from_user.id)
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[await get_default_close_button('en')]])
    if len(message.text.split()) != 3:
        await message.answer("Usage:\n<code>/gift_sub *user_tg_id* *months*</code>", reply_markup=keyboard)
        return
    _, user_id, months = message.text.split()
    uid = await db_req.get_uid_by_tg_uid(tg_uid=int(user_id))
    await db_req.grant_subscription(user_id=uid, months=int(months))
    await message.answer(f'Granted {months} month sub to {user_id}', reply_markup=keyboard)
    await message.delete()
