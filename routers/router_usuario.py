from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
from crud import crear_usuario, listar_usuarios, obtener_usuario, actualizar_usuario, borrar_usuario
from schemas import UsuarioCreate, UsuarioUpdate, UsuarioRead

router = APIRouter()

@router.post("/", response_model=UsuarioRead)
def create_usuario(usuario: UsuarioCreate, db: Session = Depends(get_db)):
    return crear_usuario(db, usuario)

@router.get("/", response_model=list[UsuarioRead])
def read_usuarios(db: Session = Depends(get_db)):
    return listar_usuarios(db)

@router.get("/{usuario_id}", response_model=UsuarioRead)
def read_usuario(usuario_id: int, db: Session = Depends(get_db)):
    return obtener_usuario(db, usuario_id)

@router.put("/{usuario_id}", response_model=UsuarioRead)
def update_usuario(usuario_id: int, usuario: UsuarioUpdate, db: Session = Depends(get_db)):
    return actualizar_usuario(db, usuario_id, usuario)

@router.delete("/{usuario_id}")
def delete_usuario(usuario_id: int, db: Session = Depends(get_db)):
    borrar_usuario(db, usuario_id)
    return {"message": "Usuario deleted"}