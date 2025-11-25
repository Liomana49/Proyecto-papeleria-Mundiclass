from typing import List
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status, Response
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
import schemas
import crud

router = APIRouter(prefix="/compras", tags=["Compras"])

@router.get("/", response_model=List[schemas.CompraRead])
async def listar_compras(db: AsyncSession = Depends(get_db)):
    return await crud.listar_compras(db)

@router.post("/", response_model=schemas.CompraRead, status_code=status.HTTP_201_CREATED)
async def crear_compra(payload: schemas.CompraCreate, db: AsyncSession = Depends(get_db)):
    return await crud.crear_compra(db, payload)

@router.delete("/{compra_id}", status_code=status.HTTP_204_NO_CONTENT)
async def eliminar_compra(compra_id: int, db: AsyncSession = Depends(get_db)):
    compra = await crud.obtener_compra(db, compra_id)
    descripcion = f"Compra eliminada id={compra.id}"

    await crud._registrar_eliminado(
        db,
        "compras",
        compra.id,
        {
            "cliente_id": compra.cliente_id,
            "producto_id": compra.producto_id,
            "cantidad": compra.cantidad,
            "precio_unitario_aplicado": compra.precio_unitario_aplicado,
            "total": compra.total,
            "fecha": compra.fecha.isoformat() if compra.fecha else None,
        },
    )
    await crud.borrar_compra(db, compra_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)

@router.get("/historial/eliminados", response_model=List[schemas.HistorialEliminadoRead])
async def historial_compras_eliminadas(db: AsyncSession = Depends(get_db)):
    return await crud.listar_historial(db)
