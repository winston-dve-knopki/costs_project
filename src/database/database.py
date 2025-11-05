from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase
from typing import AsyncGenerator
import os

DATABASE_URL = os.getenv(
    "DATABASE_URL", 
    "postgresql+asyncpg://cost_project_user:6796976@localhost/cost_project_db"
)

engine = create_async_engine(DATABASE_URL, echo=True)

async_session_maker = async_sessionmaker(engine, expire_on_commit=False)

async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Зависимость FastAPI для создания и управления сессией базы данных.
    """
    async with async_session_maker() as session:
        yield session

class Base(DeclarativeBase):
    pass

SYNC_DATABASE_URL = DATABASE_URL.replace("+asyncpg", "")
