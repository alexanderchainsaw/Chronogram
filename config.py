import os
from dotenv import load_dotenv
from dataclasses import dataclass
from structlog import get_logger
from structlog.types import FilteringBoundLogger
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from aiogram import Bot
from cryptography.fernet import Fernet

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
    LOGGER: FilteringBoundLogger = get_logger()
    BOT = Bot(token=TEST_API_TOKEN if TESTING else PROD_API_TOKEN,
              default=DefaultBotProperties(parse_mode=ParseMode.HTML))


config = Config()
