from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from database import get_async_db
import schemas
import crud

router = APIRouter(prefix="/categorias", tags=["Categorías"])

@router.post("/", response_model=schemas.CategoriaRead)
async def create_categoria(categoria: schemas.CategoriaCreate, db: AsyncSession = Depends(get_async_db)):
    return await crud.crear_categoria(db, categoria)

@router.get("/", response_model=List[schemas.CategoriaRead])
async def read_categorias(db: AsyncSession = Depends(get_async_db)):
    return await crud.listar_categorias(db)

@router.get("/{categoria_id}", response_model=schemas.CategoriaRead)
async def read_categoria(categoria_id: int, db: AsyncSession = Depends(get_async_db)):
    return await crud.obtener_categoria(db, categoria_id)

@router.put("/{categoria_id}", response_model=schemas.CategoriaRead)
async def update_categoria(categoria_id: int, categoria: schemas.CategoriaUpdate, db: AsyncSession = Depends(get_async_db)):
    return await crud.actualizar_categoria(db, categoria_id, categoria)

@router.delete("/{categoria_id}")
async def delete_categoria(categoria_id: int, db: AsyncSession = Depends(get_async_db)):
    await crud.borrar_categoria(db, categoria_id)
    return {"message": "Categoría eliminada"}
