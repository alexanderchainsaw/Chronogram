from datetime import datetime, timedelta
from aiogram.types import CallbackQuery
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters.callback_data import CallbackData
from enum import Enum
from chronogram.middlewares import L10N
from chronogram.settings_menu_models import SettingsCallback, SettingsMenuActions

UTC_MINUTE_VALUES = [0, 30, 45]
UTC_HOUR_VALUES = [x for x in range(15)]
VALID_TIMEZONES = ('UTC +00:00', 'UTC -00:00', 'UTC +01:00', 'UTC +02:00', 'UTC +03:00', 'UTC +03:30', 'UTC +04:00',
                   'UTC +04:30', 'UTC +05:00', 'UTC +05:30', 'UTC +05:45', 'UTC +06:00', 'UTC +06:30', 'UTC +07:00',
                   'UTC +08:00', 'UTC +08:45', 'UTC +09:00', 'UTC +09:30', 'UTC +10:00', 'UTC +10:30', 'UTC +11:00',
                   'UTC +12:00', 'UTC +13:00', 'UTC +13:45', 'UTC +14:00', 'UTC -01:00', 'UTC -02:00', 'UTC -02:30',
                   'UTC -03:00', 'UTC -04:00', 'UTC -05:00', 'UTC -06:00', 'UTC -07:00', 'UTC -08:00', 'UTC -09:00',
                   'UTC -09:30', 'UTC -10:00', 'UTC -11:00')


class UtcPickerActions(str, Enum):
    ignore = 'IGNORE'
    increase_hour = 'INCREASE_HOUR'
    decrease_hour = 'DECREASE_HOUR'
    increase_minute = 'INCREASE_MINUTE'
    decrease_minute = 'DECREASE_MINUTE'
    change_sign = 'CHANGE_SIGN'
    cancel_selection = 'CANCEL_SELECTION'
    confirm_utc = 'CONFIRM_UTC'


class UtcPickerCallback(CallbackData, prefix='utc_picker'):
    action: str = ''
    hour: int = 0
    minute: int = 0
    sign: str = '+'


async def get_current_value(data: UtcPickerCallback):
    return (datetime.utcnow() + timedelta(hours=int(data.sign + str(data.hour)),
                                          minutes=int(data.sign + str(data.minute)))).strftime('%H:%M')


async def process_utc_picker(callback: CallbackQuery, data: UtcPickerCallback, l10n: L10N):
    canceled, selected, utc_difference = False, False, None
    match data.action:
        case UtcPickerActions.ignore:
            await callback.answer()
        case UtcPickerActions.change_sign:
            data.sign = {'+': '-', '-': '+'}[data.sign]
            await callback.message.edit_reply_markup(reply_markup=await start_utc_picker(data, l10n=l10n))
        case UtcPickerActions.increase_hour | UtcPickerActions.decrease_hour:
            data.hour = (UTC_HOUR_VALUES * 2)[UTC_HOUR_VALUES.index(data.hour) + {
                UtcPickerActions.increase_hour: 1, UtcPickerActions.decrease_hour: -1,
            }[data.action]]
            await callback.message.edit_reply_markup(reply_markup=await start_utc_picker(data, l10n=l10n))
        case UtcPickerActions.increase_minute | UtcPickerActions.decrease_minute:
            data.minute = (UTC_MINUTE_VALUES * 2)[UTC_MINUTE_VALUES.index(data.minute) + {
                UtcPickerActions.increase_minute: 1, UtcPickerActions.decrease_minute: -1,
            }[data.action]]
            await callback.message.edit_reply_markup(reply_markup=await start_utc_picker(data, l10n=l10n))
        case UtcPickerActions.cancel_selection:
            await callback.message.delete()
            canceled = True
        # case UtcPickerActions.confirm_utc:
        #     utc_difference = data.sign, int(data.hour), int(data.minute)
        #     selected = True
    return canceled, selected, utc_difference


