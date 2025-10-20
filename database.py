# database.py
from __future__ import annotations
import os
from urllib.parse import urlparse, urlunparse, parse_qsl, urlencode
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from sqlalchemy.pool import NullPool

load_dotenv()

def to_asyncpg_url(url: str) -> str:
    """
    Convierte postgres:// o postgresql:// a postgresql+asyncpg://
    - Cambia ?sslmode=require --> ?ssl=true (asyncpg no entiende sslmode)
    - En local (host=localhost/127.0.0.1) NO fuerza SSL.
    """
    if not url:
        raise ValueError("La variable de entorno DATABASE_URL no está definida")

    # Normaliza esquema base
    if url.startswith("postgres://"):
        url = url.replace("postgres://", "postgresql://", 1)

    p = urlparse(url)
    scheme = "postgresql+asyncpg"

    # Query params
    q = dict(parse_qsl(p.query))

    host = p.hostname or ""
    is_local = host in ("localhost", "127.0.0.1")

    # Elimina sslmode (propio de psycopg)
    q.pop("sslmode", None)

    # Para asyncpg usa 'ssl' (bool). En Render (no local) lo activamos.
    if not is_local:
        q["ssl"] = "true"   # asyncpg -> ssl=True
    else:
        q.pop("ssl", None)  # sin SSL en local

    new = p._replace(scheme=scheme, query=urlencode(q))
    return urlunparse(new)

DATABASE_URL = os.getenv("DATABASE_URL", "")
ASYNC_DATABASE_URL = to_asyncpg_url(DATABASE_URL)

engine = create_async_engine(
    ASYNC_DATABASE_URL,
    echo=False,
    pool_pre_ping=True,
    poolclass=NullPool,
)

AsyncSessionLocal = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)

Base = declarative_base()

async def get_async_db() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        yield session

# Alias para tus routers
get_db = get_async_db
