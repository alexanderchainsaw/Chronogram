import datetime
from dateutil.relativedelta import relativedelta
import sys
from typing import Optional
from config import config
from chronogram.database.models import (InnerChronogramUserData, InnerChronogramPaymentData, InnerTimeCapsuleData,
                                        OuterChronogramPaymentData, OuterTimeCapsuleData)

from chronogram.database.schema import async_session
from chronogram.database.schema import DEFAULT_USER_SPACE, PREMIUM_USER_SPACE
from chronogram.database.schema import ChronogramUser, TimeCapsule, ChronogramPayment
from chronogram.database.schema import tc_image_data
from sqlalchemy import select, insert, update, delete
from sqlalchemy import desc, func

fernet = config.FERNET


async def get_uid_by_tg_uid(tg_uid: int) -> int:
    async with async_session() as session:
        return await session.scalar(select(ChronogramUser.id).where(ChronogramUser.tg_uid == tg_uid))


async def get_user_attr(col: ChronogramUser, user_id: int = None, tg_uid: int = None):
    if not user_id and not tg_uid:
        raise RuntimeError("Neither provided")
    elif not user_id:
        user_id = await get_uid_by_tg_uid(tg_uid)
    # if not user_id:
    #     await add_user_if_not_exists(tg_uid, lang='en')
    async with async_session() as session:
        return await session.scalar(select(col).where(ChronogramUser.id == user_id))


async def add_user_if_not_exists(tg_uid: int, lang: str) -> bool:
    if not await get_uid_by_tg_uid(tg_uid):
        async with async_session() as session:
            utc_offset = 0
            if lang in country_to_timezone:
                utc_offset = country_to_timezone[lang]
            if lang not in ('en', 'ru'):
                lang = 'en'
            data = InnerChronogramUserData(language=lang, utc_offset_minutes=utc_offset, tg_uid=tg_uid)
            await session.execute(insert(ChronogramUser).values(language=data.language,
                                                                utc_offset_minutes=data.utc_offset_minutes,
                                                                tg_uid=tg_uid,
                                                                joined=datetime.datetime.utcnow()
                                                                .replace(microsecond=0)))
            await session.commit()
            return True
    return False


