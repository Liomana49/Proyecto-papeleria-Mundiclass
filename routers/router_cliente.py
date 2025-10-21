from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime

from app.conf.db import get_async_db
from app.models.cliente import Cliente
from app.models.historial_eliminados import HistorialEliminados

router = APIRouter(prefix="/clientes", tags=["Clientes"])

async def log_delete(db: AsyncSession, tabla: str, registro_id: int, descripcion: str | None = None):
    h = HistorialEliminados(
        tabla=tabla,
        registro_id=registro_id,
        datos={"mensaje": descripcion} if descripcion else {},
        eliminado_en=datetime.utcnow(),
    )
    db.add(h)

@router.delete("/{cliente_id}")
async def eliminar_cliente(cliente_id: int, db: AsyncSession = Depends(get_async_db)):
    cliente = await db.get(Cliente, cliente_id)
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")

    await log_delete(db, "Cliente", cliente.id, f"Cliente '{cliente.nombre}' eliminado")
    await db.delete(cliente)
    await db.commit()
    return {"ok": True, "msg": "Cliente eliminado correctamente"}

@router.get("/historial/eliminados")
async def historial_clientes_eliminados(db: AsyncSession = Depends(get_async_db)):
    res = await db.execute(
        select(HistorialEliminados)
        .where(HistorialEliminados.tabla == "Cliente")
        .order_by(HistorialEliminados.eliminado_en.desc())
    )
    return res.scalars().all()
