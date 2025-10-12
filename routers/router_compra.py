from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from database import get_async_db
import schemas
import crud

router = APIRouter(prefix="/compras", tags=["Compras"])

@router.post("/", response_model=schemas.CompraRead)
async def create_compra(compra: schemas.CompraCreate, db: AsyncSession = Depends(get_async_db)):
    return await crud.crear_compra(db, compra)

@router.get("/", response_model=List[schemas.CompraRead])
async def read_compras(db: AsyncSession = Depends(get_async_db)):
    return await crud.listar_compras(db)

@router.get("/{compra_id}", response_model=schemas.CompraRead)
async def read_compra(compra_id: int, db: AsyncSession = Depends(get_async_db)):
    return await crud.obtener_compra(db, compra_id)

@router.delete("/{compra_id}")
async def delete_compra(compra_id: int, db: AsyncSession = Depends(get_async_db)):
    await crud.borrar_compra(db, compra_id)
    return {"message": "Compra eliminada"}
