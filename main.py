
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from database import engine, Base

# Importación correcta de tus routers según tus archivos reales
from routers import (
    router_usuario,
    router_cliente,
    router_producto,
    router_categorias,
    router_compra,
)


# -------------------------------
# Ciclo de vida (startup)
# -------------------------------
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Crea automáticamente las tablas al iniciar
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield


# -------------------------------
# Aplicación principal
# -------------------------------
app = FastAPI(
    title="Mundiclass API",
    version="1.0.0",
    description="API asíncrona de Mundiclass (modelos + endpoints).",
    lifespan=lifespan,
)

# -------------------------------
# Configuración de CORS
# -------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],       # abierto (puedes restringirlo luego)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------------------------------
# Manejo simple de errores
# -------------------------------
@app.exception_handler(Exception)
async def unhandled_exception(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"detail": "Error interno del servidor"},
    )


# -------------------------------
# Registro de routers
# -------------------------------
app.include_router(router_usuario.router)
app.include_router(router_cliente.router)
app.include_router(router_producto.router)
app.include_router(router_categorias.router)
app.include_router(router_compra.router)


# -------------------------------
# Endpoints básicos
# -------------------------------
@app.get("/", tags=["Meta"])
async def root():
    return {
        "app": "Mundiclass API",
        "version": app.version,
        "docs": "/docs",
        "openapi": "/openapi.json",
        "health": "/health"
    }


@app.get("/health", tags=["Meta"])
async def health():
    return {"status": "ok"}

