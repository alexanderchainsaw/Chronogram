from chronogram.middlewares.l10n_data import LOC
from decimal import Decimal
import aiogram.exceptions
from aiogram.fsm.context import FSMContext
import chronogram.database.requests as db_req
from chronogram.database.schema import ChronogramUser
from chronogram.database.schema import DEFAULT_USER_SPACE, PREMIUM_USER_SPACE
from aiogram.types import InlineKeyboardButton
from config import config


async def get_default_close_button(user_lang) -> InlineKeyboardButton:
    return InlineKeyboardButton(text=LOC[user_lang]['buttons']['close'], callback_data='default_close_menu')


async def perform_state_clear(state: FSMContext, uid: int):
    data = await state.get_data()
    try:
        for msg_id in data['messages_to_delete']:
            try:
                await config.BOT.delete_message(message_id=msg_id, chat_id=uid)
            except aiogram.exceptions.TelegramBadRequest as err:
                if "message to delete not found" in err.message:
                    config.LOGGER.warning('Message to delete not found error')
                else:
                    config.LOGGER.warning(f'Unknown error on message delete: {err.message}')
    except KeyError:
        config.LOGGER.debug(f'expected KeyError, No messages to delete')
    await state.clear()


async def user_space_remaining_percent(tg_uid) -> str:
    space_taken = await db_req.get_user_attr(tg_uid=tg_uid, col=ChronogramUser.space_taken)
    subscribed = await db_req.get_user_attr(tg_uid=tg_uid, col=ChronogramUser.subscription)
    return await _format_user_space_remaining_percent(space_taken=space_taken, subscribed=subscribed)


async def _format_user_space_remaining_percent(space_taken: int, subscribed: bool) -> str:
    if subscribed:
        return f"{int(100 - (space_taken / PREMIUM_USER_SPACE * 100))}%"
    return f"{int(100 - (space_taken / DEFAULT_USER_SPACE * 100))}%"


async def user_space_remaining_mb(tg_uid) -> str:
    space_taken = await db_req.get_user_attr(tg_uid=tg_uid, col=ChronogramUser.space_taken)
    subscribed = await db_req.get_user_attr(tg_uid=tg_uid, col=ChronogramUser.subscription)
    return await _format_user_space_remaining_mb(subscribed=subscribed, space_taken=space_taken)


async def _format_user_space_remaining_mb(space_taken: int, subscribed: bool) -> str:
    if subscribed:
        if space_taken == 0:
            return "10<b>|</b>10MB"
        remaining_mb = (PREMIUM_USER_SPACE - space_taken) / 1000000
        round_method = 'ROUND_UP'
        if remaining_mb >= 5:
            round_method = 'ROUND_DOWN'
        return f"{Decimal(remaining_mb).quantize(Decimal('0.001'), round_method)}<b>|</b>10MB"
    if space_taken == 0:
        return "0.1<b>|</b>0.1MB"
    remaining_mb = (DEFAULT_USER_SPACE - space_taken) / 1000000
    round_method = 'ROUND_UP'
    if remaining_mb >= 0.1:
        round_method = 'ROUND_DOWN'
    return f"{Decimal(remaining_mb).quantize(Decimal('0.001'), round_method)}<b>|</b>0.1MB"
