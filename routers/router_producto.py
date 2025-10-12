from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from database import get_async_db
import schemas
import crud  # <- tu CRUD ya migrado a async

router = APIRouter(prefix="/productos", tags=["Productos"])

@router.post("/", response_model=schemas.ProductoRead)
async def create_producto(producto: schemas.ProductoCreate, db: AsyncSession = Depends(get_async_db)):
    return await crud.crear_producto(db, producto)

@router.get("/", response_model=List[schemas.ProductoRead])
async def read_productos(db: AsyncSession = Depends(get_async_db)):
    return await crud.listar_productos(db)

@router.get("/{producto_id}", response_model=schemas.ProductoRead)
async def read_producto(producto_id: int, db: AsyncSession = Depends(get_async_db)):
    return await crud.obtener_producto(db, producto_id)

@router.put("/{producto_id}", response_model=schemas.ProductoRead)
async def update_producto(producto_id: int, producto: schemas.ProductoUpdate, db: AsyncSession = Depends(get_async_db)):
    return await crud.actualizar_producto(db, producto_id, producto)

@router.delete("/{producto_id}")
async def delete_producto(producto_id: int, db: AsyncSession = Depends(get_async_db)):
    await crud.borrar_producto(db, producto_id)
    return {"message": "Producto eliminado"}

@router.get("/bajo-stock", response_model=List[schemas.ProductoRead])
async def read_productos_bajo_stock(db: AsyncSession = Depends(get_async_db)):
    return await crud.productos_bajo_stock(db)