class TimeCapsuleDatabaseActions:

    @staticmethod
    async def get_timecapsules_to_send() -> list[TimeCapsule]:
        async with async_session() as session:
            data = [x[0] for x in
                    (await session.execute(select(TimeCapsule).where(TimeCapsule.received == False)
                                           .where(TimeCapsule.receive_timestamp <= datetime.datetime.utcnow()))).all()]
            # for tc in data:
            #     tc: TimeCapsule
            #     if tc.image:
            #         tc.image = fernet.decrypt(tc.image)
            #     if tc.text_content:
            #         tc.text_content = fernet.decrypt(tc.text_content).decode('utf-8')
            return data

    @staticmethod
    async def timecapsules_underway(tg_uid) -> bool:
        async with async_session() as session:
            return bool(await session.scalar(select(TimeCapsule.id).where(TimeCapsule.received == False)
                                             .where(TimeCapsule.user_id == await get_uid_by_tg_uid(tg_uid))))

    @staticmethod
    async def timecapsules_received(tg_uid) -> bool:
        async with async_session() as session:
            return bool(await session.scalar(select(TimeCapsule.id).where(TimeCapsule.received == True)
                                             .where(TimeCapsule.user_id == await get_uid_by_tg_uid(tg_uid))))

    @staticmethod
    async def get_received_timecapsules(tg_uid: int) -> list[TimeCapsule]:
        """Get received timecapsules timestamps"""
        async with async_session() as session:
            return (await session.execute(select(TimeCapsule.id,
                                                 TimeCapsule.send_timestamp,
                                                 TimeCapsule.receive_timestamp)
                                          .where(TimeCapsule.user_id == await get_uid_by_tg_uid(tg_uid))
                                          .where(TimeCapsule.received == True))).all()

    @staticmethod
    async def get_timecapsules_for_deletion(tg_uid: int) -> list[TimeCapsule]:
        """Get timecapsules for deletion in case of subscription revoke"""
        async with async_session() as session:
            return (await session.execute(select(TimeCapsule.id,
                                                 TimeCapsule.size)
                                          .where(TimeCapsule.user_id == await get_uid_by_tg_uid(tg_uid))
                                          .order_by(desc(TimeCapsule.received),
                                                    desc(TimeCapsule.send_timestamp)))).all()

    @staticmethod
    async def get_timecapsule_data(tg_uid: int, tc_id: int) -> TimeCapsule:
        """Return timecapsule data WITHOUT the image"""
        async with async_session() as session:
            data: TimeCapsule = (await session.execute(select(TimeCapsule.send_timestamp,
                                                              TimeCapsule.receive_timestamp,
                                                              TimeCapsule.text_content).where(TimeCapsule.id == tc_id)
                                                       .where(TimeCapsule.user_id == await get_uid_by_tg_uid(tg_uid))
                                                       .where(TimeCapsule.received == True))).one()
            return data

    @staticmethod
    async def get_timecapsule_image(tg_uid: int, tc_id: int) -> TimeCapsule.image:
        async with async_session() as session:
            return await session.scalar(
                select(TimeCapsule.image).where(TimeCapsule.id == tc_id).where(
                    TimeCapsule.user_id == await get_uid_by_tg_uid(tg_uid)))

    @staticmethod
    async def get_timecapsule_image_data(tg_uid: int, tc_id: int) -> TimeCapsule.image:
        async with async_session() as session:
            data = await session.scalar(select(TimeCapsule.image_data).where(TimeCapsule.id == tc_id)
                                        .where(TimeCapsule.user_id == await get_uid_by_tg_uid(tg_uid)))
            if not data:
                return
            return await tc_image_data(data)

    @staticmethod
    async def create_timecapsule(data: OuterTimeCapsuleData):
        async with async_session() as session:
            inner = InnerTimeCapsuleData(user_id=await get_uid_by_tg_uid(data.tg_uid),
                                         send_timestamp=data.send_timestamp,
                                         receive_timestamp=data.receive_timestamp - datetime.timedelta
                                         (minutes=await get_user_attr(tg_uid=data.tg_uid,
                                                                      col=ChronogramUser.utc_offset_minutes)),
                                         text_content=fernet.encrypt(data.text_content.encode('utf-8')) if data
                                         .text_content else None,
                                         size=data.size, image=fernet.encrypt(data.image) if data.image else None,
                                         image_data=data.image_data)
            await session.execute(insert(TimeCapsule).values(user_id=inner.user_id,
                                                             send_timestamp=inner.send_timestamp,
                                                             receive_timestamp=inner.receive_timestamp,
                                                             text_content=inner.text_content,
                                                             size=inner.size,
                                                             image=inner.image,
                                                             image_data=inner.image_data))
            await session.execute(update(ChronogramUser)
                                  .where(ChronogramUser.id == await get_uid_by_tg_uid(data.tg_uid))
                                  .values(
                space_available=await get_user_attr(
                    tg_uid=data.tg_uid, col=ChronogramUser.space_available) - data.size,
                space_taken=await get_user_attr(tg_uid=data.tg_uid, col=ChronogramUser.space_taken) + data.size))
            await session.commit()

    @staticmethod
    async def delete_timecapsule(tg_uid: int, tc_id: int):
        async with async_session() as session:
            size_to_free = await session.scalar(select(TimeCapsule.size).where(TimeCapsule.id == tc_id)
                                                .where(TimeCapsule.user_id == await get_uid_by_tg_uid(tg_uid)))

            await session.execute(delete(TimeCapsule).where(TimeCapsule.id == tc_id)
                                  .where(TimeCapsule.user_id == await get_uid_by_tg_uid(tg_uid)))
            await session.execute(update(ChronogramUser).where(ChronogramUser.id == await get_uid_by_tg_uid(tg_uid))
                                  .values(
                space_available=await get_user_attr(tg_uid=tg_uid, col=ChronogramUser.space_available) + size_to_free,
                space_taken=await get_user_attr(tg_uid=tg_uid, col=ChronogramUser.space_taken) - size_to_free))
            await session.commit()

    @staticmethod
    async def delete_everything(tg_uid: int):
        async with async_session() as session:
            uid = await get_uid_by_tg_uid(tg_uid)
            await session.execute(delete(TimeCapsule).where(TimeCapsule.user_id == uid))
            await session.execute(update(ChronogramUser).where(
                ChronogramUser.id == await get_uid_by_tg_uid(tg_uid)).values(
                space_available=DEFAULT_USER_SPACE if not await get_user_attr(user_id=uid,
                                                                              col=ChronogramUser.subscription)
                else PREMIUM_USER_SPACE,
                space_taken=0))
            await session.commit()

    @staticmethod
    async def mark_as_received(tg_uid: int, tc_id: int):
        async with async_session() as session:
            await session.execute(
                update(TimeCapsule).where(TimeCapsule.user_id == await get_uid_by_tg_uid(tg_uid))
                .where(TimeCapsule.id == tc_id)
                .values(received=True))
            await session.commit()

    @staticmethod
    async def is_enough_space(tg_uid: int, text: str, image=Optional[bytearray]) -> bool:
        content_size = await TimeCapsuleDatabaseActions.get_timecapsule_size(text, image)
        available_space = await get_user_attr(tg_uid=tg_uid, col=ChronogramUser.space_available)
        if content_size > available_space:
            return False
        return True

    @staticmethod
    async def get_timecapsule_size(text: str, image=Optional[bytearray]) -> int:
        text_size = len(text.encode('utf-8'))
        image_size = 0
        if image:
            image_size = sys.getsizeof(image)
        return text_size + image_size


