from aiogram.types import CallbackQuery
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from datetime import datetime, timedelta
from ...database import requests as db_req
from ...database.schema import ChronogramUser
from ...settings_menu_models import SettingsCallback, SettingsMenuActions
from ...utils import user_space_remaining_mb, user_space_remaining_percent
from ...middlewares import L10N, get_l10n_by_lang
from ..payments.schemas import SubscriptionMenuCallback, choose_duration_menu
from .utc_picker import start_utc_picker, UtcPickerCallback

from config import config


async def get_init_settings_msg(tg_uid, l10n: L10N) -> str:
    utc_diff = await db_req.get_user_attr(
        tg_uid=tg_uid, col=ChronogramUser.utc_offset_minutes
    )
    msg = l10n.data["/settings"]["init"].format(
        {"en": "🇬🇧", "ru": "🇷🇺"}[l10n.lang],
        (datetime.utcnow() + timedelta(minutes=utc_diff)).strftime("%H:%M %d.%m.%Y"),
        await user_space_remaining_mb(tg_uid=tg_uid),
        await user_space_remaining_percent(tg_uid=tg_uid),
    )
    if await db_req.get_user_attr(tg_uid=tg_uid, col=ChronogramUser.subscription):
        deadline = await db_req.get_user_attr(
            tg_uid=tg_uid, col=ChronogramUser.subscription_deadline
        )
        deadline += timedelta(minutes=utc_diff)
        msg += l10n.data["/settings"]["subscription_expires"].format(
            deadline.strftime("%H:%M %d.%m.%Y")
        )
    else:
        msg += l10n.data["/settings"]["subscription_agitate"]
    msg += l10n.data["/settings"]["donate"]
    return msg


async def start_settings_menu(tg_uid, l10n: L10N) -> InlineKeyboardMarkup:
    keyboard = [[], [], [], []]
    sub_msg_text = l10n.data["/settings"]["subscription_buy"]
    if await db_req.get_user_attr(tg_uid=tg_uid, col=ChronogramUser.subscription):
        sub_msg_text = l10n.data["/settings"]["subscription_prolong"]
    keyboard[0] = [
        InlineKeyboardButton(
            text=sub_msg_text,
            callback_data=SettingsCallback(
                action=SettingsMenuActions.SUBSCRIPTION
            ).pack(),
        )
    ]
    keyboard[1] = [
        InlineKeyboardButton(
            text=l10n.data["/settings"]["timezone"],
            callback_data=SettingsCallback(action=SettingsMenuActions.TIMEZONE).pack(),
        )
    ]
    keyboard[2] = [
        InlineKeyboardButton(
            text=l10n.data["/settings"]["language"],
            callback_data=SettingsCallback(action=SettingsMenuActions.LANGUAGE).pack(),
        )
    ]
    keyboard[3] = [
        InlineKeyboardButton(
            text=l10n.data["/settings"]["close"],
            callback_data=SettingsCallback(action=SettingsMenuActions.CLOSE).pack(),
        )
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard, row_width=7)


async def _select_language_menu(l10n: L10N) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.add(
        InlineKeyboardButton(
            text="🇬🇧 English",
            callback_data=SettingsCallback(
                action=SettingsMenuActions.SELECT_LANGUAGE + "en"
            ).pack(),
        )
    )
    builder.add(
        InlineKeyboardButton(
            text="🇷🇺 Русский",
            callback_data=SettingsCallback(
                action=SettingsMenuActions.SELECT_LANGUAGE + "ru"
            ).pack(),
        )
    )
    builder.add(
        InlineKeyboardButton(
            text=l10n.data["buttons"]["back"],
            callback_data=SettingsCallback(action=SettingsMenuActions.BACK).pack(),
        )
    )
    builder.adjust(1)
    return builder.as_markup()


async def process_selection(
    callback: CallbackQuery, data: SettingsCallback, l10n: L10N
):
    match data.action:
        case SettingsMenuActions.SUBSCRIPTION:
            await callback.message.edit_reply_markup(
                reply_markup=await choose_duration_menu(
                    data=SubscriptionMenuCallback(user_id=callback.from_user.id),
                    l10n=l10n,
                )
            )
        case SettingsMenuActions.TIMEZONE:
            user_utc_diff = await db_req.get_user_attr(
                tg_uid=callback.from_user.id, col=ChronogramUser.utc_offset_minutes
            )
            hour = user_utc_diff // 60
            minute = user_utc_diff % 60
            data = UtcPickerCallback(
                tg_uid=callback.from_user.id,
                hour=f"{abs(hour):02d}",
                minute=f"{abs(minute):02d}",
                sign="+" if user_utc_diff >= 0 else "-",
            )
            await callback.message.edit_reply_markup(
                reply_markup=await start_utc_picker(data, l10n=l10n)
            )
        case SettingsMenuActions.LANGUAGE:
            await callback.message.edit_reply_markup(
                reply_markup=await _select_language_menu(l10n=l10n)
            )
        case SettingsMenuActions.BACK:
            await callback.message.edit_reply_markup(
                reply_markup=await start_settings_menu(callback.from_user.id, l10n=l10n)
            )
        case SettingsMenuActions.CLOSE:
            await callback.message.delete()
    if data.action.startswith(SettingsMenuActions.SELECT_LANGUAGE):
        new_lang = data.action.split("-")[1]
        if new_lang == l10n.lang:
            await callback.answer()
        else:
            l10n = await get_l10n_by_lang(new_lang)
            await db_req.edit_language(tg_uid=callback.from_user.id, new_lang=new_lang)
            await callback.answer(
                text=l10n.data["/settings"]["language_change_success"]
            )
            await callback.message.edit_text(
                await get_init_settings_msg(callback.from_user.id, l10n=l10n)
            )
            await callback.message.edit_reply_markup(
                reply_markup=await _select_language_menu(l10n=l10n)
            )
            await config.AIOREDIS.set(str(callback.from_user.id), new_lang)
    elif data.action.startswith(SettingsMenuActions.SELECT_UTC):
        _, sign, hour, minute = data.action.split("|")
        user_utf_diff_minutes = int(hour) * 60 + int(minute)
        if sign == "-":
            user_utf_diff_minutes = -user_utf_diff_minutes
        old_val = await db_req.get_user_attr(
            tg_uid=callback.from_user.id, col=ChronogramUser.utc_offset_minutes
        )
        if old_val == user_utf_diff_minutes:
            await callback.answer()
        else:
            await db_req.edit_utc_diff(
                tg_uid=callback.from_user.id, value=user_utf_diff_minutes
            )
            await callback.message.edit_text(
                await get_init_settings_msg(callback.from_user.id, l10n=l10n)
            )
            await callback.message.edit_reply_markup(
                reply_markup=await start_utc_picker(
                    data=UtcPickerCallback(
                        tg_uid=callback.from_user.id,
                        sign=sign,
                        hour=hour,
                        minute=minute,
                    ),
                    l10n=l10n,
                )
            )
