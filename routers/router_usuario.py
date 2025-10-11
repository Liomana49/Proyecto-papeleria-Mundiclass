from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
import crud, schemas

router = APIRouter()

@router.post("/", response_model=schemas.UsuarioRead)
def create_usuario(usuario: schemas.UsuarioCreate, db: Session = Depends(get_db)):
    return crud.crear_usuario(db, usuario)

@router.get("/", response_model=list[schemas.UsuarioRead])
def read_usuarios(db: Session = Depends(get_db)):
    return crud.listar_usuarios(db)

@router.get("/{usuario_id}", response_model=schemas.UsuarioRead)
def read_usuario(usuario_id: int, db: Session = Depends(get_db)):
    return crud.obtener_usuario(db, usuario_id)

@router.put("/{usuario_id}", response_model=schemas.UsuarioRead)
def update_usuario(usuario_id: int, usuario: schemas.UsuarioUpdate, db: Session = Depends(get_db)):
    return crud.actualizar_usuario(db, usuario_id, usuario)

@router.delete("/{usuario_id}")
def delete_usuario(usuario_id: int, db: Session = Depends(get_db)):
    crud.borrar_usuario(db, usuario_id)
    return {"message": "Usuario deleted"}
