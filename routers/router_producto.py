from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime

# Ajusta estas rutas de import según tu estructura real
from app.conf.db import get_async_db  # si usas get_db, cambia el nombre en Depends
from app.models.producto import Producto
from app.models.historial_eliminados import HistorialEliminados

router = APIRouter(prefix="/productos", tags=["Productos"])

async def log_delete(db: AsyncSession, tabla: str, registro_id: int, descripcion: str | None = None):
    h = HistorialEliminados(
        tabla=tabla,
        registro_id=registro_id,
        datos={"mensaje": descripcion} if descripcion else {},
        eliminado_en=datetime.utcnow(),
    )
    db.add(h)

@router.delete("/{producto_id}")
async def eliminar_producto(producto_id: int, db: AsyncSession = Depends(get_async_db)):
    producto = await db.get(Producto, producto_id)
    if not producto:
        raise HTTPException(status_code=404, detail="Producto no encontrado")

    await log_delete(db, "Producto", producto.id, f"Producto '{producto.nombre}' eliminado")
    await db.delete(producto)
    await db.commit()
    return {"ok": True, "msg": "Producto eliminado correctamente"}

@router.get("/historial/eliminados")
async def historial_productos_eliminados(db: AsyncSession = Depends(get_async_db)):
    res = await db.execute(
        select(HistorialEliminados)
        .where(HistorialEliminados.tabla == "Producto")
        .order_by(HistorialEliminados.eliminado_en.desc())
    )
    return res.scalars().all()
