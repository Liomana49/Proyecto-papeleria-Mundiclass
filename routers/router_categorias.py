from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from database import get_db
from models import Categoria
import schemas

router = APIRouter(prefix="/categorias", tags=["Categorias"])

@router.get("/", response_model=List[schemas.CategoriaRead])
async def listar_categorias(db: AsyncSession = Depends(get_db)):
    res = await db.execute(select(Categoria))
    return res.scalars().all()

@router.get("/filtrar")
async def filtrar_categorias(
    nombre: str = Query(..., description="cadena a buscar"),
    solo_codigos: bool = Query(True, description="si true devuelve solo códigos"),
    db: AsyncSession = Depends(get_db),
):
    res = await db.execute(select(Categoria).where(Categoria.nombre.ilike(f"%{nombre}%")))
    cats = res.scalars().all()
    if solo_codigos:
        return [{"codigo": c.codigo if c.codigo else str(c.id)} for c in cats]
    return [{"id": c.id, "codigo": c.codigo, "nombre": c.nombre} for c in cats]

@router.get("/by-codigo/{codigo}", response_model=schemas.CategoriaRead)
async def categoria_por_codigo(codigo: str, db: AsyncSession = Depends(get_db)):
    res = await db.execute(select(Categoria).where(Categoria.codigo == codigo))
    obj = res.scalar_one_or_none()
    if not obj:
        raise HTTPException(404, "Categoría no encontrada")
    return obj

@router.post("/", response_model=schemas.CategoriaRead, status_code=status.HTTP_201_CREATED)
async def crear_categoria(payload: schemas.CategoriaCreate, db: AsyncSession = Depends(get_db)):
    # evita nombre duplicado si así lo deseas
    exists = await db.execute(select(Categoria).where(Categoria.nombre == payload.nombre))
    if exists.scalar_one_or_none():
        raise HTTPException(400, "La categoría ya existe")
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
        raise HTTPException(404, "Categoría no encontrada")

    for k, v in payload.model_dump(exclude_none=True).items():
        setattr(obj, k, v)

    await db.commit()
    await db.refresh(obj)
    return obj

@router.delete("/{categoria_id}", status_code=status.HTTP_204_NO_CONTENT)
async def borrar_categoria(categoria_id: int, db: AsyncSession = Depends(get_db)):
    res = await db.execute(select(Categoria).where(Categoria.id == categoria_id))
    obj = res.scalar_one_or_none()
    if not obj:
        raise HTTPException(404, "Categoría no encontrada")
    await db.delete(obj)
    await db.commit()
