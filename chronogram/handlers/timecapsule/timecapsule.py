import html
from datetime import datetime, timedelta
import sys
import aiogram.exceptions
from PIL import Image
from chronogram.handlers.timecapsule.aiogram3_simplecalendar import SimpleCalendar, SimpleCalendarCallback
from chronogram.handlers.timecapsule.timepicker_bigstep import process_selection, start_timepicker, TimepickerCallback
from chronogram.utils import user_space_remaining_percent, perform_state_clear, get_default_close_button
import chronogram.database.requests as db_req
from chronogram.database.schema import ChronogramUser
from chronogram.database.models import OuterTimeCapsuleData
from chronogram.database.requests import TimeCapsuleDatabaseActions as TC
from aiogram import Router, F
from aiogram.filters import Command
from chronogram.photo_utils import PhotoReader
from chronogram.handlers.timecapsule.helpers import (_get_not_enough_space_message, _validate_timecapsule,
                                                     parse_date_from_message, parse_content_from_message,
                                                     parse_datetime_from_message)
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from config import config
from chronogram.middlewares import L10N

timecapsule_router = Router(name='timecapsule_router')


class TimeCapsuleCreate(StatesGroup):
    choosing_content = State()


@timecapsule_router.message(Command('timecapsule'))
async def create_timecapsule(message: Message, state: FSMContext, l10n: L10N) -> None:
    await perform_state_clear(state=state, uid=message.from_user.id)
    prompt_content_msg_id = (await message.answer(text=l10n.data['/timecapsule']["init"],
                                                  reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                                                      [InlineKeyboardButton(text=l10n.data['buttons']['cancel'],
                                                                            callback_data='default_close_menu')]]))
                             ).message_id
    await state.set_state(TimeCapsuleCreate.choosing_content)
    await state.update_data(prompt_content_msg_id=prompt_content_msg_id)
    await state.update_data(messages_to_delete=(prompt_content_msg_id,))
    await message.delete()


@timecapsule_router.edited_message(TimeCapsuleCreate.choosing_content)
@timecapsule_router.message(TimeCapsuleCreate.choosing_content)
async def timecapsule_prompt_date(message: Message, state: FSMContext, l10n: L10N):
    valid, tc_type = await _validate_timecapsule(message)

    if not valid:
        keyboard = InlineKeyboardMarkup(inline_keyboard=[[await get_default_close_button(l10n.lang)]])
        match tc_type:
            case 'Space':
                await message.answer(text=await _get_not_enough_space_message(
                    tg_uid=message.from_user.id, l10n=l10n), reply_markup=keyboard)
            case 'Data':
                await message.answer(
                    text=l10n.data['/timecapsule']['invalid_data'], reply_markup=keyboard)
            case 'Length':
                if message.photo:
                    await message.answer(
                        text=l10n.data['/timecapsule']['invalid_caption_length']
                        .format(len(message.text)), reply_markup=keyboard)
                else:
                    await message.answer(
                        text=l10n.data['/timecapsule']['invalid_length']
                        .format(len(message.text)), reply_markup=keyboard)
        try:
            data = await state.get_data()
            await config.BOT.delete_message(message_id=data['prompt_content_msg_id'], chat_id=message.from_user.id)
        except (aiogram.exceptions.TelegramBadRequest, KeyError) as err:
            config.LOGGER.warning(f"[1] Error on message delete timecapsule: {err}")
        await state.clear()
        return
    timecapsule_text = message.text if tc_type == 'Text' else message.caption
    if timecapsule_text:
        await state.update_data(tc_size=len(timecapsule_text.encode('utf-8')))
    if message.photo:
        ph = PhotoReader(photo=message.photo, file_name="None")
        photo_blob = await ph.get_blob_image()
        tc_size = sys.getsizeof(photo_blob)
        if timecapsule_text:
            tc_size += len(timecapsule_text.encode('utf-8'))
        await state.update_data(tc_size=tc_size)

    calendar = SimpleCalendar(locale=l10n.lang, show_alerts=True)
    user_time = datetime.utcnow() + timedelta(minutes=await db_req.get_user_attr(tg_uid=message.from_user.id,
                                                                                 col=ChronogramUser.utc_offset_minutes))
    calendar.set_dates_range(datetime(user_time.year, user_time.month, user_time.day),
                             datetime(user_time.year + 1000, user_time.month, user_time.day))

    message_response = ("<blockquote>{}</blockquote>\n\n".format(
        html.escape(timecapsule_text) if timecapsule_text else '') + f"{l10n.data['/timecapsule']['prompt_date']}")
    if message.photo:
        ph = PhotoReader(photo=message.photo, file_name=f"temp\\create_{message.from_user.id}.jpg")
        input_file = await ph.load_image_from_tg()
        await message.answer_photo(photo=input_file,
                                   caption=message_response,
                                   reply_markup=await calendar.start_calendar(l10n=l10n, year=user_time.year,
                                                                              month=user_time.month))
        await ph.delete()

        try:
            data = await state.get_data()
            await config.BOT.delete_message(message_id=data['prompt_content_msg_id'], chat_id=message.from_user.id)
        except (aiogram.exceptions.TelegramBadRequest, KeyError) as err:
            config.LOGGER.warning(f"[2] Error on message delete timecapsule: {err}")
        await message.delete()
        await state.clear()
        return
    await message.answer(text=message_response,
                         reply_markup=await calendar.start_calendar(l10n=l10n, year=user_time.year,
                                                                    month=user_time.month))
    try:
        data = await state.get_data()
        await config.BOT.delete_message(message_id=data['prompt_content_msg_id'], chat_id=message.from_user.id)
    except (aiogram.exceptions.TelegramBadRequest, KeyError) as err:
        config.LOGGER.warning(f"[3] Error on message delete timecapsule: {err}")
    await message.delete()
    await state.clear()


