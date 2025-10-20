# database.py
from __future__ import annotations
import os
from urllib.parse import urlparse, urlunparse, parse_qsl, urlencode
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from sqlalchemy.pool import NullPool

load_dotenv()


def _to_asyncpg_url(url: str) -> str:
    """
    Convierte postgres:// o postgresql:// a postgresql+asyncpg://
    y agrega sslmode=require si no está (necesario en Render).
    """
    if not url:
        raise ValueError("La variable de entorno DATABASE_URL no está definida")

    if url.startswith("postgres://"):
        url = url.replace("postgres://", "postgresql://", 1)

    parsed = urlparse(url)
    scheme = "postgresql+asyncpg"
    query = dict(parse_qsl(parsed.query))
    query.setdefault("sslmode", "require")

    new = parsed._replace(scheme=scheme, query=urlencode(query))
    return urlunparse(new)


# --- Configuración del motor y sesión ---
DATABASE_URL = os.getenv("DATABASE_URL")
ASYNC_DATABASE_URL = _to_asyncpg_url(DATABASE_URL)

engine = create_async_engine(
    ASYNC_DATABASE_URL,
    echo=False,
    pool_pre_ping=True,
    poolclass=NullPool,
)

AsyncSessionLocal = async_sessionmaker(
    bind=engine, class_=AsyncSession, expire_on_commit=False
)

Base = declarative_base()


# --- Dependencias para los routers ---
async def get_async_db() -> AsyncSession:
    """Sesión asíncrona para usar con FastAPI"""
    async with AsyncSessionLocal() as session:
        yield session


# 🔹 Alias para compatibilidad con los routers que usan get_db
get_db = get_async_db
