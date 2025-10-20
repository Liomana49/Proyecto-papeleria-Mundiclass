from fastapi import FastAPI
from database import engine, Base
from routers import (
    router_usuario,
    router_cliente,
    router_producto,
    router_categorias,
    router_compra,
    router_historial,   # 👈 agregar
)

app = FastAPI(title="Mundiclass API", version="1.0.0")

app.include_router(router_usuario.router)
app.include_router(router_cliente.router)
app.include_router(router_producto.router)
app.include_router(router_categorias.router)
app.include_router(router_compra.router)
app.include_router(router_historial.router)  # 👈 agregar

@app.on_event("startup")
async def startup_event():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

@app.get("/")
async def root():
    return {"mensaje": "🚀 API de Mundiclass funcionando correctamente"}
