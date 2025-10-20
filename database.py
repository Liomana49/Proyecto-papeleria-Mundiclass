# database.py
from __future__ import annotations
import os
from urllib.parse import urlparse, urlunparse
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from sqlalchemy.pool import NullPool

# URL externa de Render en env: DATABASE_URL=postgresql://user:pass@...render.com/dbname
RAW_URL = os.getenv("DATABASE_URL", "")
if not RAW_URL:
    raise ValueError("DATABASE_URL no está definida")

# Normaliza a asyncpg y elimina cualquier query (?sslmode=...)
def normalize(url: str) -> str:
    if url.startswith("postgres://"):
        url = url.replace("postgres://", "postgresql://", 1)
    p = urlparse(url)
    p = p._replace(scheme="postgresql+asyncpg", params="", query="", fragment="")
    return urlunparse(p)

ASYNC_URL = normalize(RAW_URL)

# Render requiere SSL, pero sin sslmode; asyncpg usa 'ssl=True' en connect_args
engine = create_async_engine(
    ASYNC_URL,
    echo=False,
    pool_pre_ping=True,
    poolclass=NullPool,
    connect_args={"ssl": True},   # ← sin sslmode, solo ssl=True
)

AsyncSessionLocal = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)
Base = declarative_base()

async def get_async_db() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        yield session

# alias para routers
get_db = get_async_db

