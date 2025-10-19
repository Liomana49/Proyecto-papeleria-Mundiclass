# database.py
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import declarative_base
from sqlalchemy.pool import NullPool

# Configura tu cadena de conexión
# Ejemplo para PostgreSQL en Render / local:
# postgresql+asyncpg://usuario:contraseña@host:puerto/base_datos
DATABASE_URL = "postgresql+asyncpg://postgres:1234@localhost:5432/mundiclass_db"

# Crear motor asíncrono
engine = create_async_engine(
    DATABASE_URL,
    echo=False,          # cambia a True si quieres ver las consultas SQL en consola
    poolclass=NullPool   # opcional si estás en Render o conexiones cortas
)

# Crear fábrica de sesiones asíncronas
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

# Base declarativa para tus modelos
Base = declarative_base()

# Dependencia de sesión (para usar en los routers)
async def get_db() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        yield session
