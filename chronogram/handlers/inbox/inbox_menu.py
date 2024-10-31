import math
import os
import sqlalchemy.exc
from PIL import Image
from aiogram.types.input_media_photo import InputMediaPhoto
from datetime import timedelta
from aiogram.types import CallbackQuery
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.filters.callback_data import CallbackData
import chronogram.database.requests as db_req
from chronogram.database.schema import ChronogramUser, TimeCapsule
from chronogram.database.requests import TimeCapsuleDatabaseActions as TC
from chronogram.utils import user_space_remaining_percent, user_space_remaining_mb
from aiogram.types.input_file import FSInputFile
from enum import Enum
from typing import Optional
from config import config
from chronogram.middlewares import L10N


inbox_pic = FSInputFile('media/inbox_pic.jpg')

PAGE_LEN = 4


class InboxCallbackActions(str, Enum):
    get_timecapsule = 'GET_TIMECAPSULE-'
    next_page = 'NEXT_PAGE'
    prev_page = 'PREV_PAGE'
    back_to_page = 'BACK_TO_PAGE'
    delete_timecapsule = 'DELETE_TIMECAPSULE'
    confirm_delete = 'CONFIRM_DELETE'
    close_inbox = 'CLOSE'
    ignore = 'IGNORE'


class InboxCallback(CallbackData, prefix='inbox'):
    action: str
    user_id: int
    cur_page: int = 0
    total_pages: int = 0
    cur_timecapsule: Optional[int] = None

    async def replace_and_pack(self, action: InboxCallbackActions, cur_timecapsule=None) -> str:
        return InboxCallback(action=action, user_id=self.user_id, cur_page=self.cur_page, total_pages=self.total_pages,
                             cur_timecapsule=cur_timecapsule).pack()


async def pack_timecapsule_ids(tc_ids: list[int]) -> list[list[int]]:
    res = []
    i = 0
    cur = []
    while i < len(tc_ids):
        if len(cur) == PAGE_LEN:
            res.append(cur)
            cur = []
        cur.append(tc_ids[i])
        i += 1
    if cur:
        res.append(cur)
    return res


async def get_message_timestamps_fmt(tc_id, tg_uid) -> str:
    utc_diff = await db_req.get_user_attr(tg_uid=tg_uid, col=ChronogramUser.utc_offset_minutes)
    tc_data: TimeCapsule = await TC.get_timecapsule_data(tg_uid=tg_uid, tc_id=tc_id)
    receive_t = (tc_data.receive_timestamp + timedelta(minutes=utc_diff)).strftime('%H:%M %d.%m.%Y')
    send_t = (tc_data.send_timestamp + timedelta(minutes=utc_diff)).strftime('%H:%M %d.%m.%Y')
    return f"{send_t} ⟶ {receive_t}"


async def get_message_content_fmt(tc_id, tg_uid, l10n: L10N) -> str:
    utc_diff = await db_req.get_user_attr(tg_uid=tg_uid, col=ChronogramUser.utc_offset_minutes)
    tc_data: TimeCapsule = await TC.get_timecapsule_data(tg_uid=tg_uid, tc_id=tc_id)
    receive_t = (tc_data.receive_timestamp + timedelta(minutes=utc_diff)).strftime('%H:%M %d.%m.%Y')
    send_t = (tc_data.send_timestamp + timedelta(minutes=utc_diff)).strftime('%H:%M %d.%m.%Y')

    if tc_data.text_content:
        return l10n.data['/inbox']['timecapsule_data'].format(send_t, receive_t, config.FERNET_KEY.decrypt(
            tc_data.text_content).decode('utf-8'))
    return l10n.data['/inbox']['timecapsule_data'].format(send_t, receive_t, '')


async def start_inbox_caption(tg_uid, l10n: L10N, empty: bool = False) -> str:
    if empty:
        return (l10n.data['/inbox']['empty'] + l10n.data['/inbox']['some_underway']
                * await TC.timecapsules_underway(tg_uid))
    subscribed = await db_req.get_user_attr(tg_uid=tg_uid, col=ChronogramUser.subscription)
    msg_text = l10n.data['/inbox']['init'].format(await user_space_remaining_mb(tg_uid),
                                                  await user_space_remaining_percent(tg_uid))
    if not subscribed:
        msg_text += l10n.data['/inbox']['subscribe']
    return msg_text


async def start_inbox_menu(data: InboxCallback, l10n: L10N) -> InlineKeyboardMarkup:
    timecapsule_ids = []
    timecapsules = await TC.get_received_timecapsules(tg_uid=data.user_id)
    timecapsules.sort(key=lambda x: x.receive_timestamp, reverse=True)
    for tc in timecapsules:
        timecapsule_ids.append(tc.id)
    packed_timecapsules = await pack_timecapsule_ids(timecapsule_ids)
    data.total_pages = len(packed_timecapsules)
    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(text=l10n.data['/inbox']['menu_col_sent'],
                                     callback_data=await data.replace_and_pack(action=InboxCallbackActions.ignore)),
                InlineKeyboardButton(text=f"{data.cur_page + 1}/{data.total_pages}",
                                     callback_data=await data.replace_and_pack(action=InboxCallbackActions.ignore)),
                InlineKeyboardButton(text=l10n.data['/inbox']['menu_col_received'],
                                     callback_data=await data.replace_and_pack(action=InboxCallbackActions.ignore)))

    for msg in packed_timecapsules[data.cur_page]:
        builder.button(text=await get_message_timestamps_fmt(msg, data.user_id),
                       callback_data=await data.replace_and_pack(action=InboxCallbackActions.get_timecapsule + str(msg)))
    builder.add(InlineKeyboardButton(text='«',
                                     callback_data=await data.replace_and_pack(InboxCallbackActions.prev_page)),
                InlineKeyboardButton(text=l10n.data['buttons']['close'],
                                     callback_data=await data.replace_and_pack(InboxCallbackActions.close_inbox)),
                InlineKeyboardButton(text='»',
                                     callback_data=await data.replace_and_pack(InboxCallbackActions.next_page)))
    builder.adjust(3, *[1 for _ in packed_timecapsules[data.cur_page]], 3)

    return builder.as_markup()