@timecapsule_router.callback_query(SimpleCalendarCallback.filter())
async def process_date_selection(callback: CallbackQuery, callback_data: SimpleCalendarCallback, l10n: L10N):
    calendar = SimpleCalendar(
        locale=l10n.lang, show_alerts=True
    )
    user_time = datetime.utcnow() + timedelta(minutes=await db_req.get_user_attr(tg_uid=callback.from_user.id,
                                                                                 col=ChronogramUser.utc_offset_minutes))
    selected, date, canceled = await calendar.process_selection(callback, callback_data, l10n=l10n)

    if selected:
        content = await parse_content_from_message(callback)
        timepicker_callback = TimepickerCallback(user_id=callback.from_user.id, hour=user_time.hour,
                                                 minute=user_time.minute)
        message_response = (
                f"<blockquote>{content if content else ''}"
                f"</blockquote>\n\n" + f"{l10n.data['/timecapsule']['input_time'].format(date.strftime('%d.%m.%Y'))}")
        if callback.message.photo:
            await callback.message.edit_caption(caption=message_response,
                                                reply_markup=await start_timepicker(data=timepicker_callback,
                                                                                    l10n=l10n))
            return
        await callback.message.edit_text(text=message_response,
                                         reply_markup=await start_timepicker(data=timepicker_callback, l10n=l10n))

    elif canceled:
        await timecapsule_canceled(callback, l10n=l10n)


@timecapsule_router.callback_query(TimepickerCallback.filter())
async def process_time(callback: CallbackQuery, callback_data: TimepickerCallback, l10n: L10N):
    selected, _time, canceled = await process_selection(callback, callback_data, l10n=l10n)
    if selected:
        selected_date = datetime.strptime(await parse_date_from_message(callback), '%d.%m.%Y')
        selected_datetime = datetime(selected_date.year, selected_date.month, selected_date.day,
                                     hour=int(_time.hour), minute=int(_time.minute))
        if selected_datetime < datetime.utcnow() + timedelta(
                minutes=await db_req.get_user_attr(tg_uid=callback.from_user.id,
                                                   col=ChronogramUser.utc_offset_minutes)):
            await callback.answer(l10n.data['/timecapsule']['only_future'])
            return
        await confirm_send(callback, _time, l10n=l10n)
        return
    elif canceled:
        await timecapsule_canceled(callback, l10n=l10n)


