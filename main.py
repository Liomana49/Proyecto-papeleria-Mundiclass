from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

# Routers de la API
from routers.router_usuario import router as usuarios_router
from routers.router_producto import router as productos_router
from routers.router_cliente import router as clientes_router
from routers.router_compra import router as compras_router
from routers.router_categoria import router as categorias_router
from routers.router_historial import router as historial_router

from database import engine, Base

# 📂 Configuración de plantillas
templates = Jinja2Templates(directory="templates")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: crear tablas si no existen
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        print("✔ Tablas creadas correctamente.")
    except Exception as e:
        print("⚠ Error al crear tablas:", e)
    yield
    # Shutdown: nada por ahora


app = FastAPI(
    title="Inventario / Ventas API",
    version="1.0.0",
    description="API asíncrona para gestión de usuarios, productos, clientes, compras, categorías e historial de eliminaciones.",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan,
)

# 🌐 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 📂 Archivos estáticos (CSS, JS, imágenes)
app.mount("/static", StaticFiles(directory="static"), name="static")


# ==========================
#   RUTAS BÁSICAS
# ==========================

@app.get("/", tags=["Home"])
async def root(request: Request):
    """Página de inicio."""
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/health", tags=["Health"])
async def health():
    """Endpoint simple para verificar que la API está viva."""
    return {"ok": True}


# ==========================
#   PÁGINAS HTML
# ==========================

# ---------- USUARIOS ----------

@app.get("/usuarios", tags=["Pages"])
async def usuarios_home(request: Request):
    """Vista principal de usuarios (lista)."""
    return templates.TemplateResponse("usuarios/read.html", {"request": request})


@app.get("/usuarios/read", tags=["Pages"])
async def usuarios_read_page(request: Request):
    return templates.TemplateResponse("usuarios/read.html", {"request": request})


@app.get("/usuarios/create", tags=["Pages"])
async def usuarios_create_page(request: Request):
    return templates.TemplateResponse("usuarios/create.html", {"request": request})


@app.get("/usuarios/update", tags=["Pages"])
async def usuarios_update_page(request: Request):
    return templates.TemplateResponse("usuarios/update.html", {"request": request})


# ---------- PRODUCTOS ----------

@app.get("/productos", tags=["Pages"])
async def productos_home(request: Request):
    """Vista principal de productos (lista)."""
    return templates.TemplateResponse("productos/read.html", {"request": request})


@app.get("/productos/read", tags=["Pages"])
async def productos_read_page(request: Request):
    return templates.TemplateResponse("productos/read.html", {"request": request})


@app.get("/productos/create", tags=["Pages"])
async def productos_create_page(request: Request):
    return templates.TemplateResponse("productos/create.html", {"request": request})


@app.get("/productos/update", tags=["Pages"])
async def productos_update_page(request: Request):
    return templates.TemplateResponse("productos/update.html", {"request": request})


@app.get("/productos/delete", tags=["Pages"])
async def productos_delete_page(request: Request):
    return templates.TemplateResponse("productos/delete.html", {"request": request})


# ---------- CLIENTES ----------

@app.get("/clientes", tags=["Pages"])
async def clientes_home(request: Request):
    """Vista principal de clientes (lista)."""
    return templates.TemplateResponse("clientes/read.html", {"request": request})


@app.get("/clientes/read", tags=["Pages"])
async def clientes_read_page(request: Request):
    return templates.TemplateResponse("clientes/read.html", {"request": request})


@app.get("/clientes/create", tags=["Pages"])
async def clientes_create_page(request: Request):
    return templates.TemplateResponse("clientes/create.html", {"request": request})


@app.get("/clientes/update", tags=["Pages"])
async def clientes_update_page(request: Request):
    return templates.TemplateResponse("clientes/update.html", {"request": request})


@app.get("/clientes/delete", tags=["Pages"])
async def clientes_delete_page(request: Request):
    return templates.TemplateResponse("clientes/delete.html", {"request": request})


# ---------- VENTAS ----------

@app.get("/ventas", tags=["Pages"])
async def ventas_home(request: Request):
    """Vista principal de ventas (lista)."""
    return templates.TemplateResponse("ventas/read.html", {"request": request})


@app.get("/ventas/read", tags=["Pages"])
async def ventas_read_page(request: Request):
    return templates.TemplateResponse("ventas/read.html", {"request": request})


@app.get("/ventas/create", tags=["Pages"])
async def ventas_create_page(request: Request):
    return templates.TemplateResponse("ventas/create.html", {"request": request})


@app.get("/ventas/update", tags=["Pages"])
async def ventas_update_page(request: Request):
    return templates.TemplateResponse("ventas/update.html", {"request": request})


@app.get("/ventas/delete", tags=["Pages"])
async def ventas_delete_page(request: Request):
    return templates.TemplateResponse("ventas/delete.html", {"request": request})


# ---------- CATEGORÍAS ----------

@app.get("/categorias", tags=["Pages"])
async def categorias_home(request: Request):
    """Vista principal de categorías (lista)."""
    return templates.TemplateResponse("categorias/read.html", {"request": request})


@app.get("/categorias/read", tags=["Pages"])
async def categorias_read_page(request: Request):
    return templates.TemplateResponse("categorias/read.html", {"request": request})


@app.get("/categorias/create", tags=["Pages"])
async def categorias_create_page(request: Request):
    return templates.TemplateResponse("categorias/create.html", {"request": request})


@app.get("/categorias/update", tags=["Pages"])
async def categorias_update_page(request: Request):
    return templates.TemplateResponse("categorias/update.html", {"request": request})


@app.get("/categorias/delete", tags=["Pages"])
async def categorias_delete_page(request: Request):
    return templates.TemplateResponse("categorias/delete.html", {"request": request})


# ---------- HISTORIAL, PLANIFICACIÓN, INFO PROYECTO ----------

@app.get("/historial", tags=["Pages"])
async def historial_page(request: Request):
    return templates.TemplateResponse("historial.html", {"request": request})


@app.get("/planning", tags=["Pages"])
async def planning_page(request: Request):
    return templates.TemplateResponse("planning.html", {"request": request})


@app.get("/informacion-del-proyecto", tags=["Pages"])
async def informacion_del_proyecto_page(request: Request):
    return templates.TemplateResponse("informacion_del_proyecto.html", {"request": request})


# ==========================
#   ROUTERS DE LA API
# ==========================

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
