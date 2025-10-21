from typing import List, Optional
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query, status, Response
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from models import Cliente, HistorialEliminados
import schemas

router = APIRouter(prefix="/clientes", tags=["Clientes"])

async def log_delete(db: AsyncSession, tabla: str, registro_id: int, descripcion: str | None = None):
    h = HistorialEliminados(
        tabla=tabla,
        registro_id=registro_id,
        datos={"descripcion": descripcion or "", "timestamp": datetime.utcnow().isoformat()},
    )
    db.add(h)

@router.get("/", response_model=List[schemas.ClienteRead])
async def listar_clientes(
    nombre: Optional[str] = Query(None),
    cedula: Optional[str] = Query(None),
    tipo_cliente: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
):
    stmt = select(Cliente)
    conds = []
    if nombre:
        conds.append(Cliente.nombre == nombre)
    if cedula:
        conds.append(Cliente.cedula == cedula)
    if tipo_cliente:
        conds.append(Cliente.tipo_cliente == tipo_cliente)
    if conds:
        stmt = stmt.where(and_(*conds))
    res = await db.execute(stmt)
    return res.scalars().all()

@router.post("/", response_model=schemas.ClienteRead, status_code=status.HTTP_201_CREATED)
async def crear_cliente(payload: schemas.ClienteCreate, db: AsyncSession = Depends(get_db)):
    obj = Cliente(**payload.model_dump())
    db.add(obj)
    await db.commit()
    await db.refresh(obj)
    return obj

@router.put("/{cliente_id}", response_model=schemas.ClienteRead)
async def actualizar_cliente(cliente_id: int, payload: schemas.ClienteUpdate, db: AsyncSession = Depends(get_db)):
    res = await db.execute(select(Cliente).where(Cliente.id == cliente_id))
    obj = res.scalar_one_or_none()
    if not obj:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    for k, v in payload.model_dump(exclude_none=True).items():
        setattr(obj, k, v)
    await db.commit()
    await db.refresh(obj)
    return obj

@router.delete("/{cliente_id}", status_code=status.HTTP_204_NO_CONTENT)
async def eliminar_cliente(cliente_id: int, db: AsyncSession = Depends(get_db)):
    res = await db.execute(select(Cliente).where(Cliente.id == cliente_id))
    obj = res.scalar_one_or_none()
    if not obj:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")

    await log_delete(db, "Cliente", obj.id, f"Cliente '{obj.nombre}' eliminado")
    await db.delete(obj)
    await db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)

@router.get("/historial/eliminados", response_model=List[schemas.HistorialEliminadoRead])
async def historial_clientes_eliminados(db: AsyncSession = Depends(get_db)):
    res = await db.execute(
        select(HistorialEliminados)
        .where(HistorialEliminados.tabla == "Cliente")
        .order_by(HistorialEliminados.eliminado_en.desc())
    )
    return res.scalars().all()