async def timecapsule_canceled(callback: CallbackQuery, l10n: L10N):
    content = await parse_content_from_message(callback)
    if content:
        msg = f"<blockquote>{content}</blockquote>\n\n" + f"<b>{l10n.data['/timecapsule']['canceled_no_text']}</b>"
    else:
        msg = f"<b>{l10n.data['/timecapsule']['canceled_no_text']}</b>"
    if callback.message.photo:
        await callback.message.edit_caption(caption=msg,
                                            reply_markup=InlineKeyboardMarkup(
                                                inline_keyboard=[
                                                    [InlineKeyboardButton(text=l10n.data['buttons']['close'],
                                                                          callback_data='default_close_menu')]]))
        return
    await callback.message.edit_text(
        text=msg,
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text=l10n.data['buttons']['close'],
                                      callback_data='default_close_menu')]]))


async def confirm_send(callback: CallbackQuery, _time, l10n: L10N):
    content = await parse_content_from_message(callback)
    date = await parse_date_from_message(callback)
    msg = f"<blockquote>{content}</blockquote>\n\n"
    msg += l10n.data['/timecapsule']['confirm_no_text'].format(f"{date} {_time.strftime('%H:%M')}")
    if callback.message.photo:
        await callback.message.edit_caption(caption=msg,
                                            reply_markup=InlineKeyboardMarkup(
                                                inline_keyboard=[
                                                    [InlineKeyboardButton(
                                                        text=l10n.data['buttons']['cancel'],
                                                        callback_data='send_cancel'),
                                                        InlineKeyboardButton(
                                                            text=l10n.data['buttons']['send'],
                                                            callback_data='send_confirm')]
                                                ]))

        return
    await callback.message.edit_text(text=msg,
                                     reply_markup=InlineKeyboardMarkup(
                                         inline_keyboard=[
                                             [InlineKeyboardButton(
                                                 text=l10n.data['buttons']['cancel'],
                                                 callback_data='send_cancel'),
                                                 InlineKeyboardButton(
                                                     text=l10n.data['buttons']['send'],
                                                     callback_data='send_confirm')]
                                         ]))


@timecapsule_router.callback_query(F.data == 'send_confirm')
async def message_sent(callback: CallbackQuery, l10n: L10N):
    tc_size = 0
    photo = None
    photo_data = None

    if callback.message.photo:
        ph = PhotoReader(photo=callback.message.photo, file_name=f"temp\\create_{callback.from_user.id}.jpg")
        for_size = await ph.get_blob_image()
        tc_size = sys.getsizeof(for_size)
        await ph.load_image_from_tg()
        img = Image.open(f"temp\\create_{callback.from_user.id}.jpg")
        photo = img.tobytes()
        photo_data = f"{img.mode}_{img.size[0]}-{img.size[1]}"
        img.close()

        await ph.delete()

    content = await parse_content_from_message(callback)
    date, _time = await parse_datetime_from_message(callback)

    if content:
        tc_size += len(content.encode('utf-8'))

    await TC.create_timecapsule(data=OuterTimeCapsuleData(tg_uid=callback.from_user.id,
                                                          text_content=content,
                                                          receive_timestamp=datetime.strptime(date + ' ' + _time,
                                                                                              "%d.%m.%Y %H:%M")
                                                          .replace(microsecond=0),
                                                          send_timestamp=datetime.utcnow().replace(microsecond=0),
                                                          image=photo,
                                                          image_data=photo_data,
                                                          size=tc_size))

    await callback.answer(l10n.data['/timecapsule']['sent']
                          .format(await user_space_remaining_percent(tg_uid=callback.from_user.id)))
    await callback.message.delete()
    config.LOGGER.info(f"User ...{str(callback.from_user.id)[5:]} sent timecapsule")


@timecapsule_router.callback_query(F.data == 'send_cancel')
async def cancel_send(callback: CallbackQuery, l10n: L10N):
    await timecapsule_canceled(callback, l10n=l10n)
    return
