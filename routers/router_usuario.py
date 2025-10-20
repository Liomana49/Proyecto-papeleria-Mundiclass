from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from database import get_db
from models import Usuario, HistorialEliminados
import schemas

router = APIRouter(prefix="/usuarios", tags=["Usuarios"])

async def log_delete(db: AsyncSession, tabla: str, registro_id: int, descripcion: str | None = None):
    # HistorialEliminados espera: tabla, registro_id, datos(JSONB), eliminado_en
    h = HistorialEliminados(
        tabla=tabla,
        registro_id=registro_id,
        datos={
            "descripcion": descripcion or "",
            "timestamp": datetime.utcnow().isoformat()
        },
        # eliminado_en tiene server_default=now(); lo dejamos que DB lo ponga
    )
    db.add(h)

@router.get("/", response_model=List[schemas.UsuarioRead])
async def listar_usuarios(
    rol: Optional[str] = Query(None, description="Filtra por rol: administrador/cliente"),
    cedula: Optional[str] = Query(None, description="Filtra por cédula si existe en Usuario"),
    correo: Optional[str] = Query(None, description="Filtra por correo"),
    db: AsyncSession = Depends(get_db),
):
    stmt = select(Usuario)
    conds = []
    if rol:
        conds.append(Usuario.rol == rol)
    if cedula:
        # cedula es opcional en Usuario; si no la usas, elimina esta línea
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
    # Validar correo único
    q_correo = await db.execute(select(Usuario).where(Usuario.correo == payload.correo))
    if q_correo.scalar_one_or_none():
        raise HTTPException(status_code=409, detail="Correo ya registrado")

    # Validar cédula si viene en el payload y existe en el modelo
    if getattr(payload, "cedula", None) is not None:
        q_ced = await db.execute(select(Usuario).where(Usuario.cedula == payload.cedula))
        if q_ced.scalar_one_or_none():
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

    # Unicidad de correo si cambia
    if "correo" in data:
        q = await db.execute(select(Usuario).where(Usuario.correo == data["correo"], Usuario.id != usuario_id))
        if q.s
