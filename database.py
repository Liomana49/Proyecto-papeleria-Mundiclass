# database.py (async, Render-ready)
import os
from urllib.parse import urlparse, urlunparse, parse_qsl, urlencode
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import declarative_base
from sqlalchemy.pool import NullPool

Base = declarative_base()

def to_asyncpg_url(url: str) -> str:
    """
    Convierte postgres://... a postgresql+asyncpg://... y fuerza sslmode=require
    """
    if not url:
        raise RuntimeError("DATABASE_URL no está definido")

    # 1) esquema
    if url.startswith("postgres://"):
        url = url.replace("postgres://", "postgresql://", 1)

    # 2) parsear y reconstruir con driver async
    parsed = urlparse(url)
    scheme = "postgresql+asyncpg"

    # 3) asegurar sslmode=require
    query = dict(parse_qsl(parsed.query))
    if "sslmode" not in query:
        query["sslmode"] = "require"

    new = parsed._replace(scheme=scheme, query=urlencode(query))
    return urlunparse(new)

# Usa primero la variable de entorno de Render
RAW_DB_URL = os.getenv("DATABASE_URL") or os.getenv("POSTGRES_URL")  # Render suele exponer DATABASE_URL
ASYNC_DB_URL = to_asyncpg_url(RAW_DB_URL)

engine = create_async_engine(
    ASYNC_DB_URL,
    echo=False,
    pool_pre_ping=True,
    poolclass=NullPool,  # en Render suele ir mejor
)

AsyncSessionLocal = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)

async def get_db() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        yield session

