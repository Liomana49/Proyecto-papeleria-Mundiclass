from typing import List, Optional
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query, status, Response
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
import schemas
import crud

router = APIRouter(prefix="/api/clientes", tags=["Clientes"])

@router.get("/", response_model=List[schemas.ClienteRead])
async def listar_clientes(
    nombre: Optional[str] = None,
    cedula: Optional[str] = None,
    tipo_cliente: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
):
    return await crud.listar_clientes(db)

@router.post("/", response_model=schemas.ClienteRead, status_code=status.HTTP_201_CREATED)
async def crear_cliente(payload: schemas.ClienteCreate, db: AsyncSession = Depends(get_db)):
    return await crud.crear_cliente(db, payload)

@router.put("/{cliente_id}", response_model=schemas.ClienteRead)
async def actualizar_cliente(cliente_id: int, payload: schemas.ClienteUpdate, db: AsyncSession = Depends(get_db)):
    return await crud.actualizar_cliente(db, cliente_id, payload)

@router.delete("/{cliente_id}", status_code=status.HTTP_204_NO_CONTENT)
async def eliminar_cliente(cliente_id: int, db: AsyncSession = Depends(get_db)):
    cliente = await crud.obtener_cliente(db, cliente_id)

    descripcion = f"Cliente '{cliente.nombre}' eliminado"

    await crud._registrar_eliminado(db, "clientes", cliente.id, {"nombre": cliente.nombre})
    await crud.borrar_cliente(db, cliente_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)

@router.get("/historial/eliminados", response_model=List[schemas.HistorialEliminadoRead])
async def historial_clientes_eliminados(db: AsyncSession = Depends(get_db)):
    return await crud.listar_historial(db)
