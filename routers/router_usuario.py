from typing import List, Optional
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query, status, Response
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from models import Usuario, HistorialEliminados
import schemas

router = APIRouter(prefix="/usuarios", tags=["Usuarios"])

# Helper historial
async def log_delete(db: AsyncSession, tabla: str, registro_id: int, descripcion: str | None = None):
    h = HistorialEliminados(
        tabla=tabla,
        registro_id=registro_id,
        datos={"descripcion": descripcion or "", "timestamp": datetime.utcnow().isoformat()},
    )
    db.add(h)

@router.get("/", response_model=List[schemas.UsuarioRead])
async def listar_usuarios(
    rol: Optional[str] = Query(None, description="administrador/cliente"),
    cedula: Optional[str] = Query(None),
    correo: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
):
    stmt = select(Usuario)
    conds = []
    if rol:
        conds.append(Usuario.rol == rol)
    if cedula:
        conds.append(Usuario.cedula == cedula)
    if correo:
        conds.append(Usuario.correo == correo)
    if conds:
        stmt = stmt.where(and_(*conds))
    res = await db.execute(stmt)
    return res.scalars().all()

@router.get("/{usuario_id}", response_model=schemas.UsuarioRead)
async def obtener_usuario(usuario_id: int, db: AsyncSession = Depends(get_db)):
    res = await db.execute(select(Usuario).where(Usuario.id == usuario_id))
    obj = res.scalar_one_or_none()
    if not obj:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return obj

@router.post("/", response_model=schemas.UsuarioRead, status_code=status.HTTP_201_CREATED)
async def crear_usuario(payload: schemas.UsuarioCreate, db: AsyncSession = Depends(get_db)):
    # correo único
    if (await db.execute(select(Usuario).where(Usuario.correo == payload.correo))).scalar_one_or_none():
        raise HTTPException(status_code=409, detail="Correo ya registrado")
    # cédula única (si viene)
    if payload.cedula is not None:
        if (await db.execute(select(Usuario).where(Usuario.cedula == payload.cedula))).scalar_one_or_none():
            raise HTTPException(status_code=409, detail="Cédula ya registrada")

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
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    data = payload.model_dump(exclude_none=True)

    if "correo" in data:
        q = await db.execute(select(Usuario).where(Usuario.correo == data["correo"], Usuario.id != usuario_id))
        if q.scalar_one_or_none():
            raise HTTPException(status_code=409, detail="Ya existe otro usuario con ese correo")
    if "cedula" in data:
        q = await db.execute(select(Usuario).where(Usuario.cedula == data["cedula"], Usuario.id != usuario_id))
        if q.scalar_one_or_none():
            raise HTTPException(status_code=409, detail="Ya existe otro usuario con esa cédula")

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
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    await log_delete(db, "Usuario", obj.id, f"Usuario {obj.nombre} eliminado")
    await db.delete(obj)
    await db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)

@router.get("/historial/eliminados", response_model=List[schemas.HistorialEliminadoRead])
async def historial_usuarios_eliminados(db: AsyncSession = Depends(get_db)):
    res = await db.execute(
        select(HistorialEliminados)
        .where(HistorialEliminados.tabla == "Usuario")
        .order_by(HistorialEliminados.eliminado_en.desc())
    )
    return res.scalars().all()
