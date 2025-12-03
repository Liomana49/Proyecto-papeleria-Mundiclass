from typing import List, Optional
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query, status, Response
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
import schemas
import crud

router = APIRouter(prefix="/api/usuarios", tags=["Usuarios"])

@router.get("/", response_model=List[schemas.UsuarioRead])
async def listar_usuarios(
    rol: Optional[str] = None,
    cedula: Optional[str] = None,
    correo: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
):
    return await crud.listar_usuarios(db)  # Filtering can be added to crud if necessary

@router.get("/{usuario_id}", response_model=schemas.UsuarioRead)
async def obtener_usuario(usuario_id: int, db: AsyncSession = Depends(get_db)):
    return await crud.obtener_usuario(db, usuario_id)

@router.post("/", response_model=schemas.UsuarioRead, status_code=status.HTTP_201_CREATED)
async def crear_usuario(payload: schemas.UsuarioCreate, db: AsyncSession = Depends(get_db)):
    return await crud.crear_usuario(db, payload)

@router.put("/{usuario_id}", response_model=schemas.UsuarioRead)
async def actualizar_usuario(usuario_id: int, payload: schemas.UsuarioUpdate, db: AsyncSession = Depends(get_db)):
    return await crud.actualizar_usuario(db, usuario_id, payload)

@router.delete("/{usuario_id}", status_code=status.HTTP_204_NO_CONTENT)
async def borrar_usuario(usuario_id: int, db: AsyncSession = Depends(get_db)):
    usuario = await crud.obtener_usuario(db, usuario_id)

    descripcion = f"Usuario {usuario.nombre} eliminado"

    await crud._registrar_eliminado(db, "usuarios", usuario.id, {"nombre": usuario.nombre})
    await crud.borrar_usuario(db, usuario_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)

@router.get("/historial/eliminados", response_model=List[schemas.HistorialEliminadoRead])
async def historial_usuarios_eliminados(db: AsyncSession = Depends(get_db)):
    return await crud.listar_historial(db)
