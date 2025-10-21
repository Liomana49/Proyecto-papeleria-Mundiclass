from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.conf.db import get_async_db
from app.models.historial_eliminados import HistorialEliminados

router = APIRouter(prefix="/historial", tags=["Historial"])

@router.get("/eliminados")
async def listar_eliminados(db: AsyncSession = Depends(get_async_db)):
    res = await db.execute(
        select(HistorialEliminados).order_by(HistorialEliminados.eliminado_en.desc())
    )
    return res.scalars().all()

