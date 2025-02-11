import os
from dotenv import load_dotenv
from dataclasses import dataclass
from structlog import get_logger
from structlog.types import FilteringBoundLogger
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from aiogram import Bot
from cryptography.fernet import Fernet
from redis import asyncio as aioredis

load_dotenv()


@dataclass
class Config:
    TESTING: int = int(os.getenv('TESTING'))
    PROD_API_TOKEN: str = os.getenv('PROD_API_TOKEN')
    TEST_API_TOKEN: str = os.getenv('TEST_API_TOKEN')
    FERNET: Fernet = Fernet(key=os.getenv('FERNET_KEY'))
    ADMIN_IDS: tuple = tuple(os.getenv('ADMIN_IDS').split())
    PG_LOGIN: str = os.getenv('PG_LOGIN')
    PG_PASS: str = os.getenv('PG_PASS')
    PG_DB_NAME: str = os.getenv('PG_DB_NAME')
    PG_HOST: str = os.getenv('PG_HOST')
    PG_PORT: str = os.getenv('PG_PORT')
    AIOREDIS = aioredis.Redis(host=os.getenv('REDIS_HOST'), port=int(os.getenv('REDIS_PORT')), db=0,
                              username=os.getenv('REDIS_USER'), password=os.getenv('REDIS_USER_PASSWORD'),
                              decode_responses=True)
    LOGGER: FilteringBoundLogger = get_logger()
    BOT = Bot(token=TEST_API_TOKEN if TESTING else PROD_API_TOKEN,
              default=DefaultBotProperties(parse_mode=ParseMode.HTML))

    # CONSTANTS
    SUBSCRIPTION_COST: int = 150  # 150 telegram stars a month
    DEFAULT_USER_SPACE: int = 100_000  # 0.1 megabytes
    PREMIUM_USER_SPACE: int = 10_000_000  # 10 megabytes
    PAGE_LENGTH: int = 4  # amount of items in each page in /inbox

    def __post_init__(self):
        for key, val in self.__dict__.items():
            if val is None:
                raise RuntimeError(f"Value {key} is empty")
        if self.PROD_API_TOKEN == self.TEST_API_TOKEN:
            raise RuntimeError("Same token for TEST and for PROD")


config = Config()
