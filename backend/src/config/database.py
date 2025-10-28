import os
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase

DATA_DIR = os.getenv("DATA_DIR", "./local_data")

ABS_DATA_DIR = os.path.abspath(DATA_DIR)

DB_FILE_PATH = os.path.join(ABS_DATA_DIR, "todo.db")

DATABASE_URL = f"sqlite+aiosqlite:///{DB_FILE_PATH}"

os.makedirs(ABS_DATA_DIR, exist_ok=True)

# Setup sync engine
engine  = create_async_engine(DATABASE_URL, echo=True)

# this is the factory that will create new connections for each request
async_session_factory = async_sessionmaker(engine, expire_on_commit=False)

# this is the base clas our models will commit from
class Base(DeclarativeBase):
    pass

async def create_db_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_factory() as session:
        yield session