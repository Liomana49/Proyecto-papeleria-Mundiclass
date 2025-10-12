from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from database import get_async_db
import schemas
import crud

router = APIRouter(prefix="/clientes", tags=["Clientes"])

@router.post("/", response_model=schemas.ClienteRead)
async def create_cliente(cliente: schemas.ClienteCreate, db: AsyncSession = Depends(get_async_db)):
    return await crud.crear_cliente(db, cliente)

@router.get("/", response_model=List[schemas.ClienteRead])
async def read_clientes(db: AsyncSession = Depends(get_async_db)):
    return await crud.listar_clientes(db)

@router.get("/{cliente_id}", response_model=schemas.ClienteRead)
async def read_cliente(cliente_id: int, db: AsyncSession = Depends(get_async_db)):
    return await crud.obtener_cliente(db, cliente_id)

@router.put("/{cliente_id}", response_model=schemas.ClienteRead)
async def update_cliente(cliente_id: int, cliente: schemas.ClienteUpdate, db: AsyncSession = Depends(get_async_db)):
    return await crud.actualizar_cliente(db, cliente_id, cliente)

@router.delete("/{cliente_id}")
async def delete_cliente(cliente_id: int, db: AsyncSession = Depends(get_async_db)):
    await crud.borrar_cliente(db, cliente_id)
    return {"message": "Cliente eliminado"}
