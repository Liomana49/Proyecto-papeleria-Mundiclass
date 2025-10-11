# database.py
from __future__ import annotations
import os
from dotenv import load_dotenv

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import declarative_base

load_dotenv()

# 1) Toma la URL de la BD de .env
DATABASE_URL = os.getenv("DATABASE_URL")

# 2) Si no hay URL, usa SQLite local (útil en desarrollo)
if not DATABASE_URL:
    # sqlite sync -> la convertimos a async más abajo
    DATABASE_URL = "sqlite+aiosqlite:///./app.db"

# 3) Convertir a URL asíncrona si viene como postgresql://
#    (Render/Heroku suelen dar "postgresql://...")
if DATABASE_URL.startswith("postgresql://"):
    DATABASE_URL_ASYNC = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://")
else:
    # si ya es async (postgresql+asyncpg://) o es sqlite+aiosqlite, la dejamos igual
    DATABASE_URL_ASYNC = DATABASE_URL

# 4) Engine asíncrono
async_engine = create_async_engine(
    DATABASE_URL_ASYNC,
    echo=False,  # pon True para ver SQL en consola
    pool_pre_ping=True,
)

# 5) Session factory asíncrona
AsyncSessionLocal = async_sessionmaker(
    bind=async_engine,
    expire_on_commit=False,
    autoflush=False,
    class_=AsyncSession,
)

# 6) Base de modelos
Base = declarative_base()

# 7) Dependencia para FastAPI (inyecta sesión por request)
async def get_async_db() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        yield session

# 8) Crear tablas en startup (modo asíncrono)
async def init_models():
    """
    Llama esto en el startup de FastAPI para crear tablas con los modelos importados.
    """
    async with async_engine.begin() as conn:
        # conn.run_sync ejecuta código "sync" sobre el engine async
        from models import Categoria  # importa tus modelos
        from producto import Producto
        from cliente import Cliente
        from compra import Compra
        from usuario import Usuario

        await conn.run_sync(Base.metadata.create_all)

