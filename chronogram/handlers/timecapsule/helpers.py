import sys
import html
from aiogram.types import Message
from aiogram.types import CallbackQuery
from ...database import requests as db_req
from ...database.schema import ChronogramUser
from ...database.requests import TimeCapsuleDatabaseActions as TC
from ...photo_utils import PhotoReader
from ...middlewares import L10N


async def parse_content_from_message(callback: CallbackQuery) -> str:
    raw_text = callback.message.text
    if callback.message.photo:
        raw_text = callback.message.caption
    return await _parse_content_from_message(raw_text)


async def _parse_content_from_message(raw_text: str) -> str:
    if "\n\n" not in raw_text:
        return ""
    return html.escape(raw_text.rsplit("\n\n", 1)[0])


async def parse_date_from_message(callback: CallbackQuery) -> str:
    raw_text = callback.message.text
    if callback.message.photo:
        raw_text = callback.message.caption
    return await _parse_date_from_message(raw_text)


async def _parse_date_from_message(raw_text: str) -> str:
    contains_date = raw_text.rsplit("\n\n", 1)[-1]
    return contains_date.split("\n")[0].rsplit(None, 1)[-1]


async def parse_datetime_from_message(callback: CallbackQuery) -> list[str, str]:
    raw_text = callback.message.text
    if callback.message.photo:
        raw_text = callback.message.caption
    return await _parse_datetime_from_message(raw_text)


async def _parse_datetime_from_message(raw_text: str) -> list[str, str]:
    contains_date = raw_text.rsplit("\n", 1)[-1]
    date_time = contains_date.split()
    if len(date_time) != 2:
        raise RuntimeError(f"Parse datetime error, object: {date_time}")
    return date_time


async def _validate_timecapsule(message: Message) -> tuple:
    if any([message.sticker, message.video, message.audio, message.document]):
        return False, "Data"
    elif any(
        [
            (message.text and len(message.text) > 1600),
            (message.caption and len(message.caption) > 800),
        ]
    ):
        return False, "Length"

    total_size = 0
    if message.caption:
        total_size += len(message.caption.encode("utf-8"))
    elif message.text:
        total_size += len(message.text.encode("utf-8"))
    if message.photo:
        ph = PhotoReader(photo=message.photo, file_name="None")
        photo_blob = await ph.get_blob_image()
        total_size += sys.getsizeof(photo_blob)
    available_storage = await db_req.get_user_attr(
        tg_uid=message.from_user.id, col=ChronogramUser.space_available
    )
    if available_storage < total_size:
        return False, "Space"

    if message.text:
        return True, "Text"
    elif message.photo:
        return True, "Photo"
    return False, "Data"


async def _get_not_enough_space_message(tg_uid, l10n: L10N) -> str:
    msg = l10n.data["/timecapsule"]["not_enough_space"]["common"]
    if await TC.timecapsules_received(tg_uid=tg_uid):
        msg += l10n.data["/timecapsule"]["not_enough_space"]["has_received"]
    if not await db_req.get_user_attr(tg_uid=tg_uid, col=ChronogramUser.subscription):
        msg += l10n.data["/timecapsule"]["not_enough_space"]["not_sub"]
    return msg
