from __future__ import annotations
import os
from urllib.parse import urlparse, urlunparse
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from sqlalchemy.pool import NullPool
from dotenv import load_dotenv

load_dotenv()

def normalize_asyncpg_url(url: str) -> str:
    if not url:
        raise ValueError("DATABASE_URL no está definida")

    if url.startswith("postgres://"):
        url = url.replace("postgres://", "postgresql://", 1)

    p = urlparse(url)
    p_clean = p._replace(scheme="postgresql+asyncpg", params="", query="", fragment="")
    return urlunparse(p_clean)

RAW_URL = os.getenv("DATABASE_URL", "")
ASYNC_URL = normalize_asyncpg_url(RAW_URL)

engine = create_async_engine(
    ASYNC_URL,
    echo=False,
    pool_pre_ping=True,
    poolclass=NullPool,
    connect_args={"ssl": True},
)

AsyncSessionLocal = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)
Base = declarative_base()

async def get_async_db() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        yield session

get_db = get_async_db

