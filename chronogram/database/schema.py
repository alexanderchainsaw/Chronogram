import datetime
from sqlalchemy import ForeignKey
from sqlalchemy.dialects.postgresql import (BYTEA, BIGINT, INTEGER, TIMESTAMP, BOOLEAN, CHAR,
                                            VARCHAR)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from config import config

engine = create_async_engine(f'postgresql+asyncpg://'
                             f'{config.PG_LOGIN}:{config.PG_PASS}@'
                             f'{config.PG_HOST}:{config.PG_PORT}/{config.PG_DB_NAME}')

async_session = async_sessionmaker(engine)


DEFAULT_USER_SPACE = 100000
PREMIUM_USER_SPACE = 10000000


class Base(DeclarativeBase):
    pass


class ChronogramUser(Base):
    __tablename__ = 'users'

    id: Mapped[INTEGER] = mapped_column(INTEGER, primary_key=True)
    tg_uid: Mapped[BIGINT] = mapped_column(BIGINT) 
    joined: Mapped[TIMESTAMP] = mapped_column(TIMESTAMP, default=datetime.datetime.utcnow().replace(microsecond=0))
    utc_offset_minutes: Mapped[INTEGER] = mapped_column(INTEGER)
    language: Mapped[CHAR] = mapped_column(CHAR(length=2))
    subscription: Mapped[BOOLEAN] = mapped_column(BOOLEAN, default=False)
    subscription_deadline: Mapped[TIMESTAMP] = mapped_column(TIMESTAMP, default=None, nullable=True)
    notified_deadline: Mapped[BOOLEAN] = mapped_column(BOOLEAN, default=False)
    space_available: Mapped[INTEGER] = mapped_column(INTEGER, default=100000)
    space_taken: Mapped[INTEGER] = mapped_column(INTEGER, default=0)

    def __repr__(self):
        values = ', '.join(f"{key}={self.__dict__[key]}" for key in self.__dict__.keys())
        return f"ChronogramUser({values})"


class ChronogramPayment(Base):
    __tablename__ = 'payments'

    id: Mapped[INTEGER] = mapped_column(INTEGER, primary_key=True)
    timestamp: Mapped[TIMESTAMP] = mapped_column(TIMESTAMP)
    user_id: Mapped[INTEGER] = mapped_column(ForeignKey("users.id"))
    invoice_id: Mapped[VARCHAR] = mapped_column(VARCHAR(length=100))
    tg_transaction_id: Mapped[VARCHAR] = mapped_column(VARCHAR(length=200))
    xtr_amount: Mapped[INTEGER] = mapped_column(INTEGER)
    type: Mapped[VARCHAR] = mapped_column(VARCHAR(12))
    status: Mapped[VARCHAR] = mapped_column(VARCHAR(12))

    def __repr__(self):
        values = ', '.join(f"{key}={self.__dict__[key]}" for key in self.__dict__.keys())
        return f"ChronogramPayment({values})"


class TimeCapsule(Base):
    __tablename__ = 'timecapsules'

    id: Mapped[INTEGER] = mapped_column(INTEGER, primary_key=True)
    user_id: Mapped[INTEGER] = mapped_column(ForeignKey("users.id", ondelete='CASCADE'))
    send_timestamp: Mapped[TIMESTAMP] = mapped_column(TIMESTAMP)
    receive_timestamp: Mapped[TIMESTAMP] = mapped_column(TIMESTAMP)
    text_content: Mapped[VARCHAR] = mapped_column(BYTEA, default=None, nullable=True)
    image: Mapped[BYTEA] = mapped_column(BYTEA, default=None, nullable=True)
    # image_data format = f"{mode}_{x}-{y}"
    image_data: Mapped[VARCHAR] = mapped_column(VARCHAR(20), default=None, nullable=True)
    size: Mapped[INTEGER] = mapped_column(INTEGER)
    received: Mapped[BOOLEAN] = mapped_column(BOOLEAN, default=False)

    def __repr__(self):
        values = ', '.join(f"{key}={bool(self.__dict__[key])}"
                           if key in ('text_content', 'image') else f"{key}={self.__dict__[key]}"
                           for key in self.__dict__.keys() if key != 'image_data')
        return f"TimeCapsule({values})"


async def tc_image_data(data: str) -> dict:
    mode, size = data.split('_')
    x, y = size.split('-')
    res = dict()
    res['size'] = (int(x), int(y))
    res['mode'] = mode
    return res


async def async_main():
    async with engine.begin() as con:
        await con.run_sync(Base.metadata.create_all)