async def start_utc_picker(data: UtcPickerCallback, l10n: L10N) -> InlineKeyboardMarkup:

    keyboard = [[], [], [], [], []]

    keyboard[0] = [
        InlineKeyboardButton(
            text=l10n.data['/settings']['utc_picker_display_value'].format(get_current_value(data)),
            callback_data=UtcPickerCallback(
                tg_uid=data.tg_uid,
                action=UtcPickerActions.ignore,
                hour=data.hour,
                minute=data.minute,
                sign=data.sign
            ).pack()
        )
    ]

    keyboard[1] = [
        InlineKeyboardButton(
            text='↑',
            callback_data=UtcPickerCallback(
                tg_uid=data.tg_uid,
                action=UtcPickerActions.change_sign,
                hour=data.hour,
                minute=data.minute,
                sign=data.sign
            ).pack()
        ),
        InlineKeyboardButton(
            text='↑',
            callback_data=UtcPickerCallback(
                tg_uid=data.tg_uid,
                action=UtcPickerActions.increase_hour,
                hour=data.hour,
                minute=data.minute,
                sign=data.sign
            ).pack()
        ),
        InlineKeyboardButton(
            text=' ',
            callback_data=UtcPickerCallback(
                tg_uid=data.tg_uid,
                action=UtcPickerActions.ignore,
                hour=data.hour,
                minute=data.minute,
                sign=data.sign
            ).pack()
        ),
        InlineKeyboardButton(
            text='↑',
            callback_data=UtcPickerCallback(
                tg_uid=data.tg_uid,
                action=UtcPickerActions.increase_minute,
                hour=data.hour,
                minute=data.minute,
                sign=data.sign
            ).pack()
        ),
    ]

    keyboard[2] = [
        InlineKeyboardButton(
            text=data.sign,
            callback_data=UtcPickerCallback(
                tg_uid=data.tg_uid,
                action=UtcPickerActions.change_sign,
                hour=data.hour,
                minute=data.minute,
                sign=data.sign
            ).pack()
        ),
        InlineKeyboardButton(
            text=f"{data.hour:02d}",
            callback_data=UtcPickerCallback(
                tg_uid=data.tg_uid,
                action=UtcPickerActions.ignore,
                hour=data.hour,
                minute=data.minute,
                sign=data.sign
            ).pack()
        ),
        InlineKeyboardButton(
            text=':',
            callback_data=UtcPickerCallback(
                tg_uid=data.tg_uid,
                action=UtcPickerActions.ignore,
                hour=data.hour,
                minute=data.minute,
                sign=data.sign
            ).pack()
        ),
        InlineKeyboardButton(
            text=f"{data.minute:02d}",
            callback_data=UtcPickerCallback(
                tg_uid=data.tg_uid,
                action=UtcPickerActions.ignore,
                hour=data.hour,
                minute=data.minute,
                sign=data.sign
            ).pack()
        ),
    ]

    keyboard[3] = [
        InlineKeyboardButton(
            text='↓',
            callback_data=UtcPickerCallback(
                tg_uid=data.tg_uid,
                action=UtcPickerActions.change_sign,
                hour=data.hour,
                minute=data.minute,
                sign=data.sign
            ).pack()
        ),
        InlineKeyboardButton(
            text='↓',
            callback_data=UtcPickerCallback(
                tg_uid=data.tg_uid,
                action=UtcPickerActions.decrease_hour,
                hour=data.hour,
                minute=data.minute,
                sign=data.sign
            ).pack()
        ),
        InlineKeyboardButton(
            text=' ',
            callback_data=UtcPickerCallback(
                tg_uid=data.tg_uid,
                action=UtcPickerActions.ignore,
                hour=data.hour,
                minute=data.minute,
                sign=data.sign
            ).pack()
        ),
        InlineKeyboardButton(
            text='↓',
            callback_data=UtcPickerCallback(
                tg_uid=data.tg_uid,
                action=UtcPickerActions.decrease_minute,
                hour=data.hour,
                minute=data.minute,
                sign=data.sign
            ).pack()
        ),
    ]

    keyboard[4] = [
        InlineKeyboardButton(
            text=l10n.data['buttons']['back'],
            callback_data=SettingsCallback(action=SettingsMenuActions.BACK).pack()
        ),
        InlineKeyboardButton(
            text=l10n.data['buttons']['confirm'],
            callback_data=SettingsCallback(action=SettingsMenuActions.SELECT_UTC + f"{data.sign}|{data.hour}|"
                                                                                   f"{data.minute}").pack()
        ),
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)
