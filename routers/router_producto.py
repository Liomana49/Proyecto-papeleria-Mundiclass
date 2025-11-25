from typing import List, Optional
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query, status, Response
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
import schemas
import crud

router = APIRouter(prefix="/productos", tags=["Productos"])

@router.get("/", response_model=List[schemas.ProductoRead])
async def listar_productos(
    nombre: Optional[str] = None,
    categoria_id: Optional[int] = None,
    db: AsyncSession = Depends(get_db),
):
    return await crud.listar_productos(db, nombre=nombre, min_stock=None)  # adapt as needed

@router.post("/", response_model=schemas.ProductoRead, status_code=status.HTTP_201_CREATED)
async def crear_producto(payload: schemas.ProductoCreate, db: AsyncSession = Depends(get_db)):
    return await crud.crear_producto(db, payload)

@router.put("/{producto_id}", response_model=schemas.ProductoRead)
async def actualizar_producto(producto_id: int, payload: schemas.ProductoUpdate, db: AsyncSession = Depends(get_db)):
    return await crud.actualizar_producto(db, producto_id, payload)

@router.delete("/{producto_id}", status_code=status.HTTP_204_NO_CONTENT)
async def eliminar_producto(producto_id: int, db: AsyncSession = Depends(get_db)):
    producto = await crud.obtener_producto(db, producto_id)

    descripcion = f"Producto '{producto.nombre}' eliminado"

    await crud._registrar_eliminado(db, "productos", producto.id, {"nombre": producto.nombre})
    await crud.borrar_producto(db, producto_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)

@router.get("/historial/eliminados", response_model=List[schemas.HistorialEliminadoRead])
async def historial_productos_eliminados(db: AsyncSession = Depends(get_db)):
    return await crud.listar_historial(db)

