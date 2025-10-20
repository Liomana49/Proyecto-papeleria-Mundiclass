# router_historial.py
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from database import get_db
from models import HistorialEliminados

router = APIRouter(prefix="/historial", tags=["Historial"])

@router.get("/eliminados")
async def listar_eliminados(db: AsyncSession = Depends(get_db)):
    """Devuelve todos los registros de la tabla HistorialEliminados"""
    res = await db.execute(
        select(HistorialEliminados).order_by(HistorialEliminados.fecha_eliminado.desc())
    )
    return res.scalars().all()
