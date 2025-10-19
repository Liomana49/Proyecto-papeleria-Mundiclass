# main.py

from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from database import engine, Base
from routers import usuarios, clientes, productos, categorias, compras


# -------------------------------
# Ciclo de vida de la app
# -------------------------------
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Crear tablas automáticamente al iniciar
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield


# -------------------------------
# Instancia principal
# -------------------------------
app = FastAPI(
    title="Mundiclass API",
    version="1.0.0",
    description="API asíncrona de Mundiclass con modelos y endpoints principales.",
    lifespan=lifespan,
)

# -------------------------------
# Configuración CORS (abierta)
# -------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------------------------------
# Manejo de errores global
# -------------------------------
@app.exception_handler(Exception)
async def unhandled_exception(request: Request, exc: Exception):
    return JSONResponse(status_code=500, content={"detail": "Error interno del servidor"})


# -------------------------------
# Registro de routers
# -------------------------------
app.include_router(usuarios.router)
app.include_router(clientes.router)
app.include_router(productos.router)
app.include_router(categorias.router)
app.include_router(compras.router)


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