async def get_subscribers_with_expiring_subscription() -> list[ChronogramUser]:
    async with async_session() as session:
        return [x[0] for x in
                (await session.execute(select(ChronogramUser).where(ChronogramUser.subscription_deadline is not None)
                                       .where(ChronogramUser.notified_deadline == False)
                                       .where(datetime.datetime.utcnow() >=
                                              (ChronogramUser.subscription_deadline - datetime.timedelta(days=1))))
                 ).all()]


async def get_subscribers_with_expired_subscription() -> list[ChronogramUser]:
    async with async_session() as session:
        return [x[0] for x in
                (await session.execute(select(ChronogramUser).where(ChronogramUser.subscription_deadline is not None)
                                       .where(datetime.datetime.utcnow() >= ChronogramUser.subscription_deadline)))
                .all()]


async def mark_as_notified(tg_uid: int):
    async with async_session() as session:
        await session.execute(update(ChronogramUser).where(ChronogramUser.id == await get_uid_by_tg_uid(tg_uid=tg_uid))
                              .values(notified_deadline=True))
        await session.commit()


async def edit_utc_diff(tg_uid, value: int):
    async with async_session() as session:
        await session.execute(update(ChronogramUser).where(ChronogramUser.id == await get_uid_by_tg_uid(tg_uid)).values(
            utc_offset_minutes=value))
        await session.commit()


async def edit_language(tg_uid: int, new_lang: str):
    async with async_session() as session:
        await session.execute(update(ChronogramUser).where(ChronogramUser.id == await get_uid_by_tg_uid(tg_uid)).values(
            language=new_lang))
        await session.commit()


async def revoke_subscription(tg_uid: int):
    user_id = await get_uid_by_tg_uid(tg_uid)
    space_taken = await get_user_attr(user_id=user_id, col=ChronogramUser.space_taken)
    if space_taken > DEFAULT_USER_SPACE:
        for tc in await TimeCapsuleDatabaseActions.get_timecapsules_for_deletion(tg_uid):
            await TimeCapsuleDatabaseActions.delete_timecapsule(tg_uid=tg_uid, tc_id=tc.id)
            space_taken -= tc.size
            if space_taken <= DEFAULT_USER_SPACE:
                break
    async with async_session() as session:
        await session.execute(update(ChronogramUser).where(ChronogramUser.id == user_id)
                              .values(subscription_deadline=None,
                                      subscription=False,
                                      notified_deadline=False,
                                      space_available=DEFAULT_USER_SPACE - space_taken,
                                      space_taken=space_taken))
        await session.commit()


async def invoice_exists(invoice_id: str):
    async with async_session() as session:
        if await session.scalar(select(
                ChronogramPayment.invoice_id).where(ChronogramPayment.invoice_id == invoice_id)):
            return True
        return False


