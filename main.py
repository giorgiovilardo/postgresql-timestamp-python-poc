import asyncio
from datetime import datetime
from multiprocessing import Process
from uuid import UUID, uuid4

from sqlalchemy import TIMESTAMP
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
import uvicorn
import blacksheep
from fastapi import FastAPI
from blacksheep.server.application import Application
import pydantic


class Model(DeclarativeBase):
    pass


class TimestampedModel(DeclarativeBase):
    type_annotation_map = {datetime: TIMESTAMP(timezone=True)}


class AutotzTimer(TimestampedModel):
    """
    Generated sql:

    CREATE TABLE autotz_timer (
      id UUID NOT NULL,
      should_have_tz TIMESTAMP WITH TIME ZONE NOT NULL,
      overridden TIMESTAMP WITHOUT TIME ZONE NOT NULL,
      PRIMARY KEY (id)
    )
    """

    __tablename__ = "autotz_timer"
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    should_have_tz: Mapped[datetime]
    overridden: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=False))


class TimerDTO(pydantic.BaseModel):
    tz: datetime
    no_tz: datetime


class Timer(pydantic.BaseModel):
    id: UUID
    with_tz: datetime
    without_tz: datetime

    @classmethod
    def from_db(cls, obj):
        return cls(id=obj.id, with_tz=obj.dt_with_tz, without_tz=obj.dt_without_tz)


class TimerModel(Model):
    __tablename__ = "timer"
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    dt_with_tz: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True))
    dt_without_tz: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=False))

    def __repr__(self) -> str:
        return f"{self.id} - {self.dt_with_tz} - {self.dt_without_tz}"


engine = create_async_engine(
    "postgresql+asyncpg://postgres:password@127.0.0.1:5432/postgres", echo=True
)
AsyncSessionLocal = async_sessionmaker(
    bind=engine, class_=AsyncSession, expire_on_commit=False
)


async def initialize_database():
    async with engine.begin() as conn:
        await conn.run_sync(Model.metadata.drop_all)
        await conn.run_sync(TimestampedModel.metadata.drop_all)
        await conn.run_sync(Model.metadata.create_all)
        await conn.run_sync(TimestampedModel.metadata.create_all)


async def main():
    await initialize_database()


def run_fastapi():
    uvicorn.run("main:fa", host="127.0.0.1", port=8000, log_level="info")


def run_blacksheep():
    uvicorn.run("main:bs", host="127.0.0.1", port=8001, log_level="info")


fa = FastAPI()


@fa.post("/")
async def fa_handler(timer: TimerDTO):
    async with AsyncSessionLocal() as session:
        timermodel = TimerModel(dt_with_tz=timer.tz, dt_without_tz=timer.no_tz)
        session.add(timermodel)
        await session.commit()
    return {"fw": "fa"} | Timer.from_db(timermodel).model_dump()


bs = Application()


@blacksheep.post("/")
async def bs_handler(timer: TimerDTO):
    async with AsyncSessionLocal() as session:
        timermodel = TimerModel(dt_with_tz=timer.tz, dt_without_tz=timer.no_tz)
        session.add(timermodel)
        await session.commit()
    return {"fw": "bs"} | Timer.from_db(timermodel).model_dump()


if __name__ == "__main__":
    asyncio.run(main())
    p1 = Process(target=run_fastapi)
    p2 = Process(target=run_blacksheep)
    p1.start()
    p2.start()
    p1.join()
    p2.join()
