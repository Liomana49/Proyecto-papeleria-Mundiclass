from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime

from app.conf.db import get_async_db
from app.models.categoria import Categoria
from app.models.historial_eliminados import HistorialEliminados

router = APIRouter(prefix="/categorias", tags=["Categorias"])

async def log_delete(db: AsyncSession, tabla: str, registro_id: int, descripcion: str | None = None):
    h = HistorialEliminados(
        tabla=tabla,
        registro_id=registro_id,
        datos={"mensaje": descripcion} if descripcion else {},
        eliminado_en=datetime.utcnow(),
    )
    db.add(h)

@router.delete("/{categoria_id}")
async def eliminar_categoria(categoria_id: int, db: AsyncSession = Depends(get_async_db)):
    categoria = await db.get(Categoria, categoria_id)
    if not categoria:
        raise HTTPException(status_code=404, detail="Categoría no encontrada")

    await log_delete(db, "Categoria", categoria.id, f"Categoría '{categoria.nombre}' eliminada")
    await db.delete(categoria)
    await db.commit()
    return {"ok": True, "msg": "Categoría eliminada correctamente"}

@router.get("/historial/eliminados")
async def historial_categorias_eliminadas(db: AsyncSession = Depends(get_async_db)):
    res = await db.execute(
        select(HistorialEliminados)
        .where(HistorialEliminados.tabla == "Categoria")
        .order_by(HistorialEliminados.eliminado_en.desc())
    )
    return res.scalars().all()
