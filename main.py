# main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# ✅ Importa routers (asegúrate de que existan en /routers)
from routers.router_usuario import router as usuarios_router
from routers.router_producto import router as productos_router
from routers.router_cliente import router as clientes_router
from routers.router_compra import router as compras_router
from routers.router_categoria import router as categorias_router  # 👈 sin 's'
from routers.router_historial import router as historial_router

# ✅ Inicialización de la app
app = FastAPI(
    title="Inventario / Ventas API",
    version="1.0.0",
    description="API asíncrona para gestión de usuarios, productos, clientes, compras, categorías e historial de eliminaciones.",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

# ✅ Middleware CORS (ajústalo según tu dominio)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # o ["https://tu-dominio.com"] para producción
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ Health endpoints
@app.get("/", tags=["Health"])
async def root():
    return {"status": "ok", "service": "inventario-ventas-api"}

@app.get("/health", tags=["Health"])
async def health():
    return {"ok": True}

# ✅ Montar todos los routers
app.include_router(usuarios_router)
app.include_router(productos_router)
app.include_router(clientes_router)
app.include_router(compras_router)
app.include_router(categorias_router)
app.include_router(historial_router)

# ✅ (Opcional) Crear tablas automáticamente al iniciar
# Descomenta este bloque solo si tu database.py expone `engine` y `Base`
"""
from database import engine, Base

@app.on_event("startup")
async def startup_event():
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        print("✔ Tablas creadas correctamente.")
    except Exception as e:
        print("⚠ Error al crear tablas:", e)
"""
