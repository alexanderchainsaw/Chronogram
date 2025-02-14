import asyncio
from aiogram.methods import DeleteWebhook
from aiogram import Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import CallbackQuery
from config import config
from chronogram.middlewares import StructLoggingMiddleware, LocalizationMiddleware, L10N
from chronogram.database import async_main as init_postgresql
from chronogram.handlers import routers
from chronogram.background_workers.timecapsule_sender import (
    KeepOrDeleteCallback,
    process_selection,
)
from chronogram.background_workers import (
    subscription_revoker,
    deliver_timecapsules,
    deadline_notificator,
)


async def main():
    await init_postgresql()
    dp = Dispatcher(storage=MemoryStorage())
    dp.include_routers(*routers)
    dp.update.outer_middleware(StructLoggingMiddleware(logger=config.LOGGER))
    dp.message.outer_middleware(LocalizationMiddleware(redis=config.AIOREDIS))
    dp.callback_query.outer_middleware(LocalizationMiddleware(redis=config.AIOREDIS))
    dp.pre_checkout_query.outer_middleware(
        LocalizationMiddleware(redis=config.AIOREDIS)
    )
    asyncio.ensure_future(deliver_timecapsules())
    asyncio.ensure_future(deadline_notificator())
    asyncio.ensure_future(subscription_revoker())

    # the choice was to either make a separate router for this or to just put it here
    # (it handles a menu which appears when user receives a timecapsule)
    # ./chronogram/background_workers/timecapsule_sender.py
    @dp.callback_query(KeepOrDeleteCallback.filter())
    async def process_keep_or_delete_callback(
        callback_query: CallbackQuery, callback_data: KeepOrDeleteCallback, l10n: L10N
    ):
        await process_selection(callback_query, callback_data, l10n=l10n)

    try:
        config.LOGGER.info("Initialization successful, starting polling...")
        await config.BOT(DeleteWebhook(drop_pending_updates=True))
        await dp.start_polling(config.BOT, skip_updates=True)
    finally:
        await dp.stop_polling()
        await config.BOT.session.close()
        config.LOGGER.info("Stopped polling, session closed")


if __name__ == "__main__":
    asyncio.run(main())
