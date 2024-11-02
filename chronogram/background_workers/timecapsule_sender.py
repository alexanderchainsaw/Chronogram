import asyncio
import datetime
import os
from PIL import Image
from enum import Enum
from chronogram.utils import user_space_remaining_percent
import chronogram.database.requests as db_req
from chronogram.database.schema import TimeCapsule, ChronogramUser
from chronogram.database.requests import TimeCapsuleDatabaseActions as TC
from aiogram.types.input_file import FSInputFile
from aiogram.filters.callback_data import CallbackData
from aiogram.types import CallbackQuery
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from config import config
from chronogram.middlewares import L10N, get_l10n_by_lang


class KeepOrDeleteCallback(CallbackData, prefix='keep_or_delete'):
    action: str
    tg_uid: int
    tc_id: int


class KeepOrDeleteActions(str, Enum):
    keep_message = 'KEEP_MESSAGE'
    delete_message = 'DELETE_MESSAGE'
    cancel_delete = 'CANCEL_DELETE'
    confirm_delete = 'CONFIRM_DELETE'


async def deliver_timecapsules():
    while True:
        timecapsules: list[TimeCapsule] = await TC.get_timecapsules_to_send()
        if timecapsules:
            for tc in timecapsules:
                tg_uid = await db_req.get_user_attr(user_id=tc.user_id, col=ChronogramUser.tg_uid)
                user_lang = await db_req.get_user_attr(user_id=tc.user_id, col=ChronogramUser.language)
                await send_timecapsule(tg_uid=tg_uid, sent=tc.send_timestamp,
                                       tc_id=tc.id, photo=tc.image, content=tc.text_content,
                                       l10n=await get_l10n_by_lang(lang=user_lang))
                await TC.mark_as_received(tg_uid=tg_uid, tc_id=tc.id)
                config.LOGGER.info(f"Sent timecapsule to ...{str(tg_uid)[5:]}, "
                                   f"abs time = {tc.receive_timestamp - tc.send_timestamp}")
        await asyncio.sleep(5)


async def get_formatted_msg_content(tg_uid: int, content: bytes, sent: datetime.datetime, l10n: L10N) -> str:
    utc_diff = await db_req.get_user_attr(tg_uid=tg_uid, col=ChronogramUser.utc_offset_minutes)
    if content:
        formatted_msg = l10n.data['/timecapsule']['received'].format(
            datetime.datetime.strftime(sent + datetime.timedelta(minutes=utc_diff),
                                       '%H:%M %d.%m.%Y'), config.FERNET.decrypt(content).decode('utf-8'))
    else:
        formatted_msg = l10n.data['/timecapsule']['received'].format(
            datetime.datetime.strftime(sent + datetime.timedelta(minutes=utc_diff),
                                       '%H:%M %d.%m.%Y'), '')
    return formatted_msg


async def send_timecapsule(tg_uid, sent, content, tc_id, photo, l10n: L10N):

    if photo:
        photo_data = await TC.get_timecapsule_image_data(tg_uid=tg_uid, tc_id=tc_id)
        img = Image.frombytes(data=config.FERNET.decrypt(photo), mode=photo_data['mode'], size=photo_data['size'])
        img.save(f'temp\\send_{tg_uid}.jpg')
        input_file = FSInputFile(f'temp\\send_{tg_uid}.jpg')
        await config.BOT.send_photo(has_spoiler=True,
                                    chat_id=tg_uid,
                                    photo=input_file,
                                    caption=await get_formatted_msg_content(tg_uid, content, sent, l10n=l10n),
                                    reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(
                                         text=l10n.data['buttons']['keep'],
                                         callback_data=KeepOrDeleteCallback(
                                             action=KeepOrDeleteActions.keep_message,
                                             tg_uid=tg_uid,
                                             tc_id=tc_id).pack()),
                                         InlineKeyboardButton(
                                             text=l10n.data['buttons']['delete'],
                                             callback_data=KeepOrDeleteCallback(
                                                 action=KeepOrDeleteActions.delete_message,
                                                 tg_uid=tg_uid,
                                                 tc_id=tc_id).pack())]]
                                     ))
        os.remove(f'temp\\send_{tg_uid}.jpg')
    else:
        await config.BOT.send_message(chat_id=tg_uid,
                                      text=await get_formatted_msg_content(tg_uid, content, sent, l10n=l10n),
                                      reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(
                                          text=l10n.data['buttons']['keep'],
                                          callback_data=KeepOrDeleteCallback(
                                            action=KeepOrDeleteActions.keep_message,
                                            tg_uid=tg_uid,
                                            tc_id=tc_id).pack()),
                                          InlineKeyboardButton(
                                              text=l10n.data['buttons']['delete'],
                                              callback_data=KeepOrDeleteCallback(
                                                action=KeepOrDeleteActions.delete_message,
                                                tg_uid=tg_uid,
                                                tc_id=tc_id).pack())]]))


