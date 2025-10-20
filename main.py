# main.py
from fastapi import FastAPI
from sqlalchemy import text
from database import engine, Base
from routers import (
    router_usuario,
    router_cliente,
    router_producto,
    router_categorias,   # <- plural
    router_compra,
    router_historial,    # quita esta línea si no tienes este router
)

app = FastAPI(
    title="Mundiclass API",
    description="API de gestión comercial y de inventario para Mundiclass",
    version="1.0.0",
)

# ------------------------
# Routers
# ------------------------
app.include_router(router_usuario.router)
app.include_router(router_cliente.router)
app.include_router(router_producto.router)
app.include_router(router_categorias.router)
app.include_router(router_compra.router)
app.include_router(router_historial.router)  # quita esta línea si no tienes este router


# ------------------------
# Parches de BD en startup (sin consola SQL)
# ------------------------
async def run_db_patches(conn):
    statements = [
        # --- columnas que podrían faltar por cambios de modelo ---
        "ALTER TABLE productos ADD COLUMN IF NOT EXISTS descripcion VARCHAR(250)",

        # --- asegurar DEFAULT NOW() y rellenar nulos en creado_en ---
        "ALTER TABLE categorias            ALTER COLUMN creado_en SET DEFAULT NOW()",
        "UPDATE categorias            SET creado_en = NOW() WHERE creado_en IS NULL",

        "ALTER TABLE productos             ALTER COLUMN creado_en SET DEFAULT NOW()",
        "UPDATE productos             SET creado_en = NOW() WHERE creado_en IS NULL",

        "ALTER TABLE usuarios              ALTER COLUMN creado_en SET DEFAULT NOW()",
        "UPDATE usuarios              SET creado_en = NOW() WHERE creado_en IS NULL",

        "ALTER TABLE clientes              ALTER COLUMN creado_en SET DEFAULT NOW()",
        "UPDATE clientes              SET creado_en = NOW() WHERE creado_en IS NULL",

        "ALTER TABLE compras               ALTER COLUMN creado_en SET DEFAULT NOW()",
        "UPDATE compras               SET creado_en = NOW() WHERE creado_en IS NULL",

        "ALTER TABLE historial_eliminados  ALTER COLUMN creado_en SET DEFAULT NOW()",
        "UPDATE historial_eliminados  SET creado_en = NOW() WHERE creado_en IS NULL",
    ]

    for sql in statements:
        try:
            await conn.execute(text(sql))
        except Exception:
            # Si ya estaba aplicado o la columna no existe en esa tabla, lo ignoramos.
            pass


# ------------------------
# Startup: crear tablas + parches
# ------------------------
@app.on_event("startup")
async def startup_event():
    async with engine.begin() as conn:
        # 1) Crear tablas si no existen
        await conn.run_sync(Base.metadata.create_all)
        # 2) Aplicar parches (idempotentes)
        await run_db_patches(conn)


# ------------------------
# Endpoints básicos
# ------------------------
@app.get("/", tags=["meta"])
async def root():
    return {
        "app": "Mundiclass API",
        "version": app.version,
        "docs": "/docs",
        "openapi": "/openapi.json",
        "health": "/health",
    }


@app.get("/health", tags=["meta"])
async def health():
    return {"status": "ok"}
