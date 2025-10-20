# main.py
from fastapi import FastAPI
from database import engine, Base
from routers import (
    router_usuario,
    router_cliente,
    router_producto,
    router_categoria,
    router_compra,
    router_historial,
)

app = FastAPI(
    title="Mundiclass API",
    description="API de gestión comercial y de inventario de Mundiclass",
    version="1.0.0"
)

# ------------------------
# INCLUSIÓN DE ROUTERS
# ------------------------
app.include_router(router_usuario.router)
app.include_router(router_cliente.router)
app.include_router(router_producto.router)
app.include_router(router_categoria.router)
app.include_router(router_compra.router)
app.include_router(router_historial.router)

# ------------------------
# CREAR TABLAS AUTOMÁTICAMENTE EN INICIO
# ------------------------
@app.on_event("startup")
async def startup_event():
    async with engine.begin() as conn:
        # Crea las tablas si no existen
        await conn.run_sync(Base.metadata.create_all)

# ------------------------
# ENDPOINT RAÍZ
# ------------------------
@app.get("/")
async def root():
    return {"mensaje": "🚀 API de Mundiclass funcionando correctamente"}
