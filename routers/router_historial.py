from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from models import HistorialEliminados
import schemas

router = APIRouter(prefix="/historial", tags=["Historial"])

@router.get("/eliminados", response_model=List[schemas.HistorialEliminadoRead])
async def listar_eliminados(db: AsyncSession = Depends(get_db)):
    res = await db.execute(
        select(HistorialEliminados).order_by(HistorialEliminados.eliminado_en.desc())
    )
    return res.scalars().all()


