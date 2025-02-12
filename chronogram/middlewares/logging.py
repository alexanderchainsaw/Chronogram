import time
from collections.abc import Awaitable, Callable
from typing import Any, cast
import structlog.typing
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, Update


HANDLED_STR = ["Unhandled", "Handled"]


class StructLoggingMiddleware(BaseMiddleware):
    def __init__(self, logger: structlog.typing.FilteringBoundLogger) -> None:
        self.logger = logger
        super().__init__()

    async def __call__(
        self,
        handler: Callable[[Update, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        event = cast(Update, event)
        _started_processing_at = time.time()
        logger = self.logger.bind(update_id=event.update_id)
        if event.message:
            message = event.message
            logger = logger.bind(
                message_id=message.message_id,
                # chat_type=message.chat.type,
                chat_id=f"...{str(message.chat.id)[5:]}",
            )
            if message.from_user is not None:
                logger = logger.bind(user_id=f"...{str(message.from_user.id)[5:]}")
            if message.text:
                logger = logger.bind(
                    text=message.text[:5] + "...", entities=message.entities
                )
            if message.video:
                logger = logger.bind(
                    caption=message.caption[:5] + "...",
                    caption_entities=message.caption_entities,
                    video_id=message.video.file_id,
                    video_unique_id=message.video.file_unique_id,
                )
            if message.photo:
                logger = logger.bind(
                    caption=message.caption[:5] + "...",
                    caption_entities=message.caption_entities,
                    photo_id=message.photo[-1].file_id,
                    photo_unique_id=message.photo[-1].file_unique_id,
                )
            logger.debug("Received message")
        elif event.callback_query:
            c = event.callback_query
            logger = logger.bind(
                callback_query_id=c.id,
                callback_data=c.data,
                user_id=f"...{str(c.from_user.id)[5:]}",
                inline_message_id=c.inline_message_id,
                chat_instance=c.chat_instance,
            )
            if c.message is not None:
                logger = logger.bind(
                    message_id=c.message.message_id,
                    chat_type=c.message.chat.type,
                    chat_id=f"...{str(c.message.chat.id)[5:]}",
                )
            logger.debug("Received callback query")
        elif event.inline_query:
            query = event.inline_query
            logger = logger.bind(
                query_id=query.id,
                user_id=f"...{str(query.from_user.id)[5:]}",
                query=query.query,
                offset=query.offset,
                location=query.location,
            )
            logger.debug("Received inline query")
        await handler(event, data)
        logger = logger.bind(
            process_result=True,
            spent_time_ms=round((time.time() - _started_processing_at) * 10000) / 10,
        )
        if event.callback_query:
            logger = logger.unbind("callback_data")
        if event.message:
            logger.info("Handled message")
        elif event.callback_query:
            logger.info("Handled callback query")
        elif event.inline_query:
            logger.info("Handled inline query")
        return
