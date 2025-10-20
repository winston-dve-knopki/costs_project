import asyncio
from src.database.database import engine, Base
from src.database import models

async def create_db_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
        print("Таблицы успешно созданы.")

if __name__ == "__main__":
    asyncio.run(create_db_tables())