async def process_refund(tg_uid: int, telegram_payment_charge_id: str):
    async with async_session() as session:
        pay_data: list[ChronogramPayment] = (await session.execute(
            select(ChronogramPayment).where(
                ChronogramPayment.tg_transaction_id == telegram_payment_charge_id).where(
                ChronogramPayment.user_id == await get_uid_by_tg_uid(tg_uid)))).all()

        if not pay_data:
            return 'INVALID_PAY_ID'
        pay_data = pay_data[0][0]
        # elif pay_data.timestamp + relativedelta(days=1) < datetime.datetime.utcnow():
        #     return '24_PASSED'
        # elif pay_data.type == 'subscription':
        #     return 'SUBSCRIPTION'
        if pay_data.status == 'refunded':
            return 'REFUNDED'
        else:
            await session.execute(update(ChronogramPayment)
                                  .where(ChronogramPayment.tg_transaction_id == telegram_payment_charge_id)
                                  .where(ChronogramPayment.user_id == await get_uid_by_tg_uid(tg_uid))
                                  .values(status='refunded'))
            await session.commit()
            return 'SUCCESS'


async def grant_subscription(user_id: int, months: int):
    async with async_session() as session:
        await session.execute(update(ChronogramUser).where(ChronogramUser.id == user_id)
                              .values(subscription=True,
                                      subscription_deadline=(datetime
                                                             .datetime.utcnow() + relativedelta(months=months))
                                      .replace(microsecond=0),
                                      space_available=PREMIUM_USER_SPACE - await get_user_attr(
                                          user_id=user_id, col=ChronogramUser.space_taken)))
        await session.commit()


async def _prolong_subscription(user_id: int, months: int):
    async with async_session() as session:
        cur_deadline = await get_user_attr(user_id=user_id, col=ChronogramUser.subscription_deadline)
        await session.execute(update(ChronogramUser).where(ChronogramUser.id == user_id).values(
            subscription_deadline=cur_deadline + relativedelta(months=months)))
        await session.commit()


async def process_payment(pay_data: OuterChronogramPaymentData, months: int = None) -> str:
    response = 'DONATE'
    async with async_session() as session:
        user_id = await get_uid_by_tg_uid(pay_data.tg_uid)
        inner_data = InnerChronogramPaymentData(user_id=user_id, invoice_id=pay_data.invoice_id,
                                                tg_transaction_id=pay_data.tg_transaction_id,
                                                timestamp=pay_data.timestamp, type=pay_data.type,
                                                xtr_amount=pay_data.xtr_amount)
        await session.execute(insert(ChronogramPayment).values(timestamp=inner_data.timestamp,
                                                               user_id=user_id,
                                                               invoice_id=inner_data.invoice_id,
                                                               tg_transaction_id=inner_data.tg_transaction_id,
                                                               xtr_amount=inner_data.xtr_amount,
                                                               type=inner_data.type,
                                                               status=inner_data.status))
        if pay_data.type == 'subscription':
            if await session.scalar(select(ChronogramUser.subscription).where(ChronogramUser.id == user_id)):
                print('prolong')
                response = 'PROLONG'
                await _prolong_subscription(user_id, months)
            else:
                print('grant')
                response = 'GRANT'
                await grant_subscription(user_id, months)

        await session.commit()
    return response


async def get_stats() -> tuple[int, int, int]:
    async with async_session() as session:

        total_users = (await session.execute(select(func.count(ChronogramUser.id)))).scalar_one()

        subs_bought = (await session.execute(select(
            func.count(ChronogramPayment.id)).where(ChronogramPayment.type == 'subscription'))).scalar_one()

        subs_now = (await session.execute(
            func.count(select(ChronogramUser.id)).where(ChronogramUser.subscription == True))).scalar_one()
        return total_users, subs_bought, subs_now


