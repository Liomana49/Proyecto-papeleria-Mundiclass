from typing import List, Optional
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query, status, Response
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from models import Categoria, HistorialEliminados
import schemas

router = APIRouter(prefix="/categorias", tags=["Categorias"])

async def log_delete(db: AsyncSession, tabla: str, registro_id: int, descripcion: str | None = None):
    h = HistorialEliminados(
        tabla=tabla,
        registro_id=registro_id,
        datos={"descripcion": descripcion or "", "timestamp": datetime.utcnow().isoformat()},
    )
    db.add(h)

@router.get("/", response_model=List[schemas.CategoriaRead])
async def listar_categorias(
    nombre: Optional[str] = Query(None),
    codigo: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
):
    stmt = select(Categoria)
    conds = []
    if nombre:
        conds.append(Categoria.nombre == nombre)
    if codigo:
        conds.append(Categoria.codigo == codigo)
    if conds:
        stmt = stmt.where(and_(*conds))
    res = await db.execute(stmt)
    return res.scalars().all()

@router.post("/", response_model=schemas.CategoriaRead, status_code=status.HTTP_201_CREATED)
async def crear_categoria(payload: schemas.CategoriaCreate, db: AsyncSession = Depends(get_db)):
    obj = Categoria(**payload.model_dump())
    db.add(obj)
    await db.commit()
    await db.refresh(obj)
    return obj

@router.put("/{categoria_id}", response_model=schemas.CategoriaRead)
async def actualizar_categoria(categoria_id: int, payload: schemas.CategoriaUpdate, db: AsyncSession = Depends(get_db)):
    res = await db.execute(select(Categoria).where(Categoria.id == categoria_id))
    obj = res.scalar_one_or_none()
    if not obj:
        raise HTTPException(status_code=404, detail="Categoría no encontrada")
    for k, v in payload.model_dump(exclude_none=True).items():
        setattr(obj, k, v)
    await db.commit()
    await db.refresh(obj)
    return obj

@router.delete("/{categoria_id}", status_code=status.HTTP_204_NO_CONTENT)
async def eliminar_categoria(categoria_id: int, db: AsyncSession = Depends(get_db)):
    res = await db.execute(select(Categoria).where(Categoria.id == categoria_id))
    obj = res.scalar_one_or_none()
    if not obj:
        raise HTTPException(status_code=404, detail="Categoría no encontrada")

    await log_delete(db, "Categoria", obj.id, f"Categoría '{obj.nombre}' eliminada")
    await db.delete(obj)
    await db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)

@router.get("/historial/eliminados", response_model=List[schemas.HistorialEliminadoRead])
async def historial_categorias_eliminadas(db: AsyncSession = Depends(get_db)):
    res = await db.execute(
        select(HistorialEliminados)
        .where(HistorialEliminados.tabla == "Categoria")
        .order_by(HistorialEliminados.eliminado_en.desc())
    )
    return res.scalars().all()

