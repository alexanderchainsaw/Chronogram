import calendar
from datetime import datetime, timedelta

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.types import CallbackQuery

from ....middlewares import L10N
from ....database.requests import get_user_attr
from ....database.schema import ChronogramUser
from .schemas import SimpleCalendarCallback, SimpleCalAct
from .common import GenericCalendar


class SimpleCalendar(GenericCalendar):
    ignore_callback = SimpleCalendarCallback(
        act=SimpleCalAct.ignore
    ).pack()  # placeholder for no answer buttons

    async def start_calendar(
        self,
        l10n: L10N,
        year: int = datetime.utcnow().year,
        month: int = datetime.utcnow().month,
    ) -> InlineKeyboardMarkup:
        """
        Creates an inline keyboard with the provided year and month
        :param L10N l10n: Localization object
        :param int year: Year to use in the calendar, if None the current year is used.
        :param int month: Month to use in the calendar, if None the current month is used.
        :return: Returns InlineKeyboardMarkup object with the calendar.
        """
        kb = []
        years_row = list()
        years_row.append(
            InlineKeyboardButton(
                text="«",
                callback_data=SimpleCalendarCallback(
                    act=SimpleCalAct.prev_y, year=year, month=month, day=1
                ).pack(),
            )
        )
        years_row.append(
            InlineKeyboardButton(text=str(year), callback_data=self.ignore_callback)
        )
        years_row.append(
            InlineKeyboardButton(
                text="»",
                callback_data=SimpleCalendarCallback(
                    act=SimpleCalAct.next_y, year=year, month=month, day=1
                ).pack(),
            )
        )
        kb.append(years_row)

        # Month nav Buttons
        month_row = list()
        month_row.append(
            InlineKeyboardButton(
                text="‹",
                callback_data=SimpleCalendarCallback(
                    act=SimpleCalAct.prev_m, year=year, month=month, day=1
                ).pack(),
            )
        )
        month_row.append(
            InlineKeyboardButton(
                text=self._labels.months[month - 1], callback_data=self.ignore_callback
            )
        )
        month_row.append(
            InlineKeyboardButton(
                text="›",
                callback_data=SimpleCalendarCallback(
                    act=SimpleCalAct.next_m, year=year, month=month, day=1
                ).pack(),
            )
        )
        kb.append(month_row)

        # Week Days
        week_days_labels_row = []
        for weekday in self._labels.days_of_week:
            week_days_labels_row.append(
                InlineKeyboardButton(text=weekday, callback_data=self.ignore_callback)
            )
        kb.append(week_days_labels_row)

        # Calendar rows - Days of month
        month_calendar = calendar.monthcalendar(year, month)

        for week in month_calendar:
            days_row = []
            for day in week:
                if day == 0:
                    days_row.append(
                        InlineKeyboardButton(
                            text=" ", callback_data=self.ignore_callback
                        )
                    )
                    continue
                days_row.append(
                    InlineKeyboardButton(
                        text=str(day),
                        callback_data=SimpleCalendarCallback(
                            act=SimpleCalAct.day, year=year, month=month, day=day
                        ).pack(),
                    )
                )
            kb.append(days_row)

        # nav today & cancel button
        cancel_row = list()
        cancel_row.append(
            InlineKeyboardButton(
                text=l10n.data["buttons"]["cancel"],
                callback_data=SimpleCalendarCallback(
                    act=SimpleCalAct.cancel, year=year, month=month, day=day
                ).pack(),
            )
        )
        kb.append(cancel_row)
        return InlineKeyboardMarkup(row_width=20, inline_keyboard=kb)

    async def _update_calendar(
        self, query: CallbackQuery, with_date: datetime, l10n: L10N
    ):
        await query.message.edit_reply_markup(
            reply_markup=await self.start_calendar(
                l10n, int(with_date.year), int(with_date.month)
            )
        )

    async def process_selection(
        self, query: CallbackQuery, data: SimpleCalendarCallback, l10n: L10N
    ) -> tuple:
        """
        Process the callback_query. This method generates a new calendar if forward or
        backward is pressed. This method should be called inside a CallbackQueryHandler.
        :param query: callback_query, as provided by the CallbackQueryHandler
        :param data: callback_data, dictionary, set by calendar_callback
        :param l10n: Localization object
        :return: Returns a tuple (Boolean,datetime), indicating if a date is selected
                    and returning the date if so.
        """
        return_data = False, None, False
        user_chat_id = query.from_user.id
        user_local_time = datetime.utcnow() + timedelta(
            minutes=await get_user_attr(
                col=ChronogramUser.utc_offset_minutes, tg_uid=user_chat_id
            )
        )

        # processing empty buttons, answering with no action
        if data.act == SimpleCalAct.ignore:
            await query.answer(cache_time=60)
            return return_data

        temp_date = datetime(int(data.year), int(data.month), 1)

        # user picked a day button, return date
        if data.act == SimpleCalAct.day:
            if user_local_time - datetime(
                int(data.year), int(data.month), int(data.day)
            ) > timedelta(days=1):
                await query.answer(l10n.data["/timecapsule"]["only_future"])
                return return_data
            return await self.process_day_select(data, query)

        # user navigates to previous year, editing message with new calendar
        if data.act == SimpleCalAct.prev_y:
            prev_date = datetime(int(data.year) - 1, int(data.month), 1)
            await self._update_calendar(query, prev_date, l10n=l10n)
        # user navigates to next year, editing message with new calendar
        if data.act == SimpleCalAct.next_y:
            next_date = datetime(int(data.year) + 1, int(data.month), 1)
            await self._update_calendar(query, next_date, l10n=l10n)
        # user navigates to previous month, editing message with new calendar
        if data.act == SimpleCalAct.prev_m:
            prev_date = temp_date - timedelta(days=1)
            await self._update_calendar(query, prev_date, l10n=l10n)
        # user navigates to next month, editing message with new calendar
        if data.act == SimpleCalAct.next_m:
            next_date = temp_date + timedelta(days=31)
            await self._update_calendar(query, next_date, l10n=l10n)
        if data.act == SimpleCalAct.cancel:
            # await query.message.delete()
            return_data = False, None, True
        # at some point user clicks DAY button, returning date
        return return_data
