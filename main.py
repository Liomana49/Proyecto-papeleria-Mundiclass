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

# Rutas para páginas HTML
@app.get("/usuarios.html", tags=["Pages"])
async def usuarios_page(request: Request):
    return templates.TemplateResponse("usuarios.html", {"request": request})

@app.get("/productos.html", tags=["Pages"])
async def productos_page(request: Request):
    return templates.TemplateResponse("productos.html", {"request": request})

@app.get("/clientes.html", tags=["Pages"])
async def clientes_page(request: Request):
    return templates.TemplateResponse("clientes.html", {"request": request})

@app.get("/compras.html", tags=["Pages"])
async def compras_page(request: Request):
    return templates.TemplateResponse("compras.html", {"request": request})

@app.get("/categorias.html", tags=["Pages"])
async def categorias_page(request: Request):
    return templates.TemplateResponse("categorias.html", {"request": request})

@app.get("/categorias/create.html", tags=["Pages"])
async def categorias_create_page(request: Request):
    return templates.TemplateResponse("categorias/create.html", {"request": request})

@app.get("/categorias/read.html", tags=["Pages"])
async def categorias_read_page(request: Request):
    return templates.TemplateResponse("categorias/read.html", {"request": request})

@app.get("/categorias/update.html", tags=["Pages"])
async def categorias_update_page(request: Request):
    return templates.TemplateResponse("categorias/update.html", {"request": request})

@app.get("/categorias/delete.html", tags=["Pages"])
async def categorias_delete_page(request: Request):
    return templates.TemplateResponse("categorias/delete.html", {"request": request})

@app.get("/clientes/create.html", tags=["Pages"])
async def clientes_create_page(request: Request):
    return templates.TemplateResponse("clientes/create.html", {"request": request})

@app.get("/clientes/read.html", tags=["Pages"])
async def clientes_read_page(request: Request):
    return templates.TemplateResponse("clientes/read.html", {"request": request})

@app.get("/clientes/update.html", tags=["Pages"])
async def clientes_update_page(request: Request):
    return templates.TemplateResponse("clientes/update.html", {"request": request})

@app.get("/clientes/delete.html", tags=["Pages"])
async def clientes_delete_page(request: Request):
    return templates.TemplateResponse("clientes/delete.html", {"request": request})

@app.get("/productos/read.html", tags=["Pages"])
async def productos_read_page(request: Request):
    return templates.TemplateResponse("productos/read.html", {"request": request})

@app.get("/productos/update.html", tags=["Pages"])
async def productos_update_page(request: Request):
    return templates.TemplateResponse("productos/update.html", {"request": request})

@app.get("/productos/create.html", tags=["Pages"])
async def productos_create_page(request: Request):
    return templates.TemplateResponse("productos/create.html", {"request": request})

@app.get("/productos/delete.html", tags=["Pages"])
async def productos_delete_page(request: Request):
    return templates.TemplateResponse("productos/delete.html", {"request": request})

@app.get("/ventas/read.html", tags=["Pages"])
async def ventas_read_page(request: Request):
    return templates.TemplateResponse("ventas/read.html", {"request": request})

@app.get("/ventas/create.html", tags=["Pages"])
async def ventas_create_page(request: Request):
    return templates.TemplateResponse("ventas/create.html", {"request": request})

@app.get("/ventas/update.html", tags=["Pages"])
async def ventas_update_page(request: Request):
    return templates.TemplateResponse("ventas/update.html", {"request": request})

@app.get("/ventas/delete.html", tags=["Pages"])
async def ventas_delete_page(request: Request):
    return templates.TemplateResponse("ventas/delete.html", {"request": request})

@app.get("/informacion_del_proyecto.html", tags=["Pages"])
async def informacion_del_proyecto_page(request: Request):
    return templates.TemplateResponse("informacion_del_proyecto.html", {"request": request})

@app.get("/historial.html", tags=["Pages"])
async def historial_page(request: Request):
    return templates.TemplateResponse("historial.html", {"request": request})

@app.get("/planning.html", tags=["Pages"])
async def planning_page(request: Request):
    return templates.TemplateResponse("planning.html", {"request": request})

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
