from typing import List
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status, Response
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from models import Compra, HistorialEliminados
import schemas

router = APIRouter(prefix="/compras", tags=["Compras"])

async def log_delete(db: AsyncSession, tabla: str, registro_id: int, descripcion: str | None = None):
    h = HistorialEliminados(
        tabla=tabla,
        registro_id=registro_id,
        datos={"descripcion": descripcion or "", "timestamp": datetime.utcnow().isoformat()},
    )
    db.add(h)

@router.get("/", response_model=List[schemas.CompraRead])
async def listar_compras(db: AsyncSession = Depends(get_db)):
    res = await db.execute(select(Compra))
    return res.scalars().all()

@router.post("/", response_model=schemas.CompraRead, status_code=status.HTTP_201_CREATED)
async def crear_compra(payload: schemas.CompraCreate, db: AsyncSession = Depends(get_db)):
    obj = Compra(**payload.model_dump())
    db.add(obj)
    await db.commit()
    await db.refresh(obj)
    return obj

@router.delete("/{compra_id}", status_code=status.HTTP_204_NO_CONTENT)
async def eliminar_compra(compra_id: int, db: AsyncSession = Depends(get_db)):
    res = await db.execute(select(Compra).where(Compra.id == compra_id))
    obj = res.scalar_one_or_none()
    if not obj:
        raise HTTPException(status_code=404, detail="Compra no encontrada")

    await log_delete(db, "Compra", obj.id, "Compra eliminada")
    await db.delete(obj)
    await db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)

@router.get("/historial/eliminados", response_model=List[schemas.HistorialEliminadoRead])
async def historial_compras_eliminadas(db: AsyncSession = Depends(get_db)):
    res = await db.execute(
        select(HistorialEliminados)
        .where(HistorialEliminados.tabla == "Compra")
        .order_by(HistorialEliminados.eliminado_en.desc())
    )
    return res.scalars().all()


