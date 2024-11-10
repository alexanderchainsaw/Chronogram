import dataclasses
from aiogram.types import Message, CallbackQuery, PreCheckoutQuery
from collections.abc import Awaitable, Callable
from typing import Any, Dict
from aiogram import BaseMiddleware

import config
from chronogram.database.requests import get_uid_by_tg_uid, add_user_if_not_exists, get_user_attr, ChronogramUser
from .l10n_data import LOC
from redis import Redis


@dataclasses.dataclass
class L10N:
    data: dict
    lang: str


async def get_l10n_by_lang(lang: str):
    if lang not in ('en', 'ru'):
        raise RuntimeError('Invalid language')
    return L10N(lang=lang, data=LOC[lang])


class LocalizationMiddleware(BaseMiddleware):
    def __init__(self, redis: Redis):
        self.r = redis

    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message | CallbackQuery | PreCheckoutQuery,
        data: Dict[str, Any]
    ) -> Any:
        if not (uid := await get_uid_by_tg_uid(event.from_user.id)):
            await add_user_if_not_exists(tg_uid=event.from_user.id, lang=event.from_user.language_code)
            lang = event.from_user.language_code
            if lang not in ('en', 'ru'):
                lang = 'en'
            data['l10n'] = L10N(data=LOC[lang], lang=lang)
            self.r.set(str(event.from_user.id), lang)
            return await handler(event, data)
        if not (lang := self.r.get(str(event.from_user.id))):
            config.config.LOGGER.info('Not in redis storage, going to db')
            lang = await get_user_attr(user_id=uid, col=ChronogramUser.language)
            self.r.set(str(event.from_user.id), lang)
        data['l10n'] = L10N(data=LOC[lang], lang=lang)
        return await handler(event, data)
