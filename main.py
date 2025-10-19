# main.py
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

# ⬇️ Ajusta estos imports a tu estructura real de proyecto
from database import engine, Base  # engine = create_async_engine(...), Base = Declarative Base
from routers import usuarios, clientes, productos, categorias, compras


# -------------------------------
# Lifespan (startup / shutdown)
# -------------------------------
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Crear tablas al arrancar (opcional pero útil en dev)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    # Aquí podrías cerrar conexiones externas si aplica


app = FastAPI(
    title="Mundiclass API",
    version="1.0.0",
    description="API de Mundiclass (modelos + endpoints).",
    lifespan=lifespan,
)

# -------------------------------
# CORS
# -------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],          # ajusta dominios en prod
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------------------------------
# Manejo global de errores
# -------------------------------
@app.exception_handler(Exception)
async def unhandled_exc(request: Request, exc: Exception):
    # Evita trazas crudas al cliente
    return JSONResponse(
        status_code=500,
        content={"detail": "Error interno del servidor"},
    )

# -------------------------------
# Routers
# -------------------------------
app.include_router(usuarios.router)
app.include_router(clientes.router)
app.include_router(productos.router)
app.include_router(categorias.router)
app.include_router(compras.router)

# -------------------------------
# Healthcheck / raíz
# -------------------------------
@app.get("/", tags=["Meta"])
async def root():
    return {
        "name": "Mundiclass API",
        "version": app.version,
        "docs": "/docs",
        "openapi": "/openapi.json",
        "health": "/health"
    }

@app.get("/health", tags=["Meta"])
async def health():
    return {"status": "ok"}

# -------------------------------
# Ejecución local
# -------------------------------
# Ejecuta:  uvicorn main:app --reload
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