async def process_selection(callback: CallbackQuery, data: InboxCallback, l10n: L10N):
    try:
        match data.action:
            case InboxCallbackActions.ignore:
                await callback.answer()
            case InboxCallbackActions.close_inbox:
                await callback.message.delete()
            case InboxCallbackActions.next_page:
                if data.total_pages - 1 < data.cur_page + 1:
                    await callback.answer()
                    return
                data.cur_page += 1

                await callback.message.edit_reply_markup(reply_markup=await start_inbox_menu(data, l10n=l10n))
            case InboxCallbackActions.prev_page:
                if data.cur_page == 0:
                    await callback.answer()
                    return
                data.cur_page -= 1

                await callback.message.edit_reply_markup(reply_markup=await start_inbox_menu(data, l10n=l10n))
            case InboxCallbackActions.back_to_page:
                data.cur_timecapsule = None
                await callback.message.edit_media(media=InputMediaPhoto(media=inbox_pic))
                await callback.message.edit_caption(caption=await start_inbox_caption(data.user_id, l10n=l10n),
                                                    parse_mode='HTML')
                await callback.message.edit_reply_markup(reply_markup=await start_inbox_menu(data, l10n=l10n))

            case InboxCallbackActions.delete_timecapsule:
                await callback.message.edit_caption(caption=l10n.data['/timecapsule']['delete'],
                                                    reply_markup=InlineKeyboardMarkup(
                                                        inline_keyboard=[[
                                                            InlineKeyboardButton(
                                                                text=l10n.data['buttons']['confirm_delete'],
                                                                callback_data=await data.replace_and_pack(
                                                                    action=InboxCallbackActions.confirm_delete,
                                                                    cur_timecapsule=data.cur_timecapsule)),
                                                            InlineKeyboardButton(
                                                                text=l10n.data['buttons']['cancel'],
                                                                callback_data=await data.replace_and_pack(
                                                                    InboxCallbackActions.get_timecapsule +
                                                                    str(data.cur_timecapsule))
                                                                )]]))
            case InboxCallbackActions.confirm_delete:
                await handle_delete_from_inbox(data, callback, l10n=l10n)
    except IndexError:
        await callback.answer(l10n.data['inbox_altered'])

    if data.action.startswith('GET_TIMECAPSULE'):
        try:
            tc_id = int(data.action.split('-')[1])
            photo = await TC.get_timecapsule_image(tg_uid=data.user_id, tc_id=tc_id)
            photo_data = await TC.get_timecapsule_image_data(tg_uid=data.user_id, tc_id=tc_id)
            if photo:
                img = Image.frombytes(data=config.FERNET_KEY.decrypt(photo),
                                      mode=photo_data['mode'], size=photo_data['size'])
                img.save(f'temp\\inbox_{data.user_id}.{tc_id}.jpg')
                input_file = FSInputFile(f'temp\\inbox_{data.user_id}.{tc_id}.jpg')
                input_media = InputMediaPhoto(media=input_file)
                await callback.message.edit_media(media=input_media)
                os.remove(f'temp\\inbox_{data.user_id}.{tc_id}.jpg')
            await callback.message.edit_caption(caption=await get_message_content_fmt(tc_id, data.user_id, l10n=l10n),
                                                parse_mode='HTML')
            await callback.message.edit_reply_markup(reply_markup=InlineKeyboardMarkup(
                inline_keyboard=[[
                    InlineKeyboardButton(text=l10n.data['buttons']['delete'],
                                         callback_data=await data.replace_and_pack(
                                             InboxCallbackActions.delete_timecapsule,
                                             cur_timecapsule=tc_id)),
                    InlineKeyboardButton(text=l10n.data['buttons']['back'],
                                         callback_data=await data.replace_and_pack(
                                             InboxCallbackActions.back_to_page))
                ]]
            ))
        except sqlalchemy.exc.NoResultFound:
            await callback.answer(text=l10n.data['tc_doesnt_exist'])


async def handle_delete_from_inbox(data: InboxCallback, callback, l10n: L10N):
    await TC.delete_timecapsule(tg_uid=data.user_id, tc_id=data.cur_timecapsule)
    data.cur_timecapsule = None
    received_messages = await TC.get_received_timecapsules(data.user_id)
    if not received_messages:
        await callback.answer(text=await start_inbox_caption(data.user_id, empty=True, l10n=l10n))
        await callback.message.delete()
        return
    await callback.answer(l10n.data['/timecapsule']['deleted'].format(await user_space_remaining_percent(data.user_id)))
    total_pages = math.ceil(len(received_messages) / 4)
    if data.cur_page == total_pages:
        data.cur_page -= 1

    await callback.message.edit_media(media=InputMediaPhoto(media=inbox_pic))
    await callback.message.edit_caption(caption=await start_inbox_caption(data.user_id, l10n=l10n))
    await callback.message.edit_reply_markup(reply_markup=await start_inbox_menu(data, l10n=l10n))
