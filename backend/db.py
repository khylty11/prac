from sqlalchemy import select
from sqlalchemy.orm import Mapped, mapped_column, DeclarativeBase
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from schemas import UserMod


engine = create_async_engine("sqlite+aiosqlite:///Users.db")
Session = async_sessionmaker(engine)

class Base(DeclarativeBase):
    pass

class Users(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    password: Mapped[str]
    username: Mapped[str]


async def create_all():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

async def drop_all():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


async def get_user(data: UserMod):
    async with Session() as session:
        data_d = data.model_dump()
        query = select(Users).filter_by(**data_d)
        result = await session.execute(query)
        return result.scalars().one_or_none()


async def add_user(data: UserMod):
    async with Session() as session:
        data_d = data.model_dump()
        query = Users(**data_d)
        session.add(query)
        await session.commit()
        return True

