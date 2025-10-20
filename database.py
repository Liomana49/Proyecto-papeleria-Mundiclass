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
    y ajusta los parámetros SSL para Render (usa ssl=true).
    """
    if not url:
        raise ValueError("La variable de entorno DATABASE_URL no está definida")

    # Normaliza prefijo
    if url.startswith("postgres://"):
        url = url.replace("postgres://", "postgresql://", 1)

    p = urlparse(url)
    scheme = "postgresql+asyncpg"

    # Limpia y ajusta parámetros
    q = dict(parse_qsl(p.query))
    q.pop("sslmode", None)   # asyncpg no acepta sslmode
    q["ssl"] = "true"        # Render requiere SSL

    new = p._replace(scheme=scheme, query=urlencode(q))
    return urlunparse(new)

# Carga la URL del entorno
DATABASE_URL = os.getenv("DATABASE_URL", "")
ASYNC_DATABASE_URL = to_asyncpg_url(DATABASE_URL)

# Crea el motor asíncrono
engine = create_async_engine(
    ASYNC_DATABASE_URL,
    echo=False,
    pool_pre_ping=True,
    poolclass=NullPool,
)

# Crea sesión asíncrona
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)

# Base declarativa para los modelos
Base = declarative_base()

# Dependencia para los routers
async def get_async_db() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        yield session

# Alias para compatibilidad con los routers existentes
get_db = get_async_db
