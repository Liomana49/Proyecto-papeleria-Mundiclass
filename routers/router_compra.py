from typing import List, Optional
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status, Response
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
import schemas
import crud

router = APIRouter(prefix="/compras", tags=["Compras"])

@router.get("/", response_model=List[schemas.CompraRead])
async def listar_compras(
    cliente_id: Optional[int] = None,
    producto_id: Optional[int] = None,
    min_total: Optional[float] = None,
    max_total: Optional[float] = None,
    fecha_desde: Optional[str] = None,
    fecha_hasta: Optional[str] = None,
    nombre_cliente: Optional[str] = None,
    nombre_producto: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
):
    return await crud.listar_compras(
        db,
        cliente_id=cliente_id,
        producto_id=producto_id,
        min_total=min_total,
        max_total=max_total,
        fecha_desde=fecha_desde,
        fecha_hasta=fecha_hasta,
        nombre_cliente=nombre_cliente,
        nombre_producto=nombre_producto,
    )

@router.post("/", response_model=schemas.CompraRead, status_code=status.HTTP_201_CREATED)
async def crear_compra(payload: schemas.CompraCreate, db: AsyncSession = Depends(get_db)):
    return await crud.crear_compra(db, payload)

@router.get("/{compra_id}", response_model=schemas.CompraRead)
async def obtener_compra(compra_id: int, db: AsyncSession = Depends(get_db)):
    return await crud.obtener_compra(db, compra_id)

@router.put("/{compra_id}", response_model=schemas.CompraRead)
async def actualizar_compra(compra_id: int, payload: schemas.CompraUpdate, db: AsyncSession = Depends(get_db)):
    return await crud.actualizar_compra(db, compra_id, payload)

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
