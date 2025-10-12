from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from database import get_async_db
import schemas
import crud

router = APIRouter(prefix="/usuarios", tags=["Usuarios"])

@router.post("/", response_model=schemas.UsuarioRead)
async def create_usuario(usuario: schemas.UsuarioCreate, db: AsyncSession = Depends(get_async_db)):
    return await crud.crear_usuario(db, usuario)

@router.get("/", response_model=List[schemas.UsuarioRead])
async def read_usuarios(db: AsyncSession = Depends(get_async_db)):
    return await crud.listar_usuarios(db)

@router.get("/{usuario_id}", response_model=schemas.UsuarioRead)
async def read_usuario(usuario_id: int, db: AsyncSession = Depends(get_async_db)):
    return await crud.obtener_usuario(db, usuario_id)

@router.put("/{usuario_id}", response_model=schemas.UsuarioRead)
async def update_usuario(usuario_id: int, usuario: schemas.UsuarioUpdate, db: AsyncSession = Depends(get_async_db)):
    return await crud.actualizar_usuario(db, usuario_id, usuario)

@router.delete("/{usuario_id}")
async def delete_usuario(usuario_id: int, db: AsyncSession = Depends(get_async_db)):
    await crud.borrar_usuario(db, usuario_id)
    return {"message": "Usuario eliminado"}
