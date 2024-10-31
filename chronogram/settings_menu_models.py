from aiogram.filters.callback_data import CallbackData
from enum import Enum


class SettingsMenuActions(str, Enum):
    TIMEZONE = "TIMEZONE"
    LANGUAGE = "LANGUAGE"
    SUBSCRIPTION = "SUBSCRIPTION"
    SELECT_LANGUAGE = "SELECT_LANGUAGE-"
    SELECT_UTC = "SELECT_UTC|"
    BACK = "BACK"
    CLOSE = "CLOSE"


class SettingsCallback(CallbackData, prefix='settings'):
    action: str
