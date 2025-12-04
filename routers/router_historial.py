from typing import List, Optional

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from models import HistorialEliminados
import schemas

router = APIRouter(prefix="/api/historial", tags=["Historial"])

@router.get("/eliminados", response_model=List[schemas.HistorialEliminadoRead])
async def listar_eliminados(tabla: Optional[str] = None, db: AsyncSession = Depends(get_db)):
    stmt = select(HistorialEliminados).order_by(HistorialEliminados.eliminado_en.desc())
    
    if tabla:
        stmt = stmt.where(HistorialEliminados.tabla == tabla)
    
    res = await db.execute(stmt)
    return res.scalars().all()