async def process_selection(callback: CallbackQuery, data: KeepOrDeleteCallback, l10n: L10N):
    photo = await TC.get_timecapsule_image(tg_uid=data.tg_uid, tc_id=data.tc_id)
    tc = await TC.get_timecapsule_data(tg_uid=data.tg_uid, tc_id=data.tc_id)

    match data.action:
        case KeepOrDeleteActions.keep_message:
            await callback.answer(text=l10n.data["/timecapsule"]['saved']
                                  .format(await user_space_remaining_percent(data.tg_uid)))
            await callback.message.delete()
        case KeepOrDeleteActions.delete_message:
            markup = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(
                text=l10n.data['buttons']['confirm_delete'],
                callback_data=KeepOrDeleteCallback(action=KeepOrDeleteActions.confirm_delete,
                                                   tg_uid=data.tg_uid,
                                                   tc_id=data.tc_id).pack()),
                InlineKeyboardButton(
                    text=l10n.data['buttons']['cancel'],
                    callback_data=KeepOrDeleteCallback(
                        action=KeepOrDeleteActions.cancel_delete,
                        tg_uid=data.tg_uid,
                        tc_id=data.tc_id).pack())]]
            )
            if photo:
                await callback.message.edit_caption(caption=await get_formatted_msg_content(data.tg_uid,
                                                                                            tc.text_content,
                                                                                            tc.send_timestamp,
                                                                                            l10n=l10n) +
                                                    l10n.data["/timecapsule"]['delete'],
                                                    reply_markup=markup)
                return
            await callback.message.edit_text(
                text=await get_formatted_msg_content(data.tg_uid, tc.text_content, tc.send_timestamp, l10n=l10n),
                reply_markup=markup)

        case KeepOrDeleteActions.cancel_delete:
            markup = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(
                text=l10n.data['buttons']['keep'],
                callback_data=KeepOrDeleteCallback(
                    action=KeepOrDeleteActions.keep_message,
                    tg_uid=data.tg_uid,
                    tc_id=data.tc_id).pack()),
                InlineKeyboardButton(
                    text=l10n.data['buttons']['delete'],
                    callback_data=KeepOrDeleteCallback(
                        action=KeepOrDeleteActions.delete_message,
                        tg_uid=data.tg_uid,
                        tc_id=data.tc_id).pack())]]
            )
            if photo:
                await callback.message.edit_caption(
                    caption=await get_formatted_msg_content(data.tg_uid, tc.text_content,
                                                            tc.send_timestamp, l10n=l10n), reply_markup=markup)
                return
            await callback.message.edit_text(text=await get_formatted_msg_content(data.tg_uid, tc.text_content,
                                                                                  tc.send_timestamp, l10n=l10n),
                                             reply_markup=markup)

        case KeepOrDeleteActions.confirm_delete:
            await TC.delete_timecapsule(tg_uid=data.tg_uid, tc_id=data.tc_id)
            await callback.answer(l10n.data["/timecapsule"]['deleted']
                                  .format(await user_space_remaining_percent(data.tg_uid)))
            await callback.message.delete()
