# database.py
from __future__ import annotations
import os
from urllib.parse import urlparse, urlunparse
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from sqlalchemy.pool import NullPool
from dotenv import load_dotenv

load_dotenv()  # OJO: en Render solo se usa si subiste un .env. Si no, puedes quitarlo.

def normalize_asyncpg_url(url: str) -> str:
    if not url:
        raise ValueError("DATABASE_URL no está definida")

    url = url.strip()  # elimina espacios/saltos que rompen DNS

    # Normaliza esquema
    if url.startswith("postgres://"):
        url = url.replace("postgres://", "postgresql://", 1)

    p = urlparse(url)
    host = (p.hostname or "").strip()
    if not host:
        raise ValueError("DATABASE_URL no tiene host (revisa la variable en Render).")
    if " " in host or "\n" in host or "\t" in host:
        raise ValueError(f"El host de DATABASE_URL tiene espacios/saltos: '{host}'")
    # (Opcional) advertencia si no es la URL externa de Render
    if not host.endswith(".render.com"):
        print(f"⚠️ Aviso: host '{host}' no termina en .render.com (usa la URL EXTERNA).")

    # Forzar driver asyncpg y limpiar cualquier query/fragment
    p_clean = p._replace(scheme="postgresql+asyncpg", params="", query="", fragment="")
    return urlunparse(p_clean)

RAW_URL = os.getenv("DATABASE_URL", "")
ASYNC_URL = normalize_asyncpg_url(RAW_URL)

engine = create_async_engine(
    ASYNC_URL,
    echo=False,
    pool_pre_ping=True,
    poolclass=NullPool,      # recomendable en Render
    connect_args={"ssl": True},  # SSL para Render (sin sslmode)
)

AsyncSessionLocal = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)
Base = declarative_base()

async def get_async_db() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        yield session

# Alias usado por los routers
get_db = get_async_db
