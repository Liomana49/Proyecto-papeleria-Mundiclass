# database.py
from __future__ import annotations
import os
from dotenv import load_dotenv

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import declarative_base

load_dotenv()

# 1) Lee la URL del entorno (Render la inyecta como DATABASE_URL)
DATABASE_URL = os.getenv("DATABASE_URL")

# 2) Si no hay URL (local), usa SQLite async
if not DATABASE_URL:
    DATABASE_URL = "sqlite+aiosqlite:///./app.db"

# 3) Convierte a async si viene como 'postgresql://'
if DATABASE_URL.startswith("postgresql://"):
    DATABASE_URL_ASYNC = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://")
else:
    DATABASE_URL_ASYNC = DATABASE_URL  # ya sería async o sqlite+aiosqlite

# 4) Engine y Session asíncronos
async_engine = create_async_engine(
    DATABASE_URL_ASYNC,
    echo=False,
    pool_pre_ping=True,
)

AsyncSessionLocal = async_sessionmaker(
    bind=async_engine,
    expire_on_commit=False,
    autoflush=False,
    class_=AsyncSession,
)

# 5) Base de modelos
Base = declarative_base()

# 6) Dependency para FastAPI
async def get_async_db() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        yield session

# 7) Crear tablas al inicio (se importa modelos DENTRO para evitar ciclos)
async def init_models():
    async with async_engine.begin() as conn:
        # IMPORTA TUS MODELOS AQUÍ (import dentro de la función)
        from models import Categoria
        from producto import Producto
        from cliente import Cliente
        from compra import Compra
        from usuario import Usuario

        await conn.run_sync(Base.metadata.create_all)
