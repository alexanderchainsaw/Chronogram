import asyncio
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from ..database import requests as db_req
from ..middlewares.l10n_data import LOC

from config import config


async def deadline_notificator():
    while True:
        data = await db_req.get_subscribers_with_expiring_subscription()
        if data:
            for user in data:
                message_text = LOC[user.language]['/subscription']['subscription_deadline']
                if user.space_taken > config.DEFAULT_USER_SPACE:
                    message_text = LOC[user.language]['/subscription']['subscription_deadline_surplus']
                message_text += LOC[user.language]['/subscription']['subscription_deadline_prolong']
                await config.BOT.send_message(chat_id=user.tg_uid, text=message_text,
                                              reply_markup=InlineKeyboardMarkup(inline_keyboard=[[
                                                  InlineKeyboardButton(text=LOC[user.language]['buttons']['got_it'],
                                                                       callback_data='default_close_menu')]]))
                await db_req.mark_as_notified(user.tg_uid)
                config.LOGGER.info(f"Notified of deadline: ...{str(user.tg_uid)[5:]}")
        await asyncio.sleep(30)


async def subscription_revoker():
    while True:
        data = await db_req.get_subscribers_with_expired_subscription()
        if data:
            for user in data:
                await db_req.revoke_subscription(user.tg_uid)
                config.LOGGER.info(f"Revoked subscription: ...{str(user.tg_uid)[5:]}")
        await asyncio.sleep(30)
