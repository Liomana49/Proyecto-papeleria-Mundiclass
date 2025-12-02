from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from contextlib import asynccontextmanager

# ✅ Importa routers (asegúrate de que existan en /routers)
from routers.router_usuario import router as usuarios_router
from routers.router_producto import router as productos_router
from routers.router_cliente import router as clientes_router
from routers.router_compra import router as compras_router
from routers.router_categoria import router as categorias_router
from routers.router_historial import router as historial_router

from database import engine, Base

templates = Jinja2Templates(directory="templates")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Crear tablas si no existen
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        print("✔ Tablas creadas correctamente.")
    except Exception as e:
        print("⚠ Error al crear tablas:", e)
    yield
    # Shutdown: Nada por ahora


app = FastAPI(
    title="Inventario / Ventas API",
    version="1.0.0",
    description="API asíncrona para gestión de usuarios, productos, clientes, compras, categorías e historial de eliminaciones.",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Montar archivos estáticos
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/", tags=["Home"])
async def root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/health", tags=["Health"])
async def health():
    return {"ok": True}


app.include_router(usuarios_router)
app.include_router(productos_router)
app.include_router(clientes_router)
app.include_router(compras_router)
app.include_router(categorias_router)
app.include_router(historial_router)


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
