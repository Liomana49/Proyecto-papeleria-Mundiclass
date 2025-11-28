# database.py
from __future__ import annotations
import os
from urllib.parse import urlparse, urlunparse

from sqlalchemy.ext.asyncio import (
    create_async_engine,
    AsyncSession,
    async_sessionmaker,
)
from sqlalchemy.orm import declarative_base
from sqlalchemy.pool import NullPool
from dotenv import load_dotenv

# En local carga .env; en Render no pasa nada si no existe
load_dotenv()


def normalize_asyncpg_url(url: str) -> str:
    if not url:
        raise ValueError("DATABASE_URL no está definida")

    # limpia espacios y comillas accidentales
    url = url.strip().strip('"').strip("'")

    # Normaliza esquema postgres -> postgresql
    if url.startswith("postgres://"):
        url = url.replace("postgres://", "postgresql://", 1)

    p = urlparse(url)
    host = (p.hostname or "").strip()

    if not host:
        raise ValueError(f"DATABASE_URL no tiene host válido: '{url}'")

    if " " in host or "\n" in host or "\t" in host:
        raise ValueError(f"El host de DATABASE_URL tiene espacios/saltos: '{host}'")

    # No validamos .render.com porque la URL interna NO lo lleva
    # Solo convertimos a asyncpg y limpiamos params/query/fragment
    p_clean = p._replace(
        scheme="postgresql+asyncpg",
        params="",
        query="",
        fragment="",
    )
    return urlunparse(p_clean)


RAW_URL = os.getenv("DATABASE_URL", "")

# 👇 si quieres ver qué está leyendo en Render, deja este print un rato
print(f"DATABASE_URL cruda: '{RAW_URL}'")

if not RAW_URL:
    # Fallback a SQLite para desarrollo local
    ASYNC_URL = "sqlite+aiosqlite:///./test.db"
else:
    ASYNC_URL = normalize_asyncpg_url(RAW_URL)

engine = create_async_engine(
    ASYNC_URL,
    echo=False,
    pool_pre_ping=True,
    poolclass=NullPool,
    # ❌ sin connect_args={"ssl": True}
)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

Base = declarative_base()


async def get_async_db() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        yield session


# Alias usado por los routers
get_db = get_async_db

