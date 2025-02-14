from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.filters.callback_data import CallbackData
from enum import Enum
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from aiogram.types import LabeledPrice
from aiogram.types import CallbackQuery
import dataclasses
from ...database import requests as db_req
from ...database.schema import ChronogramUser
from ...settings_menu_models import SettingsCallback, SettingsMenuActions
from ...middlewares import L10N

from ...config import config


@dataclasses.dataclass
class InvoicePayloadData:
    user_id: int
    amount_xtr: int
    payment_type: str
    timestamp: datetime
    months: int = 0

    def __post_init__(self):
        if self.payment_type not in ("subscription", "donation"):
            raise ValueError(f"Invalid pay type: {self.payment_type}")

    def __str__(self):
        return (
            f"{self.user_id}_{self.months}_{self.amount_xtr}_{self.payment_type}"
            f"_{datetime.strftime(self.timestamp, '%H:%M %d.%m.%Y')}"
        )

    @staticmethod
    def decode(payload: str):
        user_id, months, amount_xtr, payment_type, timestamp = payload.split("_")
        return InvoicePayloadData(
            user_id=int(user_id),
            amount_xtr=int(amount_xtr),
            payment_type=payment_type,
            months=int(months),
            timestamp=datetime.strptime(timestamp, "%H:%M %d.%m.%Y"),
        )


class SubscriptionMenuCallback(CallbackData, prefix="subscription"):
    action: str = "INIT"
    user_id: int

    def replace_and_pack(self, action) -> str:
        return SubscriptionMenuCallback(action=action, user_id=self.user_id).pack()


class SubscriptionMenuActions(str, Enum):
    IGNORE = "IGNORE"
    BUY = "BUY"
    CANCEL = "CANCEL"
    DURATION_MONTHS = "DURATION_MONTHS-"
    CLOSE = "CLOSE"
    BACK_TO_INIT = "BACK_TO_INIT"


async def choose_duration_menu(
    data: SubscriptionMenuCallback, l10n: L10N
) -> InlineKeyboardMarkup:
    keyboard = [[], [], [], [], [], []]
    keyboard[0] = [
        InlineKeyboardButton(
            text=l10n.data["/subscription"]["subscribe_1_month"],
            callback_data=data.replace_and_pack(
                SubscriptionMenuActions.DURATION_MONTHS + "1"
            ),
        )
    ]
    keyboard[1] = [
        InlineKeyboardButton(
            text=l10n.data["/subscription"]["subscribe_3_month"],
            callback_data=data.replace_and_pack(
                SubscriptionMenuActions.DURATION_MONTHS + "3"
            ),
        )
    ]
    keyboard[2] = [
        InlineKeyboardButton(
            text=l10n.data["/subscription"]["subscribe_6_month"],
            callback_data=data.replace_and_pack(
                SubscriptionMenuActions.DURATION_MONTHS + "6"
            ),
        )
    ]
    keyboard[3] = [
        InlineKeyboardButton(
            text=l10n.data["/subscription"]["subscribe_12_month"],
            callback_data=data.replace_and_pack(
                SubscriptionMenuActions.DURATION_MONTHS + "12"
            ),
        )
    ]
    keyboard[4] = [
        InlineKeyboardButton(
            text=l10n.data["/subscription"]["subscribe_120_month"],
            callback_data=data.replace_and_pack(
                SubscriptionMenuActions.DURATION_MONTHS + "120"
            ),
        )
    ]
    keyboard[5] = [
        InlineKeyboardButton(
            text=l10n.data["buttons"]["back"],
            callback_data=SettingsCallback(action=SettingsMenuActions.BACK).pack(),
        )
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


async def send_payment_invoice(callback: CallbackQuery, months: int, l10n: L10N):
    utc_diff = await db_req.get_user_attr(
        tg_uid=callback.from_user.id, col=ChronogramUser.utc_offset_minutes
    )
    builder = InlineKeyboardBuilder()
    amount_xtr = config.SUBSCRIPTION_COST * months
    builder.button(text=l10n.data["buttons"]["pay"].format(amount_xtr), pay=True)
    builder.button(
        text=l10n.data["buttons"]["close"],
        callback_data=SubscriptionMenuCallback(
            user_id=callback.from_user.id, action=SubscriptionMenuActions.CLOSE
        ).pack(),
    )
    builder.adjust(1)
    await callback.message.delete()
    deadline = await db_req.get_user_attr(
        tg_uid=callback.from_user.id, col=ChronogramUser.subscription_deadline
    )
    if not deadline:
        active_until = (
            datetime.utcnow()
            + timedelta(minutes=utc_diff)
            + relativedelta(months=months)
        )
    else:
        active_until = (
            deadline + timedelta(minutes=utc_diff) + relativedelta(months=months)
        )
    await callback.message.answer_invoice(
        title=l10n.data["/subscription"]["confirm_purchase"],
        description=l10n.data["/subscription"]["confirm_subscription"].format(
            months,
            l10n.data["/subscription"]["months"][months],
            amount_xtr,
            datetime.strftime(active_until, "%H:%M %d.%m.%Y"),
        ),
        payload=str(
            InvoicePayloadData(
                amount_xtr=amount_xtr,
                user_id=callback.from_user.id,
                timestamp=datetime.utcnow(),
                payment_type="subscription",
                months=months,
            )
        ),
        prices=[LabeledPrice(label="XTR", amount=amount_xtr)],
        currency="XTR",
        provider_token="",
        reply_markup=builder.as_markup(),
    )


async def process_subscription_menu_actions(
    callback: CallbackQuery, data: SubscriptionMenuCallback, l10n: L10N
):
    match data.action:
        case SubscriptionMenuActions.CLOSE:
            await callback.message.delete()
        case SubscriptionMenuActions.BUY:
            await callback.message.edit_reply_markup(
                reply_markup=await choose_duration_menu(data, l10n)
            )
    if data.action.startswith(SubscriptionMenuActions.DURATION_MONTHS):
        months = data.action.split("-")[1]
        await send_payment_invoice(callback, int(months), l10n)
