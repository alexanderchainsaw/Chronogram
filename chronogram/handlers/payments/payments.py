from datetime import datetime
from dateutil.relativedelta import relativedelta
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.types import LabeledPrice, PreCheckoutQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder, InlineKeyboardMarkup
from chronogram.database.schema import ChronogramUser
from chronogram.database.models import OuterChronogramPaymentData
import chronogram.database.requests as db_req
from chronogram.middlewares import L10N
from chronogram.utils import get_default_close_button, perform_state_clear
from chronogram.handlers.payments.schemas import (InvoicePayloadData,
                                                  process_subscription_menu_actions, SubscriptionMenuCallback)

payments_router = Router(name='payments_router')


@payments_router.message(Command('paysupport'))
async def cmd_paysupport(message: Message, state: FSMContext, l10n: L10N):
    await perform_state_clear(state=state, uid=message.from_user.id)
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[await get_default_close_button(l10n.lang)]])
    await message.answer(l10n.data['/paysupport'], reply_markup=keyboard)
    await message.delete()


@payments_router.message(Command('donate'))
async def cmd_donate(message: Message, state: FSMContext, l10n: L10N):
    await perform_state_clear(state=state, uid=message.from_user.id)
    data = message.text.split()
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[await get_default_close_button(l10n.lang)]])
    if len(data) != 2:
        await message.answer(l10n.data['/donate']['usage'], reply_markup=keyboard)
    elif not data[1].isdigit() or set(data[1]) == '0':
        await message.answer(l10n.data['/donate']['usage'], reply_markup=keyboard)
    else:
        builder = InlineKeyboardBuilder()
        amount_xtr = int(data[1])
        builder.button(text=l10n.data['buttons']['pay'].format(amount_xtr), pay=True)
        builder.add(await get_default_close_button(l10n.lang))
        builder.adjust(1)
        await message.answer_invoice(title=l10n.data['/donate']['confirm_title'],
                                     description=l10n.data['/donate']['confirm_descr'].format(amount_xtr),
                                     currency='XTR',
                                     provider_token='',
                                     prices=[LabeledPrice(label='XTR', amount=amount_xtr)],
                                     payload=str(InvoicePayloadData(user_id=message.from_user.id,
                                                                    timestamp=datetime.utcnow(),
                                                                    amount_xtr=amount_xtr,
                                                                    payment_type='donation')),
                                     reply_markup=builder.as_markup())
    await message.delete()


@payments_router.message(F.successful_payment)
async def process_successful_payment(message: Message, l10n: L10N):
    invoice_data = InvoicePayloadData.decode(message.successful_payment.invoice_payload)
    pay_data = OuterChronogramPaymentData(timestamp=datetime.utcnow().replace(microsecond=0),
                                          invoice_id=str(invoice_data),
                                          tg_transaction_id=message.successful_payment.telegram_payment_charge_id,
                                          type=invoice_data.payment_type, xtr_amount=invoice_data.amount_xtr,
                                          tg_uid=message.from_user.id)
    active_until = (datetime.utcnow() +
                    relativedelta(months=invoice_data.months,
                                  minutes=await db_req.get_user_attr(tg_uid=message.from_user.id,
                                                                     col=ChronogramUser.utc_offset_minutes),
                                  )).replace(microsecond=0).replace(second=0)
    if await db_req.get_user_attr(col=ChronogramUser.subscription, tg_uid=message.from_user.id):
        cur_deadline = await db_req.get_user_attr(col=ChronogramUser.subscription_deadline,
                                                  tg_uid=message.from_user.id)
        active_until = (cur_deadline + relativedelta(months=invoice_data.months,
                                                     minutes=await db_req.get_user_attr(
                                                        tg_uid=message.from_user.id,
                                                        col=ChronogramUser.utc_offset_minutes))
                        ).replace(microsecond=0).replace(second=0)
    r = await db_req.process_payment(pay_data=pay_data, months=invoice_data.months)
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[await get_default_close_button(l10n.lang)]])
    match r:
        case 'DONATE':
            await message.answer(text=l10n.data['/donate']['success'], message_effect_id='5104841245755180586',
                                 reply_markup=keyboard)
        case 'PROLONG':
            await message.answer(text=l10n.data['/subscription']['subscription_prolonged'].format(
                datetime.strftime(active_until, '%H:%M %d.%m.%Y')),
                                 reply_markup=keyboard)
        case 'GRANT':
            await message.answer(text=l10n.data['/subscription']['subscription_activated'].format(
                datetime.strftime(active_until, '%H:%M %d.%m.%Y')),
                                 reply_markup=keyboard)


@payments_router.message(Command('refund'))
async def cmd_refund(message: Message, state: FSMContext, l10n: L10N):
    await perform_state_clear(state=state, uid=message.from_user.id)
    user_lang = await db_req.get_user_attr(tg_uid=message.from_user.id, col=ChronogramUser.language)
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[await get_default_close_button(user_lang)]])
    await message.answer(text=l10n.data['/refund']['no_refunds'], reply_markup=keyboard)
    await message.delete()
    return


@payments_router.callback_query(SubscriptionMenuCallback.filter())
async def process_subscription_menu(callback_query: CallbackQuery, callback_data: SubscriptionMenuCallback, l10n: L10N):
    await process_subscription_menu_actions(callback_query, callback_data, l10n)


@payments_router.pre_checkout_query()
async def pre_checkout_query_process(pre_q: PreCheckoutQuery, l10n: L10N):
    if await db_req.invoice_exists(pre_q.invoice_payload):
        await pre_q.answer(ok=False, error_message=l10n.data['invoice_already_paid'])
        return
    await pre_q.answer(ok=True)