country_to_timezone = {
    'af': 270, 'al': 120, 'dz': 60, 'as': -660, 'ad': 120, 'ao': 60, 'ai': -240, 'aq': 480, 'ag': -240,
    'ar': -180, 'am': 240, 'aw': -240, 'au': 600, 'at': 120, 'az': 240, 'bs': -240, 'bh': 180, 'bd': 360,
    'bb': -240, 'by': 180, 'be': 120, 'bz': -360, 'bj': 60, 'bm': -180, 'bt': 360, 'bo': -240, 'bq': -240,
    'ba': 120, 'bw': 120, 'br': -180, 'io': 360, 'bn': 480, 'bg': 180, 'bf': 0, 'kh': 420, 'cm': 60, 'ca': -300,
    'cv': -60, 'ky': -300, 'cf': 60, 'td': 60, 'cl': -240, 'cn': 480, 'cx': 420, 'cc': 390, 'co': -300, 'km': 180,
    'cg': 60, 'cd': 60, 'ck': -600, 'cr': -360, 'hr': 120, 'cu': -240, 'cw': -240, 'cy': 180, 'cz': 120, 'ci': 0,
    'dk': 120, 'dj': 180, 'dm': -240, 'do': -240, 'ec': -300, 'eg': 180, 'sv': -360, 'gq': 60, 'er': 180, 'ee': 180,
    'et': 180, 'fk': -180, 'fo': 60, 'fj': 720, 'fi': 180, 'fr': 120, 'gf': -180, 'pf': -570, 'tf': 300, 'ga': 60,
    'gm': 0, 'ge': 240, 'de': 120, 'gh': 0, 'gi': 120, 'gr': 180, 'gl': -60, 'gd': -240, 'gp': -420, 'gu': 600,
    'gt': -360, 'gg': 60, 'gn': 0, 'gw': 0, 'gy': -240, 'ht': -240, 'va': 120, 'hn': -360, 'hk': 480, 'hu': 120,
    'is': 0, 'in': 330, 'id': 420, 'ir': 210, 'iq': 180, 'ie': 60, 'im': 60, 'il': 180, 'it': 120, 'jm': -300,
    'jp': 540, 'je': 60, 'jo': 180, 'kz': 300, 'ke': 180, 'ki': 840, 'kp': 540, 'kr': 540, 'kw': 180, 'kg': 360,
    'la': 420, 'lv': 180, 'lb': 180, 'ls': 120, 'lr': 0, 'ly': 120, 'li': 120, 'lt': 180, 'lu': 120, 'mo': 480,
    'mk': 120, 'mg': 180, 'mw': 120, 'my': 480, 'mv': 300, 'ml': 0, 'mt': 120, 'mh': 720, 'mq': -240, 'mr': 0,
    'mu': 240, 'yt': 180, 'mx': -360, 'fm': 660, 'md': 180, 'mc': 120, 'mn': 480, 'me': 120, 'ms': -240, 'ma': 60,
    'mz': 120, 'mm': 390, 'na': 120, 'nr': 720, 'np': 345, 'nl': 120, 'nc': 660, 'nz': 720, 'ni': -360, 'ne': 60,
    'ng': 60, 'nu': -660, 'nf': 660, 'mp': 600, 'no': 120, 'om': 420, 'pk': 300, 'pw': 540, 'ps': 180, 'pa': -300,
    'pg': 660, 'py': -240, 'pe': -300, 'ph': 480, 'pn': -480, 'pl': 120, 'pt': 60, 'pr': -240, 'qa': 180, 'ro': 180,
    'ru': 180, 'rw': 120, 're': 240, 'bl': -240, 'sh': 0, 'kn': -240, 'lc': -240, 'mf': -240, 'pm': -120, 'vc': -240,
    'ws': 780, 'sm': 120, 'st': 0, 'sa': 180, 'sn': 0, 'rs': 120, 'sc': 240, 'sl': 0, 'sg': 480, 'sx': -240,
    'sk': 120, 'si': 120, 'sb': 660, 'so': 180, 'za': 120, 'gs': -120, 'ss': 120, 'es': 120, 'lk': 330, 'sd': 120,
    'sr': -180, 'sj': 120, 'sz': 120, 'se': 120, 'ch': 120, 'sy': 180, 'tw': 480, 'tj': 300, 'tz': 180, 'th': 420,
    'tl': 540, 'tg': 0, 'tk': 780, 'to': 780, 'tt': -240, 'tn': 60, 'tr': 180, 'tm': 300, 'tc': -240, 'tv': 720,
    'ug': 180, 'ua': 180, 'ae': 240, 'gb': 60, 'us': -240, 'um': -660, 'uy': -180, 'uz': 300, 'vu': 660, 've': -240,
    'vn': 420, 'vg': -240, 'vi': -240, 'wf': 720, 'ye': 180, 'zm': 120, 'zw': 120, 'ax': 180
}
