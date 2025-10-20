from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from database import get_db
from models import Cliente, Usuario
import schemas

router = APIRouter(prefix="/clientes", tags=["Clientes"])

@router.get("/", response_model=List[schemas.ClienteRead])
async def listar_clientes(
    nombre: Optional[str] = Query(None, description="nombre del usuario vinculado"),
    activo: Optional[bool] = Query(None),
    tipo: Optional[str] = Query(None, description="mayorista | minorista"),
    frecuente: Optional[bool] = Query(None),
    db: AsyncSession = Depends(get_db),
):
    # join con Usuario para filtros por nombre/tipo/frecuente
    stmt = select(Cliente).join(Usuario)
    if nombre:
        stmt = stmt.where(Usuario.nombre.ilike(f"%{nombre}%"))
    if tipo:
        stmt = stmt.where(Usuario.tipo == tipo)
    if frecuente is not None:
        stmt = stmt.where(Usuario.cliente_frecuente == frecuente)
    if activo is not None:
        stmt = stmt.where(Cliente.activo == activo)
    res = await db.execute(stmt)
    return res.scalars().all()

@router.get("/{cliente_id}", response_model=schemas.ClienteRead)
async def obtener_cliente(cliente_id: int, db: AsyncSession = Depends(get_db)):
    res = await db.execute(select(Cliente).where(Cliente.id == cliente_id))
    obj = res.scalar_one_or_none()
    if not obj:
        raise HTTPException(404, "Cliente no encontrado")
    return obj

@router.get("/by-cedula/{cedula}", response_model=schemas.ClienteRead)
async def cliente_por_cedula(cedula: str, db: AsyncSession = Depends(get_db)):
    # compatibilidad: busca por cedula en tabla Cliente (la tienes en el modelo)
    res = await db.execute(select(Cliente).where(Cliente.cedula == cedula))
    obj = res.scalar_one_or_none()
    if not obj:
        raise HTTPException(404, "Cliente no encontrado con esa cédula")
    return obj

@router.post("/", response_model=schemas.ClienteRead, status_code=status.HTTP_201_CREATED)
async def crear_cliente(payload: schemas.ClienteCreate, db: AsyncSession = Depends(get_db)):
    # si usas usuario_id, valida que exista
    if payload.usuario_id is not None:
        ruser = await db.execute(select(Usuario).where(Usuario.id == payload.usuario_id))
        if not ruser.scalar_one_or_none():
            raise HTTPException(404, "Usuario no existe")

    # evita cédula duplicada si la envían
    if payload.cedula:
        exists = await db.execute(select(Cliente).where(Cliente.cedula == payload.cedula))
        if exists.scalar_one_or_none():
            raise HTTPException(400, "Ya existe un cliente con esa cédula")

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
        raise HTTPException(404, "Cliente no encontrado")

    data = payload.model_dump(exclude_none=True)
    if "cedula" in data and data["cedula"]:
        q = await db.execute(select(Cliente).where(Cliente.cedula == data["cedula"], Cliente.id != cliente_id))
        if q.scalar_one_or_none():
            raise HTTPException(400, "Ya existe otro cliente con esa cédula")

    for k, v in data.items():
        setattr(obj, k, v)

    await db.commit()
    await db.refresh(obj)
    return obj

@router.delete("/{cliente_id}", status_code=status.HTTP_204_NO_CONTENT)
async def borrar_cliente(cliente_id: int, db: AsyncSession = Depends(get_db)):
    res = await db.execute(select(Cliente).where(Cliente.id == cliente_id))
    obj = res.scalar_one_or_none()
    if not obj:
        raise HTTPException(404, "Cliente no encontrado")
    await db.delete(obj)
    await db.commit()
