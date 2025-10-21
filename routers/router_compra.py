from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime

from app.conf.db import get_async_db
from app.models.compra import Compra
from app.models.historial_eliminados import HistorialEliminados

router = APIRouter(prefix="/compras", tags=["Compras"])

async def log_delete(db: AsyncSession, tabla: str, registro_id: int, descripcion: str | None = None):
    h = HistorialEliminados(
        tabla=tabla,
        registro_id=registro_id,
        datos={"mensaje": descripcion} if descripcion else {},
        eliminado_en=datetime.utcnow(),
    )
    db.add(h)

@router.delete("/{compra_id}")
async def eliminar_compra(compra_id: int, db: AsyncSession = Depends(get_async_db)):
    compra = await db.get(Compra, compra_id)
    if not compra:
        raise HTTPException(status_code=404, detail="Compra no encontrada")

    await log_delete(db, "Compra", compra.id, "Compra eliminada")
    await db.delete(compra)
    await db.commit()
    return {"ok": True, "msg": "Compra eliminada correctamente"}

@router.get("/historial/eliminados")
async def historial_compras_eliminadas(db: AsyncSession = Depends(get_async_db)):
    res = await db.execute(
        select(HistorialEliminados)
        .where(HistorialEliminados.tabla == "Compra")
        .order_by(HistorialEliminados.eliminado_en.desc())
    )
    return res.scalars().all()

