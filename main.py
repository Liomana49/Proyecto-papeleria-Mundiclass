from fastapi import FastAPI
from contextlib import asynccontextmanager

# Importa la función que crea las tablas con SQLAlchemy async
from database import init_models

# Importa tus routers (si ya los tienes)
from router_categorias import router as categorias_router
from router_productos import router as productos_router
from router_clientes import router as clientes_router
from router_compras import router as compras_router
from router_usuarios import router as usuarios_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # 🔹 Este bloque se ejecuta al iniciar la aplicación
    await init_models()   # Crea las tablas automáticamente
    yield
    # 🔹 Aquí podrías cerrar conexiones si hiciera falta al apagar la app


app = FastAPI(title="Papelería API", version="0.1.0", lifespan=lifespan)

# 🔹 Monta los routers
app.include_router(categorias_router)
app.include_router(productos_router)
app.include_router(clientes_router)
app.include_router(compras_router)
app.include_router(usuarios_router)

# 🔹 Endpoint raíz
@app.get("/")
async def root():
    return {"ok": True, "msg": "API lista (modo asíncrono con PostgreSQL)"}
