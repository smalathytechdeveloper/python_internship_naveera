

import os
from dotenv import load_dotenv
from fastapi import Request

from sqlalchemy.ext.asyncio import create_async_engine,async_sessionmaker


from config import settings

engine = create_async_engine(
    settings.database_url,
    echo=True,
    pool_size=1,
    max_overflow=0,
    pool_timeout=2,
    pool_pre_ping=True,
)
SessionLocal = async_sessionmaker(engine, expire_on_commit=True) 

async def get_session():
    async with SessionLocal() as session:
        yield session
