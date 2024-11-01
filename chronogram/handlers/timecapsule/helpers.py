import sys
import parse
import html
from aiogram.types import CallbackQuery
import chronogram.database.requests as db_req
from chronogram.database.schema import ChronogramUser
from chronogram.database.requests import TimeCapsuleDatabaseActions as TC
from chronogram.photo_utils import PhotoReader
from aiogram.types import Message
from chronogram.middlewares import L10N


# TODO! parsing might break if we change language in the process

async def parse_content_from_message(callback: CallbackQuery) -> str:
    raw_text = callback.message.text
    if callback.message.photo:
        raw_text = callback.message.caption
    if '\n\n' not in raw_text:
        return ''
    return html.escape(raw_text.rsplit('\n\n', 1)[0])


async def parse_date_from_message(callback: CallbackQuery, l10n: L10N) -> str:
    raw_text = callback.message.text
    if callback.message.photo:
        raw_text = callback.message.caption
    contains_date = raw_text.rsplit('\n\n', 1)[-1]
    # TODO! we can make lang-insensitive search (there should be a : before the date no matter the lang)
    return parse.search(l10n.data['/timecapsule']['you_selected'] + "{:<10}", contains_date.split('\n')[0])[0]


async def parse_datetime_from_message(callback: CallbackQuery) -> list[str, str]:
    raw_text = callback.message.text
    if callback.message.photo:
        raw_text = callback.message.caption
    contains_date = raw_text.rsplit('\n', 1)[-1]
    return contains_date.split()


async def _validate_timecapsule(message: Message) -> tuple:
    if any([message.sticker, message.video, message.audio, message.document]):
        return False, 'Data'
    elif any([(message.text and len(message.text) > 1600), (message.caption and len(message.caption) > 800)]):
        return False, 'Length'

    total_size = 0
    if message.caption:
        total_size += len(message.caption.encode('utf-8'))
    elif message.text:
        total_size += len(message.text.encode('utf-8'))
    if message.photo:
        ph = PhotoReader(photo=message.photo, file_name=f"None")
        photo_blob = await ph.get_blob_image()
        total_size += sys.getsizeof(photo_blob)
    available_storage = await db_req.get_user_attr(tg_uid=message.from_user.id, col=ChronogramUser.space_available)
    if available_storage < total_size:
        return False, 'Space'

    if message.text:
        return True, 'Text'
    elif message.photo:
        return True, 'Photo'
    return False, 'Data'


async def _get_not_enough_space_message(tg_uid, l10n: L10N) -> str:
    msg = l10n.data["/timecapsule"]["not_enough_space"]['common']
    if await TC.timecapsules_received(tg_uid=tg_uid):
        msg += l10n.data["/timecapsule"]["not_enough_space"]["has_received"]
    if not await db_req.get_user_attr(tg_uid=tg_uid, col=ChronogramUser.subscription):
        msg += l10n.data["/timecapsule"]["not_enough_space"]["not_sub"]
    return msg
