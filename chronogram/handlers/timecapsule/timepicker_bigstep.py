from enum import Enum
from datetime import time
from aiogram.types import CallbackQuery
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters.callback_data import CallbackData
from chronogram.middlewares import L10N


class TimepickerActions(str, Enum):
    INCR_HOUR_1 = 'INCR_HOUR_1'
    INCR_MIN_1 = 'INCR_MIN_1'
    DECR_HOUR_1 = 'DECR_HOUR_1'
    DECR_MIN_1 = 'DECR_MIN_1'
    INCR_HOUR_4 = 'INCR_HOUR_4'
    INCR_MIN_15 = 'INCR_MIN_15'
    DECR_HOUR_4 = 'DECR_HOUR_4'
    DECR_MIN_15 = 'DECR_MIN_15'
    CANCEL = 'CANCEL'
    CONFIRM = 'CONFIRM'
    IGNORE = 'IGNORE'


class TimepickerCallback(CallbackData, prefix='timepicker'):
    action: str = 'INIT'
    user_id: int
    hour: int
    minute: int

    def replace_and_pack(self, action: TimepickerActions) -> str:
        return TimepickerCallback(action=action, user_id=self.user_id,
                                  hour=self.hour, minute=self.minute).pack()


async def start_timepicker(data: TimepickerCallback, l10n: L10N) -> InlineKeyboardMarkup:

    keyboard = [[], [], [], []]

    keyboard[0] = [
        InlineKeyboardButton(text='↑', callback_data=data.replace_and_pack(action=TimepickerActions.INCR_HOUR_1)),
        InlineKeyboardButton(text='⇈', callback_data=data.replace_and_pack(action=TimepickerActions.INCR_HOUR_4)),
        InlineKeyboardButton(text='⇈', callback_data=data.replace_and_pack(action=TimepickerActions.INCR_MIN_15)),
        InlineKeyboardButton(text='↑', callback_data=data.replace_and_pack(action=TimepickerActions.INCR_MIN_1)),
    ]

    keyboard[1] = [
        InlineKeyboardButton(text=f"{data.hour:02d}",
                             callback_data=data.replace_and_pack(action=TimepickerActions.IGNORE)),
        InlineKeyboardButton(text=f"{data.minute:02d}",
                             callback_data=data.replace_and_pack(action=TimepickerActions.IGNORE))
    ]

    keyboard[2] = [
        InlineKeyboardButton(text='↓', callback_data=data.replace_and_pack(action=TimepickerActions.DECR_HOUR_1)),
        InlineKeyboardButton(text='⇊', callback_data=data.replace_and_pack(action=TimepickerActions.DECR_HOUR_4)),
        InlineKeyboardButton(text='⇊', callback_data=data.replace_and_pack(action=TimepickerActions.DECR_MIN_15)),
        InlineKeyboardButton(text='↓', callback_data=data.replace_and_pack(action=TimepickerActions.DECR_MIN_1)),
    ]

    keyboard[3] = [
        InlineKeyboardButton(text=l10n.data['buttons']['cancel'],
                             callback_data=data.replace_and_pack(action=TimepickerActions.CANCEL)),
        InlineKeyboardButton(text=l10n.data['buttons']['confirm'],
                             callback_data=data.replace_and_pack(action=TimepickerActions.CONFIRM))
    ]

    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def process_time_change(hh_mm: tuple[int, int], to_add: tuple[int, int], sign: str) -> tuple[int, int]:
    if sign == '+':
        new_hour, new_min = hh_mm[0] + to_add[0], hh_mm[1] + to_add[1]
        if new_min >= 60:
            new_min -= 60
        if new_hour >= 24:
            new_hour -= 24
    elif sign == '-':
        new_hour, new_min = hh_mm[0] - to_add[0], hh_mm[1] - to_add[1]
        if new_min < 0:
            new_min = 60 + new_min
        if new_hour < 0:
            new_hour = 24 + new_hour
    else:
        raise RuntimeError('Invalid operation sign')
    return new_hour, new_min


async def process_selection(callback: CallbackQuery, data: TimepickerCallback, l10n: L10N):

    selected, selected_time, canceled = False, time(hour=data.hour, minute=data.minute), False

    match data.action:
        case TimepickerActions.IGNORE:
            await callback.answer()
        case TimepickerActions.CANCEL:
            canceled = True
        case TimepickerActions.CONFIRM:
            selected = True
        case TimepickerActions.INCR_MIN_1:
            data.hour, data.minute = process_time_change((data.hour, data.minute), (0, 1), '+')
            await callback.message.edit_reply_markup(reply_markup=await start_timepicker(data, l10n=l10n))
        case TimepickerActions.INCR_MIN_15:
            data.hour, data.minute = process_time_change((data.hour, data.minute), (0, 15), '+')
            await callback.message.edit_reply_markup(reply_markup=await start_timepicker(data, l10n=l10n))
        case TimepickerActions.INCR_HOUR_1:
            data.hour, data.minute = process_time_change((data.hour, data.minute), (1, 0), '+')
            await callback.message.edit_reply_markup(reply_markup=await start_timepicker(data, l10n=l10n))
        case TimepickerActions.INCR_HOUR_4:
            data.hour, data.minute = process_time_change((data.hour, data.minute), (4, 0), '+')
            await callback.message.edit_reply_markup(reply_markup=await start_timepicker(data, l10n=l10n))
        case TimepickerActions.DECR_MIN_1:
            data.hour, data.minute = process_time_change((data.hour, data.minute), (0, 1), '-')
            await callback.message.edit_reply_markup(reply_markup=await start_timepicker(data, l10n=l10n))
        case TimepickerActions.DECR_MIN_15:
            data.hour, data.minute = process_time_change((data.hour, data.minute), (0, 15), '-')
            await callback.message.edit_reply_markup(reply_markup=await start_timepicker(data, l10n=l10n))
        case TimepickerActions.DECR_HOUR_1:
            data.hour, data.minute = process_time_change((data.hour, data.minute), (1, 0), '-')
            await callback.message.edit_reply_markup(reply_markup=await start_timepicker(data, l10n=l10n))
        case TimepickerActions.DECR_HOUR_4:
            data.hour, data.minute = process_time_change((data.hour, data.minute), (4, 0), '-')
            await callback.message.edit_reply_markup(reply_markup=await start_timepicker(data, l10n=l10n))
    return selected, selected_time, canceled
