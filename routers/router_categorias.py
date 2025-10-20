from typing import List
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from database import get_db
from models import Categoria, HistorialEliminados
import schemas

router = APIRouter(prefix="/categorias", tags=["Categorias"])

async def log_delete(db: AsyncSession, tabla: str, registro_id: int, descripcion: str | None = None):
    h = HistorialEliminados(tabla=tabla, registro_id=registro_id, datos=descripcion or "", eliminado_en=datetime.utcnow())
    db.add(h)

@router.get("/", response_model=List[schemas.CategoriaRead])
async def listar_categorias(db: AsyncSession = Depends(get_db)):
    res = await db.execute(select(Categoria)); return res.scalars().all()

@router.get("/filtrar")
async def filtrar_categorias(nombre: str = Query(...), solo_codigos: bool = Query(True), db: AsyncSession = Depends(get_db)):
    res = await db.execute(select(Categoria).where(Categoria.nombre.ilike(f"%{nombre}%")))
    cats = res.scalars().all()
    if solo_codigos: return [{"codigo": c.codigo if c.codigo else str(c.id)} for c in cats]
    return [{"id": c.id, "codigo": c.codigo, "nombre": c.nombre} for c in cats]

@router.post("/", response_model=schemas.CategoriaRead, status_code=status.HTTP_201_CREATED)
async def crear_categoria(payload: schemas.CategoriaCreate, db: AsyncSession = Depends(get_db)):
    dup = await db.execute(select(Categoria).where(Categoria.nombre == payload.nombre))
    if dup.scalar_one_or_none(): raise HTTPException(400, "La categoría ya existe")
    obj = Categoria(**payload.model_dump())
    db.add(obj); await db.commit(); await db.refresh(obj); return obj

@router.put("/{categoria_id}", response_model=schemas.CategoriaRead)
async def actualizar_categoria(categoria_id: int, payload: schemas.CategoriaUpdate, db: AsyncSession = Depends(get_db)):
    res = await db.execute(select(Categoria).where(Categoria.id == categoria_id))
    obj = res.scalar_one_or_none()
    if not obj: raise HTTPException(404, "Categoría no encontrada")
    for k, v in payload.model_dump(exclude_none=True).items(): setattr(obj, k, v)
    await db.commit(); await db.refresh(obj); return obj

@router.delete("/{categoria_id}", status_code=status.HTTP_204_NO_CONTENT)
async def borrar_categoria(categoria_id: int, db: AsyncSession = Depends(get_db)):
    res = await db.execute(select(Categoria).where(Categoria.id == categoria_id))
    obj = res.scalar_one_or_none()
    if not obj: raise HTTPException(404, "Categoría no encontrada")
    await log_delete(db, "Categoria", obj.id, f"Categoría {obj.nombre} eliminada")
    await db.delete(obj); await db.commit()

@router.get("/historial/eliminados")
async def historial_categorias_eliminadas(db: AsyncSession = Depends(get_db)):
    res = await db.execute(
        select(HistorialEliminados)
        .where(HistorialEliminados.tabla == "Categoria")
        .order_by(HistorialEliminados.eliminado_en.desc())
    )
    return res.scalars().all()
