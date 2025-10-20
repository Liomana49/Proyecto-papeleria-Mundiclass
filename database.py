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
    Normaliza la URL para SQLAlchemy + asyncpg:
    - postgres://  -> postgresql://
    - postgresql(s):// -> postgresql+asyncpg://
    - elimina sslmode=... (asyncpg no lo acepta)
    - añade ssl=true (Render requiere SSL)
    """
    if not url:
        raise ValueError("La variable de entorno DATABASE_URL no está definida")

    # 1) normaliza esquema base
    if url.startswith("postgres://"):
        url = url.replace("postgres://", "postgresql://", 1)

    p = urlparse(url)

    # 2) normaliza a driver asyncpg SIEMPRE
    scheme = "postgresql+asyncpg"

    # 3) limpia query params y fuerza ssl para asyncpg
    q = dict(parse_qsl(p.query))
    # eliminar cualquier 'sslmode' que venga de Render/psycopg
    q.pop("sslmode", None)
    # si ya hubiera 'ssl', lo respetamos; si no, lo activamos
    q.setdefault("ssl", "true")

    new = p._replace(scheme=scheme, query=urlencode(q))
    return urlunparse(new)

# --- construir URL final ---
DATABASE_URL = os.getenv("DATABASE_URL", "")
ASYNC_DATABASE_URL = to_asyncpg_url(DATABASE_URL)

# --- engine/Session/Base ---
engine = create_async_engine(
    ASYNC_DATABASE_URL,
    echo=False,
    pool_pre_ping=True,
    poolclass=NullPool,
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

# Alias para routers
get_db = get_async_db
