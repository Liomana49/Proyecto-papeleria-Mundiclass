# main.py
from fastapi import FastAPI
from database import engine, Base
from routers import (
    router_usuario,
    router_cliente,
    router_producto,
    router_categorias,   # ✅ plural (nombre correcto del archivo)
    router_compra,
    router_historial,    # si tienes el historial de eliminados
)

app = FastAPI(
    title="Mundiclass API",
    description="API de gestión comercial y de inventario para Mundiclass",
    version="1.0.0"
)

# ------------------------
# INCLUSIÓN DE ROUTERS
# ------------------------
app.include_router(router_usuario.router)
app.include_router(router_cliente.router)
app.include_router(router_producto.router)
app.include_router(router_categorias.router)   # ✅ plural
app.include_router(router_compra.router)
app.include_router(router_historial.router)    # ✅ si existe el router_historial

# ------------------------
# CREACIÓN AUTOMÁTICA DE TABLAS AL INICIAR
# ------------------------
@app.on_event("startup")
async def startup_event():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

# ------------------------
# ENDPOINT PRINCIPAL
# ------------------------
@app.get("/")
async def root():
    return {"mensaje": "🚀 API de Mundiclass funcionando correctamente"}

