from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from database import get_db
from models import Usuario
import schemas

router = APIRouter(prefix="/usuarios", tags=["Usuarios"])

@router.get("/", response_model=List[schemas.UsuarioRead])
async def listar_usuarios(
    tipo: Optional[str] = Query(None, description="mayorista | minorista"),
    cedula: Optional[str] = Query(None, description="coincidencia exacta"),
    frecuente: Optional[bool] = Query(None, description="cliente frecuente"),
    db: AsyncSession = Depends(get_db),
):
    stmt = select(Usuario)
    if tipo:
        stmt = stmt.where(Usuario.tipo == tipo)
    if cedula:
        stmt = stmt.where(Usuario.cedula == cedula)
    if frecuente is not None:
        stmt = stmt.where(Usuario.cliente_frecuente == frecuente)
    res = await db.execute(stmt)
    return res.scalars().all()

@router.get("/{usuario_id}", response_model=schemas.UsuarioRead)
async def obtener_usuario(usuario_id: int, db: AsyncSession = Depends(get_db)):
    res = await db.execute(select(Usuario).where(Usuario.id == usuario_id))
    obj = res.scalar_one_or_none()
    if not obj:
        raise HTTPException(404, "Usuario no encontrado")
    return obj

@router.get("/by-cedula/{cedula}", response_model=schemas.UsuarioRead)
async def obtener_por_cedula(cedula: str, db: AsyncSession = Depends(get_db)):
    res = await db.execute(select(Usuario).where(Usuario.cedula == cedula))
    obj = res.scalar_one_or_none()
    if not obj:
        raise HTTPException(404, "Usuario no encontrado")
    return obj

@router.post("/", response_model=schemas.UsuarioRead, status_code=status.HTTP_201_CREATED)
async def crear_usuario(payload: schemas.UsuarioCreate, db: AsyncSession = Depends(get_db)):
    # unicidad de cédula
    exists = await db.execute(select(Usuario).where(Usuario.cedula == payload.cedula))
    if exists.scalar_one_or_none():
        raise HTTPException(409, "Cédula ya registrada")
    obj = Usuario(**payload.model_dump())
    db.add(obj)
    await db.commit()
    await db.refresh(obj)
    return obj

@router.put("/{usuario_id}", response_model=schemas.UsuarioRead)
async def actualizar_usuario(usuario_id: int, payload: schemas.UsuarioUpdate, db: AsyncSession = Depends(get_db)):
    res = await db.execute(select(Usuario).where(Usuario.id == usuario_id))
    obj = res.scalar_one_or_none()
    if not obj:
        raise HTTPException(404, "Usuario no encontrado")

    data = payload.model_dump(exclude_none=True)
    if "cedula" in data:
        q = await db.execute(
            select(Usuario).where(Usuario.cedula == data["cedula"], Usuario.id != usuario_id)
        )
        if q.scalar_one_or_none():
            raise HTTPException(409, "Ya existe otro usuario con esa cédula")

    for k, v in data.items():
        setattr(obj, k, v)

    await db.commit()
    await db.refresh(obj)
    return obj

@router.delete("/{usuario_id}", status_code=status.HTTP_204_NO_CONTENT)
async def borrar_usuario(usuario_id: int, db: AsyncSession = Depends(get_db)):
    res = await db.execute(select(Usuario).where(Usuario.id == usuario_id))
    obj = res.scalar_one_or_none()
    if not obj:
        raise HTTPException(404, "Usuario no encontrado")
    await db.delete(obj)
    await db.commit()
