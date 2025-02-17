from .schemas import CalendarLabels
from datetime import datetime


class GenericCalendar:
    def __init__(
        self,
        locale: str = None,
        cancel_btn: str = None,
        today_btn: str = None,
        show_alerts: bool = False,
    ) -> None:
        """Pass labels if you need to have alternative language of buttons

        Parameters:
        locale (str): Locale calendar must have captions in (in format uk_UA), if None - default English will be used
        cancel_btn (str): label for button Cancel to cancel date input
        today_btn (str): label for button Today to set calendar back to today's date
        show_alerts (bool): defines how the date range error would have shown (defaults to False)
        """
        self._labels = CalendarLabels()
        if locale:
            # getting month names and days of week in specified locale
            # locale = {'en_EN'}[locale]
            # with calendar.different_locale(locale):
            self._labels.days_of_week = {
                "ru": ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"],
                "en": ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"],
            }[locale]
            self._labels.months = {
                "ru": [
                    "янв",
                    "фев",
                    "мар",
                    "апр",
                    "май",
                    "июн",
                    "июл",
                    "авг",
                    "сен",
                    "окт",
                    "ноя",
                    "дек",
                ],
                "en": [
                    "Jan",
                    "Feb",
                    "Mar",
                    "Apr",
                    "May",
                    "Jun",
                    "Jul",
                    "Aug",
                    "Sep",
                    "Oct",
                    "Nov",
                    "Dec",
                ],
            }[locale]

        if cancel_btn:
            self._labels.cancel_caption = cancel_btn
        if today_btn:
            self._labels.today_caption = today_btn

        self.min_date = None
        self.max_date = None
        self.show_alerts = show_alerts

    def set_dates_range(self, min_date: datetime, max_date: datetime):
        """Sets range of minimum & maximum dates"""
        self.min_date = min_date
        self.max_date = max_date

    async def process_day_select(self, data, query):
        """Checks selected date is in allowed range of dates"""
        date = datetime(int(data.year), int(data.month), int(data.day))
        if self.min_date and self.min_date > date:
            await query.answer(
                f"The date have to be later {self.min_date.strftime('%d/%m/%Y')}",
                show_alert=self.show_alerts,
            )
            return False, None
        elif self.max_date and self.max_date < date:
            await query.answer(
                f"The date have to be before {self.max_date.strftime('%d/%m/%Y')}",
                show_alert=self.show_alerts,
            )
            return False, None
        await query.message.delete_reply_markup()  # removing inline keyboard
        return True, date, False
